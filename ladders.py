"""Score the controlled ladders (paper, Appendix "Controlled ladders and robustness ablations").

  python ladders.py                 # all six studies, 18 ladders
  python ladders.py --uiclip-endpoint http://host:8000

A ladder is three cumulative edits, L1-L3, with a known direction. In a convergence study a seed
design is edited towards a fixed reference, so similarity to the reference should rise; in a
perturbation study a design is edited away from its original, so similarity to it should fall.
DS edits change the visual styles, IA edits the information architecture, DS+IA both. The edits
are written out per variant in data/ladders/<study>/specs/.

Each rung is scored as S(anchor, variant), where the anchor is the reference (convergence) or the
original (perturbation). A ladder passes when both adjacent steps move strictly in its direction.
Results are printed next to the paper's (data/ladders/paper_ladders.csv) and written to
runs/ladders/ladders.csv. Needs OPENAI_API_KEY and GEMINI_API_KEY (see README); preparing the 60
pages costs about $1.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from pathlib import Path
import sys

from dcbench import uiclip
from dcbench.prepare import prepare
from dcbench.similarity import Scorer

ROOT = Path(__file__).resolve().parent
LADDERS = ROOT / "data/ladders"
STUDIES = {"convergence_incidents": "rise", "convergence_storefront": "rise", "convergence_schedule": "rise",
           "perturbation": "fall", "perturbation62": "fall", "perturbation_landing": "fall"}
FACETS = ("ds", "ia", "ds+ia")
LEVELS = (1, 2, 3)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--work", type=Path, default=ROOT / "runs/ladders")
  parser.add_argument("--uiclip-endpoint", help="a UIClip server instead of running the model locally")
  parser.add_argument("--workers", type=int, default=4)
  args = parser.parse_args()

  pages = [(study, name) for study in STUDIES
           for name in ["anchor"] + [f"{f}_L{n}" for f in FACETS for n in LEVELS]]
  encoder = uiclip.Remote(args.uiclip_endpoint) if args.uiclip_endpoint else uiclip.Local()

  def run(page: tuple[str, str]) -> str | None:
    study, name = page
    try:
      prepare(LADDERS / study / f"{name}.html", args.work / study / name, encoder)
      return None
    except Exception as error:  # noqa: BLE001
      return f"{study}/{name}: {type(error).__name__}: {error}"

  print(f"preparing {len(pages)} pages -> {args.work}", flush=True)
  with ThreadPoolExecutor(args.workers) as pool:
    errors = [e for e in pool.map(run, pages) if e]
  for error in errors:
    print(f"  {error}", file=sys.stderr)
  if errors:
    return 1

  paper = {(r["case"], r["facets"]): r for r in csv.DictReader((LADDERS / "paper_ladders.csv").open())
           if r["series"] == "shipped metric"}
  scorer = Scorer()
  rows, passed = [], 0
  print(f"\n{'study':24}{'facets':8}{'dir':6}{'L1':>7}{'L2':>7}{'L3':>7}  {'pass':6}{'paper L1-L3':>22}")
  for study, direction in STUDIES.items():
    for facets in FACETS:
      scores = [scorer.score(args.work / study / "anchor", args.work / study / f"{facets}_L{n}")["similarity"] / 100
                for n in LEVELS]
      steps = [b - a for a, b in zip(scores, scores[1:])]
      ok = all(s > 0 for s in steps) if direction == "rise" else all(s < 0 for s in steps)
      passed += ok
      ref = paper.get((study, facets), {})
      ref_text = " ".join(ref.get(f"L{n}", "-") for n in LEVELS)
      print(f"{study:24}{facets:8}{direction:6}" + "".join(f"{s:7.2f}" for s in scores)
            + f"  {'yes' if ok else 'NO':6}{ref_text:>22}")
      rows.append({"study": study, "facets": facets, "direction": direction,
                   **{f"L{n}": round(s, 4) for n, s in zip(LEVELS, scores)},
                   "travel": round(scores[-1] - scores[0], 4), "monotone": "yes" if ok else "no"})
  print(f"\n{passed}/{len(rows)} ladders move strictly in their expected direction (paper: 18/18)")
  out = args.work / "ladders.csv"
  with out.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
  print(f"wrote {out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
