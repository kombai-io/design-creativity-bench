"""Build the paired perturbation dataset a projection trains on (paper, Appendix "Projection dataset, training, and metrics").

  python projection/build_pairs.py --encoder gemini     # -> data/projection/gemini/
  python projection/build_pairs.py --encoder uiclip     # -> data/projection/uiclip/

For every page of the corpus: pick anchor elements by a deterministic containership rule,
screenshot each one in isolation, then apply each edit live and screenshot the same anchors again.
Nuisance edits (viewport, copy, theme, spacing, reflow, type scale, wrapper depth, icon or graphic,
zoom; the UIClip set adds chrome, tone and letterforms) must not change the score; structural edits
(delete, clone, keep first, layout axis, remove layout rules, reorder, flatten, reparent) must.
A structural edit whose screenshot does not visibly change is marked invalid. Every pair carries
its two screenshots, its two vectors, a structural distance and a validity verdict.

No model calls besides the embeddings: stamping, anchor selection, isolation and every edit are
deterministic. Rendering is not bit-stable across machines and browser versions, and the Gemini API
is not byte-stable over time, so a rebuild matches the original dataset statistically rather than
exactly. Gemini embeddings cost about $0.00012 per crop (roughly $11 for the corpus); UIClip runs
locally.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


PILOT_DIR = Path(__file__).resolve().parent.parent
if str(PILOT_DIR) not in sys.path:
  sys.path.insert(0, str(PILOT_DIR))

from dcbench import embedding, uiclip  # noqa: E402

VIEWPORT = {"width": 1280, "height": 800}
MAX_ANCHORS = 16
MIN_AREA = 8000
MAX_CAPTURE_HEIGHT = 6000
JPEG_QUALITY = 85
# A structural pair whose picture did not change is an unlearnable target: no function of the pixels
# can separate two identical screenshots. 
INVISIBLE_DPX = 0.5
MAX_PAGE_HEIGHT_DRIFT = 0.20
# Families exempt from the page-height drift check, because changing height IS the point of them.
# Without the exemption every reflow pair would be thrown away as invalid and the class the corpus
# is missing would stay missing.
DRIFT_EXEMPT = frozenset({"n1_viewport", "n5_reflow", "n6_type_scale", "n9_zoom",
                          "n10_chrome", "n12_letterforms"})

# ---------------------------------------------------------------- JS: stamping, geometry, anchors

STAMP_JS = """() => {
  // Deterministic tree ids, same scheme the rest of the pipeline uses: 1-based child index path.
  const walk = (el, path) => {
    el.setAttribute('data-kid', path);
    let i = 0;
    for (const child of el.children) { i += 1; walk(child, path ? path + '-' + i : String(i)); }
  };
  let i = 0;
  for (const child of document.body.children) { i += 1; walk(child, String(i)); }
  return document.querySelectorAll('[data-kid]').length;
}"""

ANCHOR_JS = """(minArea) => {
  const TEXTISH = new Set(['P','H1','H2','H3','H4','H5','H6','LI','SPAN','A','BUTTON','LABEL',
                           'STRONG','EM','SMALL','CODE','PRE','TD','TH','OPTION','TEXTAREA','INPUT']);
  const GRAPHIC = new Set(['IMG','VIDEO','SVG','CANVAS','PICTURE','IFRAME','OBJECT']);
  const insideGraphic = (el) => {
    for (let n = el.parentElement; n; n = n.parentElement) if (GRAPHIC.has(n.tagName)) return true;
    return false;
  };
  const out = [];
  for (const el of document.querySelectorAll('[data-kid]')) {
    if (TEXTISH.has(el.tagName) || GRAPHIC.has(el.tagName) || insideGraphic(el)) continue;
    const style = getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none' || parseFloat(style.opacity) < 0.05) continue;
    const rect = el.getBoundingClientRect();
    const area = rect.width * rect.height;
    if (area < minArea || rect.width < 24 || rect.height < 16) continue;
    // Composition, not a leaf: at least two element children that themselves have boxes.
    const boxed = [...el.children].filter(c => { const r = c.getBoundingClientRect(); return r.width > 1 && r.height > 1; });
    if (boxed.length < 2) continue;
    // Text-heavy blocks are runs of copy, not compositions.
    const text = (el.innerText || '').length;
    if (text > 0 && area / text < 60) continue;
    out.push({kid: el.getAttribute('data-kid'), w: Math.round(rect.width), h: Math.round(rect.height),
              area: Math.round(area), children: boxed.length,
              depth: el.getAttribute('data-kid').split('-').length});
  }
  return out;
}"""

# Isolation: keep the page's layout but paint only the target and its ancestor chain, so a clip of
# the target is a picture of that component and not of whatever floats over those coordinates.
ISOLATE_CSS = """
body * { visibility: hidden !important; }
[data-anc] { visibility: visible !important; }
[data-target], [data-target] * { visibility: visible !important; }
"""

MARK_JS = """(kid) => {
  document.querySelectorAll('[data-target]').forEach(e => e.removeAttribute('data-target'));
  document.querySelectorAll('[data-anc]').forEach(e => e.removeAttribute('data-anc'));
  const el = document.querySelector(`[data-kid="${kid}"]`);
  if (!el) return null;
  el.setAttribute('data-target', '');
  for (let n = el.parentElement; n; n = n.parentElement) n.setAttribute('data-anc', '');
  const r = el.getBoundingClientRect();
  return {w: Math.round(r.width), h: Math.round(r.height)};
}"""

# Tree shape AND child layout. Counting nodes alone gives a reorder, an axis flip and a
# de-layout a distance of exactly zero - same nodes at the same depths - which is the one thing the
# ranking loss must not see. The normalised child rectangles catch all three.
SIGNATURE_JS = """(kid) => {
  const el = document.querySelector(`[data-kid="${kid}"]`);
  if (!el) return null;
  const nodes = el.querySelectorAll('*');
  const hist = {};
  const depthOf = (n) => { let d = 0; for (let p = n; p && p !== el; p = p.parentElement) d += 1; return d; };
  for (const n of nodes) { const d = depthOf(n); hist[d] = (hist[d] || 0) + 1; }
  const box = el.getBoundingClientRect();
  const layout = [...el.children].map(c => {
    const r = c.getBoundingClientRect();
    return [(r.x - box.x) / Math.max(box.width, 1), (r.y - box.y) / Math.max(box.height, 1),
            r.width / Math.max(box.width, 1), r.height / Math.max(box.height, 1)];
  });
  return {count: nodes.length, hist: hist, children: el.children.length, layout: layout};
}"""

PAGE_HEIGHT_JS = "() => document.documentElement.scrollHeight"

# ---------------------------------------------------------------- perturbations

# Nuisance: applied to the whole page, so every anchor gets a pair from one load.
NUISANCE = {
  "n1_viewport": None,   # handled by resizing the viewport, then checked for breakpoint safety
  "n2_text": """() => {
    const WORDS = ['Harding','Voss','Marlowe','Ansel','Delacroix','Keating','Rowan','Sable'];
    let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const n of nodes) {
      const t = n.nodeValue; if (!t || !t.trim()) continue;
      n.nodeValue = t.replace(/[A-Za-z]{2,}/g, (w) => {
        const pick = WORDS[Math.floor(rnd() * WORDS.length)];
        const out = pick.slice(0, Math.max(2, w.length));
        return w[0] === w[0].toUpperCase() ? out : out.toLowerCase();
      }).replace(/\\d/g, () => String(Math.floor(rnd() * 10)));
    }
    return 'ok';
  }""",
  "n3_theme": """() => {
    const root = document.documentElement; const style = getComputedStyle(root);
    let seed = 987; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    let touched = 0;
    for (const sheet of document.styleSheets) {
      let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
      for (const rule of rules) {
        if (!rule.selectorText || !rule.selectorText.includes(':root')) continue;
        for (const name of rule.style) {
          if (!name.startsWith('--')) continue;
          const value = style.getPropertyValue(name).trim();
          if (/^#|^rgb|^hsl/.test(value)) {
            root.style.setProperty(name, `hsl(${Math.floor(rnd()*360)} ${20+Math.floor(rnd()*60)}% ${20+Math.floor(rnd()*60)}%)`);
            touched += 1;
          }
        }
      }
    }
    return touched ? 'ok' : 'n/a';
  }""",
  # The class the first four families do not contain: same structure, very different height.
  #
  # Every original nuisance preserves geometry - n2 caps each substitute at the original word's
  # length so text cannot reflow, n3 touches only colours, n4 bounds spacing jitter - so the four
  # invariant families sit at a median |dlog h| of 0.00 to 0.03 while the structural families run to
  # 0.49. A model trained on that reasonably concludes that a height difference means a different
  # design, which is wrong on real pages: two designs that made the same layout choice routinely
  # differ by half their height because one has longer copy.
  #
  # The multiplier is drawn PER ELEMENT rather than applied globally. Multiplying every text node by
  # the same factor grows every box together and leaves the layout's proportions intact, which is a
  # global scale change and an easy invariance; varying it per element is what actually changes the
  # proportions, and is also what real copy does.
  #
  # Graded rather than extreme, and the draw is recorded in the return value: the lesson to teach is
  # that height is weak evidence, not that it is no evidence. Some structural families - cloning a
  # child, keeping only the first - change height because they really did change the design, and a
  # model taught to ignore height outright would lose those too.
  #
  # The range stops at 3x, which is measured rather than guessed. Drawing up to 10x did remove the
  # artifact - the fitted geometry premium fell from +0.065 to +0.015 and the height weights flipped
  # sign - but it also taught size invariance wholesale, and the unrelated decision depends on size:
  # one ladder's unrelated-by-construction floor rose from 9.41 to 26.67 and ladder monotonicity fell
  # from 13/15 to 12/15. Capped at 3x, which is about as far as real copy volume varies, the artifact
  # stays suppressed (+0.024) and monotonicity reaches 14/15 - better than either extreme.
  "n5_reflow": """() => {
    const FACTORS = [0.4, 0.7, 1.5, 2.2, 3.0];
    const FILLER = ['operations','throughput','reconciliation','provisioning','allocation',
                    'downstream','settlement','compliance','remediation','onboarding'];
    let seed = 24680; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const hosts = Array.from(document.querySelectorAll('[data-kid]'));
    let touched = 0; const used = [];
    for (const host of hosts) {
      const factor = FACTORS[Math.floor(rnd() * FACTORS.length)];
      const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
      const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
      for (const n of nodes) {
        const t = n.nodeValue; if (!t || !t.trim()) continue;
        if (n.parentElement && n.parentElement.closest('[data-kid]') !== host) continue;
        const words = t.trim().split(/\\s+/);
        const target = Math.max(1, Math.round(words.length * factor));
        const out = [];
        for (let i = 0; i < target; i += 1) {
          out.push(i < words.length ? words[i] : FILLER[Math.floor(rnd() * FILLER.length)]);
        }
        n.nodeValue = out.join(' ');
        touched += 1;
      }
      if (nodes.length) used.push(factor);
    }
    return touched ? 'ok:' + used.length + ':' + Math.min(...used) + '-' + Math.max(...used) : 'n/a';
  }""",
  # Line metrics, not layout: a different family and root size moves every box's height through the
  # type it contains while the tree is untouched.
  "n6_type_scale": """() => {
    const STACKS = ['Georgia, serif', '"Courier New", monospace', 'Verdana, Geneva, sans-serif'];
    let seed = 3141; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    // Every element's own computed size, scaled: setting the root font-size moves nothing here,
    // because generated designs overwhelmingly declare type in px rather than rem, and an em-based
    // rule would compound down the tree instead of scaling it. Same approach n4_spacing takes.
    const factor = 0.8 + rnd() * 0.7;
    const stack = STACKS[Math.floor(rnd() * STACKS.length)];
    const sizes = [];
    for (const el of Array.from(document.querySelectorAll('body, body *'))) {
      sizes.push([el, parseFloat(getComputedStyle(el).fontSize) || 16]);
    }
    for (const [el, size] of sizes) {
      el.style.fontSize = (size * factor).toFixed(2) + 'px';
      el.style.fontFamily = stack;
    }
    return 'ok:' + factor.toFixed(2);
  }""",
  # A wrapper that changes the tree and not the picture. s11_flatten is the negative of this and is
  # labelled structural, so the two together say what the benchmark thinks a wrapper is worth.
  "n7_wrapper_depth": """() => {
    let touched = 0;
    for (const el of Array.from(document.querySelectorAll('[data-kid]'))) {
      const parent = el.parentElement; if (!parent) continue;
      const wrapper = document.createElement('div');
      wrapper.style.display = 'contents';
      parent.insertBefore(wrapper, el);
      wrapper.appendChild(el);
      touched += 1;
    }
    return touched ? 'ok' : 'n/a';
  }""",
  # Decoration, not architecture: swap what the icons and images are without touching where they go.
  "n8_icon_graphic": """() => {
    let seed = 777; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const GLYPHS = ['\u25A0','\u25CF','\u25B2','\u2726','\u2756','\u25C6'];
    let touched = 0;
    for (const svg of Array.from(document.querySelectorAll('svg'))) {
      const span = document.createElement('span');
      span.textContent = GLYPHS[Math.floor(rnd() * GLYPHS.length)];
      const box = svg.getBoundingClientRect();
      span.style.cssText = 'display:inline-block;width:' + Math.max(8, box.width) + 'px;height:'
        + Math.max(8, box.height) + 'px;line-height:1;text-align:center;';
      svg.replaceWith(span); touched += 1;
    }
    for (const img of Array.from(document.querySelectorAll('img'))) {
      img.style.filter = 'grayscale(1) contrast(' + (0.5 + rnd()).toFixed(2) + ')';
      touched += 1;
    }
    return touched ? 'ok' : 'n/a';
  }""",
  # The same page at a different rendering scale, which the reader chose and the design did not.
  "n9_zoom": """() => {
    document.body.style.zoom = '1.25';
    return 'ok';
  }""",
  # The visual language minus colour. Four of the six categorical fields DS scores - corner_style,
  # elevation_style, border_style, heading_weight - were never perturbed by any nuisance, so the
  # projection had never been shown that a rounded corner or a new shadow leaves the architecture
  # alone. It read them as architecture: on a design-system-only ladder, where IA is constant by
  # construction, IA drifted by up to 23 points and moved with DS every time. At a 0.9 IA / 0.1 DS
  # headline that means the design system was counted twice, most of it through the wrong facet.
  #
  # Applied per element from computed styles rather than through :root, both because that is how
  # n4_spacing and n6_type_scale already reach every element and because only 12% of the ladder
  # designs declare anything in :root at all. Layout survives: box-shadow never affects it, and
  # border-width is neutral under the border-box sizing these designs use.
  "n10_chrome": """() => {
    const RADII = ['0px','2px','6px','14px','9999px'];
    const SHADOWS = ['none','0 1px 2px rgba(0,0,0,.08)','0 4px 14px rgba(0,0,0,.12)',
                     '0 10px 30px rgba(0,0,0,.16)'];
    const STYLES = ['solid','dashed','dotted'];
    const WEIGHTS = ['300','400','500','700','800'];
    let seed = 8642; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const pick = (a) => a[Math.floor(rnd() * a.length)];
    let touched = 0;
    for (const el of Array.from(document.querySelectorAll('body, body *'))) {
      const s = getComputedStyle(el);
      if (parseFloat(s.borderTopLeftRadius) > 0 || parseFloat(s.borderTopWidth) > 0
          || s.boxShadow !== 'none') {
        el.style.borderRadius = pick(RADII);
        el.style.boxShadow = pick(SHADOWS);
        if (parseFloat(s.borderTopWidth) > 0) {
          el.style.borderWidth = pick(['1px','2px','3px']);
          el.style.borderStyle = pick(STYLES);
        }
        touched += 1;
      }
      const weight = parseInt(s.fontWeight, 10) || 400;
      if (weight >= 600 || el.matches('h1,h2,h3,h4,h5,h6,th,strong,b')) {
        el.style.fontWeight = pick(WEIGHTS);
        touched += 1;
      }
      el.style.lineHeight = (1.1 + rnd() * 0.7).toFixed(2);
    }
    return touched ? 'ok:' + touched : 'n/a';
  }""",
  # Colour invariance that does not depend on how the colours were declared. n3_theme rewrites
  # :root custom properties, which reaches 96% of the training corpus and 12% of the ladder designs;
  # a filter on the root element recolours whatever actually rendered. hue-rotate is a linear colour
  # matrix, so contrast - and therefore legibility - survives the rotation.
  "n11_tone": """() => {
    let seed = 1618; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    document.documentElement.style.filter =
      'hue-rotate(' + Math.floor(rnd() * 360) + 'deg) saturate(' + (0.6 + rnd() * 0.9).toFixed(2) + ')';
    return 'ok';
  }""",
  # Letterforms: the same words set differently. Tracking and casing are design-system choices that
  # change every text box's width and sometimes its line count, and change no structure at all.
  "n12_letterforms": """() => {
    const TRANSFORMS = ['none','uppercase','capitalize'];
    let seed = 2718; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const tag = document.createElement('style');
    tag.textContent = 'body, body * { letter-spacing: ' + (rnd() * 0.12).toFixed(3) + 'em !important;'
      + ' word-spacing: ' + (rnd() * 0.2).toFixed(3) + 'em !important; }';
    document.head.appendChild(tag);
    for (const el of Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,th,label,button,a'))) {
      el.style.textTransform = TRANSFORMS[Math.floor(rnd() * TRANSFORMS.length)];
    }
    return 'ok';
  }""",
  "n4_spacing": """() => {
    let seed = 5150; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const tag = document.createElement('style'); let css = '';
    for (const el of document.querySelectorAll('[data-kid]')) {
      const s = getComputedStyle(el);
      const jitter = (v) => { const n = parseFloat(v) || 0; return Math.max(0, Math.round(n * (0.6 + rnd() * 0.8))) + 'px'; };
      el.style.padding = [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft].map(jitter).join(' ');
      el.style.margin = [s.marginTop, s.marginRight, s.marginBottom, s.marginLeft].map(jitter).join(' ');
      if (s.gap && s.gap !== 'normal') el.style.gap = jitter(s.gap);
    }
    return 'ok';
  }""",
}

# Structural: applied to a set of mutually disjoint anchors in one pass, so one load serves many.
STRUCTURAL = {
  "s1_delete": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const sig = {}; for (const c of e.children) { const k = c.tagName + '.' + c.className; sig[k] = (sig[k]||[]); sig[k].push(c); }
    const run = Object.values(sig).sort((a,b)=>b.length-a.length)[0];
    if (!run || run.length < 2) return 'n/a';
    const drop = Math.max(1, Math.floor(run.length / 2));
    for (let i = 0; i < drop; i++) run[run.length - 1 - i].remove();
    return 'ok';
  }""",
  "s2_clone": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const sig = {}; for (const c of e.children) { const k = c.tagName + '.' + c.className; sig[k] = (sig[k]||[]); sig[k].push(c); }
    const run = Object.values(sig).sort((a,b)=>b.length-a.length)[0];
    if (!run || run.length < 2) return 'n/a';
    for (let i = 0; i < run.length; i++) e.appendChild(run[i].cloneNode(true));
    return 'ok';
  }""",
  "s4_axis": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const s = getComputedStyle(e);
    if (s.display === 'flex' || s.display === 'inline-flex') {
      e.style.flexDirection = (s.flexDirection.startsWith('column')) ? 'row' : 'column';
      e.style.flexWrap = 'wrap'; return 'ok';
    }
    if (s.display === 'grid') {
      const cols = s.gridTemplateColumns.split(' ').filter(Boolean).length;
      e.style.gridTemplateColumns = cols > 1 ? `repeat(${Math.max(1, cols - 1)}, 1fr)` : 'repeat(3, 1fr)';
      return 'ok';
    }
    return 'n/a';
  }""",
  "s6_unlayout": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const s = getComputedStyle(e);
    if (s.display !== 'flex' && s.display !== 'inline-flex' && s.display !== 'grid') return 'n/a';
    e.style.display = 'block'; return 'ok';
  }""",
  "s3_keep_first": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const k = [...e.children]; if (k.length < 3) return 'n/a';
    for (let i = 1; i < k.length; i++) k[i].remove();
    return 'ok';
  }""",
  "s7_order": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const k = [...e.children]; if (k.length < 2) return 'n/a';
    k.reverse().forEach(c => e.appendChild(c)); return 'ok';
  }""",
  "s11_flatten": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const c = [...e.children].find(n => n.children.length > 1); if (!c) return 'n/a';
    c.replaceWith(...c.children); return 'ok';
  }""",
  "s12_reparent": """(kid) => {
    const e = document.querySelector(`[data-kid="${kid}"]`); if (!e) return 'n/a';
    const k = [...e.children]; if (k.length < 2) return 'n/a';
    k[0].appendChild(k[k.length - 1]); return 'ok';
  }""",
}
VIEWPORT_WIDTHS = (1120, 1440)
# The Gemini dataset was built before these three nuisance families existed; the UIClip one with them.
UICLIP_ONLY = frozenset({"n10_chrome", "n11_tone", "n12_letterforms"})


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--encoder", choices=("gemini", "uiclip"), required=True)
  parser.add_argument("--corpus", type=Path, default=PILOT_DIR / "data/projection/corpus/html")
  parser.add_argument("--out", type=Path, help="default: data/projection/<encoder>")
  parser.add_argument("--pages", type=int, help="Limit to this many pages (for a pilot)")
  parser.add_argument("--max-anchors", type=int, default=MAX_ANCHORS)
  parser.add_argument("--max-workers", type=int, default=6, help="Concurrent browser contexts")
  parser.add_argument("--embed-workers", type=int, default=16)
  parser.add_argument("--seed", type=int, default=7)
  parser.add_argument("--skip-existing", action="store_true")
  parser.add_argument("--embed-only", action="store_true",
                      help="Embed whatever is already captured and rebuild the pair index, no browser. "
                           "Lets embedding overlap a long capture instead of queueing behind it.")
  return parser.parse_args()


