#!/usr/bin/env python3
"""Apply the Hestenes-notation variable renames (scalars->Greek, terse multivectors->CAPITAL).

Token-position rename: only NAME tokens are rewritten, so string literals (e.g. a
`sympy.symbols("theta")` label, a `symbolic_multivector(prefix="c")` prefix) and comments are
left untouched -- the Python identifier changes, the math/label does not. Each rename is scoped:
`func` renames within the innermost enclosing function of the anchor line; `module` renames every
matching NAME token in the file (used for the shared-namespace jupytext notebooks, where every
target was verified unique). Idempotent: a second run finds no `old` tokens left, so makes no
change. Repo-root-relative; run from the repo root.
"""

from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

# (relpath, anchor_line, old, new, scope). scope: "func" | "module".
RENAMES: list[tuple[str, int, str, str, str]] = [
    # --- src: angles -> Greek ---
    ("src/gacalc/base.py", 2095, "theta", "θ", "func"),
    ("src/gacalc/transforms.py", 321, "theta", "θ", "func"),
    ("src/gacalc/nbplotutils.py", 249, "theta", "θ", "func"),
    # --- src: blade locals -> CAPITAL (docstring already writes A_{k-1}/A_k) ---
    ("src/gacalc/frame.py", 172, "a_prev", "A_prev", "func"),
    ("src/gacalc/frame.py", 175, "a_k", "A_k", "func"),
    # --- tests: angles -> Greek ---
    ("tests/test_bivector_rotation.py", 99, "theta", "θ", "func"),
    ("tests/test_exp.py", 97, "theta", "θ", "func"),
    ("tests/test_exp.py", 114, "theta", "θ", "func"),
    ("tests/test_plane_rotation.py", 131, "theta", "θ", "func"),
    ("tests/test_plane_rotation.py", 174, "theta", "θ", "func"),
    ("tests/test_versor_extraction.py", 34, "theta", "θ", "func"),
    ("tests/test_versor_extraction.py", 80, "phi", "φ", "func"),
    ("tests/test_versor_extraction.py", 100, "theta", "θ", "func"),
    ("tests/test_rotor_from_vectors.py", 171, "theta", "θ", "func"),
    ("tests/test_matrix_template.py", 135, "theta", "θ", "func"),
    ("tests/test_matrix_template.py", 176, "theta", "θ", "func"),
    ("tests/test_matrix_template.py", 232, "theta", "θ", "func"),
    # --- tests: versor/rotor/bivector/trivector locals -> CAPITAL ---
    ("tests/test_exp.py", 39, "r", "R", "func"),
    ("tests/test_exp.py", 51, "r", "R", "func"),
    ("tests/test_exp.py", 73, "t", "T", "func"),
    ("tests/test_exp.py", 78, "b", "B", "func"),
    ("tests/test_exp.py", 102, "r", "R", "func"),
    ("tests/test_exp.py", 119, "r", "R", "func"),
    ("tests/test_versor_extraction.py", 40, "r", "R", "func"),
    ("tests/test_versor_extraction.py", 51, "r", "R", "func"),
    ("tests/test_versor_extraction.py", 90, "r", "R", "func"),
    ("tests/test_versor_extraction.py", 103, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 56, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 75, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 92, "rhat", "Rhat", "func"),
    ("tests/test_rotor_from_vectors.py", 110, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 110, "rhat", "Rhat", "func"),
    ("tests/test_rotor_from_vectors.py", 125, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 154, "r", "R", "func"),
    ("tests/test_rotor_from_vectors.py", 162, "rhat", "Rhat", "func"),
    ("tests/test_rotor_from_vectors.py", 174, "rhat", "Rhat", "func"),
    ("tests/test_odd3.py", 48, "r", "R", "func"),
    ("tests/test_odd3.py", 63, "r", "R", "func"),
    ("tests/test_odd3.py", 66, "t", "T", "func"),
    ("tests/test_odd3.py", 74, "r", "R", "func"),
    ("tests/test_operator_typing.py", 115, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 130, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 131, "r2", "R2", "func"),
    ("tests/test_operator_typing.py", 195, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 204, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 215, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 231, "i2", "I2", "func"),
    ("tests/test_operator_typing.py", 251, "i3", "I3", "func"),
    ("tests/test_operator_typing.py", 253, "t3", "T3", "func"),
    ("tests/test_operator_typing.py", 255, "r3", "R3", "func"),
    ("tests/test_operator_typing.py", 261, "i2", "I2", "func"),
    ("tests/test_graded.py", 192, "b3", "B3", "func"),
    ("tests/test_graded.py", 217, "r", "R", "func"),
    ("tests/test_graded.py", 252, "r", "R", "func"),
    ("tests/test_graded.py", 266, "r2", "R2", "func"),
    ("tests/test_graded.py", 271, "r3", "R3", "func"),
    ("tests/test_graded.py", 283, "r2", "R2", "func"),
    ("tests/test_graded.py", 286, "r3", "R3", "func"),
    ("tests/test_graded.py", 404, "r", "R", "func"),
    ("tests/test_graded.py", 416, "r", "R", "func"),
    ("tests/test_graded.py", 426, "r2", "R2", "func"),
    ("tests/test_graded.py", 435, "r3", "R3", "func"),
    ("tests/test_graded.py", 455, "r", "R", "func"),
    ("tests/test_transforms.py", 439, "r", "R", "func"),
    ("tests/test_transforms.py", 452, "r", "R", "func"),
    ("tests/test_transforms.py", 461, "r", "R", "func"),
    ("tests/test_conformance.py", 262, "b", "B", "func"),
    ("tests/test_unit_bivector_i.py", 81, "b", "B", "func"),
    ("tests/test_unit_bivector_i.py", 87, "r", "R", "func"),
    ("tests/test_multivector.py", 214, "i3", "I3", "func"),
    # test_multivector_unit_pseudoscalar: i1..i15 -> I1..I15 (all one function, anchor 374)
    *[("tests/test_multivector.py", 374, f"i{k}", f"I{k}", "func") for k in range(1, 16)],
    # --- notebooks (module scope; every target verified unique) ---
    ("notebooks/displaymv.py", 0, "biv", "B", "module"),
    ("notebooks/displaymv.py", 0, "g2_1", "G2_1", "module"),
    ("notebooks/displaymv.py", 0, "g2_2", "G2_2", "module"),
    ("notebooks/displaymv.py", 0, "g2_3", "G2_3", "module"),
    ("notebooks/displayg2.py", 0, "a_full", "A_full", "module"),
    ("notebooks/displayg2.py", 0, "g2_1", "G2_1", "module"),
    ("notebooks/displayg2.py", 0, "g2_2", "G2_2", "module"),
    ("notebooks/displayg2.py", 0, "g2_3", "G2_3", "module"),
    ("notebooks/displayg2.py", 0, "c", "C", "module"),
    ("notebooks/displayg3.py", 0, "a_full", "A_full", "module"),
    ("notebooks/displayg3.py", 0, "g3_1", "G3_1", "module"),
    ("notebooks/displayg3.py", 0, "g3_2", "G3_2", "module"),
    ("notebooks/displayg3.py", 0, "g3_3", "G3_3", "module"),
    ("notebooks/displayg3.py", 0, "c", "C", "module"),
    ("notebooks/displayg3.py", 0, "biv", "B", "module"),
    ("notebooks/displaygraded.py", 0, "i2", "I2", "module"),
    ("notebooks/displaygraded.py", 0, "r", "R0", "module"),
    ("notebooks/displaygraded.py", 0, "biv", "B", "module"),
    ("notebooks/displayrotations.py", 0, "theta", "θ", "module"),
    ("notebooks/displayrotations.py", 0, "phi", "φ", "module"),
]

