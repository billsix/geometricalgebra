#!/usr/bin/env python3
# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

"""Report the book PDF's math and tables that run past the right margin.

LaTeX writes an ``Overfull \\hbox (Npt too wide) in paragraph at lines A--B`` line to
its log for every box wider than the text. This tool reads
``book/docs/_build/latex/geometry2.log`` and ``geometry2.tex`` (from ``make docs``),
looks at ``.tex`` lines A to B to tell a display equation from a table from text,
prints a count per kind, and lists every equation and table wider than the tolerance,
widest first, with its ``.tex`` line and the start of its content. A wide equation or
table is cut off in the printed book. It also counts the ``Overfull \\vbox (Npt too
high)`` boxes: one taller than the tolerance is usually a table that cannot break
across pages and is taller than one, so its last rows are not printed.

A display equation from a notebook is usually a gacalc value, a ``show_mult`` table or
a ``show_difference`` line; ``gacalc.base.blade_dict_latex`` and ``gacalc.nbdisplay``
break those between whole terms past ``LATEX_LINE_WIDTH`` (``TABLE_CELL_WIDTH`` in a
table). A wide hand-written equation in a ``.rst`` page needs ``\\\\`` and ``&`` at its
line breaks.

Usage: ``python tools/check_math_overflow.py [--tolerance PT] [--latex-dir DIR]``.
Exit 1 if an equation or a table is wider than the tolerance (default 10pt), or a box
is taller than the page by more than it.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
OVERFULL: re.Pattern[str] = re.compile(
    r"Overfull \\hbox \((?P<width>[\d.]+)pt too wide\) "
    r"(?:in paragraph at lines (?P<first>\d+)--(?P<last>\d+)"
    r"|detected at line (?P<at>\d+))"
)
TOO_HIGH: re.Pattern[str] = re.compile(
    r"Overfull \\vbox \((?P<height>[\d.]+)pt too high\)"
)


def kind_of(block: list[str]) -> str:
    """``table``, ``equation`` or ``text``: what the ``.tex`` lines of one box are.

    >>> kind_of([r"\\end{tabulary}"])
    'table'
    >>> kind_of([r"\\begin{split}a + b\\end{split}", r"\\end{equation}"])
    'equation'
    >>> kind_of(["Some words."])
    'text'
    """
    text: str = "\n".join(block)
    if "tabulary" in text or "longtable" in text:
        return "table"
    if any(marker in text for marker in ("{equation", "{split}", "{aligned}", "\\[")):
        return "equation"
    return "text"


def main() -> int:
    """Print the report; return 1 when an equation or table is too wide, or a box too
    high."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=10.0,
        help="points a box may overflow before it counts (default 10)",
    )
    parser.add_argument(
        "--latex-dir",
        type=pathlib.Path,
        default=ROOT / "book" / "docs" / "_build" / "latex",
        help="the Sphinx LaTeX build directory (default book/docs/_build/latex)",
    )
    arguments: argparse.Namespace = parser.parse_args()
    log: str = (arguments.latex_dir / "geometry2.log").read_text(errors="replace")
    tex: list[str] = (arguments.latex_dir / "geometry2.tex").read_text().splitlines()
    wide: list[tuple[float, int, str, str]] = []
    counts: dict[str, int] = {}
    match: re.Match[str]
    for match in OVERFULL.finditer(log):
        width: float = float(match.group("width"))
        first: int = int(match.group("first") or match.group("at"))
        last: int = int(match.group("last") or match.group("at"))
        block: list[str] = tex[max(first - 2, 0) : last]
        kind: str = kind_of(block)
        counts[kind] = counts.get(kind, 0) + 1
        if kind != "text" and width > arguments.tolerance:
            content: str = next((line.strip() for line in block if line.strip()), "")
            wide.append((width, last, kind, content[:120]))
    kind: str
    for kind in ("equation", "table", "text"):
        print(f"{kind}: {counts.get(kind, 0)} overfull boxes")
    width: float
    line: int
    content: str
    for width, line, kind, content in sorted(wide, reverse=True):
        print(f"{width:8.1f}pt  {kind:8}  tex:{line}  {content}")
    print(
        f"{len(wide)} equations and tables more than {arguments.tolerance:g}pt too wide"
    )
    high: list[float] = [
        height
        for height in (float(found.group("height")) for found in TOO_HIGH.finditer(log))
        if height > arguments.tolerance
    ]
    print(
        f"{len(high)} boxes more than {arguments.tolerance:g}pt taller than the page"
        + "".join(
            f"\n{height:8.1f}pt  too high" for height in sorted(high, reverse=True)
        )
    )
    return 1 if wide or high else 0


if __name__ == "__main__":
    sys.exit(main())
