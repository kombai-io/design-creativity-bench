"""Find, capture and embed a page's segments (paper, Appendix "Segment extraction and image capture").

A segment is a container in the rendered page: it holds at least two boxed children and covers at
least 6,000 px of area. Detection is deterministic and calls no model. Every eligible segment is
screenshotted in isolation, letterboxed onto a 1280x448 canvas and embedded with
gemini-embedding-2 (1536 dimensions).

Writes, into the design directory:
  design.csv              every measured element, in the schema pair_scoring reads
  design_with_kid.html    the page with the data-kid stamps the CSV refers to
  segments/<kid>.jpg      one screenshot per eligible segment
  segments/<kid>.npy      its Gemini embedding, shape (1, 1536)
  segments/segment_images.json   capture size and status per segment
"""
from __future__ import annotations

import asyncio
import csv
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys

import numpy as np

from . import element_state
from . import embedding

VIEWPORT = dict(element_state.DEFAULT_VIEWPORT)
MIN_AREA = 6000
MAX_CANDIDATES = 90
JPEG_QUALITY = 85
MAX_CAPTURE_HEIGHT = 6000

MEASURE_JS = """(minArea) => {
  // Not el.children: a <form> exposes its controls as named properties, so a control called
  // "children" (or "length", "elements", ...) shadows the HTMLCollection and the walk dies on
  // "el.children is not iterable". Walking the element siblings is immune to that shadowing.
  const kids = (el) => {
    const out = [];
    for (let c = el.firstElementChild; c; c = c.nextElementSibling) out.push(c);
    return out;
  };
  const walk = (el, path) => {
    el.setAttribute('data-kid', path);
    let i = 0;
    for (const c of kids(el)) { i += 1; walk(c, path ? path + '-' + i : String(i)); }
  };
  let i = 0;
  for (const c of kids(document.body)) { i += 1; walk(c, String(i)); }
  document.body.setAttribute('data-kid', '0');

  const GRAPHIC = new Set(['IMG','VIDEO','SVG','CANVAS','PICTURE','IFRAME','OBJECT']);
  const rows = [];
  for (const el of document.querySelectorAll('[data-kid]')) {
    const kid = el.getAttribute('data-kid');
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const hidden = style.visibility === 'hidden' || style.display === 'none' || parseFloat(style.opacity) < 0.05;
    const boxed = kids(el).filter(c => { const r = c.getBoundingClientRect(); return r.width > 1 && r.height > 1; });
    let childArea = 0;
    for (const c of boxed) { const r = c.getBoundingClientRect(); childArea += r.width * r.height; }
    rows.push({
      kid: kid,
      tag: el.tagName,
      children: el.childElementCount,
      boxed: boxed.length,
      descendants: el.querySelectorAll('*').length,
      depth: kid === '0' ? 0 : kid.split('-').length,
      w: Math.round(rect.width), h: Math.round(rect.height),
      child_area: Math.round(childArea),
      state: hidden ? 'hidden' : (rect.bottom < 0 || rect.top > window.innerHeight * 20 ? 'offscreen' : 'visible'),
      viewport: rect.top < window.innerHeight ? 'first' : 'below',
      graphic: GRAPHIC.has(el.tagName),
      text: (el.innerText || '').length,
      candidate: !GRAPHIC.has(el.tagName) && !hidden && boxed.length >= 2 &&
                 rect.width * rect.height >= minArea && rect.width >= 24 && rect.height >= 16,
      preview: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
               ? '.' + el.className.trim().split(/\\s+/).slice(0, 3).join('.') : '')
    });
  }
  return rows;
}"""

# Expand every internally-scrolling container, deepest first, so an element does not report one
# screenful when it holds a page of content. It runs ONCE over the whole page before any capture,
# rather than per target, because this path
# photographs every anchor from a single page load and per-target expansion would leave each capture
# seeing a different amount of expansion depending on the order it was taken in.
#
# Without it, a shell styled `height:100vh` is captured as 720px while the same design written
# without that rule is captured at its full height - the two are then compared as if one had a
# fraction of the content it actually has.
EXPAND_OVERFLOW_JS = """() => {
  const unclip = (node) => {
    node.style.setProperty("overflow", "visible", "important");
    node.style.setProperty("overflow-x", "visible", "important");
    node.style.setProperty("overflow-y", "visible", "important");
    node.style.setProperty("height", "auto", "important");
    node.style.setProperty("max-height", "none", "important");
  };
  const clips = (n) => n.scrollHeight > n.clientHeight + 1 || n.scrollWidth > n.clientWidth + 1;
  // Reversed document order = deepest first, so a parent is only checked after everything nested
  // inside it has already grown; otherwise the parent is measured before its scrolling descendant
  // expands, looks fine, and is skipped forever.
  const nodes = [...document.querySelectorAll("body *")].reverse();
  let expanded = 0;
  for (const node of nodes) { if (clips(node)) { unclip(node); expanded += 1; } }
  if (clips(document.body)) { unclip(document.body); expanded += 1; }
  return expanded;
}"""

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