# Exact-line raw substring fixes (coupled strings that the NAME pass cannot reach):
# the @parametrize decorator's param-name string must match its renamed function param.
STRING_FIXES: list[tuple[str, int, str, str]] = [
    ("tests/test_versor_extraction.py", 32, '"theta"', '"θ"'),
]

ROOT = Path(__file__).resolve()
while not (ROOT / ".git").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent


def enclosing_span(tree: ast.AST, anchor: int) -> tuple[int, int]:
    best: tuple[int, int] | None = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end = node.lineno, (node.end_lineno or node.lineno)
            if start <= anchor <= end and (best is None or (end - start) < (best[1] - best[0])):
                best = (start, end)
    if best is None:
        raise SystemExit(f"no enclosing function for anchor line {anchor}")
    return best


def apply_file(relpath: str, renames: list[tuple[int, str, str, str]]) -> int:
    path = ROOT / relpath
    src = path.read_text()
    tree = ast.parse(src)
    # Resolve each rename to a (lo, hi, old, new) line-span rule.
    rules: list[tuple[int, int, str, str]] = []
    for anchor, old, new, scope in renames:
        if scope == "module":
            rules.append((1, 10**9, old, new))
        else:
            lo, hi = enclosing_span(tree, anchor)
            rules.append((lo, hi, old, new))
    # Collect NAME-token replacements by position.
    edits: list[tuple[int, int, int, str]] = []  # (row, col_start, col_end, new)
    toks = tokenize.generate_tokens(io.StringIO(src).readline)
    for tok in toks:
        if tok.type != tokenize.NAME:
            continue
        row = tok.start[0]
        for lo, hi, old, new in rules:
            if tok.string == old and lo <= row <= hi:
                edits.append((row, tok.start[1], tok.end[1], new))
                break
    lines = src.splitlines(keepends=True)
    # Apply per line, rightmost column first, to keep offsets valid.
    by_row: dict[int, list[tuple[int, int, str]]] = {}
    for row, c0, c1, new in edits:
        by_row.setdefault(row, []).append((c0, c1, new))
    for row, repls in by_row.items():
        line = lines[row - 1]
        for c0, c1, new in sorted(repls, reverse=True):
            line = line[:c0] + new + line[c1:]
        lines[row - 1] = line
    path.write_text("".join(lines))
    return len(edits)


def main() -> None:
    per_file: dict[str, list[tuple[int, str, str, str]]] = {}
    for relpath, anchor, old, new, scope in RENAMES:
        per_file.setdefault(relpath, []).append((anchor, old, new, scope))
    total = 0
    for relpath, renames in per_file.items():
        n = apply_file(relpath, renames)
        total += n
        print(f"{relpath}: {n} token(s) renamed")
    for relpath, line, old_s, new_s in STRING_FIXES:
        path = ROOT / relpath
        lines = path.read_text().splitlines(keepends=True)
        before = lines[line - 1]
        after = before.replace(old_s, new_s)
        if after != before:
            lines[line - 1] = after
            path.write_text("".join(lines))
            print(f"{relpath}:{line}: string fix {old_s} -> {new_s}")
        else:
            print(f"{relpath}:{line}: string fix already applied (no change)")
    print(f"TOTAL NAME tokens renamed: {total}")


if __name__ == "__main__":
    main()
