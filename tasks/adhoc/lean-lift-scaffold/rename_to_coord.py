#!/usr/bin/env python3
"""Rename scaffold Lean theorems to `<name>_coord` and repoint their call sites.

Part of tasks/lean-lift-theorem-statements-to-objects.md, Increment 21 (objectify the
internal scaffold/plumbing layer). For each named theorem this renames the definition
`theorem NAME (` -> `theorem NAME_coord (` and every CALL `NAME <arg>` -> `NAME_coord <arg>`,
on code lines only (docstring/comment lines are skipped so prose references are untouched).
Uses a whole-word `\bNAME\b` match, which hits the def and every call (incl. `rw [NAME]`
no-arg uses) but never `NAME_coord` (the `_` is a word char, so there is no word boundary
after NAME -> no double-append) and never a longer name that merely has NAME as a prefix
(e.g. `normSq_reverse_sandwich` does not match inside `normSq_reverse_sandwich_wedge`).
The bespoke object wrappers are added separately by hand.

Idempotent: re-running makes no further change (calls already read `_coord`).
Paths are relative to the repo root (resolved from this script's location)."""
from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PROOFS = REPO_ROOT / "proofs" / "GacalcProofs"

# file basename -> theorem names whose def and/or calls live in that file
TARGETS: dict[str, list[str]] = {
    "ProjectionRotation3D.lean": [
        "plane_pythagorean", "project_perp_reject", "inplane_perp_reject",
        "project_onto_in_plane_self", "reject_in_plane_self", "wedge_vec_wedge_self",
        "inner_vb_mul_reverse_self", "normSq_mul_vec",
        "normalizeVec_to_mul_versor_eq_bisector", "vec_mul_bisector_eq",
        "normalizeVec_mul_versor_eq_reverse", "versor_mul_project_eq",
        "versor_mul_reject_comm",
        "versorFromVectors_mul_inverse",  # calls only here (def in Sandwich)
    ],
    "ProjectionRotation2D.lean": [
        "mul_vec_self", "reject_plane_eq_zero", "magnitude_sq_of_normSq",
        "normSq_mul_three_vec", "versorFromVectors_mul_vec_eq",
        "reverse_versorFromVectors_mul", "key_reverse_sq",
        "fhat_that_eq_reverse_mul_inverse",
    ],
    "Sandwich.lean": [
        "versorFromVectors_mul_reverse", "versorFromVectors_mul_inverse",
        "mul_biv_reverse_self", "mul_biv_inverse_self", "normSq_reverse_sandwich",
        "normSq_reverse_sandwich_wedge", "wedge_reverse_sandwich",
    ],
    "Projection2D.lean": [
        "wedge_reverse_sandwich", "normSq_reverse_sandwich_wedge",
    ],
}


def is_comment(line: str) -> bool:
    s = line.lstrip()
    return s.startswith(("--", "/-", "-/", "*", "/--"))


def rename_in_file(path: pathlib.Path, names: list[str]) -> int:
    lines = path.read_text().splitlines(keepends=True)
    in_doc = False
    changed = 0
    out: list[str] = []
    for line in lines:
        # track multi-line /-- ... -/ docstrings; skip them for call-repoint
        doc_line = in_doc or is_comment(line)
        if "/-" in line and "-/" not in line.split("/-", 1)[1]:
            in_doc = True
        if "-/" in line:
            in_doc = False
        if doc_line:
            out.append(line)
            continue
        new = line
        for name in names:
            new = re.sub(rf"\b{re.escape(name)}\b", f"{name}_coord", new)
        if new != line:
            changed += 1
        out.append(new)
    path.write_text("".join(out))
    return changed


def main() -> None:
    # Safety guard — this codemod is SINGLE-USE. It renames `theorem NAME (` defs and
    # whole-word call sites to `_coord`. After the object wrappers (`theorem NAME {…}`) are
    # added, a second run would re-match those wrapper defs and append `_coord` again,
    # colliding with the leaves. So refuse once the wrapper blocks exist.
    if any("Object-form wrappers" in (PROOFS / base).read_text() for base in TARGETS):
        print("object wrappers already present — refusing to re-run (would corrupt them)")
        return
    total = 0
    for base, names in TARGETS.items():
        n = rename_in_file(PROOFS / base, names)
        print(f"{base}: {n} line(s) changed")
        total += n
    print(f"total: {total} line(s) changed")


if __name__ == "__main__":
    main()
