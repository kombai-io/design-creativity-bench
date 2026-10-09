"""Compare a retrained projection with the shipped one, array by array.

  python projection/compare.py runs/projection.npz assets/projection.npz
"""
from __future__ import annotations

import sys

import numpy as np


def main(new: str, shipped: str) -> int:
  a, b = np.load(new), np.load(shipped)
  worst = 0.0
  for key in b.files:
    if key not in a.files or a[key].shape != b[key].shape:
      print(f"{key}: missing or shape differs")
      return 1
    if not np.issubdtype(b[key].dtype, np.number):
      diff = 0.0 if np.array_equal(a[key], b[key]) else float("inf")
    else:
      diff = float(np.abs(a[key].astype(np.float64) - b[key].astype(np.float64)).max()) if a[key].size else 0.0
    worst = max(worst, diff)
    print(f"{key:24} max |diff| {diff:.3g}")
  print("identical" if worst == 0 else f"max |diff| {worst:.3g}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main(*sys.argv[1:3]))
