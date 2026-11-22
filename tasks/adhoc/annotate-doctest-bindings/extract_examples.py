#!/usr/bin/env python3
"""Write the ``>>>`` examples of every docstring to one scratch module, so ``ty`` can check them.

``ty`` does not read inside a docstring, so a wrong type in a doctest annotation is caught by
nothing else. Each docstring's examples become the body of one function (so its names do not
leak into the next), with the expected-output lines dropped.

Usage: ``python tasks/adhoc/annotate-doctest-bindings/extract_examples.py OUT_DIR`` then
``ty check OUT_DIR`` with ``gacalc`` importable.
"""

from __future__ import annotations

import ast
import doctest
import pathlib
import sys

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
FILES: tuple[str, ...] = (
    "src/gacalc/base.py",
    "src/gacalc/transforms.py",
    "src/gacalc/functions.py",
    "src/gacalc/measure.py",
    "src/gacalc/frame.py",
    "src/gacalc/nbdisplay.py",
    "src/gacalc/standardposition.py",
    "src/gacalc/vectorcalc.py",
    "src/gacalc/gn.py",
    "src/gacalc/cayley/cayleygraph.py",
    "src/gacalc/cayley/cayleyscene.py",
    "src/gacalc/g1.py",
    "src/gacalc/g2.py",
    "src/gacalc/g3.py",
)


def examples_of(path: pathlib.Path) -> list[tuple[int, str]]:
    """Each docstring's examples in ``path``, as (docstring line, source) pairs.

    Args:
        path: A Python file.

    Returns:
        list[tuple[int, str]]: the examples' source, joined, per docstring that has any.
    """
    parser: doctest.DocTestParser = doctest.DocTestParser()
    found: list[tuple[int, str]] = []
    node: ast.AST
    for node in ast.walk(ast.parse(path.read_text())):
        if not isinstance(
            node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        ):
            continue
        head: ast.stmt | None = node.body[0] if node.body else None
        if not (
            isinstance(head, ast.Expr)
            and isinstance(head.value, ast.Constant)
            and isinstance(head.value.value, str)
        ):
            continue
        sources: list[str] = [e.source for e in parser.get_examples(head.value.value)]
        if sources:
            found.append((head.lineno, "".join(sources)))
    return found


def main() -> None:
    """Write one scratch module per source file into the directory named on the command line."""
    out: pathlib.Path = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    name: str
    for name in FILES:
        path: pathlib.Path = REPO / name
        lines: list[str] = ["# ruff: noqa", "from __future__ import annotations", ""]
        line: int
        source: str
        for line, source in examples_of(path):
            lines.append(f"def example_line_{line}() -> None:")
            body: list[str] = [ln for ln in source.splitlines() if ln.strip()]
            lines.extend(f"    {ln}" for ln in body or ["pass"])
            lines.append("")
        (out / (name.replace("/", "_").removesuffix(".py") + ".py")).write_text(
            "\n".join(lines)
        )
        print(f"{name}: written")


if __name__ == "__main__":
    main()
