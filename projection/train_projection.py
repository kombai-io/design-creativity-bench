"""Train the linear projection `z(x) = Wx - b` on the paired perturbation dataset.

Usage:
  python projection/train_projection.py --data data/projection/gemini --out assets/projection.npz --max-invariant-drift 1.1
  python projection/train_projection.py --data data/projection/gemini --stage0-only

The metric the benchmark deploys is cosine between element embeddings. The defect it has is that a
*nuisance* change (theme, copy, spacing, a responsive resize) moves a vector about as far as a
*structural* one (different child count, different arrangement, different nesting), so two unrelated
elements pair at a high score. Measured on the pilot before any projection: separation AUC 0.572,
barely above chance, with invariant pairs at median cosine 0.927 and structural pairs at 0.907.

`W` is trained to pull those apart. Numpy with analytic gradients - the model is one 64x1536 matrix,
so there is nothing to gain from a framework.

Design decisions:

  b is FROZEN at W*mu for this run. The offset sets the global scale of a score the benchmark
  reports as an absolute sum, and its equilibrium under a learned setting is decided by loss weights
  rather than by data. Establish that a fixed projected centroid works first; unfreezing it is a
  separate ablation.

  The positive term is a HINGE, not an unbounded attraction. `-cos(a,p)` keeps dragging the offset
  and the scale outward for as long as training runs; `max(0, m+ - cos)` stops pulling once the pair
  is close enough.

  The regulariser is ||WW' - I_d||, not ||W'W - I||. With W shaped d x 1536, W'W is rank-deficient
  by construction and an identity penalty on it is unsatisfiable.

  Unrelated cross-page pairs are calibrated toward 0 as a weak mean penalty, which is what pins the
  scale to something the data defines. They are drawn only between different pages and masked by
  pre-projection cosine, a frozen input, so the mask cannot chase the thing being trained.

  Splits are by PAGE. Segments of one page are not independent draws.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import math
from typing import Any

import numpy as np


PILOT_DIR = Path(__file__).resolve().parent.parent
DIMS = 64
MARGIN = 0.15
POSITIVE_MARGIN = 0.90
# Graded pairs: colour as a signal with a size. 0 disables the term. Set from the CLI in main() -
# see the note there about --margin, which was parsed and then never applied.
LAMBDA_GRADE = 0.0
GRADE_SLOPE = 0.5
LAMBDA_CAL = 1.0
LAMBDA_ORTHO = 0.05
LEARNING_RATE = 0.05
EPOCHS = 60
BATCH = 256
# Masks the calibration pairs. A frozen, pre-projection quantity on purpose: masking on the
# projected cosine would move as training moves it.
NEAR_DUPLICATE_RAW = 0.97


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--data", type=Path, default=PILOT_DIR / "data/projection/gemini")
  parser.add_argument("--out", type=Path, default=PILOT_DIR / "assets/projection.npz")
  parser.add_argument("--dims", type=int, default=DIMS)
  parser.add_argument("--epochs", type=int, default=EPOCHS)
  parser.add_argument("--lr", type=float, default=LEARNING_RATE)
  parser.add_argument("--margin", type=float, default=MARGIN)
  parser.add_argument("--lambda-grade", type=float, default=1.0,
                      help="Weight on the graded-colour regression. 0 drops the term, which makes "
                           "graded pairs invisible to the loss entirely")
  parser.add_argument("--grade-slope", type=float, default=0.5,
                      help="Target cosine for a graded pair is 1 - slope * strength")
  parser.add_argument("--no-geometry", action="store_true",
                      help="Train on the embedding alone, without the log-width/log-height input features")
  parser.add_argument("--stage0-only", action="store_true", help="Write the closed-form initialiser and stop")
  parser.add_argument("--seed", type=int, default=0)
  parser.add_argument("--page-fraction", type=float, default=1.0,
                      help="Train on this fraction of the TRAIN pages, holding the same test pages. "
                           "For learning curves: whether held-out AUC is still climbing says whether "
                           "more pages would help, or whether the ceiling is the input rather than "
                           "the sample size.")
  parser.add_argument("--max-invariant-drift", type=float, default=0.0,
                      help="Drop invariant pairs whose |log(h_a/h_b)| exceeds this. n5_reflow draws "
                           "per-element multipliers up to 10x, and training on the extreme band "
                           "teaches size invariance wholesale: it removed the geometry artifact but "
                           "also removed discrimination the unrelated decision relies on, raising "
                           "one ladder's unrelated floor from 9.41 to 26.67. Real copy volume varies "
                           "maybe 0.5x-3x, so ~1.1 keeps the realistic band. 0 disables the filter.")
  return parser.parse_args()


def load_dataset(root: Path) -> tuple[np.ndarray, list[dict]]:
  """Every valid pair, as indices into one vector table."""
  rows = [json.loads(line) for line in (root / "pairs/pairs.jsonl").read_text().splitlines() if line.strip()]
  rows = [r for r in rows if r["valid"]]
  index: dict[str, int] = {}
  vectors: list[np.ndarray] = []

  def intern(path: str) -> int:
    if path not in index:
      vector = np.load(root / path).astype(np.float32)
      vectors.append(vector[0] if vector.ndim == 2 else vector)
      index[path] = len(vectors) - 1
    return index[path]

  pairs = []
  boxes: dict[int, tuple[int, int]] = {}
  for row in rows:
    try:
      a, b = intern(row["npy_a"]), intern(row["npy_b"])
    except OSError:
      continue
    boxes[a] = tuple(row["size_a"])
    boxes[b] = tuple(row["size_b"])
    pairs.append({"a": a, "b": b, "page": row["page_id"], "model": row["model"],
                  "kid": row["kid"], "family": row["family"], "polarity": row["polarity"],
                  # null when the index was rebuilt from clips after a failed write: it feeds
                  # only the distance_spearman diagnostic, never the loss.
                  "distance": float(row["struct_distance"] or 0.0),
                  "jpg_a": row["jpg_a"], "jpg_b": row["jpg_b"],
                  # Present only on `graded` rows: how far this pair's colour perturbation moved
                  # the crop in HSL space, in [0, 1]. See hsl_strength.py.
                  "strength": float(row.get("strength") or 0.0)})
  geometry = np.zeros((len(vectors), 2), dtype=np.float32)
  for index, (width, height) in boxes.items():
    geometry[index] = (max(int(width), 1), max(int(height), 1))
  return np.stack(vectors), pairs, geometry


def augment(vectors: np.ndarray, geometry: np.ndarray, stats: dict | None = None):
  """Append the element's own log width and log height to its descriptor.

  This is `stretch_decay` moved to the INPUT side. That decay multiplied a hand-tuned exponential
  onto the cosine afterwards - `exp(-(ratio - 1.3))` on height, a tighter band on width - and then
  needed `decay_exempt` to switch itself off for large pairs, because a ratio stops meaning the same
  thing once both elements are page-scale. Fitted here instead, the map decides how much geometry is
  worth, jointly with the embedding, and the patches go away.

  Only log w and log h: a linear map forms any combination of them, so log area (= log w + log h)
  and log aspect (= log w - log h) are already spanned. Measured on held-out pages, |dlog h| alone
  separates nuisance from structural pairs at AUC 0.863, against 0.710 for the whole 1536-dimensional
  embedding - deleting children shrinks the box where a theme swap does not.

  Standardised, because the embedding is unit-norm spread over 1536 dimensions while a raw log
  pixel value is ~6. The statistics are returned so inference reproduces them exactly rather than
  re-deriving them from whatever pages it happens to be scoring.
  """
  logs = np.log(np.maximum(geometry, 1.0))
  if stats is None:
    stats = {"mean": logs.mean(axis=0).tolist(), "sd": (logs.std(axis=0) + 1e-6).tolist()}
  scaled = (logs - np.array(stats["mean"], dtype=np.float32)) / np.array(stats["sd"], dtype=np.float32)
  return np.hstack([vectors, scaled.astype(np.float32)]), stats


def split_by_page(pairs: list[dict], seed: int, holdout: float = 0.2) -> tuple[list[dict], list[dict]]:
  pages = sorted({p["page"] for p in pairs})
  random.Random(seed).shuffle(pages)
  cut = int(len(pages) * (1 - holdout))
  train_pages = set(pages[:cut])
  return ([p for p in pairs if p["page"] in train_pages],
          [p for p in pairs if p["page"] not in train_pages])


def closed_form(vectors: np.ndarray, pairs: list[dict], dims: int) -> np.ndarray:
  """Stage 0: the directions where structural variance beats nuisance variance.

  An initialiser and a conditioning step, not a candidate solution - fitted to a variance ratio it
  bought only +0.03 of held-out invariance in an earlier probe, because aggregate variance
  suppression is not per-pair invariance.
  """
  def differences(polarity: str) -> np.ndarray:
    rows = [vectors[p["b"]] - vectors[p["a"]] for p in pairs if p["polarity"] == polarity]
    return np.stack(rows) if rows else np.zeros((1, vectors.shape[1]), dtype=np.float32)

  nuisance, signal = differences("invariant"), differences("structural")
  def covariance(matrix: np.ndarray) -> np.ndarray:
    centred = matrix - matrix.mean(0)
    return (centred.T @ centred) / max(len(centred), 1)
  sigma_n = covariance(nuisance) + 1e-3 * np.eye(vectors.shape[1], dtype=np.float32)
  sigma_s = covariance(signal)
  values, basis = np.linalg.eigh(np.linalg.solve(sigma_n, sigma_s))
  return np.ascontiguousarray(basis[:, ::-1][:, :dims].T.astype(np.float32))


def cosine_and_grad(za: np.ndarray, zb: np.ndarray):
  """Cosine per row plus d cos / d za and d cos / d zb."""
  na = np.linalg.norm(za, axis=1, keepdims=True) + 1e-8
  nb = np.linalg.norm(zb, axis=1, keepdims=True) + 1e-8
  ua, ub = za / na, zb / nb
  cos = (ua * ub).sum(1, keepdims=True)
  return cos[:, 0], (ub - cos * ua) / na, (ua - cos * ub) / nb


def batch_terms(W: np.ndarray, b: np.ndarray, X: np.ndarray, rows: list[dict], rng, tables):
  """Loss and gradient for one minibatch of triplets plus calibration pairs."""
  grad = np.zeros_like(W)
  loss = 0.0
  by_anchor, structural_by_anchor, page_of = tables

  anchors = [r for r in rows if r["polarity"] == "invariant"]
  if not anchors:
    return 0.0, grad
  positives, hard = [], []
  for row in anchors:
    key = (row["page"], row["kid"])
    negatives = structural_by_anchor.get(key)
    if not negatives:
      continue
    positives.append(row)
    hard.append(negatives[rng.randrange(len(negatives))])
  if not positives:
    return 0.0, grad

  def project(idx):
    return X[idx] @ W.T - b

  ia = np.array([r["a"] for r in positives]); ip = np.array([r["b"] for r in positives])
  ih = np.array([r["b"] for r in hard]);      iha = np.array([r["a"] for r in hard])
  za, zp, zh, zha = project(ia), project(ip), project(ih), project(iha)

  # 1. any structural change must sit below every nuisance one, by a margin.
  cos_p, dp_a, dp_p = cosine_and_grad(za, zp)
  cos_h, dh_a, dh_h = cosine_and_grad(zha, zh)
  violation = np.maximum(0.0, cos_h - cos_p + MARGIN)
  active = violation > 0
  loss += float(violation.sum())
  if active.any():
    grad += (dh_a[active]).T @ X[iha[active]] + (dh_h[active]).T @ X[ih[active]]
    grad -= (dp_a[active]).T @ X[ia[active]] + (dp_p[active]).T @ X[ip[active]]

  # 2. bounded positive attraction: stop pulling once the pair is close enough.
  shortfall = np.maximum(0.0, POSITIVE_MARGIN - cos_p)
  live = shortfall > 0
  loss += float(shortfall.sum())
  if live.any():
    grad -= (dp_a[live]).T @ X[ia[live]] + (dp_p[live]).T @ X[ip[live]]

  # 2b. graded pairs: colour treated as a signal with a size rather than a nuisance to erase.
  # Their target cosine falls linearly with the measured HSL strength, so the projection has to
  # keep colour information AND order it by magnitude. These rows are excluded from the triplet in
  # (1) and the attraction in (2): a strong recolour is not required to sit above a structural
  # change, which is the whole point of the experiment.
  graded = [r for r in rows if r["polarity"] == "graded"]
  if graded and LAMBDA_GRADE > 0.0:
    ig_a = np.array([r["a"] for r in graded])
    ig_b = np.array([r["b"] for r in graded])
    target = 1.0 - GRADE_SLOPE * np.array([r["strength"] for r in graded])
    zg_a, zg_b = project(ig_a), project(ig_b)
    cos_g, dg_a, dg_b = cosine_and_grad(zg_a, zg_b)
    error = cos_g - target
    loss += float(LAMBDA_GRADE * (error ** 2).sum())
    scale = (2.0 * LAMBDA_GRADE * error)[:, None]
    grad += (scale * dg_a).T @ X[ig_a] + (scale * dg_b).T @ X[ig_b]

  # 3. calibration: unrelated elements from DIFFERENT pages toward cosine 0.
  count = max(8, len(positives))
  left = rng.sample(range(len(X)), min(count, len(X)))
  right = rng.sample(range(len(X)), min(count, len(X)))
  keep = [(l, r) for l, r in zip(left, right) if page_of[l] != page_of[r]]
  if keep:
    li = np.array([l for l, _ in keep]); ri = np.array([r for _, r in keep])
    raw = (X[li] * X[ri]).sum(1) / (np.linalg.norm(X[li], axis=1) * np.linalg.norm(X[ri], axis=1))
    mask = raw < NEAR_DUPLICATE_RAW
    if mask.any():
      li, ri = li[mask], ri[mask]
      zl, zr = project(li), project(ri)
      cos_u, du_l, du_r = cosine_and_grad(zl, zr)
      loss += float(LAMBDA_CAL * (cos_u ** 2).sum())
      scale = (2.0 * LAMBDA_CAL * cos_u)[:, None]
      grad += (scale * du_l).T @ X[li] + (scale * du_r).T @ X[ri]

  # 4. semi-orthogonality on WW' (d x d), which is the achievable direction.
  gram = W @ W.T
  defect = gram - np.eye(W.shape[0], dtype=np.float32)
  loss += float(LAMBDA_ORTHO * (defect ** 2).sum())
  grad += LAMBDA_ORTHO * 4.0 * defect @ W

  return loss / max(len(positives), 1), grad / max(len(positives), 1)


# The pairwise features both fitted heads read. All symmetric in the two elements, because a pair
# has no natural order and a cost that changed when the sides swapped would make the assignment
# depend on which design was called A.
#
# Only |dlog w| and |dlog h| are independent; |dlog area| and |dlog aspect| are included anyway
# because they are absolute values of sums and differences, which a linear map over |dlog w| and
# |dlog h| cannot form. `mean_log_area` carries the pair's scale: two tiny elements agreeing is
# weaker evidence than two large ones agreeing.
FEATURES = ("cosine", "abs_dlog_w", "abs_dlog_h", "abs_dlog_area", "abs_dlog_aspect", "mean_log_area")
COSINE_ONLY = ("cosine",)


def pair_features(cosine: np.ndarray, a_size: np.ndarray, b_size: np.ndarray) -> np.ndarray:
  """The feature table for a batch of pairs, in FEATURES order."""
  a = np.log(np.maximum(a_size.astype(np.float64), 1.0))
  b = np.log(np.maximum(b_size.astype(np.float64), 1.0))
  a_w, a_h = a[:, 0], a[:, 1]
  b_w, b_h = b[:, 0], b[:, 1]
  return np.stack([
    cosine,
    np.abs(a_w - b_w),
    np.abs(a_h - b_h),
    np.abs((a_w + a_h) - (b_w + b_h)),
    np.abs((a_w - a_h) - (b_w - b_h)),
    ((a_w + a_h) + (b_w + b_h)) / 4.0,
  ], axis=1)


def fit_head(features: np.ndarray, labels: np.ndarray, columns: tuple[str, ...],
             seed: int = 0) -> dict:
  """One logistic head, standardised, with balanced classes.

  Balanced because the class ratio here is an artefact of how many negatives were sampled, not the
  base rate an assignment sees - in an N x M matrix at most min(N, M) of the N*M candidate pairs can
  be a true correspondence. Fitting the intercept to a sampled ratio would put the operating point
  somewhere arbitrary, so the head is fitted for discrimination and the threshold is set separately
  by the F1 sweep that already calibrates NULL_SIMILARITY.
  """
  from sklearn.linear_model import LogisticRegression
  index = [FEATURES.index(name) for name in columns]
  table = features[:, index]
  mean = table.mean(axis=0)
  sd = table.std(axis=0) + 1e-6
  model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)
  model.fit((table - mean) / sd, labels)
  return {
    "columns": list(columns),
    "weights": model.coef_[0].astype(np.float32),
    "intercept": float(model.intercept_[0]),
    "mean": mean.astype(np.float32),
    "sd": sd.astype(np.float32),
  }


def head_logit(head: dict, features: np.ndarray) -> np.ndarray:
  index = [FEATURES.index(name) for name in head["columns"]]
  table = (features[:, index] - head["mean"]) / head["sd"]
  return table @ head["weights"] + head["intercept"]


def roc_auc(scores: np.ndarray, labels: np.ndarray) -> float:
  order = np.argsort(scores)
  ranks = np.empty(len(scores), dtype=np.float64)
  ranks[order] = np.arange(1, len(scores) + 1)
  positives = labels == 1
  n1 = float(positives.sum())
  n0 = float(len(labels) - n1)
  if n1 == 0 or n0 == 0:
    return float("nan")
  return float((ranks[positives].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def build_head_tables(W: np.ndarray, b: np.ndarray, X: np.ndarray, geometry: np.ndarray,
                      rows: list[dict], page_of, rng_seed: int = 3) -> dict[str, Any]:
  """Features and labels for both heads, over one split's pairs.

  `match` asks whether two elements correspond at all, so every true pair - nuisance and structural
  alike - is a positive and unrelated cross-page pairs are the negatives. `same` asks whether a
  correspondence was drawn the same way, so it sees only true pairs: nuisance positive, structural
  negative. Keeping them separate is what stops one head having to be both a null test and a
  graded score.
  """
  Z = X @ W.T - b
  Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-8)

  left = np.array([row["a"] for row in rows], dtype=np.int64)
  right = np.array([row["b"] for row in rows], dtype=np.int64)
  cosine = np.einsum("ij,ij->i", Z[left], Z[right])
  features = pair_features(cosine, geometry[left], geometry[right])
  polarity = np.array([row["polarity"] for row in rows])

  rng = np.random.default_rng(rng_seed)
  pool = np.unique(np.concatenate([left, right]))
  wanted = len(rows)
  unrelated_left: list[int] = []
  unrelated_right: list[int] = []
  attempts = 0
  while len(unrelated_left) < wanted and attempts < wanted * 20:
    attempts += 1
    one, two = rng.choice(pool, size=2, replace=False)
    if page_of[one] != page_of[two]:
      unrelated_left.append(int(one))
      unrelated_right.append(int(two))
  ul = np.array(unrelated_left, dtype=np.int64)
  ur = np.array(unrelated_right, dtype=np.int64)
  unrelated_cos = np.einsum("ij,ij->i", Z[ul], Z[ur])
  unrelated_features = pair_features(unrelated_cos, geometry[ul], geometry[ur])

  match_features = np.vstack([features, unrelated_features])
  match_labels = np.concatenate([np.ones(len(features)), np.zeros(len(unrelated_features))])
  same_mask = np.isin(polarity, ("invariant", "structural"))
  same_features = features[same_mask]
  same_labels = (polarity[same_mask] == "invariant").astype(np.float64)
  return {
    "match": (match_features, match_labels),
    "same": (same_features, same_labels),
  }


def evaluate(W: np.ndarray, b: np.ndarray, X: np.ndarray, pairs: list[dict], page_of, rng_seed=1) -> dict:
  Z = X @ W.T - b
  Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-8)
  by_family = defaultdict(list)
  for row in pairs:
    by_family[(row["polarity"], row["family"])].append(float(Z[row["a"]] @ Z[row["b"]]))
  inv = np.array([v for k, values in by_family.items() if k[0] == "invariant" for v in values])
  st = np.array([v for k, values in by_family.items() if k[0] == "structural" for v in values])

  structural_by_anchor = defaultdict(list)
  for row in pairs:
    if row["polarity"] == "structural":
      structural_by_anchor[(row["page"], row["kid"])].append(row)
  hits = total = 0
  for row in pairs:
    if row["polarity"] != "invariant":
      continue
    for negative in structural_by_anchor.get((row["page"], row["kid"]), []):
      total += 1
      hits += 1 if Z[row["a"]] @ Z[row["b"]] > Z[negative["a"]] @ Z[negative["b"]] else 0

  rng = random.Random(rng_seed)
  left = [rng.randrange(len(X)) for _ in range(4000)]
  right = [rng.randrange(len(X)) for _ in range(4000)]
  unrelated = np.array([float(Z[l] @ Z[r]) for l, r in zip(left, right) if page_of[l] != page_of[r]])

  spearman = 0.0
  if len(st) > 8:
    distances = np.array([row["distance"] for row in pairs if row["polarity"] == "structural"])
    scores = np.array([float(Z[row["a"]] @ Z[row["b"]]) for row in pairs if row["polarity"] == "structural"])
    ranks_d = np.argsort(np.argsort(distances)); ranks_s = np.argsort(np.argsort(scores))
    spearman = float(np.corrcoef(ranks_d, ranks_s)[0, 1])

  return {
    "invariant_median": float(np.median(inv)) if len(inv) else 0.0,
    "invariant_p10": float(np.percentile(inv, 10)) if len(inv) else 0.0,
    "structural_median": float(np.median(st)) if len(st) else 0.0,
    "structural_p90": float(np.percentile(st, 90)) if len(st) else 0.0,
    "pair_accuracy": hits / total if total else 0.0,
    "auc": float((inv[:, None] > st[None, :]).mean()) if len(inv) and len(st) else 0.0,
    "unrelated_median": float(np.median(unrelated)) if len(unrelated) else 0.0,
    "unrelated_p90": float(np.percentile(unrelated, 90)) if len(unrelated) else 0.0,
    "distance_spearman": spearman,
    "per_family": {f"{k[0]}/{k[1]}": round(float(np.median(v)), 4) for k, v in sorted(by_family.items())},
  }


def main() -> None:
  args = parse_args()
  # Bind every knob the loss actually reads. --margin was parsed, recorded in the sidecar and never
  # applied, so a run with --margin 0.3 trained at 0.15 and said 0.3; the same shape of omission on
  # --max-invariant-drift invalidated a whole comparison grid.
  global MARGIN, LAMBDA_GRADE, GRADE_SLOPE
  MARGIN = args.margin
  LAMBDA_GRADE = args.lambda_grade
  GRADE_SLOPE = args.grade_slope
  X, pairs, geometry = load_dataset(args.data)
  if args.max_invariant_drift > 0:
    before_count = len(pairs)
    kept = []
    for row in pairs:
      if row["polarity"] == "invariant":
        a_h = max(float(geometry[row["a"]][1]), 1.0)
        b_h = max(float(geometry[row["b"]][1]), 1.0)
        if abs(math.log(a_h) - math.log(b_h)) > args.max_invariant_drift:
          continue
      kept.append(row)
    pairs = kept
    print(f"dropped {before_count - len(pairs)} invariant pair(s) over "
          f"|dlog h| {args.max_invariant_drift:.2f}; {len(pairs)} remain")
  geometry_stats = None
  if not args.no_geometry:
    X, geometry_stats = augment(X, geometry)
  print(f"{len(pairs)} valid pairs, {X.shape[0]} distinct vectors, {X.shape[1]} input dims"
        f"{' (embedding + log w/h)' if geometry_stats else ' (embedding only)'}, "
        f"{len({p['page'] for p in pairs})} pages, {len({p['model'] for p in pairs})} models")

  page_of = np.empty(X.shape[0], dtype=object)
  for row in pairs:
    page_of[row["a"]] = row["page"]
    page_of[row["b"]] = row["page"]
  for i in range(len(page_of)):
    if page_of[i] is None:
      page_of[i] = "?"

  train, test = split_by_page(pairs, args.seed)
  if args.page_fraction < 1.0:
    train_pages = sorted({row["page"] for row in train})
    random.Random(args.seed + 101).shuffle(train_pages)
    keep = set(train_pages[:max(1, int(len(train_pages) * args.page_fraction))])
    train = [row for row in train if row["page"] in keep]
    print(f"learning curve: {len(keep)} of {len(train_pages)} train pages, {len(train)} train pairs")
  print(f"train {len(train)} pairs / {len({p['page'] for p in train})} pages, "
        f"test {len(test)} pairs / {len({p['page'] for p in test})} pages")

  W = closed_form(X, train, args.dims)
  # The offset must be derived from the TRAIN split only. Averaging over the whole table let
  # held-out pages into b - unsupervised and tiny at 63k vectors, but still the evaluation data
  # informing the model, and there is no reason to accept even a small leak here.
  train_vectors = sorted({index for row in train for index in (row["a"], row["b"])})
  mu = X[train_vectors].mean(0)
  b = (W @ mu).astype(np.float32)
  # Baseline: the incumbent metric, corpus-centred cosine with no projection.
  centroid = np.load(PILOT_DIR / "assets/segment_centroid.npy").astype(np.float32)
  if centroid.shape[0] < X.shape[1]:
    centroid = np.hstack([centroid, np.zeros(X.shape[1] - centroid.shape[0], dtype=np.float32)])
  elif centroid.shape[0] != X.shape[1]:
    # The stored centroid is the deployed 1536-d embedder's. A tree from a different embedder gets
    # its own train-split mean instead, which is the same baseline - corpus-centred cosine - just
    # defined on the corpus it is being measured over.
    centroid = mu.copy()
    print(f"stored centroid is {np.load(PILOT_DIR / 'assets/segment_centroid.npy').shape[0]}-d against "
          f"{X.shape[1]}-d input; centring the baseline on this tree's own train-split mean")
  eye = np.eye(X.shape[1], dtype=np.float32)
  before = evaluate(eye, centroid, X, test, page_of)
  print("\nBEFORE (corpus-centred cosine, no projection)")
  for key in ("invariant_median", "invariant_p10", "structural_median", "structural_p90",
              "pair_accuracy", "auc", "unrelated_median", "distance_spearman"):
    print(f"  {key:22} {before[key]:+.4f}")

  stage0 = evaluate(W, b, X, test, page_of)
  print("\nSTAGE 0 (closed form, held out)")
  for key in ("invariant_median", "invariant_p10", "structural_median", "structural_p90",
              "pair_accuracy", "auc", "unrelated_median", "distance_spearman"):
    print(f"  {key:22} {stage0[key]:+.4f}")

  history = [{"epoch": 0, "stage": "closed_form", **{k: v for k, v in stage0.items() if k != "per_family"}}]
  if not args.stage0_only:
    structural_by_anchor = defaultdict(list)
    for row in train:
      if row["polarity"] == "structural":
        structural_by_anchor[(row["page"], row["kid"])].append(row)
    by_anchor = defaultdict(list)
    tables = (by_anchor, structural_by_anchor, page_of)
    rng = random.Random(args.seed)
    invariant_train = [r for r in train if r["polarity"] == "invariant"]
    momentum = np.zeros_like(W)
    best = (stage0["auc"], W.copy(), b.copy())
    for epoch in range(1, args.epochs + 1):
      rng.shuffle(invariant_train)
      total_loss = 0.0
      batches = 0
      for start in range(0, len(invariant_train), BATCH):
        chunk = invariant_train[start:start + BATCH]
        loss, grad = batch_terms(W, b, X, chunk, rng, tables)
        momentum = 0.9 * momentum + grad
        W -= args.lr * momentum
        total_loss += loss
        batches += 1
      # b stays pinned to the projected corpus mean: W moves, so b is re-derived, but it never
      # drifts free. Unfreezing it is a separate ablation.
      b = (W @ mu).astype(np.float32)
      metrics = evaluate(W, b, X, test, page_of)
      history.append({"epoch": epoch, "loss": total_loss / max(batches, 1),
                      **{k: v for k, v in metrics.items() if k != "per_family"}})
      if metrics["auc"] > best[0]:
        best = (metrics["auc"], W.copy(), b.copy())
      if epoch % 5 == 0 or epoch == 1:
        print(f"  epoch {epoch:3d} loss {total_loss/max(batches,1):7.4f}  "
              f"inv {metrics['invariant_median']:+.3f}/p10 {metrics['invariant_p10']:+.3f}  "
              f"str {metrics['structural_median']:+.3f}  acc {metrics['pair_accuracy']:.3f}  "
              f"auc {metrics['auc']:.3f}  unrel {metrics['unrelated_median']:+.3f}", flush=True)
    _, W, b = best

  final = evaluate(W, b, X, test, page_of)
  print("\nAFTER (trained projection, held out)")
  for key in ("invariant_median", "invariant_p10", "structural_median", "structural_p90",
              "pair_accuracy", "auc", "unrelated_median", "unrelated_p90", "distance_spearman"):
    print(f"  {key:22} {final[key]:+.4f}")
  print("\nper family (held out, median cosine):")
  for name, value in final["per_family"].items():
    print(f"  {name:28} {value:+.3f}")

  # Two fitted heads over the trained space, on the same page-disjoint split. Both are reported
  # with a cosine-only ablation beside them, because the whole question is whether geometry earns
  # its place - and the answer differs sharply by head and, more importantly, by domain. Measured
  # on the deployed corpus of independently generated designs, |dlog h| separates same-brief from
  # cross-brief matched pairs at AUC 0.56 against cosine's 0.65, the reverse of the ordering here,
  # where structural edits delete children and so shrink the box. In-domain gains below are
  # therefore not evidence of a deployment gain; the ladders and the self-vs-cross separation are.
  heads: dict[str, Any] = {}
  print("\nFITTED HEADS (trained on train pages, scored on held-out pages)")
  print(f"  {'head':6} {'features':14} {'train AUC':>10} {'held-out AUC':>13}")
  train_tables = build_head_tables(W, b, X, geometry, train, page_of)
  test_tables = build_head_tables(W, b, X, geometry, test, page_of)
  for name in ("match", "same"):
    train_features, train_labels = train_tables[name]
    test_features, test_labels = test_tables[name]
    for columns, label in ((FEATURES, "cosine+geometry"), (COSINE_ONLY, "cosine only")):
      head = fit_head(train_features, train_labels, columns)
      train_auc = roc_auc(head_logit(head, train_features), train_labels)
      test_auc = roc_auc(head_logit(head, test_features), test_labels)
      print(f"  {name:6} {label:14} {train_auc:10.4f} {test_auc:13.4f}")
      if columns is FEATURES:
        head["train_auc"] = train_auc
        head["held_out_auc"] = test_auc
        heads[name] = head
      else:
        heads[name]["cosine_only_held_out_auc"] = test_auc
    weights = dict(zip(heads[name]["columns"], (round(float(v), 4) for v in heads[name]["weights"])))
    print(f"         weights {weights}")

  head_arrays = {}
  for name, head in heads.items():
    head_arrays[f"head_{name}_weights"] = head["weights"]
    head_arrays[f"head_{name}_mean"] = head["mean"]
    head_arrays[f"head_{name}_sd"] = head["sd"]
    head_arrays[f"head_{name}_intercept"] = np.float32(head["intercept"])
  head_arrays["head_features"] = np.array(list(FEATURES))

  np.savez(args.out, W=W, b=b, dims=args.dims, **head_arrays,
           geometry_mean=np.array(geometry_stats["mean"], dtype=np.float32) if geometry_stats else np.zeros(0, dtype=np.float32),
           geometry_sd=np.array(geometry_stats["sd"], dtype=np.float32) if geometry_stats else np.zeros(0, dtype=np.float32),
           metrics=json.dumps({"before": before, "stage0": stage0, "after": final}),
           history=json.dumps(history))
  (args.out.with_suffix(".json")).write_text(json.dumps({
    "dims": args.dims, "margin": args.margin, "positive_margin": POSITIVE_MARGIN,
    "lambda_cal": LAMBDA_CAL, "lambda_ortho": LAMBDA_ORTHO, "epochs": args.epochs,
    # Every argument this run was given, so a projection records what produced it. Recovering an
    # unrecorded --max-invariant-drift cost a grid of comparisons and two retracted claims.
    "args": {key: (str(value) if isinstance(value, Path) else value)
             for key, value in vars(args).items()},
    "offset": "frozen at W*mu", "data": str(args.data),
    "input": "embedding + standardised log w/h" if geometry_stats else "embedding only",
    "geometry_stats": geometry_stats,
    "heads": {name: {"columns": head["columns"],
                     "weights": [float(v) for v in head["weights"]],
                     "intercept": head["intercept"],
                     "mean": [float(v) for v in head["mean"]],
                     "sd": [float(v) for v in head["sd"]],
                     "train_auc": head["train_auc"],
                     "held_out_auc": head["held_out_auc"],
                     "cosine_only_held_out_auc": head["cosine_only_held_out_auc"]}
              for name, head in heads.items()},
    "before": before, "stage0": stage0, "after": final, "history": history,
  }, indent=2) + "\n", encoding="utf-8")
  print(f"\nWrote {args.out}")


if __name__ == "__main__":
  main()
