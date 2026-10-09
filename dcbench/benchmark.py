"""The diversity measures on the public subset (paper, "Details of the metrics" and Appendix "The overall score").

  originality      mean of 1 - S over pairs with every panel model from a different lab, same prompt
  creative range   mean of 1 - S over a model's two designs of each task (the two domain prompts)
  diversity        0.9 originality + 0.1 creative range

S is on 0-1 here (similarity.py returns 0-100).
"""
from __future__ import annotations

import csv
from pathlib import Path
import statistics as st

from .similarity import Scorer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
W_ORIGINALITY, W_RANGE = 0.9, 0.1


def tasks() -> list[dict]:
  return list(csv.DictReader((DATA / "tasks.csv").open()))


def prompt_ids() -> list[str]:
  return [row["prompt_id"] for row in tasks()]


def panel() -> list[dict]:
  return list(csv.DictReader((DATA / "models.csv").open()))


def panel_design(model: str, prompt_id: str) -> Path:
  return DATA / "features" / model / prompt_id


def originality(scorer: Scorer, design_of, lab: str, exclude: str = "") -> tuple[float, int]:
  """Mean 1 - S over (prompt, panel model of another lab) pairs; `design_of(prompt_id)` is the model's design."""
  distances = []
  for pid in prompt_ids():
    mine = design_of(pid)
    if mine is None:
      continue
    for row in panel():
      if row["lab"] == lab or row["model"] == exclude:
        continue
      theirs = panel_design(row["model"], pid)
      # One orientation per pair, so a pair met from both sides is scored once and reads the same.
      result = scorer.score(*sorted((mine, theirs), key=str))
      if result is not None:
        distances.append(1 - result["similarity"] / 100)
  return (st.fmean(distances) if distances else float("nan")), len(distances)


def creative_range(scorer: Scorer, design_of) -> tuple[float, int]:
  """Mean 1 - S over the two-prompt pair of every task."""
  distances = []
  for row in tasks():
    if row["domain"] != "1":
      continue
    a, b = design_of(f"task{row['task']}_1"), design_of(f"task{row['task']}_2")
    if a is None or b is None:
      continue
    result = scorer.score(a, b)
    if result is not None:
      distances.append(1 - result["similarity"] / 100)
  return (st.fmean(distances) if distances else float("nan")), len(distances)


def diversity(o: float, r: float) -> float:
  return W_ORIGINALITY * o + W_RANGE * r


def subset_reference() -> list[dict]:
  return list(csv.DictReader((DATA / "reference/subset_scores.csv").open()))
