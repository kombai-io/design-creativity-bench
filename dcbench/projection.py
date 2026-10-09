"""The trained linear projection applied to every segment embedding before it is compared.

A projection maps a (windows, dims) strip window by window as z(x) = Wx - b. The Gemini projection
(assets/projection.npz) also takes the segment's standardised log width and height as two extra
inputs; the statistics for that standardisation are stored with the weights.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

# Every segment is resampled to the same number of windows so that two strips of different length
# can be compared position by position.
RESAMPLE_WINDOWS = 8

# An unmatched segment that resembles one of its own page's matched segments at least this closely
# is a repeat of it, and is removed before the page weights are recomputed.
NEAR_DUPLICATE_SIMILARITY = 0.90


def load_projection(path: Path) -> tuple[np.ndarray, np.ndarray, dict | None]:
  """The trained projection, as (W, b) with z(x) = Wx - b, and its geometry statistics if any."""
  if not path.is_file():
    raise ValueError(f"No projection at {path}")
  payload = np.load(path, allow_pickle=False)
  if "W" not in payload or "b" not in payload:
    raise ValueError(f"{path} has no W/b")
  W = payload["W"].astype(np.float32)
  b = payload["b"].astype(np.float32)
  if W.ndim != 2 or b.ndim != 1 or W.shape[0] != b.shape[0]:
    raise ValueError(f"Projection shapes disagree: W {W.shape}, b {b.shape}")
  stats = None
  if "geometry_mean" in payload and payload["geometry_mean"].size:
    stats = {"mean": payload["geometry_mean"].astype(np.float32),
             "sd": payload["geometry_sd"].astype(np.float32)}
  return W, b, stats


def augment_strip(strip: np.ndarray, size: tuple[int, int] | None, stats: dict) -> np.ndarray:
  """Append the segment's standardised log width and height to each of its windows.

  A segment whose capture size is unknown gets the training mean, which standardises to zero.
  """
  windows = strip.shape[0]
  if size is None:
    scaled = np.zeros((windows, stats["mean"].shape[0]), dtype=np.float32)
  else:
    logs = np.log(np.maximum(np.asarray(size, dtype=np.float32), 1.0))
    scaled = np.tile(((logs - stats["mean"]) / stats["sd"]).astype(np.float32), (windows, 1))
  return np.hstack([strip, scaled])


def project_vectors(
  vectors: dict[str, np.ndarray],
  W: np.ndarray,
  b: np.ndarray,
  sizes: dict[str, tuple[int, int]] | None = None,
  stats: dict | None = None,
) -> dict[str, np.ndarray]:
  """Map every (windows, dims) strip through the projection, window by window."""
  if stats is None:
    return {name: (strip @ W.T - b).astype(np.float32) for name, strip in vectors.items()}
  sizes = sizes or {}
  return {
    name: (augment_strip(strip, sizes.get(Path(name).stem), stats) @ W.T - b).astype(np.float32)
    for name, strip in vectors.items()
  }


def resample(strip: np.ndarray, count: int) -> np.ndarray:
  """Stretch or compress a (windows, dims) strip onto a fixed number of windows."""
  windows = strip.shape[0]
  if windows == count:
    return strip
  if windows == 1:
    return np.repeat(strip, count, axis=0)
  position = np.linspace(0.0, windows - 1, count)
  lower = np.floor(position).astype(int)
  upper = np.minimum(lower + 1, windows - 1)
  weight = (position - lower)[:, None]
  return strip[lower] * (1.0 - weight) + strip[upper] * weight