def choose_anchors(rows: list[dict], cap: int, rng: random.Random) -> list[dict]:
  """Cap anchors per page, stratified by area so it is not all page-level containers."""
  if len(rows) <= cap:
    return rows
  ordered = sorted(rows, key=lambda r: -r["area"])
  big = ordered[: cap // 3]
  rest = ordered[cap // 3:]
  return big + rng.sample(rest, cap - len(big))


def disjoint_groups(anchors: list[dict]) -> list[list[dict]]:
  """Partition anchors into groups where no member is an ancestor of another.

  One pass can edit every member of a group at once without the edits interfering. The pilot used a
  single maximal disjoint set and got 4-13 structural pairs per family against 197-394 nuisance
  ones; covering every anchor across a few groups fixes that imbalance, at one extra page load per
  group per family.
  """
  remaining = sorted(anchors, key=lambda r: r["depth"])
  groups: list[list[dict]] = []
  while remaining:
    group: list[dict] = []
    leftover: list[dict] = []
    for row in remaining:
      kid = row["kid"]
      if any(kid.startswith(k["kid"] + "-") or k["kid"].startswith(kid + "-") for k in group):
        leftover.append(row)
      else:
        group.append(row)
    groups.append(group)
    remaining = leftover
  return groups


def signature_distance(before: dict | None, after: dict | None) -> float:
  """Computed structural distance: tree-shape change plus child-layout movement.

  Both terms are needed. Tree shape alone scores a reorder, an axis flip and a de-layout at zero,
  since none of them adds or removes a node. Layout alone misses a deletion that leaves the
  survivors where they were. The layout term is normalised by the anchor's own box, so it measures
  rearrangement rather than resizing of the whole element.
  """
  if not before or not after:
    return 0.0
  hist_keys = set(before["hist"]) | set(after["hist"])
  shape = abs(after["count"] - before["count"]) \
      + sum(abs(int(after["hist"].get(k, 0)) - int(before["hist"].get(k, 0))) for k in hist_keys) \
      + abs(after["children"] - before["children"])
  left, right = before.get("layout") or [], after.get("layout") or []
  shared = min(len(left), len(right))
  moved = sum(abs(l - r) for i in range(shared) for l, r in zip(left[i], right[i]))
  moved += 2.0 * abs(len(left) - len(right))
  return float(shape + 10.0 * moved)


async def capture_anchor(page, kid: str, quality: int) -> tuple[bytes | None, tuple[int, int], str]:
  box = await page.evaluate(MARK_JS, kid)
  if not box or box["w"] < 1 or box["h"] < 1:
    return None, (0, 0), "no-box"
  target = page.locator("[data-target]").first
  try:
    if box["h"] > MAX_CAPTURE_HEIGHT:
      await target.scroll_into_view_if_needed()
      rect = await target.bounding_box()
      shot = await page.screenshot(type="jpeg", quality=quality, animations="disabled",
                                   clip={"x": rect["x"], "y": rect["y"], "width": rect["width"],
                                         "height": MAX_CAPTURE_HEIGHT})
    else:
      shot = await target.screenshot(type="jpeg", quality=quality, animations="disabled")
  except Exception as error:  # noqa: BLE001 - recorded, not raised
    return None, (box["w"], box["h"]), f"shot-failed:{type(error).__name__}"
  return shot, (box["w"], box["h"]), "ok"


def mean_abs_dpx(a: bytes, b: bytes) -> float | None:
  from PIL import Image
  ia, ib = Image.open(io.BytesIO(a)).convert("L"), Image.open(io.BytesIO(b)).convert("L")
  if ia.size != ib.size:
    return None
  return float(np.abs(np.asarray(ia, np.float32) - np.asarray(ib, np.float32)).mean())


async def process_page(browser, html_path: Path, model: str, out_root: Path, args) -> dict:
  page_id = f"{model}/{html_path.stem}"
  page_dir = out_root / "pages" / model / html_path.stem
  views_dir = page_dir / "views"
  if args.skip_existing and (page_dir / "page.meta.json").is_file():
    return {"page_id": page_id, "status": "skipped"}
  views_dir.mkdir(parents=True, exist_ok=True)
  rng = random.Random(f"{args.seed}:{page_id}")
  rows: list[dict] = []
  shots: dict[tuple[str, str], bytes] = {}

  page = await browser.new_page(viewport=dict(VIEWPORT))
  try:
    await page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=30000)
    await page.wait_for_timeout(400)
    await page.evaluate(STAMP_JS)
    anchors = choose_anchors(await page.evaluate(ANCHOR_JS, MIN_AREA), args.max_anchors, rng)
    if not anchors:
      await page.close()
      return {"page_id": page_id, "status": "no-anchors"}
    base_height = await page.evaluate(PAGE_HEIGHT_JS)
    await page.add_style_tag(content=ISOLATE_CSS)
    base_sig = {}
    for row in anchors:
      base_sig[row["kid"]] = await page.evaluate(SIGNATURE_JS, row["kid"])
      shot, size, status = await capture_anchor(page, row["kid"], JPEG_QUALITY)
      if shot:
        shots[("base", row["kid"])] = shot
        row["base_size"] = size
    await page.close()

    # ---- nuisance views: one page load each, every anchor re-captured
    for family, js in NUISANCE.items():
      if args.encoder == "gemini" and family in UICLIP_ONLY:
        continue
      widths = VIEWPORT_WIDTHS if family == "n1_viewport" else (VIEWPORT["width"],)
      for width in widths:
        view = f"{family}_{width}" if family == "n1_viewport" else family
        page = await browser.new_page(viewport={"width": width, "height": VIEWPORT["height"]})
        try:
          await page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=30000)
          await page.wait_for_timeout(300)
          await page.evaluate(STAMP_JS)
          status = "ok"
          if js is not None:
            status = await page.evaluate(js)
          # startswith, not equality: a family may return diagnostics after the verdict - n5_reflow
          # reports how many elements it touched and the range of multipliers it drew - and an exact
          # match silently threw away every page of it.
          if not str(status).startswith("ok"):
            await page.close(); continue
          await page.wait_for_timeout(250)
          height = await page.evaluate(PAGE_HEIGHT_JS)
          drift = abs(height - base_height) / max(base_height, 1)
          await page.add_style_tag(content=ISOLATE_CSS)
          for row in anchors:
            if ("base", row["kid"]) not in shots:
              continue
            shot, size, cap_status = await capture_anchor(page, row["kid"], JPEG_QUALITY)
            reject = None
            if not shot:
              reject = cap_status
            elif family not in DRIFT_EXEMPT and drift > MAX_PAGE_HEIGHT_DRIFT:
              reject = f"page-height-drift:{drift:.2f}"
            if shot:
              shots[(view, row["kid"])] = shot
            rows.append({"kid": row["kid"], "view": view, "family": family, "polarity": "invariant",
                         "struct_distance": 0.0, "size_a": row["base_size"], "size_b": list(size),
                         "valid": reject is None, "reject_reason": reject})
        finally:
          if not page.is_closed():
            await page.close()

    # ---- structural views: one load per family, edit every mutually disjoint anchor
    groups = disjoint_groups([r for r in anchors if ("base", r["kid"]) in shots])
    for family, js in STRUCTURAL.items():
     for editable in groups:
      page = await browser.new_page(viewport=dict(VIEWPORT))
      try:
        await page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=30000)
        await page.wait_for_timeout(300)
        await page.evaluate(STAMP_JS)
        applied = []
        for row in editable:
          status = await page.evaluate(f"(kid) => ({js})(kid)", row["kid"])
          if status == "ok":
            applied.append(row)
        if not applied:
          await page.close(); continue
        await page.wait_for_timeout(250)
        height = await page.evaluate(PAGE_HEIGHT_JS)
        drift = abs(height - base_height) / max(base_height, 1)
        await page.add_style_tag(content=ISOLATE_CSS)
        for row in applied:
          after_sig = await page.evaluate(SIGNATURE_JS, row["kid"])
          shot, size, cap_status = await capture_anchor(page, row["kid"], JPEG_QUALITY)
          distance = signature_distance(base_sig.get(row["kid"]), after_sig)
          # No page-height check here: a structural edit is SUPPOSED to change the page, and
          # rejecting on drift threw away the strongest examples in the pilot.
          reject = None
          if not shot:
            reject = cap_status
          else:
            delta = mean_abs_dpx(shots[("base", row["kid"])], shot)
            if delta is not None and delta < INVISIBLE_DPX:
              reject = f"invisible:{delta:.3f}"
          if shot:
            shots[(family, row["kid"])] = shot
          rows.append({"kid": row["kid"], "view": family, "family": family, "polarity": "structural",
                       "struct_distance": distance, "size_a": row["base_size"], "size_b": list(size),
                       "valid": reject is None, "reject_reason": reject})
      finally:
        if not page.is_closed():
          await page.close()
  except Exception as error:  # noqa: BLE001 - one bad page must not stop the run
    if not page.is_closed():
      await page.close()
    return {"page_id": page_id, "status": f"failed:{type(error).__name__}:{str(error)[:120]}"}

  # ---- write the images
  for (view, kid), data in shots.items():
    path = views_dir / view / f"{kid}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
  (page_dir / "page.meta.json").write_text(json.dumps({
    "page_id": page_id, "model": model, "source": str(html_path),
    "source_sha1": hashlib.sha1(html_path.read_bytes()).hexdigest(),
    "anchors": anchors, "base_height": base_height,
    "anchor_rule": {"min_area": MIN_AREA, "max_anchors": args.max_anchors,
                    "rule": "2+ boxed element children, not textish/graphic, visible, area>=min"},
    "views": sorted({v for v, _ in shots}),
  }, indent=2) + "\n", encoding="utf-8")
  (page_dir / "pairs.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
  return {"page_id": page_id, "status": "ok", "anchors": len(anchors), "pairs": len(rows),
          "shots": len(shots)}


async def capture_all(pages: list[tuple[Path, str]], args) -> list[dict]:
  from playwright.async_api import async_playwright
  results = []
  async with async_playwright() as pw:
    browser = await pw.chromium.launch()
    semaphore = asyncio.Semaphore(args.max_workers)

    async def bounded(item):
      html_path, model = item
      async with semaphore:
        result = await process_page(browser, html_path, model, args.out, args)
        results.append(result)
        if len(results) % 10 == 0:
          ok = sum(1 for r in results if r["status"] == "ok")
          print(f"  [capture] {len(results)}/{len(pages)} pages, {ok} ok", flush=True)
        return result

    await asyncio.gather(*(bounded(item) for item in pages))
    await browser.close()
  return results


def embed_all(out_root: Path, workers: int, encoder: str) -> int:
  """Embed every captured clip: Gemini on the 1280x448 canvas, or UIClip on the native-scale pad."""
  jobs = sorted(p for p in out_root.rglob("views/*/*.jpg") if not p.with_suffix(".npy").is_file())
  print(f"[embed] {len(jobs)} clip(s) with {encoder}", flush=True)
  if encoder == "uiclip":
    model = uiclip.Local()
    for start in range(0, len(jobs), 512):
      batch = jobs[start:start + 512]
      for path, vector in zip(batch, model.embed([uiclip.shape_pad_native(p) for p in batch])):
        np.save(path.with_suffix(".npy"), vector.astype(np.float32))
      print(f"  [embed] {min(start + 512, len(jobs))}/{len(jobs)}", flush=True)
    return 0
  client = embedding.client()
  done = failed = 0

  def run(path: Path) -> bool:
    try:
      vector = embedding.embed_bytes(client, embedding.canvas_bytes(path), path.name)
      np.save(path.with_suffix(".npy"), vector.astype(np.float32))
      return True
    except Exception as error:  # noqa: BLE001
      print(f"  [embed] failed {path.name}: {type(error).__name__}", flush=True)
      return False

  with ThreadPoolExecutor(max_workers=workers) as pool:
    for index, ok in enumerate(pool.map(run, jobs), 1):
      done += 1 if ok else 0
      failed += 0 if ok else 1
      if index % 500 == 0:
        print(f"  [embed] {index}/{len(jobs)}", flush=True)
  print(f"[embed] {done} embedded, {failed} failed")
  return failed


def write_pairs_index(out_root: Path) -> int:
  """One JSONL row per pair, with paths to both screenshots and both vectors."""
  lines, kept = [], 0
  for meta_path in sorted(out_root.rglob("page.meta.json")):
    page_dir = meta_path.parent
    meta = json.loads(meta_path.read_text())
    pairs_path = page_dir / "pairs.json"
    if not pairs_path.is_file():
      continue
    for row in json.loads(pairs_path.read_text()):
      base_jpg = page_dir / "views/base" / f"{row['kid']}.jpg"
      view_jpg = page_dir / "views" / row["view"] / f"{row['kid']}.jpg"
      base_npy, view_npy = base_jpg.with_suffix(".npy"), view_jpg.with_suffix(".npy")
      if not (base_npy.is_file() and view_npy.is_file()):
        continue
      lines.append(json.dumps({
        "page_id": meta["page_id"], "model": meta["model"], "kid": row["kid"],
        "view": row["view"], "family": row["family"], "polarity": row["polarity"],
        "struct_distance": row["struct_distance"], "valid": row["valid"],
        "reject_reason": row["reject_reason"],
        "size_a": row["size_a"], "size_b": row["size_b"],
        "jpg_a": str(base_jpg.relative_to(out_root)), "jpg_b": str(view_jpg.relative_to(out_root)),
        "npy_a": str(base_npy.relative_to(out_root)), "npy_b": str(view_npy.relative_to(out_root)),
      }))
      kept += 1
  (out_root / "pairs").mkdir(parents=True, exist_ok=True)
  (out_root / "pairs/pairs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
  return kept


def main() -> None:
  args = parse_args()
  args.out = args.out or PILOT_DIR / "data/projection" / args.encoder
  args.out.mkdir(parents=True, exist_ok=True)
  if args.embed_only:
    failed = embed_all(args.out, args.embed_workers, args.encoder)
    kept = write_pairs_index(args.out)
    print(f"{kept} pairs indexed, {failed} embed failure(s)")
    return

  pages = [(p, p.parent.name) for p in sorted(args.corpus.glob("*/*.html"))]
  random.Random(args.seed).shuffle(pages)
  if args.pages:
    pages = pages[: args.pages]
  print(f"{len(pages)} page(s) from {args.corpus}")

  results = asyncio.run(capture_all(pages, args))
  status = {}
  for row in results:
    status[row["status"].split(":")[0]] = status.get(row["status"].split(":")[0], 0) + 1
  print("capture:", status)
  for row in results:
    if row["status"] not in ("ok", "skipped"):
      print(f"  {row['page_id']}: {row['status']}")

  failed = embed_all(args.out, args.embed_workers, args.encoder)
  kept = write_pairs_index(args.out)
  families = sorted(f for f in NUISANCE if args.encoder == "uiclip" or f not in UICLIP_ONLY)
  manifest = {
    "pages": len(pages), "capture_status": status,
    "embed_failures": failed, "pairs": kept,
    "encoder": args.encoder,
    "embedding_model": embedding.EMBEDDING_MODEL if args.encoder == "gemini" else uiclip.MODEL,
    "nuisance_families": families, "structural_families": sorted(STRUCTURAL),
    "invisible_dpx_threshold": INVISIBLE_DPX, "max_page_height_drift": MAX_PAGE_HEIGHT_DRIFT,
  }
  (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
  print(f"{kept} pairs -> {args.out/'pairs/pairs.jsonl'}")


if __name__ == "__main__":
  main()
