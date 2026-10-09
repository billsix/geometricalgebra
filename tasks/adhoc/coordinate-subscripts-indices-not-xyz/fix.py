#!/usr/bin/env python3
"""Codemod for tasks/coordinate-subscripts-indices-not-xyz: axis-letter coordinate
subscripts -> indexed ones, matched on CONTENT (never on saved line numbers).

Two spellings are rewritten, in every file ``discover.sh`` scans:

* LaTeX in the book pages and the outline: ``\\vec{a}_x`` -> ``a_1``,
  ``\\vec{b}'_y`` -> ``b'_2``, ``\\vec{b}_z`` -> ``b_3`` (braced ``_{x}`` too).
  The arrow goes: a coordinate is a scalar.
* Plain identifiers in notebooks, figure labels and markdown: ``a_x`` -> ``a_1``,
  ``v_y`` -> ``v_2``, ``p_z`` -> ``p_3`` -- including inside the strings handed to
  ``sympy.symbols(...)``, so the symbols print with the subscripts the prose uses.

Idempotent: a second run changes nothing. Paths are repo-relative (resolved from the
repo root, which is three directories above this file). Run from anywhere::

    python tasks/adhoc/coordinate-subscripts-indices-not-xyz/fix.py
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
INDEX: dict[str, str] = {"x": "1", "y": "2", "z": "3"}

# The closing brace is consumed only when the subscript opened one (`_{x}`), never a
# brace belonging to an enclosing `\\frac{...}`: `\\vec{a}_x}` must become `a_1}`.
LATEX: re.Pattern[str] = re.compile(r"\\vec\{([a-z])\}('?)_(?:\{([xyz])\}|([xyz]))")
PLAIN: re.Pattern[str] = re.compile(r"\b([a-z])('?)_([xyz])\b")


def rewrite(text: str) -> str:
    text = LATEX.sub(
        lambda m: f"{m.group(1)}{m.group(2)}_{INDEX[m.group(3) or m.group(4)]}", text
    )
    return PLAIN.sub(lambda m: f"{m.group(1)}{m.group(2)}_{INDEX[m.group(3)]}", text)


def main() -> int:
    targets: list[pathlib.Path] = [
        *sorted((REPO / "book/docs").glob("*.rst")),
        *sorted((REPO / "book/docs/notebooks").glob("*.py")),
        *sorted((REPO / "book/figures/epix").glob("*.py")),
        REPO / "tasks/reference/book-outline.md",
    ]
    changed: int = 0
    path: pathlib.Path
    for path in targets:
        before: str = path.read_text(encoding="utf-8")
        after: str = rewrite(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"rewrote {path.relative_to(REPO)}")
    print(f"{changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
