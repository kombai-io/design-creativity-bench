"""The extraction schema for a design's own theme, and how two of them are compared.

This is deliberately categorical rather than pixel-precise wherever a model would have to
*estimate* a value (corner roundness, elevation, density): a model reading rendered CSS can
reliably say "this uses soft shadows" but not reliably agree with itself across two runs on
"this shadow's blur radius is 14px". Palette is the exception - hex values are usually read
directly off the source (a `:root` custom property or a literal color), which is a transcription
task, not an estimate, so exact hex is kept there.

Every field is optional. ``theme.py`` tells the model to omit a field entirely rather than guess
when the design does not clearly express it - a design with no elevation anywhere should produce
``elevation_style: null``, not a guessed "none".
"""

from __future__ import annotations

import colorsys
import math
from typing import Literal

from pydantic import BaseModel, Field


FontStyle = Literal["serif", "sans_serif", "monospace", "display", "mixed"]
Weight = Literal["normal", "medium", "bold"]
CornerStyle = Literal["sharp", "slightly_rounded", "rounded", "pill"]
ElevationStyle = Literal["none", "soft_shadow", "hard_shadow"]
BorderStyle = Literal["none", "hairline", "thick"]
Density = Literal["compact", "comfortable", "spacious"]


# Every field is now compared as a magnitude, never as an identity. Most of these categories are
# ordered scales - corners run sharp to pill, elevation runs flat to hard shadow - and scoring
# them `1.0 if equal else 0.0` threw away everything except the first step. On meridian's ds
# ladder that was fatal: corner, elevation and border all flipped together at L2 and pinned at
# zero, so DS mass went 11.14 -> 4.86 -> 4.74 and DS-3's further rounding registered as no change
# at all. The later rungs were then decided entirely by IA and RC noise, which is where that
# ladder rises. It also charged a one-step difference the full weight: slightly_rounded against
# rounded scored exactly as far apart as sharp against pill.
#
# Ranked here, a difference costs a fraction of the weight proportional to how far apart the two
# values sit on their own scale, so three levels of rounding produce three distinct scores.
_ORDERED_SCALES: dict[str, tuple[str, ...]] = {
  "corner_style": ("sharp", "slightly_rounded", "rounded", "pill"),
  "elevation_style": ("none", "soft_shadow", "hard_shadow"),
  "border_style": ("none", "hairline", "thick"),
  "density": ("compact", "comfortable", "spacious"),
  "heading_weight": ("normal", "medium", "bold"),
}

# font_style is the one field with no ordering to exploit - serif, monospace and display are
# different families, not more or less of one thing - so it stays an identity comparison. The
# near-miss worth crediting is that both sides are proportional text rather than monospace, so
# a mismatch between two proportional families scores a partial rather than a zero.
_FONT_NEIGHBOURS = {"serif", "sans_serif", "display", "mixed"}


# What a field means when the extractor omits it: the design did not express that decision, so
# it falls back to what an unstyled page looks like - white ground, black text, square corners,
# no shadow, no border. Every key is scored against these rather than skipped.
#
# Skipping was the alternative and it was unstable in two ways. The reachable ceiling moved from
# pair to pair (11.9, 13.4, 14.75 across one grid), so two scores were not on the same scale; and
# a key the extractor merely forgot changed the total silently - `surface` was absent at rc+ia_L2
# and present at L3, which handed that ladder a +1.00 rise out of nothing. With defaults, a key
# missing on BOTH sides scores 1.0 either way, so agreement-by-absence is stable, and a key
# missing on ONE side is a real difference: one design expresses an accent and the other does not.
_FIELD_DEFAULTS: dict[str, object] = {
  "bg": "#ffffff",
  "surface": "#ffffff",
  "ink": "#000000",
  "ink_muted": "#666666",
  "accent": "#808080",
  "border_color": "#cccccc",
  "font_style": "sans_serif",
  "heading_weight": "normal",
  "line_height": 1.5,
  "corner_style": "sharp",
  "elevation_style": "none",
  "border_style": "none",
  "density": "comfortable",
}


def ordered_similarity(field: str, a: str, b: str) -> float:
  """1.0 identical, falling linearly with distance along the field's own scale."""
  scale = _ORDERED_SCALES[field]
  if a not in scale or b not in scale:
    return 1.0 if a == b else 0.0
  return 1.0 - abs(scale.index(a) - scale.index(b)) / (len(scale) - 1)


def font_similarity(a: str, b: str) -> float:
  if a == b:
    return 1.0
  return 0.5 if a in _FONT_NEIGHBOURS and b in _FONT_NEIGHBOURS else 0.0


