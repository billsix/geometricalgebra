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

"""List each public function/method of the hand-written modules with its doctest status.

Prints ``module:line qualname examples=<count of >>> lines> first=<first example>``,
one per public callable, for the docstring-simple-before-complex-examples task.
"""

import ast
import pathlib

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
MODULES: list[str] = [
    "base.py", "transforms.py", "frame.py", "measure.py", "vectorcalc.py",
    "standardposition.py", "functions.py", "gn.py",
]


def main() -> None:
    name: str
    for name in MODULES:
        tree: ast.Module = ast.parse((ROOT / "src/gacalc" / name).read_text())

        def visit(node: ast.AST, prefix: str) -> None:
            child: ast.AST
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.ClassDef) and not child.name.startswith("_"):
                    visit(child, prefix + child.name + ".")
                elif isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                    public: bool = not child.name.startswith("_") or child.name in (
                        "__mul__", "__xor__", "__lt__", "__gt__", "__truediv__",
                    )
                    if not public:
                        continue
                    doc: str = ast.get_docstring(child) or ""
                    examples: list[str] = [
                        line.strip()[4:] for line in doc.splitlines()
                        if line.strip().startswith(">>> ")
                        and "import" not in line
                    ]
                    first: str = examples[0][:70] if examples else "-"
                    print(f"{name}:{child.lineno} {prefix}{child.name} "
                          f"examples={len(examples)} first={first}")

        visit(tree, "")


if __name__ == "__main__":
    main()