async def capture(html_path: Path, kids: list[str], segments_dir: Path) -> list[dict]:
  from playwright.async_api import async_playwright
  results = []
  async with async_playwright() as pw:
    browser = await pw.chromium.launch()
    page = await browser.new_page(viewport=dict(VIEWPORT))
    await page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=40000)
    await page.wait_for_timeout(500)
    await page.evaluate(MEASURE_JS, MIN_AREA)
    expanded = await page.evaluate(EXPAND_OVERFLOW_JS)
    await page.wait_for_timeout(200)
    await page.add_style_tag(content=ISOLATE_CSS)
    for kid in kids:
      box = await page.evaluate(MARK_JS, kid)
      if not box or box["w"] < 1 or box["h"] < 1:
        results.append({"data_kid": kid, "status": "no-box", "width": 0, "height": 0})
        continue
      target = page.locator("[data-target]").first
      clipped = box["h"] > MAX_CAPTURE_HEIGHT
      try:
        if clipped:
          await target.scroll_into_view_if_needed()
          rect = await target.bounding_box()
          shot = await page.screenshot(type="jpeg", quality=JPEG_QUALITY, animations="disabled",
                                       clip={"x": rect["x"], "y": rect["y"], "width": rect["width"],
                                             "height": MAX_CAPTURE_HEIGHT})
        else:
          shot = await target.screenshot(type="jpeg", quality=JPEG_QUALITY, animations="disabled")
      except Exception as error:  # noqa: BLE001
        results.append({"data_kid": kid, "status": f"shot-failed:{type(error).__name__}",
                        "width": box["w"], "height": box["h"]})
        continue
      (segments_dir / f"{kid}.jpg").write_bytes(shot)
      # An element taller than the cap keeps its measured height but only its head is photographed;
      # recording that is the difference between a known limitation and a silent one.
      results.append({"data_kid": kid, "status": "captured", "width": box["w"], "height": box["h"],
                      "clipped": clipped})
    await browser.close()
  results.append({"data_kid": "__expanded__", "status": "note", "width": 0, "height": 0,
                  "detail": f"{expanded} scroll container(s) expanded before capture"})
  return results


def write_csv(path: Path, rows: list[dict], containers: set[str]) -> None:
  """The schema pair_scoring reads, so its eligibility rules apply unchanged.

  Every geometric candidate is a container. Other elements are text (a short run with fewer than
  two boxed children) or other; media elements are graphic.
  """
  with path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["data-kid", "category", "description", "num_children", "depth", "repeated",
                     "state", "descendants", "viewport"])
    for row in rows:
      category = "container" if row["kid"] in containers else (
        "text" if row["text"] and row["boxed"] < 2 else "other")
      if row["graphic"]:
        category = "graphic"
      writer.writerow([row["kid"], category, "", row["boxed"], row["depth"], "no",
                       row["state"], row["descendants"], row["viewport"]])


def embed(segments_dir: Path, results: list[dict], workers: int) -> None:
  genai_client = embedding.client()
  pending = [r for r in results if r["status"] == "captured"]

  def run(row: dict) -> None:
    path = segments_dir / f"{row['data_kid']}.jpg"
    try:
      vector = embedding.embed_bytes(genai_client, embedding.canvas_bytes(path), path.name)
      np.save(segments_dir / f"{row['data_kid']}.npy", vector.astype(np.float32)[None, :])
      row["status"] = "embedded"
    except Exception as error:  # noqa: BLE001
      row["status"] = f"embed-failed:{type(error).__name__}"

  with ThreadPoolExecutor(max_workers=workers) as pool:
    list(pool.map(run, pending))


def build(html: Path, design: Path, workers: int = 8) -> int:
  """Measure, filter, capture and embed one page into `design`. Returns the embedded count."""
  from playwright.async_api import async_playwright
  from . import pair_scoring

  segments_dir = design / "segments"
  segments_dir.mkdir(parents=True, exist_ok=True)

  async def measure() -> tuple[list[dict], str]:
    async with async_playwright() as pw:
      browser = await pw.chromium.launch()
      page = await browser.new_page(viewport=dict(VIEWPORT))
      await page.goto(html.resolve().as_uri(), wait_until="load", timeout=40000)
      await page.wait_for_timeout(500)
      await page.evaluate(MEASURE_JS, MIN_AREA)
      await page.evaluate(EXPAND_OVERFLOW_JS)
      await page.wait_for_timeout(200)
      rows = await page.evaluate(MEASURE_JS, MIN_AREA)
      stamped = await page.evaluate("() => document.documentElement.outerHTML")
      await browser.close()
      return rows, stamped

  rows, stamped = asyncio.run(measure())
  (design / "design_with_kid.html").write_text(stamped, encoding="utf-8")
  candidates = sorted((r for r in rows if r["candidate"]), key=lambda r: -r["w"] * r["h"])[:MAX_CANDIDATES]
  write_csv(design / "design.csv", rows, {r["kid"] for r in candidates})
  eligible = sorted(pair_scoring.eligible_kids(design / "design.csv"))

  results = asyncio.run(capture(html, eligible, segments_dir))
  embed(segments_dir, results, workers)
  by_kid = {r["kid"]: r for r in rows}
  for row in results:
    row["child_area"] = int(by_kid.get(row["data_kid"], {}).get("child_area") or 0)
    row.setdefault("clipped", False)
  manifest = {
    "model": embedding.EMBEDDING_MODEL, "dimensions": embedding.DIMENSIONS,
    "canvas_shape": list(embedding.CANVAS_SHAPE), "canvas_anchor": embedding.CANVAS_ANCHOR,
    "canvas_background": embedding.CANVAS_BACKGROUND, "viewport": VIEWPORT,
    "jpeg_quality": JPEG_QUALITY, "results": results,
  }
  (segments_dir / "segment_images.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")

  # Drop containers whose largest child fills >= 90% of them, then containers with no content.
  for module, args in (("wrapper_filter", [segments_dir, design / "design.csv", "--apply"]),
                       ("content_filter", [design / "design.csv", "--apply"])):
    subprocess.run([sys.executable, "-m", f"dcbench.{module}", *map(str, args)], check=True,
                   stdout=subprocess.DEVNULL, cwd=Path(__file__).resolve().parent.parent)
  return sum(1 for r in results if r["status"] == "embedded")