class ThemeAttributes(BaseModel):
  """One design's extracted theme. Every field: omit rather than guess if not clearly present."""

  bg: str | None = Field(default=None, description="Page background hex.")
  surface: str | None = Field(default=None, description="Raised panel/card background hex.")
  ink: str | None = Field(default=None, description="Primary text hex.")
  ink_muted: str | None = Field(default=None, description="Secondary/muted text hex.")
  accent: str | None = Field(default=None, description="Primary interactive/accent hex.")
  border_color: str | None = Field(default=None, description="Hairline/divider border hex, if borders are used as a separator.")


  font_style: FontStyle | None = Field(default=None, description="The dominant type family's character.")
  line_height: float | None = Field(default=None, description="Approximate base body line-height as a unitless ratio, e.g. 1.4.")
  heading_weight: Weight | None = Field(default=None, description="Heading font-weight character.")

  corner_style: CornerStyle | None = Field(default=None, description="Dominant corner-radius treatment across panels/cards/buttons.")
  elevation_style: ElevationStyle | None = Field(default=None, description="How surfaces are separated: drop shadows, or none at all.")
  border_style: BorderStyle | None = Field(default=None, description="How surfaces are separated by borders, if at all - independent of elevation_style; a design can use both, either, or neither.")
  density: Density | None = Field(default=None, description="Overall padding/spacing character.")


class ColorAttributes(BaseModel):
  """The six colour keys, and nothing else - the only keys the color-system facet scores.

  A separate schema rather than ThemeAttributes with fields ignored, because the schema IS the
  request. Asking a model for `corner_style`, `elevation_style` and `density` and then weighting
  them zero spends part of every call on estimates this module's own header warns are unreliable
  ("a model reading rendered CSS can *estimate* a value") and that were measured
  at chance against the human labels.

  A theme extracted this way is still scoreable: `diff_themes` falls back to _FIELD_DEFAULTS for
  any absent key, and those keys carry weight 0, so a colour-only theme and a thirteen-key theme
  produce the same color-system score for the same design.
  """

  bg: str | None = Field(default=None, description="Page background hex.")
  surface: str | None = Field(default=None, description="Raised panel/card background hex.")
  ink: str | None = Field(default=None, description="Primary text hex.")
  ink_muted: str | None = Field(default=None, description="Secondary/muted text hex.")
  accent: str | None = Field(default=None, description="Primary interactive/accent hex.")
  border_color: str | None = Field(default=None, description="Hairline/divider border hex, if borders are used as a separator.")


# --- comparing two extracted themes -----------------------------------------------------

_HEX_FIELDS = ("bg", "surface", "ink", "ink_muted", "accent", "border_color")
# Semantic colors (danger/warning/success/info, each a bg+ink pair) were REMOVED permanently on
# 2026-09-04. Eight keys at 0.25 each carried 2.0 of a 14.75 ceiling - 14% of every DS score - and
# almost no design declares them, so both sides fell back to _FIELD_DEFAULTS, matched each other and
# scored 1.000. That is 14% of the score spent on agreement about a decision neither design made.
# Measured on the 20 gold pairs: all 8 keys scored 1.000 on every pair. The ceiling is now 12.75.
_SEMANTIC_FIELDS: tuple[str, ...] = ()
_CATEGORICAL_FIELDS = ("font_style", "heading_weight", "corner_style", "elevation_style", "border_style", "density")

def _hex_to_rgb(value: str) -> tuple[int, int, int] | None:
  value = value.strip().lstrip("#")
  if len(value) == 3:
    value = "".join(ch * 2 for ch in value)
  if len(value) != 6:
    return None
  try:
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
  except ValueError:
    return None


# Below this much total chroma, two colors are grays and their hues are noise. At or above it the
# hue comparison counts in full. Two muted colors at C=0.15 each reach it.
CHROMA_FLOOR = 0.30


