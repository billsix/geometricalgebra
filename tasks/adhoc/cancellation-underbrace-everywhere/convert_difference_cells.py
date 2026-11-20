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

"""Rewrite each notebook "difference" check cell to ``show_difference(left, right)``.

A check cell is a code cell whose whole body is one expression of the form
``sympy.simplify(sympy.sympify(L - R))``, ``sympy.simplify(L - R)``,
``(L - R).simplified()``, ``(L - R).expanded()`` or a bare ``L - R``, and whose
preceding Markdown cell mentions a difference. It becomes
``show_difference(L, R)``, which shows the terms of the two sides cancelling under
numbered underbraces. ``L - R`` is the top-level subtraction, so ``a - b - c``
splits as ``(a - b)`` against ``c``. Cells listed in ``SKIP`` are left alone:
matrix checks (``show_difference`` takes numbers and multivectors) and cells
where "difference" names the vector ``a - b`` itself rather than a check. The
script adds ``show_difference`` to the notebook's
``gacalc.nbdisplay`` import, or adds that import after the notebook's last import.

Every cell that follows a "difference" Markdown cell but does not match is
written to ``data/unmatched.txt`` for hand review. Idempotent: a converted cell no
longer matches, so a second run changes nothing.

Usage: ``python tasks/adhoc/cancellation-underbrace-everywhere/convert_difference_cells.py``
"""

import ast
import pathlib
import re

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
DATA: pathlib.Path = pathlib.Path(__file__).resolve().parent / "data"
CELL_MARKER: re.Pattern[str] = re.compile(r"^# %%", re.MULTILINE)
#: ``(notebook, cell body)`` pairs never converted, each for the reason given.
SKIP: frozenset[tuple[str, str]] = frozenset(
    {
        # defines the difference vector, not a check that something cancels
        ("defining-g2.py", "a - b"),
        # matrices: show_difference takes numbers and multivectors
        ("proof-reciprocal-frame.py", "delta_table - sympy.eye(2)"),
        ("proof-reciprocal-frame.py", "space_delta_table - sympy.eye(3)"),
    }
)


def difference_operands(source: str) -> tuple[str, str] | None:
    """The ``(L, R)`` source texts of a check cell's ``L - R``, or ``None``.

    >>> difference_operands("sympy.simplify(sympy.sympify(a.x() - b))")
    ('a.x()', 'b')
    >>> difference_operands("(A * B - C).simplified()")
    ('A * B', 'C')
    >>> difference_operands("(a - b) - (a + (-b))")
    ('a - b', 'a + (-b)')
    >>> difference_operands("(p - q - r).expanded()")
    ('p - q', 'r')
    >>> difference_operands("a + b") is None
    True
    """
    try:
        tree: ast.Module = ast.parse(source)
    except SyntaxError:
        return None
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return None
    node: ast.expr = tree.body[0].value
    subtraction: ast.expr | None
    match node:
        case ast.Call(
            func=ast.Attribute(value=ast.Name(id="sympy"), attr="simplify"),
            args=[
                ast.Call(
                    func=ast.Attribute(value=ast.Name(id="sympy"), attr="sympify"),
                    args=[inner],
                )
            ],
        ):
            subtraction = inner
        case ast.Call(
            func=ast.Attribute(value=ast.Name(id="sympy"), attr="simplify"),
            args=[inner],
        ):
            subtraction = inner
        case ast.Call(
            func=ast.Attribute(value=inner, attr="simplified" | "expanded"), args=[]
        ):
            subtraction = inner
        case ast.BinOp(op=ast.Sub()):
            subtraction = node
        case _:
            subtraction = None
    match subtraction:
        case ast.BinOp(op=ast.Sub(), left=left, right=right):
            left_text: str | None = ast.get_source_segment(source, left)
            right_text: str | None = ast.get_source_segment(source, right)
            if left_text is None or right_text is None:
                return None
            return left_text, right_text
        case _:
            return None


def add_import(text: str) -> str:
    """``text`` with ``show_difference`` imported from ``gacalc.nbdisplay``."""
    if re.search(
        r"^from gacalc\.nbdisplay import .*\bshow_difference\b", text, re.MULTILINE
    ) or re.search(r"^\s+show_difference,$", text, re.MULTILINE):
        return text
    existing: re.Match[str] | None = re.search(
        r"^from gacalc\.nbdisplay import (?P<names>[^(\n]+)$", text, re.MULTILINE
    )
    if existing is not None:
        names: list[str] = [
            name.strip() for name in existing.group("names").split(",")
        ]
        line: str = "from gacalc.nbdisplay import " + ", ".join(
            sorted({*names, "show_difference"})
        )
        return text[: existing.start()] + line + text[existing.end() :]
    parenthesised: re.Match[str] | None = re.search(
        r"^from gacalc\.nbdisplay import \(\n", text, re.MULTILINE
    )
    if parenthesised is not None:
        return (
            text[: parenthesised.end()]
            + "    show_difference,\n"
            + text[parenthesised.end() :]
        )
    imports: list[re.Match[str]] = list(
        re.finditer(
            r"^(from [.\w]+ import (\([^)]*\)|[^\n]*)|import [.\w]+)$",
            text,
            re.MULTILINE,
        )
    )
    if not imports:
        raise ValueError("no import to add show_difference after")
    end: int = imports[-1].end()
    return text[:end] + "\nfrom gacalc.nbdisplay import show_difference" + text[end:]


def convert(path: pathlib.Path, unmatched: list[str]) -> int:
    """Rewrite ``path``'s check cells in place; return how many changed."""
    text: str = path.read_text()
    starts: list[int] = [match.start() for match in CELL_MARKER.finditer(text)]
    bounds: list[tuple[int, int]] = list(
        zip(starts, [*starts[1:], len(text)], strict=True)
    )
    pieces: list[str] = [text[: starts[0]]] if starts else [text]
    changed: int = 0
    previous_markdown: str = ""
    start: int
    end: int
    for start, end in bounds:
        cell: str = text[start:end]
        header: str
        body: str
        header, _, body = cell.partition("\n")
        if "[markdown]" in header:
            previous_markdown = body
            pieces.append(cell)
            continue
        follows_difference: bool = "difference" in previous_markdown.lower()
        previous_markdown = ""
        skipped: bool = (path.name, body.strip()) in SKIP
        operands: tuple[str, str] | None = (
            difference_operands(body.strip())
            if follows_difference and not skipped
            else None
        )
        if operands is None:
            if follows_difference and not skipped and "show_difference" not in body:
                unmatched.append(f"{path.relative_to(ROOT)}:\n{body.strip()}\n")
            pieces.append(cell)
            continue
        trailing: str = body[len(body.rstrip()) :]
        pieces.append(
            f"{header}\nshow_difference({operands[0]}, {operands[1]}){trailing}"
        )
        changed += 1
    if changed:
        path.write_text(add_import("".join(pieces)))
    return changed


def main() -> None:
    """Convert every notebook and report the counts."""
    unmatched: list[str] = []
    total: int = 0
    path: pathlib.Path
    for path in sorted((ROOT / "notebooks").glob("*.py")):
        count: int = convert(path, unmatched)
        if count:
            print(f"{path.relative_to(ROOT)}: {count}")
        total += count
    DATA.mkdir(exist_ok=True)
    (DATA / "unmatched.txt").write_text("\n".join(unmatched))
    print(f"converted {total} cells; {len(unmatched)} unmatched (data/unmatched.txt)")


if __name__ == "__main__":
    main()
