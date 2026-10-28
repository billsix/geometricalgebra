#!/usr/bin/env python3
"""Content-preserving reorder of a GacalcProofs ``.lean`` file.

Part of ``tasks/study-and-reorder-lean-file-structure.md`` (Axis 2 — the within-file
ordering sweep). The point is that a reorder must change ONLY the order of declarations
and the ``/-! ### ... -/`` section headers, never a single proof body. This tool makes
that guarantee mechanical instead of trusting a hand-move:

  * split the file into a preamble (through the inner ``namespace <X>``), a body of
    blank-line-separated blocks, and a trailer (the closing ``end``s);
  * classify each body block as a section header (``/-! ... -/``) or a declaration
    (optional ``/-- ... -/`` doc comment + the ``def``/``theorem``/... ), keyed by name;
  * reassemble the declaration blocks in the order given by a PLAN (a list of
    ``(section-header-or-None, [names...])`` groups), emitting fresh headers;
  * ASSERT the set of planned names equals the set of declaration names found (nothing
    dropped or invented) AND the multiset of declaration-block *texts* is identical
    before vs. after (so only order + headers changed).

Idempotent: running it again on an already-ordered file yields byte-identical output
(the PLAN is a total order), so it is safe to re-run. Paths are resolved relative to the
repo root (``git rev-parse --show-toplevel``); nothing is hard-coded to a container path.

Usage:  python reorder_lean.py <G3|G2|G1|...>   # the PLAN key (= inner namespace name)
        python reorder_lean.py <key> --check    # verify-only; nonzero exit if it would change
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+|private\s+|protected\s+)*"
    r"(?:def|theorem|lemma|abbrev|instance|structure)\s+"
    r"([A-Za-z_][A-Za-z0-9_.'À-ɏͰ-Ͽ]*)"
)


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
    """One block per declaration unit (optional ``/--`` doc comment + the decl + its
    continuation lines) or per ``/-!`` section header. Blank lines separate; consecutive
    declarations with NO blank line between them (G3's packed basis constants and
    multiplication table) are still split, because a new decl keyword ends the prior unit."""
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
            if buf and (cur_stripped.startswith("/--") or cur_stripped.startswith("/-!")):
                break
            if buf and _has_decl(buf) and _DECL_RE.match(cur):
                break
            buf.append(cur)
            i += 1
        blocks.append("\n".join(buf))
    return blocks


def reorder(text: str, inner: str, plan: list[tuple[str | None, list[str]]]) -> str:
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

    planned: list[str] = [n for group in plan for n in group[1]]
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

    # Emit the body, joining declaration blocks with a blank line, EXCEPT a group tagged
    # "packed" (a visual table — basis constants, the multiplication table) keeps its
    # one-liner members tight, inserting a blank only before a member that has a doc comment.
    placed: list[str] = []  # for the content-preservation proof
    pieces: list[str] = []  # (text, separator-before) flattened into a string below
    for group in plan:
        header: str | None = group[0]
        names: list[str] = group[1]
        packed: bool = len(group) > 2 and group[2] == "packed"
        if header is not None:
            pieces.append(("\n\n" if pieces else "") + header)
        for k, name in enumerate(names):
            block: str = by_name[name]
            placed.append(block)
            first_of_group: bool = header is not None and k == 0
            if not pieces:
                sep = ""
            elif packed and not first_of_group and not block.lstrip().startswith("/--"):
                sep = "\n"
            else:
                sep = "\n\n"
            pieces.append(sep + block)

    # Content-preservation proof: same multiset of declaration-block texts.
    if sorted(by_name.values()) != sorted(placed):
        raise SystemExit("INTERNAL: declaration-block text changed — aborting")

    rebuilt: str = (
        "\n".join(preamble)
        + "\n\n"
        + "".join(pieces)
        + "\n\n"
        + "\n".join(trailer)
    )
    if not rebuilt.endswith("\n"):
        rebuilt += "\n"
    return rebuilt


# ----- Per-file PLANs (key = inner namespace name). -----------------------------------
# Each entry: (section-header line or None, [declaration names in order]).
# Order respects Lean top-down resolution (a decl appears above every use).

PLANS: dict[str, tuple[str, list[tuple[str | None, list[str]]]]] = {
    # (target-file-basename, plan)
    "G1": (
        "G1.lean",
        [
            (
                "/-! ### Basis blades as elements, and the constants -/",
                ["zero", "one", "e_1", "vec", "I", "I_inv"],
                "packed",
            ),
            (
                "/-! ### The elementary operations: geometric product, wedge, and the vector-space ops -/",
                ["mul", "wedge", "add", "smul", "reverse"],
            ),
            (
                "/-! ### Magnitude (squared is the primitive) -/",
                ["normSq", "magnitude"],
            ),
            (
                "/-! ### The scalar product (dot), the dual, and the inverse -/",
                ["dot", "dual", "inverse"],
            ),
            (
                "/-! ### The multiplication table and the pseudoscalar sign (I² = +1) -/",
                ["e_1_sq", "I_sq", "I_sq_eq_sign", "I_mul_I_inv", "reverse_reverse"],
                "packed",
            ),
            (
                "/-! ### Commutativity and the algebra laws -/",
                ["mul_comm", "mul_assoc", "one_mul", "mul_add"],
            ),
            (
                "/-! ### Grade-1 predicate -/",
                ["IsVector"],
            ),
            (
                "/-! ### Vectors: products, wedge, dot, magnitude, dual, and the vector inverse -/",
                [
                    "vec_mul", "wedge_vec", "dot_vec", "vec_mul_eq_dot_add_wedge",
                    "normSq_vec", "magnitude_vec", "dual_vec", "mul_vec_inverse_self",
                ],
            ),
        ],
    ),
    "G3": (
        "G3.lean",
        [
            (
                "/-! ### Basis blades as genuine `G3` elements, and the grade constructors -/",
                [
                    "zero", "one", "e_1", "e_2", "e_3", "e_12", "e_13", "e_23",
                    "e_123", "vec", "I", "bivector", "trivector", "scalar",
                ],
                "packed",
            ),
            (
                "/-! ### The elementary operations: geometric product, wedge, and the vector-space ops -/",
                ["mul", "wedge", "add", "sub", "neg", "smul", "reverse"],
            ),
            (
                "/-! ### Magnitude (squared is the primitive) -/",
                [
                    "normSq", "magnitude", "normSq_eq_sum_sq", "normSq_nonneg",
                    "magnitude_sq_eq_normSq", "magnitude_ne_zero_of_normSq_ne_zero",
                ],
            ),
            (
                "/-! ### The scalar product (dot), the inverse pseudoscalar, and the dual -/",
                ["dot", "I_inv", "I_mul_I_inv", "dual"],
            ),
            (
                "/-! ### The geometric-product multiplication table (confirms the transcription) -/",
                [
                    "e_1_sq", "e_2_sq", "e_3_sq", "e_1_mul_e_2", "e_1_mul_e_3",
                    "e_2_mul_e_3", "e_2_mul_e_1", "e_12_mul_e_3", "I_sq",
                    "I_sq_eq_sign", "reverse_reverse",
                ],
                "packed",
            ),
            (
                "/-! ### Inner-product (dot) leaf lemmas — bilinearity and the coordinate form -/",
                [
                    "dot_comm", "dot_add_left", "dot_sub_left", "dot_smul_left",
                    "dot_add_right", "dot_sub_right", "dot_smul_right", "dot_vec",
                ],
            ),
            (
                "/-! ### Outer-product (wedge) leaf lemmas — bilinearity and the coordinate forms -/",
                [
                    "wedge_add_left", "wedge_sub_left", "wedge_smul_left",
                    "wedge_add_right", "wedge_sub_right", "wedge_smul_right",
                    "wedge_self_vec_coord", "wedge_vec_eq_biv",
                ],
            ),
            (
                "/-! ### Coordinate-vector leaves: magnitude, self-product, and reverse -/",
                [
                    "normSq_vec", "normSq_wedge_vec", "mul_vec_self_coord",
                    "dot_self_vec_eq_normSq_coord", "reverse_vec",
                ],
            ),
            (
                "/-! ### The fundamental split `a b = a·b + a∧b` (coordinate form) -/",
                ["vec_mul_eq_dot_add_wedge", "vec_mul_perp"],
            ),
            (
                "/-! ### Grade-structure predicates (vector / bivector / trivector) with their bridges -/",
                [
                    "IsVector", "eq_vec_of_isVector", "isVector_vec",
                    "IsVector.smul", "IsVector.sub",
                    "IsBivector", "eq_bivector_of_isBivector", "isBivector_bivector",
                    "IsTrivector", "eq_trivector_of_isTrivector", "isTrivector_trivector",
                ],
            ),
            (
                "/-! ### Object-form facts: the split, antisymmetry, self-products, and dot/wedge as the two parts -/",
                [
                    "mul_eq_dot_add_wedge", "mul_eq_wedge_of_perp", "wedge_antisymm",
                    "wedge_self_vec", "dot_self_vec_eq_normSq", "mul_vec_self",
                    "dot_is_sym_part", "wedge_is_antisym_part",
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
