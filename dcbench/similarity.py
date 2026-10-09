"""The pair similarity S(A, B) between two prepared designs (paper, Appendix "Similarity calibration and score implementation" and "Colour system and the final score").

S = 0.9 * S_IA + 0.1 * S_colour, both on 0-100.

S_IA matches the two pages' segments one to one. Each segment pair's similarity is the cosine of
its projected Gemini strips, blended with the cosine of its projected UIClip vectors on the
smaller segment's area: UIClip's weight is r^2 / (1 + r^2) with r = min(a_i, a_j) / (1280 x 720).
UIClip is mapped onto Gemini's scale first, unrelated median to unrelated median and nuisance
median to nuisance median, so one threshold means the same thing in both spaces. The assignment
prefers a match to leaving both segments unmatched only when its similarity clears tau = 0.45.
Unmatched segments that repeat a matched segment of their own page (similarity >= 0.90) are
dropped, the importance weights are recomputed over what remains, and S_IA is the weighted sum of
matched similarities over the larger page total.

S_colour compares the six palette roles of the two extracted themes (theme_spec.diff_themes).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import pair_scoring as PS
from . import projection as P
from . import theme_spec

ROOT = Path(__file__).resolve().parent.parent
GEMINI_PROJECTION = ROOT / "assets/projection.npz"
UIClip_PROJECTION = ROOT / "assets/uiclip_projection.npz"

TAU = 0.45
IA_WEIGHT = 0.9
VIEWPORT_AREA = 1280 * 720
HYBRID_A0 = 1.0       # crossover, in reference viewports of the smaller segment
HYBRID_WIDTH = 0.5    # logistic width in natural-log area units; with a0 = 1 this is r^2/(1+r^2)


def calibration(projection_path: Path) -> tuple[float, float]:
  """(unrelated median, nuisance median) on held-out pages, from the projection's sidecar."""
  payload = json.loads(projection_path.with_suffix(".json").read_text())["after"]
  return float(payload["unrelated_median"]), float(payload["invariant_median"])


class Scorer:
  """Holds both projections and the calibration map; score() compares two design directories.

  A design directory holds design.csv (the measured elements), theme.json (the palette),
  segments/segment_images.json (each segment's captured size), segments/<kid>.npy (Gemini) and
  uiclip/<kid>.npy (UIClip). prepare.py writes exactly this layout.
  """

  def __init__(self) -> None:
    self.gemini = P.load_projection(GEMINI_PROJECTION)
    self.uiclip = P.load_projection(UIClip_PROJECTION)
    lo_s, hi_s = calibration(UIClip_PROJECTION)
    lo_p, hi_p = calibration(GEMINI_PROJECTION)
    self.map = lambda cos: lo_p + (cos - lo_s) / max(hi_s - lo_s, 1e-9) * (hi_p - lo_p)
    self._strips: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    self._themes: dict[str, dict] = {}
    self._scores: dict[tuple[str, str], dict | None] = {}

  # -- per design, cached: every design appears in many pairs ------------------------------------

  def strips(self, design: Path, encoder: str) -> dict[str, np.ndarray]:
    key = (str(design), encoder)
    if key not in self._strips:
      projection = self.gemini if encoder == "gemini" else self.uiclip
      self._strips[key] = _strips(design / "design.csv", design / "segments", load_vectors(design, encoder), projection)
    return self._strips[key]

  def theme(self, design: Path) -> dict:
    if str(design) not in self._themes:
      path = design / "theme.json"
      self._themes[str(design)] = json.loads(path.read_text()) if path.is_file() else {}
    return self._themes[str(design)]

  # -- one pair -----------------------------------------------------------------------------------

  def score(self, a: Path, b: Path) -> dict | None:
    """S(A, B) and its parts, memoised: originality meets every panel pair from both sides."""
    key = (str(a), str(b))
    if key not in self._scores:
      self._scores[key] = self._score(a, b)
    return self._scores[key]

  def _score(self, a: Path, b: Path) -> dict | None:
    prepared = self.pair_matrix(a, b)
    if prepared is None:
      return None
    ia, matched = score_at(prepared, TAU)
    cs = theme_spec.diff_themes(self.theme(a), self.theme(b)).get("overall_score")
    overall = IA_WEIGHT * ia + (1 - IA_WEIGHT) * cs if cs is not None else ia
    return {"similarity": overall, "ia_pct": ia, "cs_pct": cs, "matched": matched,
            "a_count": len(prepared[1]), "b_count": len(prepared[2])}

  def pair_matrix(self, a: Path, b: Path):
    left, right = self.strips(a, "gemini"), self.strips(b, "gemini")
    if not left or not right:
      return None
    a_names, b_names = sorted(left), sorted(right)
    size_a, size_b = sizes_of_dir(a / "segments"), sizes_of_dir(b / "segments")
    matrix = _unit(np.stack([left[k] for k in a_names])) @ _unit(np.stack([right[k] for k in b_names])).T

    second_left, second_right = self.strips(a, "uiclip"), self.strips(b, "uiclip")
    # A segment missing from the UIClip tree keeps its Gemini similarity: the blend acts only where
    # both spaces saw the segment.
    shared_a = [k for k in a_names if k in second_left]
    shared_b = [k for k in b_names if k in second_right]
    if shared_a and shared_b:
      mapped = self.map(_unit(np.stack([second_left[k] for k in shared_a]))
                        @ _unit(np.stack([second_right[k] for k in shared_b])).T)
      row_of = {k: i for i, k in enumerate(a_names)}
      col_of = {k: i for i, k in enumerate(b_names)}
      rows = np.array([row_of[k] for k in shared_a])
      cols = np.array([col_of[k] for k in shared_b])
      w = blend_weights(np.array([_area(size_a.get(k, (0, 0))) for k in shared_a]),
                        np.array([_area(size_b.get(k, (0, 0))) for k in shared_b]))
      block = matrix[np.ix_(rows, cols)]
      matrix[np.ix_(rows, cols)] = np.where(w > 0.0, (1.0 - w) * block + w * mapped, block)

    geometry_a = PS.read_geometry(a / "design.csv", a / "segments")
    geometry_b = PS.read_geometry(b / "design.csv", b / "segments")
    return (matrix, a_names, b_names, {"a": left, "b": right}, {"a": size_a, "b": size_b},
            {"a": geometry_a, "b": geometry_b})