def color_similarity(a: str | None, b: str | None) -> float | None:
  """1.0 identical, 0.0 maximally different, None if either is unreadable.

  Compared in HSL as a chroma vector plus a lightness axis, and combined with max() rather than a
  weighted sum. The sum was the problem: with fixed weights adding to 1.0 no single dimension could
  ever drive the score to 0, so two opposite hues scored 0.45 and black against white scored 0.75.
  The colour third of DS could only range over about 0.63-1.0, which is why 20 gold pairs *built*
  to contrast on design system came out at DS 89.96 with a floor of 78.

  The three components, and what each is responsible for:

    hue         the DIRECTION of the chroma vector, and the only thing that can zero the score on
                its own. The chord between the two vectors is normalised by the chroma actually
                present, so opposite hues disagree completely at ANY lightness - two dark opposite
                hues score 0, not 0.5.

    chroma      the LENGTH of that vector, doing two jobs. It gates hue: two near-grays have short
                vectors, so their hues cannot pull the score down whatever they read as, which is
                what stops a warm white and a cool gray from being called opposites. And it is part
                of the disagreement in its own right, so a pale blue against a vivid blue at the
                same hue still costs something (0.61, where the old metric said 0.92).

                Chroma, not HSL saturation: S is ill-conditioned near the extremes, where a single
                RGB unit swings it wildly - #fdfcfc reports S=0.204 despite being white, which made
                two whites score 0.90. C = S * (1 - |2L - 1|) removes that.

    lightness   an independent axis, taken through max() so a light-vs-dark difference can never be
                masked by hue agreement. This is what makes black against white score 0 even though
                both are achromatic and agree on hue and chroma trivially.
  """
  if not a or not b:
    return None
  rgb_a, rgb_b = _hex_to_rgb(a), _hex_to_rgb(b)
  if rgb_a is None or rgb_b is None:
    return None
  hue_a, light_a, sat_a = colorsys.rgb_to_hls(*(channel / 255 for channel in rgb_a))
  hue_b, light_b, sat_b = colorsys.rgb_to_hls(*(channel / 255 for channel in rgb_b))

  chroma_a = sat_a * (1.0 - abs(2.0 * light_a - 1.0))
  chroma_b = sat_b * (1.0 - abs(2.0 * light_b - 1.0))
  ax, ay = chroma_a * math.cos(2 * math.pi * hue_a), chroma_a * math.sin(2 * math.pi * hue_a)
  bx, by = chroma_b * math.cos(2 * math.pi * hue_b), chroma_b * math.sin(2 * math.pi * hue_b)

  total_chroma = chroma_a + chroma_b
  hue_disagreement = (math.hypot(ax - bx, ay - by) / total_chroma) if total_chroma > 1e-6 else 0.0
  colour_disagreement = min(1.0, total_chroma / CHROMA_FLOOR) * hue_disagreement
  return max(0.0, 1.0 - max(colour_disagreement, abs(light_a - light_b)))


# What each individual key is worth, in the same "shared design facets" unit the segment
# score uses: a key that matches perfectly contributes exactly its weight, and the DS score
# is the un-normalised sum of those contributions. There is no category grouping and no
# denominator - grouping existed only to stop palette's sheer field count from dominating a
# *mean*, and once the score is a sum the fix belongs on the keys themselves, where it can
# say what each decision is actually worth rather than splitting a fixed budget six ways.
#
# The weights say: the four colors a reader actually sees as "the palette" (page, panel,
# text, accent) are full decisions, while muted-ink and hairline-color are derived from them
# and count half. Semantic colors are eight keys but largely conventional - red reads as
# Serif-vs-sans,
# sharp-vs-pill corners and shadow-vs-flat are the loudest identity decisions a design
# system makes and carry 1.5 each.
#
# Density is back at full weight. It was held at 0.15 while every categorical was scored as an
# identity, because the extractor disagreeing with itself by one step - "comfortable" against
# "compact" on unchanged CSS - cost the entire weight, the same as "compact" against
# "spacious". Ranked on its own scale a one-step disagreement now costs half, so the field can
# carry its real share without a near-miss reading as a total mismatch. It is also the only
# key that sees a spacing change at all: meridian's DS-3 rewrites every section's padding and
# type scale, and density moving spacious -> comfortable is the whole of what DS detects.
_FIELD_WEIGHT: dict[str, float] = {
  "bg": 1.0,
  "surface": 1.0,
  "ink": 1.0,
  "accent": 1.0,
  "ink_muted": 0.5,
  "border_color": 0.5,
  "font_style": 1.5,
  "heading_weight": 0.75,
  "line_height": 0.5,
  "corner_style": 1.5,
  "elevation_style": 1.5,
  "border_style": 1.0,
  "density": 1.0,
}

