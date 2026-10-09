"""Drop containers that hold no content - only decoration.

A `<div class="bg" aria-hidden="true">` wrapping three empty divs styled into hairlines, a grid
overlay and a glow is a full-viewport element with nothing in it. The pipeline scored one as a
top-weight container: size 1.000 because it covers the first screen, position 1.00 because it is
in the viewport, intrinsic weight 1.000 - and because the design it was compared against had no
decorative layer of its own, nothing matched it, so its whole weight became an unmatched penalty.
On opus_5_max/page_5/domain_1_2 that was 0.94 of the design's 5.4 budget, 17% of its importance,
spent on an invisible near-black rectangle. Measured across 250 pairs, such elements hold a median
4.4% of a design's weight and up to 24.3%.

The test is deterministic and reads the rendered DOM, not the classifier: does this container's
subtree contain a text node with any non-whitespace character, or any graphic element? If neither,
there is nothing in it to compare. `data-kid` is stamped on the post-load DOM, so script-built
content counts like anything else.

Rewrites `category` to `decoration`, which `eligible_kids` then drops, so nothing else needs to
change - the same route wrapper_filter.py takes.

Known limit: a container whose only content is a CSS background-image is dropped too, because
resolving that needs the stylesheet. Its picture is decoration by any reasonable reading, but it is
a picture, so this errs toward dropping.

Usage:
  python -m dcbench.content_filter CSV_PATH [HTML_PATH] [--apply]
  python -m dcbench.content_filter --tree DIR [--apply]      # every CSV under DIR, paired by name
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

# Same set segments.py's measure pass calls a graphic.
GRAPHIC = {"img", "video", "svg", "canvas", "picture", "iframe", "object"}
# Nothing these contain is rendered content.
NON_RENDERING = {"script", "style", "template", "noscript", "title", "meta", "link"}
DECORATION = "decoration"


def html_for(csv_path: Path) -> Path:
    """The stamped document beside a CSV.

    Three naming conventions are in use: the pair directories hold `A.csv` next to `A.html`, the
    benchmark designs hold `design.csv` next to `design_with_kid.html`, and the ladder runs hold
    `<name>.csv` next to `<name>_with_kid.html`. The `_with_kid` form is tried first because a
    plain `<name>.html` may also exist there and is the unstamped copy.
    """
    stamped = csv_path.with_name(f"{csv_path.stem}_with_kid.html")
    if stamped.is_file():
        return stamped
    return csv_path.with_suffix(".html")


def contentless(html_path: Path) -> set[str]:
    """Every `data-kid` whose subtree renders no text and holds no graphic."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    empty: set[str] = set()
    for element in soup.find_all(attrs={"data-kid": True}):
        if element.name in NON_RENDERING:
            continue
        has_graphic = element.name in GRAPHIC or element.find(lambda t: t.name in GRAPHIC) is not None
        if has_graphic:
            continue
        has_text = False
        for node in element.descendants:
            if isinstance(node, NavigableString):
                parent = node.parent.name if node.parent else ""
                if parent not in NON_RENDERING and str(node).strip():
                    has_text = True
                    break
        if not has_text:
            empty.add(str(element["data-kid"]))
    return empty


def filter_csv(csv_path: Path, html_path: Path, apply: bool) -> tuple[int, int]:
    empty = contentless(html_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    changed = 0
    for row in rows:
        kid = (row.get("data-kid") or "").strip()
        if (row.get("category") or "").strip() == "container" and kid in empty:
            row["category"] = DECORATION
            changed += 1
    if apply and changed:
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return changed, sum(1 for r in rows if (r.get("category") or "").strip() == "container") + changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path", type=Path, nargs="?")
    parser.add_argument("html_path", type=Path, nargs="?")
    parser.add_argument("--tree", type=Path, help="Process every CSV beneath this directory")
    parser.add_argument("--apply", action="store_true", help="Rewrite the CSVs; otherwise just report")
    args = parser.parse_args()

    if args.tree:
        targets = [(p, html_for(p)) for p in sorted(args.tree.rglob("*.csv"))
                   if not p.stem.endswith(("_with_kid", ".cost"))]
        targets = [(c, h) for c, h in targets if h.is_file()]
    elif args.csv_path:
        targets = [(args.csv_path, args.html_path or html_for(args.csv_path))]
    else:
        parser.error("give a CSV path or --tree")

    total_changed = total_containers = 0
    touched = 0
    for csv_path, html_path in targets:
        changed, containers = filter_csv(csv_path, html_path, args.apply)
        total_changed += changed
        total_containers += containers
        touched += bool(changed)
        if changed:
            print(f"{'reclassified' if args.apply else 'would reclassify'} {changed:>3} of "
                  f"{containers:>3} containers  {csv_path.relative_to(args.tree) if args.tree else csv_path}")
    share = 100 * total_changed / total_containers if total_containers else 0.0
    print(f"\n{total_changed} of {total_containers} scored containers ({share:.2f}%) hold no content, "
          f"across {touched} of {len(targets)} designs")
    if not args.apply:
        print("Nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
