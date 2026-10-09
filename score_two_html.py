"""The paper's pair similarity S for any two HTML pages.

  python score_two_html.py A.html B.html
  python score_two_html.py A.html B.html --uiclip-endpoint http://host:8000 --work runs/pair

Both pages go through the benchmark's design preparation (segments, Gemini and UIClip embeddings,
colour palette); S = 0.9 S_IA + 0.1 S_colour on 0-100, and the pair's distinctiveness is 1 - S/100.
Needs OPENAI_API_KEY and GEMINI_API_KEY (see README).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile

from dcbench import uiclip
from dcbench.prepare import prepare
from dcbench.similarity import Scorer


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("html_a", type=Path)
  parser.add_argument("html_b", type=Path)
  parser.add_argument("--work", type=Path, help="keep intermediates here (default: a temp directory)")
  parser.add_argument("--uiclip-endpoint", help="a UIClip server instead of running the model locally")
  args = parser.parse_args()

  work = (args.work or Path(tempfile.mkdtemp(prefix="dcbench_pair_"))).resolve()
  encoder = uiclip.Remote(args.uiclip_endpoint) if args.uiclip_endpoint else uiclip.Local()
  sides = {"a": args.html_a, "b": args.html_b}
  with ThreadPoolExecutor(2) as pool:
    list(pool.map(lambda side: prepare(sides[side], work / side, encoder), sides))
  result = Scorer().score(work / "a", work / "b")
  if result is None:
    print("one of the pages has no scorable segments")
    return 1
  result = {k: round(v, 4) if isinstance(v, float) else v for k, v in result.items()}
  result["distinctiveness"] = round(1 - result["similarity"] / 100, 4)
  print(json.dumps({**result, "a": str(args.html_a), "b": str(args.html_b), "work": str(work)}, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
