"""Turn one HTML page into a scoreable design directory.

  segments   measure the page, find its segments, screenshot and Gemini-embed each one
  theme      read the page's six-role colour palette from its CSS (one LLM call)
  uiclip     UIClip-embed each segment screenshot

Each step skips when its output already exists, so an interrupted run resumes.
"""
from __future__ import annotations

from pathlib import Path

from . import segments, theme, uiclip


def prepare(html: Path, design: Path, encoder: "uiclip.Local | uiclip.Remote", workers: int = 8,
            theme_model: str = theme.MODEL) -> Path:
  design.mkdir(parents=True, exist_ok=True)
  if not ((design / "design.csv").is_file() and (design / "segments/segment_images.json").is_file()):
    segments.build(html, design, workers)
  if not (design / "theme.json").is_file():
    theme.extract(html, design / "theme.json", theme_model)
  uiclip.embed_design(design, encoder)
  return design
