# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
"""Run a percent-format notebook cell by cell and print each code cell's last value.

Usage (from the notebook's directory, so its relative imports resolve):
``python run_cells.py <notebook.py>``. Prints ``[cell N] <repr>`` for each code cell
that ends in an expression, so a revised notebook's check cells can be read (each
should print ``0``) without a Jupyter build. Exits 1 if a cell raises.
"""

import ast
import pathlib
import sys
import traceback


def code_cells(source: str) -> list[str]:
    """The code cells of a percent-format notebook, in order (Markdown cells dropped)."""
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
                exec(compile(ast.Module(tree.body[:-1], []), str(path), "exec"), namespace)  # noqa: S102
                value: object = eval(  # noqa: S307
                    compile(ast.Expression(last.value), str(path), "eval"), namespace
                )
                print(f"[cell {index}] {value!r}"[:300])  # noqa: T201
            else:
                exec(compile(tree, str(path), "exec"), namespace)  # noqa: S102
        except Exception:  # noqa: BLE001
            print(f"[cell {index}] RAISED")  # noqa: T201
            traceback.print_exc()
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