# THE SCORED FACET IS COLOUR ONLY, and the facet is named the color system for that reason.
#
# All thirteen keys above are still extracted and still reported in `field_scores`, because the
# analysis that produced this decision needs them - but only the six colour keys carry weight in
# the score. Measured on the 82 committed human cases:
#
#   - the six colour keys alone reproduce the whole thirteen-key facet's standalone agreement,
#     0.735 AUC against 0.736, while font_style, heading_weight, line_height, corner_style,
#     elevation_style, border_style and density are at or barely above chance on their own;
#   - restricting the facet to colour and changing nothing else moves agreement from 0.780 to
#     0.829 accuracy at the shipped 0.9 IA weight, and 0.853 to 0.867 AUC;
#   - it also removes the facet's cost to the ladders: 28/38 -> 30/38, rc-free 16/18 -> 17/18,
#     tau(ds-ia) +0.968 -> +0.984, and the two convergence rises the full facet was losing;
#   - and fitting the IA/facet weight by k-fold over briefs returns 0.90 for a colour-only facet
#     where it returned 0.50 for the thirteen-key one. The shipped weight was right for the facet
#     it was chosen for; the contents were what the fit objected to.
#
# The dropped keys are also the ones that leak into the IA facet, so they
# were being counted twice - most of it through the wrong facet.
COLOR_FIELDS = ("bg", "surface", "ink", "ink_muted", "accent", "border_color")
_SCORING_WEIGHT: dict[str, float] = {
  field: weight for field, weight in _FIELD_WEIGHT.items() if field in COLOR_FIELDS
}

# The most any pair can score if every scored key is present on both sides and matches exactly -
# the ceiling the color-system half of the combined number is measured against.
DS_WEIGHT_CEILING = sum(_SCORING_WEIGHT.values())


def diff_themes(a: dict, b: dict) -> dict:
  """Compare two extracted theme dicts. EVERY key is scored, none skipped.

  A key either design omits falls back to _FIELD_DEFAULTS - what an unstyled page looks like -
  so the set of scored keys, and therefore the reachable ceiling, is the same constant for every
  pair. Two designs that both omit a key agree on it and score 1.0; one that omits a key its
  counterpart expresses is charged the real distance, because expressing a decision and not
  expressing it is itself a difference.
  """
  scored: dict[str, float] = {}

  def sub_value(pair: object, sub: str) -> object:
    if isinstance(pair, dict):
      return pair.get(sub)
    return getattr(pair, sub, None)

  for field in _HEX_FIELDS:
    value_a = a.get(field) or _FIELD_DEFAULTS[field]
    value_b = b.get(field) or _FIELD_DEFAULTS[field]
    similarity = color_similarity(str(value_a), str(value_b))
    scored[field] = 1.0 if similarity is None else similarity

  for field in _SEMANTIC_FIELDS:
    pair_a, pair_b = a.get(field), b.get(field)
    for sub in ("bg", "ink"):
      key = f"{field}.{sub}"
      value_a = sub_value(pair_a, sub) or _FIELD_DEFAULTS[key]
      value_b = sub_value(pair_b, sub) or _FIELD_DEFAULTS[key]
      similarity = color_similarity(str(value_a), str(value_b))
      scored[key] = 1.0 if similarity is None else similarity

  for field in _CATEGORICAL_FIELDS:
    value_a = a.get(field) or _FIELD_DEFAULTS[field]
    value_b = b.get(field) or _FIELD_DEFAULTS[field]
    if field in _ORDERED_SCALES:
      scored[field] = ordered_similarity(field, str(value_a), str(value_b))
    elif field == "font_style":
      scored[field] = font_similarity(str(value_a), str(value_b))
    else:
      scored[field] = 1.0 if value_a == value_b else 0.0

  line_height_a = a.get("line_height")
  line_height_b = b.get("line_height")
  line_height_a = _FIELD_DEFAULTS["line_height"] if line_height_a is None else line_height_a
  line_height_b = _FIELD_DEFAULTS["line_height"] if line_height_b is None else line_height_b
  scored["line_height"] = max(0.0, 1.0 - abs(float(line_height_a) - float(line_height_b)) / 1.0)

  # Un-normalised, exactly like the segment score: sum of weight x similarity. Every scored key is
  # present, so weight_comparable always equals DS_WEIGHT_CEILING and two pairs' color-system
  # scores are on the same scale by construction. The unscored keys stay in `field_scores` at
  # weight 0 - measured, reported, and deliberately not counted.
  contributions = {field: _SCORING_WEIGHT.get(field, 0.0) * value
                   for field, value in scored.items()}
  weight_comparable = sum(_SCORING_WEIGHT.get(field, 0.0) for field in scored)
  overall_mass = sum(contributions.values())

  return {
    "overall_mass": overall_mass,
    "overall_score": (overall_mass / weight_comparable * 100.0) if weight_comparable else None,
    "field_scores": scored,
    "field_weights": {field: _SCORING_WEIGHT.get(field, 0.0) for field in scored},
    "field_contributions": contributions,
    "weight_comparable": weight_comparable,
    "weight_ceiling": DS_WEIGHT_CEILING,
    "fields_compared": len(scored),
  }
