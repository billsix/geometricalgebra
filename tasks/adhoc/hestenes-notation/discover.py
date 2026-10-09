#!/usr/bin/env python3
"""Discover function-local variable bindings that are candidates for the Hestenes
notation sweep (scalars -> Greek, vectors -> lowercase, multivectors -> CAPITAL).

Run from the repo root. Reads every in-scope .py file (src/tools/tests/notebooks,
excluding the generated g1/g2/g3), walks each function body with `ast`, and reports
each name BOUND as a local (assignment / for-target / walrus / comprehension target),
with the file and line, grouped by a rough name-class heuristic. Grade-class is a
judgment call the heuristic cannot make -- this just enumerates the candidate set so a
human reads every hit. Paths are repo-root-relative (run via `git rev-parse` cwd).
"""

from __future__ import annotations

import ast
import collections
import subprocess
import sys
from pathlib import Path

ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
)

# Names fixed from outside the code -- never renamed (CLAUDE.md "externally-defined name").
EXEMPT = {
    "cls",
    "self",
    "n",
    "m",
    "b",
    "i",
    "j",
    "k",
    "_",
}

GREEK_SPELLED = {
    "alpha",
    "beta",
    "gamma",
    "delta",
    "theta",
    "phi",
    "psi",
    "lambda_",
    "lambda",
    "omega",
    "sigma",
    "tau",
    "rho",
    "mu",
    "nu",
    "kappa",
}


def in_scope(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith(("g1.py", "g2.py", "g3.py", "g4.py", "g5.py")):
        return False
    return rel.startswith(("src/", "tools/", "tests/", "notebooks/"))


def local_binds(tree: ast.AST) -> collections.abc.Iterator[tuple[str, int]]:
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, (ast.Assign,)):
            targets = list(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        elif isinstance(node, (ast.For, ast.comprehension)):
            targets = [node.target]
        elif isinstance(node, ast.NamedExpr):
            targets = [node.target]
        for t in targets:
            for sub in ast.walk(t):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                    yield sub.id, getattr(sub, "lineno", 0)


def main() -> None:
    files = sorted(p for p in ROOT.rglob("*.py") if in_scope(p))
    by_name: dict[str, list[str]] = collections.defaultdict(list)
    for path in files:
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError as exc:
            print(f"SKIP (syntax) {path}: {exc}", file=sys.stderr)
            continue
        rel = path.relative_to(ROOT).as_posix()
        for name, lineno in local_binds(tree):
            if name in EXEMPT or name.startswith("__"):
                continue
            by_name[name].append(f"{rel}:{lineno}")

    spelled_greek: list[str] = []
    short_lower: list[str] = []
    for name in sorted(by_name):
        sites = by_name[name]
        line = f"{name}  ({len(sites)})  -> {', '.join(sites[:8])}"
        if name.lower() in GREEK_SPELLED:
            spelled_greek.append(line)
        elif len(name) <= 2 and name.islower():
            short_lower.append(line)

    print("# Spelled-out Greek-name locals (prime Greek-identifier candidates)")
    print("\n".join(spelled_greek) or "(none)")
    print("\n# Short (<=2 char) lowercase locals (classify: scalar->Greek / vector->lower / mv->CAP)")
    print("\n".join(short_lower) or "(none)")
    print(f"\n# total distinct local names: {len(by_name)} across {len(files)} files")


if __name__ == "__main__":
    main()
