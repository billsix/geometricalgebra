# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
"""Turn backticked math in the Part III notebooks' Markdown into $...$ LaTeX (one-shot).

Only Markdown comment lines are touched. A backticked span becomes LaTeX unless it is
in ``CODE`` (an identifier or call the reader types), which stays backticked. The
symbol table below is the whole translation; a second run finds no backticked math
left and changes nothing.
"""

import pathlib
import re
import sys

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
NOTEBOOKS: list[str] = [
    "bootstrap-rotation",
    "bootstrap-projection",
    "bootstrap-rotation-from-projection",
    "bootstrap-product",
    "bootstrap-projection-from-product",
    "bootstrap-rotation-from-product",
]
CODE: frozenset[str] = frozenset(
    {"Vector.rotate(θ)", "versor_rotation", "projection_rotation"}
)
SYMBOLS: list[tuple[str, str]] = [
    ("a_hat", r"\hat{a}"),
    ("b_hat", r"\hat{b}"),
    ("R̃", r"\tilde{R}"),
    ("⁻¹", "^{-1}"),
    ("θ", r"\theta"),
    ("π", r"\pi"),
    ("α", r"\alpha"),
    ("β", r"\beta"),
    ("·", r"\cdot"),
    ("∧", r"\wedge"),
    ("∘", r"\circ"),
    ("cos(", r"\cos("),
    ("sin(", r"\sin("),
    ("proj_", r"\operatorname{proj}_"),
    ("rej_", r"\operatorname{rej}_"),
    ("e_12", "e_{12}"),
]


def to_latex(span: str) -> str:
    """``span`` (the text between backticks) written as LaTeX."""
    out: str = span
    old: str
    new: str
    for old, new in SYMBOLS:
        out = out.replace(old, new)
    return out


def convert_line(line: str) -> str:
    """A Markdown comment line with its backticked math as ``$...$``."""
    if not line.startswith("# ") or line.startswith("# %%"):
        return line
    return re.sub(
        r"`([^`]+)`",
        lambda match: (
            match.group(0)
            if match.group(1) in CODE
            else "$" + to_latex(match.group(1)) + "$"
        ),
        line,
    )


def main() -> int:
    """Convert every listed notebook in place; print the lines now over 88 columns."""
    name: str
    for name in NOTEBOOKS:
        path: pathlib.Path = ROOT / "book" / "docs" / "notebooks" / f"{name}.py"
        lines: list[str] = [
            convert_line(line) for line in path.read_text().splitlines()
        ]
        path.write_text("\n".join(lines) + "\n")
        number: int
        line: str
        for number, line in enumerate(lines, start=1):
            if len(line) > 88:
                print(f"{name}.py:{number}: {len(line)}")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