def _unit(matrix: np.ndarray) -> np.ndarray:
  return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)


def sizes_of_dir(segments: Path) -> dict[str, tuple[int, int]]:
  manifest = segments / "segment_images.json"
  if not manifest.is_file():
    return {}
  return {row["data_kid"]: (int(row.get("width") or 0), int(row.get("height") or 0))
          for row in json.loads(manifest.read_text()).get("results", [])}


def load_vectors(design: Path, encoder: str) -> dict[str, np.ndarray]:
  """{kid: vector} for one encoder, from vectors.npz (packed) or from per-segment .npy files."""
  packed = design / "vectors.npz"
  if packed.is_file():
    with np.load(packed) as payload:
      prefix = f"{encoder}/"
      return {name.removeprefix(prefix): payload[name] for name in payload.files if name.startswith(prefix)}
  source = design / ("segments" if encoder == "gemini" else "uiclip")
  return {p.stem: np.load(p) for p in sorted(source.glob("*.npy"))}


def pack(design: Path) -> None:
  """Fold a design's per-segment .npy files into one vectors.npz, keeping only eligible segments."""
  wanted = PS.eligible_kids(design / "design.csv")
  arrays = {f"{encoder}/{kid}": vector for encoder in ("gemini", "uiclip")
            for kid, vector in load_vectors(design, encoder).items() if kid in wanted}
  np.savez_compressed(design / "vectors.npz", **arrays)


def _strips(csv_path: Path, segments: Path, vectors: dict[str, np.ndarray], projection) -> dict[str, np.ndarray]:
  """Projected, resampled, flattened strip per eligible segment."""
  if not csv_path.is_file():
    return {}
  wanted = PS.eligible_kids(csv_path)
  sizes = sizes_of_dir(segments)
  raw, geometry = {}, {}
  for kid in sorted(wanted):
    if kid not in vectors:
      continue
    strip = vectors[kid]
    # Gemini vectors are stored as (windows, dims), UIClip as a bare (dims,).
    raw[f"{kid}.npy"] = strip if strip.ndim == 2 else strip.reshape(1, -1)
    width, height = sizes.get(kid, (0, 0))
    if width and height:
      geometry[kid] = (width, height)
  if not raw:
    return {}
  projected = P.project_vectors(raw, projection[0], projection[1], geometry, projection[2])
  return {name.removesuffix(".npy"): P.resample(np.asarray(strip, dtype=np.float64), P.RESAMPLE_WINDOWS).ravel()
          for name, strip in projected.items()}


