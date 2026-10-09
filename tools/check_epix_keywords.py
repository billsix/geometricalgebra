#!/usr/bin/env python3
"""Every argument in the book's ePiX figure files is passed by keyword -- check or fix.

The figures under ``book/figures/epix/`` read like a scene description, so a call
such as ``epix.label(at=head, offset=Point(x=7, y=0), text="$x$", align=...)`` says
what each value is; ``polar(1, BETA)`` does not. This tool walks each figure file's
AST and reports every positional argument to a call whose parameter names it knows
(the ``epix`` binding's ``nb::arg`` names and the figure helpers' own parameters);
with ``--fix`` it inserts the ``name=`` in front of each one (text edits from the
end of the file backwards, so positions stay valid), leaving comments and layout
alone -- run ``ruff format`` afterwards.

Exempt: calls whose parameters are positional-only (``math.*`` and the other C
builtins) and calls this table does not know (reported as "unknown", never
rewritten -- extend the table instead of guessing).

Usage: ``python tools/check_epix_keywords.py [--fix] [PATH ...]``
(default: every ``*.py`` under book/figures/epix). Exit 1 if any positional
argument remains.
"""

from __future__ import annotations

import argparse
import ast
from collections.abc import Sequence
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[1]
FIGURES: Path = REPO / "book" / "figures" / "epix"

# (module, function) -> parameter names in positional order; a dict keyed by arity
# where the binding has overloads with different parameter lists.
Names = list[str] | dict[int, list[str]]
KNOWN: dict[tuple[str, str], Names] = {
    # the epix binding (python/epix/_epix.cc nb::arg names) + the Python front-end
    ("epix", "label"): {2: ["at", "text"], 4: ["at", "offset", "text", "align"]},
    ("epix", "masklabel"): {2: ["at", "text"], 4: ["at", "offset", "text", "align"]},
    ("epix", "pen"): {1: ["color"], 2: ["color", "width"]},
    ("epix", "fill"): ["color"],
    ("epix", "font_size"): ["size"],
    ("epix", "label_angle"): ["t"],
    ("epix", "label_color"): ["color"],
    ("epix", "dot"): {1: ["at"], 4: ["at", "offset", "text", "align"]},
    ("epix", "ddot"): {1: ["at"], 4: ["at", "offset", "text", "align"]},
    ("epix", "circle"): ["center", "radius", "normal"],
    ("epix", "arrow"): ["tail", "head", "scale"],
    ("epix", "line"): ["tail", "head", "expand"],
    ("epix", "arc"): ["center", "radius", "start", "finish"],
    ("epix", "rect"): ["lower_left", "upper_right"],
    ("epix", "triangle"): ["a", "b", "c"],
    ("epix", "rgb"): ["r", "g", "b"],
    ("epix", "figure"): ["lower_left", "upper_right", "size", "dpi"],
    ("epix", "line_style"): ["style"],
    ("epix", "Path"): ["data", "closed", "filled"],
    ("epix", "Point"): ["x", "y", "z"],
    ("", "Point"): ["x", "y", "z"],
    # the figure helpers (book/figures/epix/_scene2d.py)
    ("", "polar"): ["radius", "angle"],
    ("", "vector"): ["head", "text", "offset", "align"],
    ("", "dashed_vector"): ["tail", "head", "text", "offset", "align"],
    ("", "parallelogram"): ["corner_a", "corner_b", "color"],
    ("", "wedge"): ["start", "finish", "text", "radius"],
    ("", "right_angle_marker"): ["angle", "size"],
    ("", "right_angle_at"): ["corner", "angle", "size"],
    ("", "leg"): ["tail", "head", "color", "text", "angle", "offset"],
    ("", "unit_circle_scene"): ["lower_left", "upper_right", "disc"],
}
tint: str
for tint in ("black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"):
    KNOWN[("epix", tint)] = ["intensity"]
# positional-only callees: nothing to do, nothing to report
EXEMPT_MODULES: frozenset[str] = frozenset({"math"})
EXEMPT_BUILTINS: frozenset[str] = frozenset(
    {"range", "len", "int", "float", "str", "print", "open", "list", "set", "sorted"}
    # exception constructors take a positional message by convention
    | {"ValueError", "TypeError", "KeyError", "RuntimeError", "NotImplementedError"}
)


def callee(node: ast.Call) -> tuple[str, str] | None:
    """(module, name) for ``name(...)`` / ``module.name(...)``; None otherwise."""
    func: ast.expr = node.func
    if isinstance(func, ast.Name):
        return ("", func.id)
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return (func.value.id, func.attr)
    return None


def names_for(key: tuple[str, str], arity: int) -> list[str] | None:
    """The parameter list for ``key`` at this arity, if the table knows it."""
    entry: Names | None = KNOWN.get(key)
    if entry is None:
        return None
    if isinstance(entry, dict):
        return entry.get(arity)
    return entry


def scan(path: Path) -> tuple[list[tuple[int, int, str]], list[str]]:
    """Positional args to rewrite as (lineno, col, name) + unknown-callee reports."""
    tree: ast.Module = ast.parse(path.read_text())
    edits: list[tuple[int, int, str]] = []
    unknown: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        key: tuple[str, str] | None = callee(node)
        if key is None:
            # method calls (fig.save(...), Path(...).draw()): none take args here
            continue
        module, name = key
        if module in EXEMPT_MODULES or (module == "" and name in EXEMPT_BUILTINS):
            continue
        params: list[str] | None = names_for(key, len(node.args) + len(node.keywords))
        if params is None:
            params = names_for(key, len(node.args))
        if params is None:
            unknown.append(
                f"{path.name}:{node.lineno}: {module + '.' if module else ''}{name}(…)"
            )
            continue
        arg: ast.expr
        param: str
        for arg, param in zip(node.args, params, strict=False):
            if isinstance(arg, ast.Starred):
                continue
            edits.append((arg.lineno, arg.col_offset, param))
    return edits, unknown


def apply(path: Path, edits: Sequence[tuple[int, int, str]]) -> None:
    """Insert ``name=`` before each positional argument, last position first."""
    lines: list[str] = path.read_text().split("\n")
    lineno: int
    col: int
    name: str
    for lineno, col, name in sorted(edits, reverse=True):
        line: str = lines[lineno - 1]
        lines[lineno - 1] = line[:col] + f"{name}=" + line[col:]
    path.write_text("\n".join(lines))


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix", action="store_true", help="insert the keywords in place"
    )
    parser.add_argument(
        "paths", nargs="*", type=Path, help="files (default: the figures)"
    )
    args: argparse.Namespace = parser.parse_args()
    paths: list[Path] = args.paths or sorted(FIGURES.glob("*.py"))

    status: int = 0
    for path in paths:
        edits, unknown = scan(path)
        report: str
        for report in unknown:
            print(f"unknown callee (not rewritten): {report}")
            status = 1
        if not edits:
            continue
        if args.fix:
            apply(path, edits)
            print(f"{path.relative_to(REPO)}: {len(edits)} keyword(s) inserted")
        else:
            status = 1
            lineno: int
            col: int
            name: str
            for lineno, col, name in sorted(edits):
                print(
                    f"{path.relative_to(REPO)}:{lineno}:{col + 1}: "
                    f"positional argument; use {name}="
                )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
