"""Extract a page's colour system: six palette roles read from its own CSS (paper, Appendix "Colour system and the final score").

An LLM reads the page source and returns the six roles in a structured schema - page background,
panel background, primary text, muted text, accent, divider - omitting any role the page does not
express and excluding content-specific tints. The comparison of two palettes is deterministic
(theme_spec.diff_themes).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import llm
from .theme_spec import ColorAttributes

MODEL = "gpt-5.6-luna"
EFFORT = "low"
TOOL_NAME = "submit_theme"
SYSTEM = "You are a meticulous design-systems reviewer reading a page's source CSS to catalogue its theme."

COLOR_PROMPT_TEMPLATE = """Read this HTML document's own CSS (usually a `:root` custom-property
block, sometimes literal values on individual rules) and report its six palette colours.

Rules:
- Read values off the source, do not estimate from imagining the rendered page.
- If the design does not clearly express a field - no borders used anywhere, for instance, so
  `border_color` cannot be read - OMIT that field entirely. Do not guess a default.
- Report only these six: the page background, the raised panel/card background, primary text,
  secondary/muted text, the primary interactive accent, and the hairline/divider colour.
- Per-item tints that identify content rather than the product - a per-person avatar colour, a
  per-category chip - are not part of the palette. Skip them.

<input_doc>
{html}
</input_doc>

Call {tool_name} and exit.
"""


def extract(html_path: Path, out_path: Path, model: str = MODEL) -> dict:
  html = html_path.read_text(encoding="utf-8")
  parsed = llm.call_tool(
    model=model, system=SYSTEM,
    content=[llm.text_part(COLOR_PROMPT_TEMPLATE.format(html=html, tool_name=TOOL_NAME))],
    tool_name=TOOL_NAME, description="Submit the extracted colour palette for this design.",
    schema=ColorAttributes, effort=EFFORT)
  theme = parsed.model_dump(exclude_none=True)
  out_path.write_text(json.dumps(theme, indent=2), encoding="utf-8")
  return theme
