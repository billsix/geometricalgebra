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

"""Run a percent-format notebook cell by cell and print each code cell's last value.

Usage, from the notebook's directory so its relative imports resolve:
``python <repo>/tools/run_notebook_cells.py <notebook.py>``. Prints ``[cell N] <repr>``
for each code cell that ends in an expression, so a notebook's check cells (each
should show ``0``) can be read without a Jupyter or book build. Exits 1 if a cell
raises. A report, not a gate: nothing in the build runs it.
"""

import ast
import pathlib
import sys
import traceback


def code_cells(source: str) -> list[str]:
    r"""The code cells of a percent-format notebook, in order, Markdown cells dropped.

    >>> code_cells("# %% [markdown]\n# Prose\n\n# %%\nx = 1\n\n# %%\nx + 1\n")
    ['x = 1\n\n', 'x + 1\n']
    """
    cells: list[str] = []
    current: list[str] | None = None
    line: str
    for line in source.splitlines(keepends=True):
        if line.startswith("# %%"):
            if current is not None:
                cells.append("".join(current))
            current = None if "[markdown]" in line else []
        elif current is not None:
            current.append(line)
    if current is not None:
        cells.append("".join(current))
    return cells


def main() -> int:
    """Execute each cell in one namespace; print the value of a trailing expression."""
    path: pathlib.Path = pathlib.Path(sys.argv[1])
    namespace: dict[str, object] = {"__name__": "__main__"}
    index: int
    cell: str
    for index, cell in enumerate(code_cells(path.read_text()), start=1):
        tree: ast.Module = ast.parse(cell)
        last: ast.stmt | None = tree.body[-1] if tree.body else None
        try:
            if isinstance(last, ast.Expr):
                exec(
                    compile(ast.Module(tree.body[:-1], []), str(path), "exec"),
                    namespace,
                )
                value: object = eval(
                    compile(ast.Expression(last.value), str(path), "eval"), namespace
                )
                print(f"[cell {index}] {value!r}"[:300])  # noqa: T201
            else:
                exec(compile(tree, str(path), "exec"), namespace)
        except Exception:
            print(f"[cell {index}] RAISED")  # noqa: T201
            traceback.print_exc()
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
