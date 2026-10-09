"""Score a model's designs on the public subset and place it among the 15 panel models.

  python evaluate_model.py outputs/my_model --lab "My Lab"

The directory holds one HTML file per prompt in data/prompts, named after the prompt:
task1_1.html, task1_2.html, ..., task10_2.html (20 files). Each page should be a complete,
self-contained desktop design (1280px wide) generated from the matching prompt.

Per design: segments + Gemini embeddings, the colour palette and UIClip embeddings. Then:

  originality      vs. each panel model from a different lab (--lab), same prompt
  creative range   the model's two designs of each task
  diversity        0.9 originality + 0.1 creative range

Intermediates go to runs/<model>/ and are reused on a rerun. Needs OPENAI_API_KEY and
GEMINI_API_KEY (see README). UIClip runs locally unless --uiclip-endpoint is given.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys

from dcbench import benchmark as BM
from dcbench import uiclip
from dcbench.prepare import prepare
from dcbench.similarity import Scorer


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("designs", type=Path, help="directory of task<N>_<d>.html files")
  parser.add_argument("--name", help="model name for the report (default: the directory name)")
  parser.add_argument("--lab", default="", help="the model's lab; panel models from the same lab are "
                                                "left out of its originality pairs, as in the paper")
  parser.add_argument("--work", type=Path, default=Path("runs"), help="where intermediates go")
  parser.add_argument("--uiclip-endpoint", help="a UIClip server instead of running the model locally")
  parser.add_argument("--workers", type=int, default=4, help="designs processed in parallel")
  parser.add_argument("--json", type=Path, help="also write the result here")
  args = parser.parse_args()

  name = args.name or args.designs.resolve().name
  work = (args.work / name).resolve()
  ids = BM.prompt_ids()
  missing = [pid for pid in ids if not (args.designs / f"{pid}.html").is_file()]
  if missing:
    print(f"missing {len(missing)} of {len(ids)} designs: {', '.join(missing)}", file=sys.stderr)
    if len(missing) == len(ids):
      return 1

  encoder = uiclip.Remote(args.uiclip_endpoint) if args.uiclip_endpoint else uiclip.Local()
  present = [pid for pid in ids if pid not in missing]

  def run(pid: str) -> tuple[str, str | None]:
    try:
      prepare(args.designs / f"{pid}.html", work / pid, encoder)
      return pid, None
    except Exception as error:  # noqa: BLE001 - one bad page should not lose the others
      return pid, f"{type(error).__name__}: {error}"

  print(f"preparing {len(present)} designs -> {work}", flush=True)
  with ThreadPoolExecutor(args.workers) as pool:
    failed = {pid: err for pid, err in pool.map(run, present) if err}
  for pid, err in failed.items():
    print(f"  {pid}: {err}", file=sys.stderr)
  ready = [pid for pid in present if pid not in failed]

  scorer = Scorer()
  design_of = lambda pid: (work / pid) if pid in ready else None
  o, o_pairs = BM.originality(scorer, design_of, args.lab)
  r, r_pairs = BM.creative_range(scorer, design_of)
  result = {"model": name, "lab": args.lab, "designs": len(ready),
            "diversity": round(BM.diversity(o, r), 4), "originality": round(o, 4),
            "originality_pairs": o_pairs, "creative_range": round(r, 4), "range_pairs": r_pairs}
  print(json.dumps(result, indent=2))

  rows = BM.subset_reference() + [{**result, "label": f"> {name}"}]
  rows.sort(key=lambda row: -float(row["diversity"]))
  print(f"\n{'':4}{'model':28}{'divers.':>8}{'orig.':>8}{'range':>8}")
  for rank, row in enumerate(rows, 1):
    print(f"{rank:<4}{row['label']:28}{float(row['diversity']):8.3f}{float(row['originality']):8.3f}"
          f"{float(row['creative_range']):8.3f}")
  print("\nScores are on the 20 public prompts and compare only with the rows above, not with the "
        "paper's results.")
  if args.json:
    args.json.write_text(json.dumps(result, indent=2) + "\n")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
