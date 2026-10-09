"""Drop containers whose picture is really their child's picture.

A container holding a 26px header plus a panel that fills the rest is scored, and so is the panel -
the same content twice, with the parent's similarity largely restating the child's. `eligible_kids`
does not catch it: its wrapper rule needs exactly one visible child with a withheld sibling, and the
`num_children > 1` gate passes a two-child wrapper straight through.

The test has to be the LARGEST single child, not the sum. On one real pair, `1-2-2` (1032x346) holds
`1-2-2-2` (1032x320) - 92.5% of its area, so the two screenshots differ by a thin strip. Its own
parent `1-2` has four children summing to 99.96% of it, but its largest is 41%, and `1-2` is a
genuine composition. Summed area cannot tell those apart; the max can.

Rewrites `category` to `wrapper` for the offenders, which `eligible_kids` then drops, so nothing
else needs to change. Only parent/child pairs where BOTH were captured are considered - those are
exactly the rows that would otherwise be double-counted.

Usage:
  python -m dcbench.wrapper_filter SEGMENTS_DIR CSV_PATH [--ratio 0.9] [--apply]
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("segments_dir", type=Path)
  parser.add_argument("csv_path", type=Path)
  parser.add_argument("--ratio", type=float, default=0.9)
  parser.add_argument("--apply", action="store_true", help="Rewrite the CSV; otherwise just report")
  return parser.parse_args()


def dominated(segments_dir: Path, ratio: float) -> dict[str, tuple[str, float]]:
  """kid -> (child that fills it, fraction) for every captured parent a captured child dominates."""
  manifest = segments_dir / "segment_images.json"
  if not manifest.is_file():
    return {}
  boxes = {}
  for row in json.loads(manifest.read_text(encoding="utf-8")).get("results", []):
    area = int(row.get("width") or 0) * int(row.get("height") or 0)
    if area > 0:
      boxes[row["data_kid"]] = area
  out: dict[str, tuple[str, float]] = {}
  for kid, area in boxes.items():
    best, fraction = None, 0.0
    for other, child_area in boxes.items():
      if other.startswith(kid + "-") and child_area / area > fraction:
        best, fraction = other, child_area / area
    if best and fraction >= ratio:
      out[kid] = (best, fraction)
  return out


def main() -> int:
  args = parse_args()
  hits = dominated(args.segments_dir, args.ratio)
  rows = list(csv.DictReader(args.csv_path.open(encoding="utf-8", newline="")))
  fields = list(rows[0].keys()) if rows else []
  changed = 0
  for row in rows:
    kid = (row.get("data-kid") or "").strip()
    if kid in hits and (row.get("category") or "").strip() == "container":
      row["category"] = "wrapper"
      changed += 1
  print(f"{args.csv_path.name}: {changed} wrapper(s) of {len(rows)} rows"
        + (f" -> {', '.join(f'{k} filled {v[1]:.0%} by {v[0]}' for k, v in list(hits.items())[:3])}" if hits else ""))
  if args.apply and changed:
    with args.csv_path.open("w", encoding="utf-8", newline="") as handle:
      writer = csv.DictWriter(handle, fieldnames=fields)
      writer.writeheader()
      writer.writerows(rows)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
