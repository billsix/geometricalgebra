#!/usr/bin/env python
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

"""Content-preserving reorder of a ``proofs/GacalcProofs/*.lean`` file.

A gacalc dev tool (sibling of ``gen_specialized.py``). A within-file reorder of Lean
declarations must change ONLY their order and the ``/-! ### … -/`` section headers — never a
proof body — or it is not content-preserving. This tool makes that guarantee mechanical instead
of trusting a hand-move:

  * split the file into a preamble (through the inner ``namespace <X>``), a body of declaration
    units, and a trailer (the closing ``end``s);
  * classify each body unit as a section header (``/-! … -/``) or a declaration (optional
    ``/-- … -/`` doc comment + the ``def``/``theorem``/… and its continuation lines), keyed by
    name — consecutive declarations with no blank line between them (G3's packed basis constants
    and multiplication table) are still split, because a new decl keyword ends the prior unit;
  * reassemble the declaration units in the order a ``PLAN`` gives, emitting fresh headers;
  * ASSERT the set of planned names equals the set of declaration names found (nothing dropped or
    invented) AND the multiset of declaration-unit *texts* is identical before vs. after — so the
    change is only order + headers.

Each file's target order is a ``PLAN`` in ``PLANS`` below, keyed by the inner namespace name. To
reorder a new file, add a ``PLAN``: every top-level declaration, grouped under section headers, in
a dependency-legal order (Lean resolves top-down, so a declaration must appear above every use);
the tool refuses if the PLAN's names do not exactly match the file's. Mark a group ``packed=True``
to keep one-liner members tight (a visual table — the basis constants, the multiplication table).

Idempotent: re-running on an already-ordered file is a no-op, so ``--check`` can gate drift.
Resolves paths from the repo root (``git rev-parse --show-toplevel``); no container-absolute path.

The G1/G2/G3 basis-first normalization (2026-10-28) was done with this; the resulting shape is
recorded in ``tasks/reference/lean-ga-proof-architecture.md`` → "Within-file order of the
algebra-core files".

Usage:  python tools/reorder_lean.py <G1|G3|…>        # apply the PLAN for that file
        python tools/reorder_lean.py <key> --check    # verify-only; nonzero if it would change
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+|private\s+|protected\s+)*"
    r"(?:def|theorem|lemma|abbrev|instance|structure)\s+"
    r"([A-Za-z_][A-Za-z0-9_.'À-ɏͰ-Ͽ]*)"
)


class Group(NamedTuple):
    """One section of a PLAN: a header line (or None) and its declarations, in order.

    ``packed`` keeps one-liner members tight (a blank line is inserted only before a member that
    carries its own doc comment) — for the basis-constant and multiplication-table visual tables.
    """

    header: str | None
    names: list[str]
    packed: bool = False


def repo_root() -> Path:
    out: str = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return Path(out)


def decl_name(block: str) -> str | None:
    """The declared name of a block, or None if the block is a section header / other."""
    for line in block.splitlines():
        if line.lstrip().startswith("/-!"):
            return None
        m = _DECL_RE.match(line)
        if m:
            return m.group(1)
    return None


def _has_decl(buf: list[str]) -> bool:
    return any(_DECL_RE.match(line) for line in buf)


def split_blocks(body_lines: list[str]) -> list[str]:
    """One block per declaration unit (optional ``/--`` doc comment + the decl + its continuation
    lines) or per ``/-!`` section header. Consecutive declarations with no blank line between them
    are still split, because a new decl keyword ends the prior unit."""
    blocks: list[str] = []
    i: int = 0
    n: int = len(body_lines)
    while i < n:
        line: str = body_lines[i]
        if line.strip() == "":
            i += 1
            continue
        stripped: str = line.lstrip()
        if stripped.startswith("/-!"):  # a section header, possibly multi-line
            buf: list[str] = []
            while i < n:
                buf.append(body_lines[i])
                done: bool = "-/" in body_lines[i]
                i += 1
                if done:
                    break
            blocks.append("\n".join(buf))
            continue
        buf = []
        if stripped.startswith("/--"):  # a leading doc comment, possibly multi-line
            while i < n:
                buf.append(body_lines[i])
                done = "-/" in body_lines[i]
                i += 1
                if done:
                    break
        while i < n:  # the declaration + its continuation lines
            cur: str = body_lines[i]
            if cur.strip() == "":
                break
            cur_stripped: str = cur.lstrip()
            if buf and (
                cur_stripped.startswith("/--") or cur_stripped.startswith("/-!")
            ):
                break
            if buf and _has_decl(buf) and _DECL_RE.match(cur):
                break
            buf.append(cur)
            i += 1
        blocks.append("\n".join(buf))
    return blocks


def reorder(text: str, inner: str, plan: list[Group]) -> str:
    lines: list[str] = text.split("\n")
    ns_idx: int = lines.index(f"namespace {inner}")
    end_idx: int = lines.index(f"end {inner}")
    preamble: list[str] = lines[: ns_idx + 1]
    body_lines: list[str] = lines[ns_idx + 1 : end_idx]
    trailer: list[str] = lines[end_idx:]

    blocks: list[str] = split_blocks(body_lines)
    by_name: dict[str, str] = {}
    for block in blocks:
        name: str | None = decl_name(block)
        if name is None:
            continue  # a section header; dropped and re-emitted fresh from the plan
        if name in by_name:
            raise SystemExit(f"duplicate declaration name in body: {name}")
        by_name[name] = block

    planned: list[str] = [n for group in plan for n in group.names]
    found: set[str] = set(by_name)
    missing: set[str] = found - set(planned)
    unknown: set[str] = set(planned) - found
    if missing or unknown:
        raise SystemExit(
            f"PLAN mismatch for {inner}:\n  not placed by plan: {sorted(missing)}\n"
            f"  named by plan but absent: {sorted(unknown)}"
        )
    if len(planned) != len(set(planned)):
        dupes: list[str] = sorted({n for n in planned if planned.count(n) > 1})
        raise SystemExit(f"PLAN lists a name twice: {dupes}")

    # Emit the body, joining declaration blocks with a blank line, EXCEPT a packed group (a visual
    # table) keeps its one-liner members tight, inserting a blank only before a doc-commented member.
    placed: list[str] = []  # for the content-preservation proof
    pieces: list[str] = []
    for group in plan:
        if group.header is not None:
            pieces.append(("\n\n" if pieces else "") + group.header)
        for k, name in enumerate(group.names):
            block: str = by_name[name]
            placed.append(block)
            first_of_group: bool = group.header is not None and k == 0
            if not pieces:
                sep: str = ""
            elif (
                group.packed
                and not first_of_group
                and not block.lstrip().startswith("/--")
            ):
                sep = "\n"
            else:
                sep = "\n\n"
            pieces.append(sep + block)

    # Content-preservation proof: same multiset of declaration-block texts.
    if sorted(by_name.values()) != sorted(placed):
        raise SystemExit("INTERNAL: declaration-block text changed — aborting")

    rebuilt: str = (
        "\n".join(preamble) + "\n\n" + "".join(pieces) + "\n\n" + "\n".join(trailer)
    )
    if not rebuilt.endswith("\n"):
        rebuilt += "\n"
    return rebuilt


# ----- Per-file PLANs (key = inner namespace name) ------------------------------------
# Order respects Lean top-down resolution (a decl appears above every use). Add a Group per
# section header; mark a visual-table group packed=True.

PLANS: dict[str, tuple[str, list[Group]]] = {
    # key: (target-file-basename, plan)
    "G1": (
        "G1.lean",
        [
            Group(
                "/-! ### Basis blades as elements, and the constants -/",
                ["zero", "one", "e_1", "vec", "I", "I_inv"],
                packed=True,
            ),
            Group(
                "/-! ### The elementary operations: geometric product, wedge, and the vector-space ops -/",
                ["mul", "wedge", "add", "smul", "reverse"],
            ),
            Group(
                "/-! ### Magnitude (squared is the primitive) -/",
                ["normSq", "magnitude"],
            ),
            Group(
                "/-! ### The scalar product (dot), the dual, and the inverse -/",
                ["dot", "dual", "inverse"],
            ),
            Group(
                "/-! ### The multiplication table and the pseudoscalar sign (I² = +1) -/",
                ["e_1_sq", "I_sq", "I_sq_eq_sign", "I_mul_I_inv", "reverse_reverse"],
                packed=True,
            ),
            Group(
                "/-! ### Commutativity and the algebra laws -/",
                ["mul_comm", "mul_assoc", "one_mul", "mul_add"],
            ),
            Group("/-! ### Grade-1 predicate -/", ["IsVector"]),
            Group(
                "/-! ### Vectors: products, wedge, dot, magnitude, dual, and the vector inverse -/",
                [
                    "vec_mul",
                    "wedge_vec",
                    "dot_vec",
                    "vec_mul_eq_dot_add_wedge",
                    "normSq_vec",
                    "magnitude_vec",
                    "dual_vec",
                    "mul_vec_inverse_self",
                ],
            ),
        ],
    ),
    "G3": (
        "G3.lean",
        [
            Group(
                "/-! ### Basis blades as genuine `G3` elements, and the grade constructors -/",
                [
                    "zero",
                    "one",
                    "e_1",
                    "e_2",
                    "e_3",
                    "e_12",
                    "e_13",
                    "e_23",
                    "e_123",
                    "vec",
                    "I",
                    "bivector",
                    "trivector",
                    "scalar",
                ],
                packed=True,
            ),
            Group(
                "/-! ### The elementary operations: geometric product, wedge, and the vector-space ops -/",
                ["mul", "wedge", "add", "sub", "neg", "smul", "reverse"],
            ),
            Group(
                "/-! ### Magnitude (squared is the primitive) -/",
                [
                    "normSq",
                    "magnitude",
                    "normSq_eq_sum_sq",
                    "normSq_nonneg",
                    "magnitude_sq_eq_normSq",
                    "magnitude_ne_zero_of_normSq_ne_zero",
                ],
            ),
            Group(
                "/-! ### The scalar product (dot), the inverse pseudoscalar, and the dual -/",
                ["dot", "I_inv", "I_mul_I_inv", "dual"],
            ),
            Group(
                "/-! ### The geometric-product multiplication table (confirms the transcription) -/",
                [
                    "e_1_sq",
                    "e_2_sq",
                    "e_3_sq",
                    "e_1_mul_e_2",
                    "e_1_mul_e_3",
                    "e_2_mul_e_3",
                    "e_2_mul_e_1",
                    "e_12_mul_e_3",
                    "I_sq",
                    "I_sq_eq_sign",
                    "reverse_reverse",
                ],
                packed=True,
            ),
            Group(
                "/-! ### Inner-product (dot) leaf lemmas — bilinearity and the coordinate form -/",
                [
                    "dot_comm",
                    "dot_add_left",
                    "dot_sub_left",
                    "dot_smul_left",
                    "dot_add_right",
                    "dot_sub_right",
                    "dot_smul_right",
                    "dot_vec",
                ],
            ),
            Group(
                "/-! ### Outer-product (wedge) leaf lemmas — bilinearity and the coordinate forms -/",
                [
                    "wedge_add_left",
                    "wedge_sub_left",
                    "wedge_smul_left",
                    "wedge_add_right",
                    "wedge_sub_right",
                    "wedge_smul_right",
                    "wedge_self_vec_coord",
                    "wedge_vec_eq_biv",
                ],
            ),
            Group(
                "/-! ### Coordinate-vector leaves: magnitude, self-product, and reverse -/",
                [
                    "normSq_vec",
                    "normSq_wedge_vec",
                    "mul_vec_self_coord",
                    "dot_self_vec_eq_normSq_coord",
                    "reverse_vec",
                ],
            ),
            Group(
                "/-! ### The fundamental split `a b = a·b + a∧b` (coordinate form) -/",
                ["vec_mul_eq_dot_add_wedge", "vec_mul_perp"],
            ),
            Group(
                "/-! ### Grade-structure predicates (vector / bivector / trivector) with their bridges -/",
                [
                    "IsVector",
                    "eq_vec_of_isVector",
                    "isVector_vec",
                    "IsVector.smul",
                    "IsVector.sub",
                    "IsBivector",
                    "eq_bivector_of_isBivector",
                    "isBivector_bivector",
                    "IsTrivector",
                    "eq_trivector_of_isTrivector",
                    "isTrivector_trivector",
                ],
            ),
            Group(
                "/-! ### Object-form facts: the split, antisymmetry, self-products, and dot/wedge as the two parts -/",
                [
                    "mul_eq_dot_add_wedge",
                    "mul_eq_wedge_of_perp",
                    "wedge_antisymm",
                    "wedge_self_vec",
                    "dot_self_vec_eq_normSq",
                    "mul_vec_self",
                    "dot_is_sym_part",
                    "wedge_is_antisym_part",
                ],
            ),
        ],
    ),
}


def main() -> None:
    args: list[str] = sys.argv[1:]
    check_only: bool = "--check" in args
    keys: list[str] = [a for a in args if not a.startswith("--")]
    if not keys:
        raise SystemExit("usage: reorder_lean.py <PLAN-key> [--check]")
    root: Path = repo_root()
    for key in keys:
        if key not in PLANS:
            raise SystemExit(f"no PLAN for {key!r}; known: {sorted(PLANS)}")
        basename, plan = PLANS[key]
        path: Path = root / "proofs" / "GacalcProofs" / basename
        original: str = path.read_text()
        rebuilt: str = reorder(original, key, plan)
        if rebuilt == original:
            print(f"{basename}: already in order (no change)")
            continue
        if check_only:
            raise SystemExit(f"{basename}: WOULD change (run without --check to apply)")
        path.write_text(rebuilt)
        print(f"{basename}: reordered ({len(plan)} sections)")


if __name__ == "__main__":
    main()
