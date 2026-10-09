"""Shared pair-scoring machinery: which segments are scored, their weights, and the assignment.

Everything here is independent of *how* a segment was turned into a vector. The weight comes from
what ``element_state.py`` measured on the loaded page, and the assignment is a minimum-sum
one-to-one match over a similarity matrix built elsewhere (similarity.py).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path

from . import element_state
import numpy as np


# How much each matched segment counts toward the pair's overall score. The two
# measured signals stand for the two halves of "this element matters": how much of
# the page it holds, and whether a reader meets it before scrolling. They multiply
# rather than add, so a large element parked below the fold and a small one at the
# top both land in the middle, and only something both large and immediately visible
# carries full weight.
#
# Position, applied to a segment already sized:
POSITION_IN_VIEWPORT = 1.0
POSITION_BELOW_FOLD = 0.6
# Overlays and conditional regions are design decisions too, but they are not part of
# the page as it arrives, so they weigh least.
POSITION_HIDDEN = 0.1
# A line:col row, or any row from a CSV written before the columns existed. Sitting it
# between the two measured positions keeps an unmeasured run scoring rather than
# quietly collapsing to zero.
POSITION_UNMEASURED = 0.6
SIZE_UNMEASURED = 0.5

# A design's total importance is capped. Without a cap the only way to read a weighted sum is
# either as an un-normalised total, which a long page inflates by having more sections, or as a
# mean over matched rows, which charges nothing at all for content the other design never answers.
# Both were tried and both are gameable in the same direction: add sections, score better.
#
# Instead every element gets an intrinsic r = size x position that does not depend on its
# counterpart, R = Sigma(r) for the design, and the weights are scaled by min(1, B / R) so that
# Sigma(w) = min(R, B) <= B. A short design may carry little importance; a long one cannot carry
# more than B, so extra sections dilute the weight of the real ones instead of adding to it.
#
# B mostly cancels: when both designs are over budget the scale factor appears in numerator and
# denominator alike, and when both are under it never appears. Its real job is to decide which
# regime a pair is compared in - absolute importance below it, normalised shares above. Measured
# over 917 designs, R has median 6.82, so 5.4 puts roughly 70% of them on shares.
IMPORTANCE_BUDGET = 5.4
# Below-fold content may not carry more than this share of any design's weight. Applied relative to
# the design's own viewport mass rather than as a fixed slice of the budget: a fixed slice bounds
# only the absolute mass, so any design under budget could still spend most of its weight below the
# fold. Scaling below-fold weights by min(1, R_viewport / R_below) at a 0.5 share bounds the share
# unconditionally, and because the pair weight is min(w_A, w_B) and the denominator is
# max(Sigma w_A, Sigma w_B), it bounds below-fold's contribution to the reported percentage too.
#
# Safe on this corpus: viewport mass has minimum 1.000 over 917 designs, so the ratio never
# collapses a page. Only 13% of designs exceed a 0.5 below-fold share, so the cap bites the long
# fluffy tail it is aimed at and is a no-op elsewhere.
BELOW_FOLD_SHARE = 0.5
# A matched pair is kept only if its similarity clears this. Below it the assignment prefers to
# leave both elements unmatched, which is what stops two unrelated pages force-matching every
# element and reporting the extreme-value draw as agreement.
#
# Calibrated on the held-out validation pages under the deployed projection: 6,094 invariant
# positives against 4,000 unrelated cross-page pairs. F1 peaks at 0.45 (0.9934) on a plateau
# running 0.35-0.55, keeping 99.6% of true matches while rejecting 99.1% of unrelated ones.
# Structural pairs mostly survive (89%), which is correct - a structural pair is a real
# correspondence whose layout changed, and scoring it as non-existent would count the change twice.
NULL_SIMILARITY = 0.45


# One screenful is as large as an element usefully gets: past that a reader has to
# scroll, and a column three screens tall is not three times the design decision that a
# one-screen column is. Capping there stops a single long page section from being the
# only row that carries any weight.
VIEWPORT_AREA = element_state.DEFAULT_VIEWPORT["width"] * element_state.DEFAULT_VIEWPORT["height"]

PILOT_DIR = Path(__file__).resolve().parent


def children_by_parent(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
  """Direct children of each container, read off the tree ids.

  A tree id is a path of 1-based child positions, so "1-2-3" hangs off "1-2" by string
  alone. Two ids sit outside that: a line:col row names an element JavaScript builds,
  which has no tree position, and the page row is the root - the depth-1 rows are its
  children even though they are not named "0-1", "0-2".
  """
  by_parent: dict[str, list[dict[str, str]]] = {}
  for row in rows:
    data_kid = (row.get("data-kid") or "").strip()
    if not data_kid or ":" in data_kid or data_kid == element_state.PAGE_KID:
      continue
    parent = data_kid.rsplit("-", 1)[0] if "-" in data_kid else element_state.PAGE_KID
    by_parent.setdefault(parent, []).append(row)
  return by_parent


def one_visible_child(children: list[dict[str, str]]) -> bool:
  """Whether a container shows exactly one child and keeps the rest back.

  Such a container is a wrapper around a single visible thing: its screenshot is that
  child's screenshot plus padding, so scoring both counts the same pixels twice and
  gives a wrapper the weight of the component it holds. The hidden siblings are what
  make its child count look like a composition when it is not one.
  """
  visible = sum(1 for row in children if (row.get("state") or "").strip() == element_state.STATE_VISIBLE)
  withheld = sum(1 for row in children if (row.get("state") or "").strip() in (element_state.STATE_OVERLAY, element_state.STATE_CONDITIONAL))
  return visible == 1 and withheld >= 1


def page_wraps_single_visible_container(children: list[dict[str, str]]) -> bool:
  """Whether the synthetic PAGE row should promote its only visible container child.

  A normal row's ``num_children`` is its direct element-child count, so the eligibility
  gate already drops an ordinary unary wrapper. PAGE is exceptional: normalized
  classification records the total stamped-tag count there to ensure a page-level row
  exists. Use the tree ids to recover its real direct children. When exactly one visible
  child is itself a container, PAGE adds no composition boundary; excluding it lets the
  ordinary child-count gate continue through the unary chain to the first branching node.
  """
  visible = [
    row for row in children
    if (row.get("state") or "").strip() == element_state.STATE_VISIBLE
  ]
  return len(visible) == 1 and (visible[0].get("category") or "").strip() == "container"


def eligible_kids(csv_path: Path) -> set[str]:
  """The rows worth scoring: containers that actually hold a composition.

  Pure CSV logic. Leaf text and icons are excluded because a screenshot of one carries almost nothing
  the parent's screenshot does not already carry, ``repeat_others`` rows are excluded
  because scoring the second through twentieth identical table row would weigh one
  repeated component twenty times, and a container showing a single child while
  withholding the rest is excluded because it is a wrapper, not a composition.
  Anything inside a ``graphic`` is excluded too - see below.
  """
  with csv_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    if reader.fieldnames is None or "data-kid" not in reader.fieldnames:
      raise ValueError(f"Missing data-kid column in {csv_path}")
    rows = list(reader)

  by_parent = children_by_parent(rows)

  # A graphic is one picture, however many elements were needed to draw it. Scoring its insides
  # asks whether two designs agree about a label printed on a drawn coffee packet, which is not a
  # question about their designs, and it is where the classifier is least sure of itself - the
  # inside of an illustration is exactly where shape, container and text are hardest to tell
  # apart. Everything below a graphic is dropped, so the picture is compared as a picture.
  graphics = {
    (row.get("data-kid") or "").strip()
    for row in rows
    if (row.get("category") or "").strip() == "graphic" and (row.get("data-kid") or "").strip()
  }

  kids: set[str] = set()
  for row in rows:
    data_kid = (row.get("data-kid") or "").strip()
    if not data_kid or (row.get("category") or "").strip() != "container":
      continue
    if data_kid == element_state.PAGE_KID and page_wraps_single_visible_container(by_parent.get(data_kid, [])):
      continue
    if any(data_kid.startswith(f"{graphic}-") for graphic in graphics):
      continue
    if (row.get("repeated") or "").strip() == "repeat_others":
      continue
    try:
      num_children = int((row.get("num_children") or "").strip())
    except ValueError:
      continue
    if not (num_children > 1 or num_children == -1):
      continue
    if one_visible_child(by_parent.get(data_kid, [])):
      continue
    kids.add(data_kid)
  return kids


@dataclass(frozen=True)
class Geometry:
  """What the classifier measured about one element on the loaded page.

  ``descendants`` and ``in_viewport`` are ``None`` for a row nothing could measure:
  a ``line:col`` element JavaScript writes at runtime, or any row from a CSV
  written before ``element_state`` measured those columns.
  """

  descendants: int | None
  in_viewport: bool | None
  state: str
  # Rendered area of the captured element, floored by its children and capped at one
  # screen. None when nothing measured it.
  area: int | None = None


def has_geometry(entry: Geometry | None) -> bool:
  """Whether this element was measured well enough to carry a weight.

  A segment missing its geometry used to score anyway, on fallback constants: no
  stretch decay, a neutral size, a neutral position. That is the worst of the options -
  it does not merely lose information, it invents a plausible-looking row and lets it
  pull the weighted mean around. Such a row is dropped before the assignment instead,
  so a gap in measurement shows up as a smaller matched count rather than as a score.
  """
  return entry is not None and entry.area is not None and entry.area > 0 and entry.in_viewport is not None


def read_areas(segments_dir: Path) -> dict[str, int]:
  """Effective area per data-kid, from the manifest segments.py wrote.

  Area comes from the capture rather than from the page at load: an overlay or a tab
  panel is unhidden before its screenshot, so the capture is the only place its real
  size is ever known - on the live page it has no box at all.
  """
  manifest = segments_dir / "segment_images.json"
  if not manifest.is_file():
    return {}
  areas: dict[str, int] = {}
  for row in json.loads(manifest.read_text(encoding="utf-8")).get("results", []):
    own = int(row.get("width") or 0) * int(row.get("height") or 0)
    area = effective_area(own, int(row.get("child_area") or 0))
    if area:
      areas[row["data_kid"]] = area
  return areas


def read_geometry(csv_path: Path, segments_dir: Path | None = None) -> dict[str, Geometry]:
  """Load the measured columns the segment weight is built from."""
  areas = read_areas(segments_dir) if segments_dir is not None else {}
  with csv_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    if reader.fieldnames is None or "data-kid" not in reader.fieldnames:
      raise ValueError(f"Missing data-kid column in {csv_path}")

    geometry: dict[str, Geometry] = {}
    for row in reader:
      data_kid = (row.get("data-kid") or "").strip()
      if not data_kid:
        continue
      raw_descendants = (row.get("descendants") or "").strip()
      raw_viewport = (row.get("viewport") or "").strip()
      geometry[data_kid] = Geometry(
        descendants=int(raw_descendants) if raw_descendants.isdigit() else None,
        in_viewport=(raw_viewport == element_state.VIEWPORT_FIRST) if raw_viewport in element_state.VIEWPORT_VALUES else None,
        state=(row.get("state") or "").strip(),
        area=areas.get(data_kid),
      )
  return geometry


def effective_area(own_area: int | None, child_area: int | None) -> int | None:
  """The area an element really occupies, floored by its children and capped at a screen.

  Its own bounding rect is the obvious measure and is wrong in one common case: a
  wrapper a few pixels tall whose children overflow or are positioned outside it reads
  as nothing at all. Taking the larger of the two keeps such a container sized by what
  it holds, and the cap keeps a very long section from swamping the pair.
  """
  if own_area is None and child_area is None:
    return None
  return min(VIEWPORT_AREA, max(own_area or 0, child_area or 0))


def size_factor(area: int | None, _max_area: int = 0) -> float:
  """The literal share of one viewport covered by this element.

  A segment covering x% of the viewport receives x/100, and anything covering at
  least one viewport receives 1.0. ``_max_area`` remains only so flat and experimental
  weight functions share a signature; this size term is fixed, not pair-relative.
  """
  if area is None:
    return SIZE_UNMEASURED
  return min(1.0, max(area, 0) / VIEWPORT_AREA)


def position_factor(in_viewport: bool | None, state: str) -> float:
  """How early a reader meets this element."""
  if state in (element_state.STATE_OVERLAY, element_state.STATE_CONDITIONAL):
    return POSITION_HIDDEN
  if in_viewport is None:
    return POSITION_UNMEASURED
  return POSITION_IN_VIEWPORT if in_viewport else POSITION_BELOW_FOLD


def describe_position(entry: Geometry) -> str:
  if entry.state in (element_state.STATE_OVERLAY, element_state.STATE_CONDITIONAL):
    return f"hidden on load ({entry.state})"
  if entry.in_viewport is None:
    return "at an unmeasured position"
  return "inside the first viewport" if entry.in_viewport else "below the fold"


def segment_position(entry: Geometry) -> tuple[float, str]:
  return position_factor(entry.in_viewport, entry.state), describe_position(entry)


def below_the_fold(entry: Geometry | None) -> bool:
  """Whether this element is outside what a reader meets on arrival.

  Overlay and conditional regions count as outside too: they are design decisions, but not part of
  the page as it arrives, so they belong under the same cap as below-fold content. An unmeasured
  position also counts as outside, which is the conservative reading - the cap can only lower a
  weight, so a mis-classified element loses influence rather than gaining it.
  """
  if entry is None:
    return True
  if entry.state in (element_state.STATE_OVERLAY, element_state.STATE_CONDITIONAL):
    return True
  return entry.in_viewport is not True


def container_element_weight(entry: Geometry | None) -> tuple[float, str]:
  """One element's intrinsic importance, size x position, with no reference to a counterpart.

  This replaces the pair-relative rule that took size from the larger side and position from the
  less prominent one. Nothing is lost: the pair weight is now min(w_A, w_B), so a hero matched to a
  below-fold panel is still charged at the panel's weight - the old rule's intent, arrived at as a
  consequence of the symmetric pair weight rather than as a special case.
  """
  if entry is None or not has_geometry(entry):
    fallback = SIZE_UNMEASURED * POSITION_UNMEASURED
    return fallback, f"Unmeasured element; intrinsic weight falls back to {fallback:.3f}."
  size = size_factor(entry.area)
  position, position_text = segment_position(entry)
  return size * position, (
    f"{entry.area:,}px2 of {VIEWPORT_AREA:,} viewport -> size {size:.3f}; {position_text} -> "
    f"position {position:.2f}; intrinsic weight {size * position:.3f}."
  )


def hungarian_minimize(cost: np.ndarray) -> list[tuple[int, int]]:
  """Return a minimum-cost assignment for a square matrix."""
  rows, columns = cost.shape
  if rows != columns:
    raise ValueError("Hungarian input must be square")

  size = rows
  u = np.zeros(size + 1, dtype=np.float64)
  v = np.zeros(size + 1, dtype=np.float64)
  matching = np.zeros(size + 1, dtype=np.int64)
  way = np.zeros(size + 1, dtype=np.int64)

  for row in range(1, size + 1):
    matching[0] = row
    column_zero = 0
    minimum = np.full(size + 1, np.inf, dtype=np.float64)
    used = np.zeros(size + 1, dtype=bool)

    while True:
      used[column_zero] = True
      row_zero = matching[column_zero]
      delta = np.inf
      column_one = 0

      for column in range(1, size + 1):
        if used[column]:
          continue
        candidate = cost[row_zero - 1, column - 1] - u[row_zero] - v[column]
        if candidate < minimum[column]:
          minimum[column] = candidate
          way[column] = column_zero
        if minimum[column] < delta:
          delta = minimum[column]
          column_one = column

      for column in range(size + 1):
        if used[column]:
          u[matching[column]] += delta
          v[column] -= delta
        else:
          minimum[column] -= delta

      column_zero = column_one
      if matching[column_zero] == 0:
        break

    while True:
      column_one = way[column_zero]
      matching[column_zero] = matching[column_one]
      column_zero = column_one
      if column_zero == 0:
        break

  assignments: list[tuple[int, int]] = []
  for column in range(1, size + 1):
    row = int(matching[column])
    if row:
      assignments.append((row - 1, column - 1))
  return assignments


def null_augmented_cost(similarities: np.ndarray, null_cost: float, blocked: float = 1e6) -> np.ndarray:
  """The (N+M) x (N+M) cost matrix whose optimum may leave elements unmatched.

  Rows are the N real A elements followed by M null slots, one per B element; columns are the M real
  B elements followed by N null slots, one per A element. Real costs sit top-left, each element's
  own null slot carries ``null_cost`` on the diagonal of its block and ``blocked`` off it, and the
  bottom-right block is free so unused slots pair off with each other.

  With a symmetric penalty the solver prefers a match to two nulls exactly when
  ``1 - s < 2 * null_cost``, so ``null_cost = (1 - tau) / 2`` implements the threshold tau.

  Padding to square and reading the leftovers as unmatched - what this replaced - is not the same
  thing. There the first min(N, M) elements are *forced* to match at any cost while the surplus on
  the longer side is dropped for free, which is exactly backwards: two unrelated pages of equal
  length force-match every element, and genuinely absent content costs nothing. Nor is it enough to
  match as before and then discard pairs below tau, because discarding does not let the freed
  element re-match; only solving the augmented problem finds the true optimum.
  """
  n, m = similarities.shape
  size = n + m
  cost = np.full((size, size), float(blocked), dtype=np.float64)
  cost[:n, :m] = 1.0 - similarities
  cost[n:, m:] = 0.0
  if n:
    rows = np.arange(n)
    cost[rows, m + rows] = null_cost
  if m:
    columns = np.arange(m)
    cost[n + columns, columns] = null_cost
  return cost