def _area(size: tuple[int, int]) -> float:
  return (size[0] * size[1]) / VIEWPORT_AREA


def blend_weights(areas_a: np.ndarray, areas_b: np.ndarray) -> np.ndarray:
  """UIClip's weight for every segment pair, from the SMALLER segment's area (in viewports)."""
  smaller = np.minimum(areas_a[:, None], areas_b[None, :])
  safe = np.where(smaller > 0, smaller, 1.0)
  logistic = 1.0 / (1.0 + np.exp(-(np.log(safe) - np.log(HYBRID_A0)) / HYBRID_WIDTH))
  return np.where(smaller > 0, logistic, 0.0)


def weigh(names: list[str], geometry: dict) -> tuple[dict[str, float], float]:
  """Importance weights: intrinsic, then the below-the-fold cap, then the page budget."""
  intrinsic = {n: PS.container_element_weight(geometry.get(n))[0] for n in names}
  below = {n: PS.below_the_fold(geometry.get(n)) for n in names}
  viewport = sum(v for n, v in intrinsic.items() if not below[n])
  beneath = sum(v for n, v in intrinsic.items() if below[n])
  allowed = (PS.BELOW_FOLD_SHARE / (1 - PS.BELOW_FOLD_SHARE)) * viewport
  kappa = 1.0 if beneath <= allowed else (allowed / beneath if beneath else 1.0)
  capped = viewport + kappa * beneath
  scale = min(1.0, PS.IMPORTANCE_BUDGET / capped) if capped else 1.0
  weights = {n: intrinsic[n] * (kappa if below[n] else 1.0) * scale for n in names}
  return weights, sum(weights.values())


def score_at(prepared, tau: float) -> tuple[float, float]:
  """Assign, drop near-duplicates, then weigh what is left. Returns (S_IA on 0-100, match share)."""
  matrix, a_names, b_names, strips_by_side, sizes, geometry = prepared
  null_cost = (1.0 - tau) / 2.0
  rows = []
  for row, column in PS.hungarian_minimize(PS.null_augmented_cost(matrix, null_cost)):
    if row < len(a_names) and column < len(b_names):
      rows.append({"a": a_names[row], "b": b_names[column], "score": float(matrix[row, column])})
    elif row < len(a_names):
      rows.append({"a": a_names[row], "b": None, "score": None})
    elif column < len(b_names):
      rows.append({"a": None, "b": b_names[column], "score": None})

  # An unmatched row goes if it repeats one of its own page's MATCHED segments.
  matched_names = {side: {r[side] for r in rows if r["a"] and r["b"]} for side in "ab"}
  kept = []
  for row in rows:
    if row["score"] is not None:
      kept.append(row)
      continue
    side = "a" if row["a"] else "b"
    name = row[side]
    siblings = sorted(matched_names[side])
    best = 0.0
    if siblings:
      own = strips_by_side[side][name]
      stack = np.stack([strips_by_side[side][other] for other in siblings])
      cosines = _unit(stack) @ (own / max(np.linalg.norm(own), 1e-12))
      best = max(float(c) for c in cosines)
    if best < P.NEAR_DUPLICATE_SIMILARITY:
      kept.append(row)
  rows = kept

  present = {side: [r[side] for r in rows if r[side]] for side in "ab"}
  weights, totals = {}, {}
  for side in "ab":
    weights[side], totals[side] = weigh(present[side], geometry[side])
  numerator = matched = 0.0
  for row in rows:
    if row["a"] and row["b"]:
      numerator += row["score"] * min(weights["a"][row["a"]], weights["b"][row["b"]])
      matched += 1
  denominator = max(totals["a"], totals["b"])
  return (100.0 * numerator / denominator if denominator else 0.0,
          matched / max(min(len(present["a"]), len(present["b"])), 1))
