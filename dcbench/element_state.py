"""Measure whether each stamped element is part of the page's initial visual state.

The classifier and the segment generator both need to know that an element is a
closed drawer or a selection-only toolbar rather than something the page shows on
load. Geometry answers that half exactly, so it is measured here rather than
guessed: an element either has a layout box the page's own scrolling can reach or
it does not.

Geometry cannot answer the other half. A slide-over hidden with ``display:none``
and a bulk-action bar hidden with ``display:none`` are the same measurement, and
only the surrounding markup says which is which. So this module reports a
mechanism; naming the kind on top of it would take a model, which this pipeline does not call.

  visible    - has a layout box reachable in the page's own scroll space, or is
               shown for whatever it is worth: an empty divider, a flex spacer, an
               <option> its control paints, a ``display:contents`` wrapper
  offscreen  - lays out at full size but parks outside every scroll extent
               (``position:fixed`` slide-overs, off-canvas rails)
  boxless    - the page withholds it at load - ``display:none``, ``visibility:hidden``
               or ``opacity:0``, on the element or on any ancestor

  Only the last two are states a snippet can open. Collapsing the merely-empty in with
  the withheld sends the model after previews that cannot exist: an <option> has no box
  in any state, so every attempt fails and the row still ends up mislabelled.

The same pass answers two questions the similarity weight needs, and answers them
by measurement for the same reason:

  descendants  - how many elements the subtree holds, counted on the live DOM so a
                 list the page's own JavaScript fills counts what it ends up with
                 rather than the empty shell in the markup
  in_viewport  - whether the element's box falls inside the first screenful before
                 anything is scrolled

Run as a script to add those two columns to a classifier CSV written before they
existed - the measurement needs no model, so a backfill is free:

  python -m dcbench.element_state PAGE_with_kid.html PAGE.csv
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import csv
from dataclasses import dataclass
import os
from pathlib import Path
import re
import sys
from typing import Literal


Mechanism = Literal["visible", "offscreen", "boxless"]

VISIBLE: Mechanism = "visible"
OFFSCREEN: Mechanism = "offscreen"
BOXLESS: Mechanism = "boxless"

STATE_VISIBLE = "visible"
STATE_OVERLAY = "overlay"
STATE_CONDITIONAL = "conditional"
STATE_VALUES: tuple[str, ...] = (STATE_VISIBLE, STATE_OVERLAY, STATE_CONDITIONAL)
STATE_LIST = ", ".join(STATE_VALUES)

VIEWPORT_FIRST = "first"
VIEWPORT_BELOW = "below"
VIEWPORT_VALUES: tuple[str, ...] = (VIEWPORT_FIRST, VIEWPORT_BELOW)

DEFAULT_VIEWPORT = {"width": 1280, "height": 720}

# The page itself, as a scorable element. assign_data_kids treats html/body as
# transparent, so nothing normally stands for "the whole design": a run that wraps its
# markup in one <div> gets a page-level element and a run that puts ten siblings
# straight in <body> does not. The pair then has a large element on one side with no
# counterpart on the other, and the scoring charges a full-weight zero for what is only
# a markup convention. Stamping <body> gives both sides the same page-level row.
PAGE_KID = "0"
PAGE_DEPTH = 0
_BODY_TAG_PATTERN = re.compile(r"<body(?![^>]*\bdata-kid=)([^>]*)>", re.IGNORECASE)


def stamp_page_element(html_path: Path) -> bool:
  """Give <body> a data-kid, in place. True when the file was changed.

  Edited as text rather than through a parser: the stamped page is the artifact every
  later stage reads by line and column, and reserialising it would move every one of
  those references.
  """
  text = html_path.read_text(encoding="utf-8", errors="ignore")
  stamped, count = _BODY_TAG_PATTERN.subn(f'<body data-kid="{PAGE_KID}"\\1>', text, count=1)
  if not count:
    return False
  html_path.write_text(stamped, encoding="utf-8")
  return True


# Elements sit still long enough to measure once the page's own load handlers have
# run. Entry animations are the reason for the settle rather than the load event.
SETTLE_MS = 400


@dataclass(frozen=True)
class Measurement:
  """What one pass over the loaded page can say about a stamped element."""

  mechanism: Mechanism
  descendants: int
  in_viewport: bool


_MEASURE_JS = """
() => {
  const out = {};
  const boxed = [];
  const nodes = document.querySelectorAll("[data-kid]");
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  /* Some elements never get a box of their own however visible they are. An <option>
     is painted by the native control, and a display:contents element is replaced by
     its children. Calling either hidden would be wrong twice over: the label lies,
     and a reveal snippet gets commissioned for a state no snippet can reach. */
  const NATIVE_CHILD_TAGS = { OPTION: 1, OPTGROUP: 1 };
  const measurementTarget = (el) => {
    let node = el;
    while (node && NATIVE_CHILD_TAGS[node.tagName] === 1) node = node.parentElement;
    return node || el;
  };

  /* Counted on the element itself rather than on the measurement target: an <option>
     redirects its geometry to the <select>, but its subtree is still its own. Counted
     live, so a table the page fills from a script counts its rows and not the empty
     <tbody> that shipped in the markup. */
  const record = (kid, el, mechanism, inViewport) => {
    out[kid] = {
      mechanism: mechanism,
      descendants: el.querySelectorAll("*").length,
      inViewport: inViewport,
    };
  };

  /* Pass 1 - withheld, or merely empty. Nothing has scrolled yet, so every rect read
     here is already measured against the first screenful, which is the question
     inViewport asks. Reading it later would answer a different one: pass 2 scrolls. */
  for (const el of nodes) {
    const kid = el.getAttribute("data-kid");
    if (!kid || kid in out) continue;
    /* An <option> reports checkVisibility() === false and a zero rect however open its
       control is, so the redirect has to come first: ask about the <select> instead. */
    const subject = measurementTarget(el);
    /* checkVisibility, not a local style read: display:none on an ancestor leaves the
       descendant's own computed display untouched, so reading this element alone would
       call every child of a closed drawer merely collapsed. */
    const withheld = !subject.checkVisibility({
      contentVisibilityAuto: true,
      opacityProperty: true,
      visibilityProperty: true,
    });
    if (withheld) { record(kid, el, "boxless", false); continue; }
    const r = subject.getBoundingClientRect();
    /* Top edge inside the screenful, not the whole box: a main column that starts under
       the header and runs three screens down is exactly the element this is meant to
       weigh up, and an overlap fraction would score it near zero. */
    const inViewport = r.left < vw && r.right > 0 && r.top < vh && r.bottom > 0;
    if (r.width < 1 || r.height < 1) {
      /* Nothing is withholding this one - it is an empty divider, a flex spacer, a
         display:contents wrapper. The page is showing it for whatever it is worth, so
         it is not a hidden state and no snippet could add anything. The generator's
         promote() already stands such a target on its nearest boxed ancestor. */
      record(kid, el, "visible", inViewport);
      continue;
    }
    boxed.push([kid, el, subject, inViewport]);
  }

  /* Pass 2 - reachable or parked. Testing the box against a scroll extent looks
     cheaper but reads the wrong number: an off-canvas panel overflows the document
     and so inflates documentElement.scrollWidth past its own left edge, which makes
     it measure as inside the extent it created. scrollIntoView asks the question
     directly instead - it moves the page or a nested scroller to whatever can be
     reached, and cannot move a fixed element at all - so it is run per element and
     the answer is read from the viewport. */
  const sx = window.scrollX, sy = window.scrollY;
  for (const [kid, el, subject, inViewport] of boxed) {
    try { subject.scrollIntoView({ block: "center", inline: "center" }); } catch (_) { /* ignore */ }
    const r = subject.getBoundingClientRect();
    const onScreen = r.left < window.innerWidth && r.right > 0 && r.top < window.innerHeight && r.bottom > 0;
    /* A parked element was never in the first screenful whatever pass 1 read of it. */
    record(kid, el, onScreen ? "visible" : "offscreen", onScreen && inViewport);
  }
  window.scrollTo(sx, sy);
  return out;
}
"""


_NODE_REQUIRE_PATTERN = re.compile(r"--require(?:=|\s+)(\S+)")


def repair_node_options() -> str | None:
  """Drop ``--require`` preloads from NODE_OPTIONS whose file no longer exists.

  Playwright starts its driver with node, which inherits this process's environment.
  HTTP Toolkit and similar interceptors export a version-pinned ``--require`` preload
  into every shell they open; upgrading or removing the tool leaves that path dangling
  and node then refuses to start at all. Playwright reports the fallout as
  ``Connection closed while reading from the driver``, which reads like a Playwright
  fault and sends you looking in the wrong place entirely.

  Only entries whose file is genuinely gone are dropped, so a working interceptor
  keeps intercepting. Returns what was removed, or None when nothing was wrong.
  """
  options = os.environ.get("NODE_OPTIONS")
  if not options:
    return None

  stale = [match.group(0) for match in _NODE_REQUIRE_PATTERN.finditer(options) if not Path(match.group(1)).exists()]
  if not stale:
    return None

  repaired = options
  for fragment in stale:
    repaired = repaired.replace(fragment, "")
  repaired = " ".join(repaired.split())
  if repaired:
    os.environ["NODE_OPTIONS"] = repaired
  else:
    del os.environ["NODE_OPTIONS"]
  return " ".join(stale)


def measure_elements(html_path: Path, viewport: dict[str, int] | None = None) -> dict[str, Measurement]:
  """Return the load-time measurement for every ``data-kid`` in a stamped page.

  Missing from the result means the kid has no element in the markup at all, which
  is what a ``line:col`` row is: JavaScript builds it, so nothing can be measured.
  """
  from playwright.sync_api import sync_playwright

  repair_node_options()
  size = dict(DEFAULT_VIEWPORT if viewport is None else viewport)
  with sync_playwright() as runner:
    browser = runner.chromium.launch()
    try:
      page = browser.new_page(viewport={"width": int(size["width"]), "height": int(size["height"])})
      page.goto(html_path.resolve().as_uri())
      page.wait_for_timeout(SETTLE_MS)
      raw: dict[str, dict[str, object]] = page.evaluate(_MEASURE_JS)
    finally:
      browser.close()

  return {
    kid: Measurement(
      mechanism=str(entry["mechanism"]),  # type: ignore[arg-type]
      descendants=int(entry["descendants"]),  # type: ignore[arg-type]
      in_viewport=bool(entry["inViewport"]),
    )
    for kid, entry in raw.items()
  }


def viewport_label(measurement: Measurement | None) -> str:
  """The CSV value for one measurement, empty when the element was never measured."""
  if measurement is None:
    return ""
  return VIEWPORT_FIRST if measurement.in_viewport else VIEWPORT_BELOW


def default_state(mechanism: Mechanism | None) -> str:
  """The state to use when no model label is available for a hidden element.

  ``offscreen`` is an overlay often enough to be the better default, and a boxless
  element is far more often a conditional region than a closed panel. Both are only
  the fallback for when no model label exists.
  """
  if mechanism == VISIBLE:
    return STATE_VISIBLE
  if mechanism == OFFSCREEN:
    return STATE_OVERLAY
  return STATE_CONDITIONAL


def reconcile(mechanism: Mechanism | None, model_state: str | None) -> str:
  """Combine the measurement with the model's label, measurement winning.

  Whether the element shows on load is measured, so the model never gets to
  contradict it. The model only chooses between ``overlay`` and ``conditional``
  for an element already measured hidden, which is the part geometry cannot see.
  """
  if mechanism == VISIBLE:
    return STATE_VISIBLE
  if model_state in (STATE_OVERLAY, STATE_CONDITIONAL):
    return model_state
  return default_state(mechanism)


CSV_HEADER = (
  "data-kid",
  "category",
  "description",
  "num_children",
  "depth",
  "repeated",
  "state",
  "descendants",
  "viewport",
)
BASE_CSV_HEADER = CSV_HEADER[:6]
STATE_UNKNOWN = ""

# Every column the measurement added arrived at the end, so a run classified before
# any of them is a prefix of the current header rather than a different shape.
ACCEPTED_CSV_HEADERS = tuple(CSV_HEADER[:count] for count in range(len(BASE_CSV_HEADER), len(CSV_HEADER) + 1))


def check_csv_header(fieldnames: object, source: str) -> None:
  """Accept the classifier header with or without the measured trailing columns.

  Runs classified before ``state``, ``descendants`` and ``viewport`` existed still
  have to load, so their rows come back with those fields empty. Callers treat an
  empty value as "never measured" rather than as visible - guessing visible would
  quietly hand a closed drawer to a preview that cannot show it, which is the
  failure the state column exists to stop.
  """
  actual = tuple(fieldnames or ())
  if actual in ACCEPTED_CSV_HEADERS:
    return
  expected = ",".join(CSV_HEADER)
  raise ValueError(
    f"{source} must start with the exact {expected} header; the trailing "
    f"state, descendants and viewport columns may be omitted for runs classified before they existed"
  )


def with_page_row(rows: list[dict[str, str]]) -> list[dict[str, str]]:
  """Prepend the page row, unless the CSV already carries one.

  It is written rather than classified: <body> is a container by construction, it is
  never repeated, and it is on screen at load by definition, so there is nothing for a
  model to decide. Its child count is the number of depth-1 rows, which is exactly the
  set of stamped elements <body> holds.
  """
  if any((row.get("data-kid") or "").strip() == PAGE_KID for row in rows):
    return rows
  top_level = sum(1 for row in rows if (row.get("depth") or "").strip() == "1")
  page = {
    "data-kid": PAGE_KID,
    "category": "container",
    "description": "",
    "num_children": str(top_level),
    "depth": str(PAGE_DEPTH),
    "repeated": "no",
    "state": STATE_VISIBLE,
    "descendants": "",
    "viewport": "",
  }
  return [page, *rows]


def backfill_csv(html_path: Path, csv_path: Path, viewport: dict[str, int] | None = None) -> int:
  """Add the measured columns to a CSV written before they existed.

  The measurement costs no model calls, so an existing run does not have to be
  reclassified to gain the columns. Rows the measurement cannot reach - the
  ``line:col`` rows JavaScript builds - keep empty values and stay unweighted.
  """
  with csv_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    check_csv_header(reader.fieldnames, str(csv_path))
    rows = list(reader)

  stamp_page_element(html_path)
  rows = with_page_row(rows)
  measurements = measure_elements(html_path, viewport)
  measured = 0
  for row in rows:
    measurement = measurements.get((row.get("data-kid") or "").strip())
    row["descendants"] = "" if measurement is None else str(measurement.descendants)
    row["viewport"] = viewport_label(measurement)
    if measurement is None:
      continue
    measured += 1
    # A CSV old enough to be missing the measured columns is usually missing state
    # too, and leaving it blank would let a closed drawer weigh as much as anything
    # else merely below the fold. reconcile picks the model's label when the row
    # already carries one and falls back to the mechanism when it does not.
    row["state"] = reconcile(measurement.mechanism, (row.get("state") or "").strip() or None)

  with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(CSV_HEADER))
    writer.writeheader()
    for row in rows:
      writer.writerow({column: row.get(column, "") for column in CSV_HEADER})

  return measured


def main(arguments: Sequence[str]) -> int:
  parser = argparse.ArgumentParser(description="Backfill the measured columns of a classifier CSV.")
  parser.add_argument("html_path", type=Path, help="Stamped page (the *_with_kid.html the classifier wrote).")
  parser.add_argument("csv_path", type=Path, help="Classifier CSV to rewrite in place.")
  parsed = parser.parse_args(arguments)

  try:
    measured = backfill_csv(parsed.html_path, parsed.csv_path)
  except (OSError, ValueError) as error:
    print(f"Error: {error}", file=sys.stderr)
    return 1

  print(f"Measured {measured} rows in {parsed.csv_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
