"""Rebuild data/reference/subset_scores.csv: the 15 panel models' diversity on the public subset.

Uses only what ships in data/: the panel's precomputed features (data/features). No API calls.

  python build_reference.py
"""
from __future__ import annotations

import csv

from dcbench import benchmark as BM
from dcbench.similarity import Scorer


def main() -> int:
  scorer = Scorer()
  rows = []
  for model in BM.panel():
    name = model["model"]
    design_of = lambda pid, name=name: BM.panel_design(name, pid)
    o, o_pairs = BM.originality(scorer, design_of, model["lab"], exclude=name)
    r, r_pairs = BM.creative_range(scorer, design_of)
    rows.append({"model": name, "label": model["label"], "lab": model["lab"],
                 "diversity": round(BM.diversity(o, r), 4), "originality": round(o, 4),
                 "creative_range": round(r, 4), "originality_pairs": o_pairs, "range_pairs": r_pairs})
    print(f"{model['label']:22} originality {o:.4f} ({o_pairs})  range {r:.4f} ({r_pairs})", flush=True)
  rows.sort(key=lambda row: -row["diversity"])
  out = BM.DATA / "reference/subset_scores.csv"
  with out.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
  print(f"wrote {out.relative_to(BM.ROOT)}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
