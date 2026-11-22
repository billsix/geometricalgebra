#!/usr/bin/env python3
"""Delete named declarations (with their doc comments) from the Lean proofs.

Each target is a file and a name qualified by its namespace suffix (``G2.vec_mul``, or just the
bare name when it is unique in the file). The script tracks ``namespace`` / ``end`` lines, so the
``G2`` and ``G3`` copies of a theorem in one file are told apart, and removes the declaration
together with the ``/-- ... -/`` doc comment and ``-- twin:`` lines directly above it and the
blank line after it. A name that matches nothing is reported, not an error, so a second run
changes nothing. Whether a deleted name was really unused is decided by the build that follows.

Usage: ``python tasks/adhoc/lean-proofs-fit-cleanup/delete_decls.py``
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
PROOFS: pathlib.Path = REPO / "proofs" / "GacalcProofs"

DECL: re.Pattern[str] = re.compile(
    r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(?:noncomputable\s+)?"
    r"(theorem|lemma|def|abbrev|instance)\s+([^\s({:\[]+)"
)
NAMESPACE: re.Pattern[str] = re.compile(r"^namespace\s+(\S+)")
END: re.Pattern[str] = re.compile(r"^end\s+(\S+)")
# A column-0 line that starts something new, so the current declaration has ended.
TOP_LEVEL: re.Pattern[str] = re.compile(
    r"^(?:/--|/-!|/-|--|theorem|lemma|def|noncomputable|private|protected|namespace|end|open|"
    r"section|variable|@\[|set_option|attribute|instance|abbrev|#|import)"
)


@dataclass(frozen=True)
class Target:
    """One declaration to delete.

    Attributes:
        file: File name under ``proofs/GacalcProofs``.
        name: The declaration's name, qualified by as much of its namespace as needed.
    """

    file: str
    name: str


def block_bounds(lines: list[str], start: int) -> tuple[int, int]:
    """The line range of the declaration starting at ``start``, doc comment included.

    Args:
        lines: The file's lines.
        start: Index of the line that begins the declaration (``theorem ...``).

    Returns:
        tuple[int, int]: first line to delete and one past the last, trailing blank included.
    """
    top: int = start
    cursor: int = start - 1
    while cursor >= 0 and lines[cursor].startswith("-- twin:"):
        top = cursor
        cursor -= 1
    if cursor >= 0 and lines[cursor].rstrip().endswith("-/"):
        while cursor >= 0 and not lines[cursor].lstrip().startswith("/--"):
            cursor -= 1
        top = cursor
        while top - 1 >= 0 and lines[top - 1].startswith("-- twin:"):
            top -= 1
    end: int = start + 1
    while end < len(lines) and not (lines[end] and TOP_LEVEL.match(lines[end])):
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    if end < len(lines) and not lines[end].strip():
        end += 1
    return top, end


def delete_from(path: pathlib.Path, names: list[str]) -> list[str]:
    """Delete every declaration in ``path`` whose qualified name ends with one of ``names``.

    Args:
        path: The Lean file.
        names: Name suffixes to delete (every match is deleted).

    Returns:
        list[str]: the names that matched nothing.
    """
    lines: list[str] = path.read_text().split("\n")
    stack: list[str] = []
    spans: list[tuple[int, int]] = []
    found: set[str] = set()
    index: int
    for index, line in enumerate(lines):
        ns: re.Match[str] | None = NAMESPACE.match(line)
        if ns is not None:
            stack.append(ns.group(1))
            continue
        if END.match(line):
            if stack:
                stack.pop()
            continue
        decl: re.Match[str] | None = DECL.match(line)
        if decl is None:
            continue
        qualified: str = ".".join([*stack, decl.group(2)])
        wanted: str
        for wanted in names:
            if qualified == wanted or qualified.endswith("." + wanted):
                spans.append(block_bounds(lines, index))
                found.add(wanted)
                break
    first: int
    last: int
    for first, last in sorted(spans, reverse=True):
        del lines[first:last]
    if spans:
        path.write_text("\n".join(lines))
    return [n for n in names if n not in found]


TARGETS: tuple[Target, ...] = (
    # the IsScalar apparatus and the unused recognizers (record section A.2)
    *(Target(f, n) for f in ("G2.lean", "G3.lean") for n in (
        "IsScalar", "eq_scalar_of_isScalar", "isScalar_scalar", "isScalar_one",
        "isScalar_mul_self_of_isVector",
    )),
    Target("G2.lean", "eq_smul_e12_of_isBivector"),
    Target("G2.lean", "isBivector_e12"),
    Target("G2.lean", "isBivector_wedge_of_isVector"),
    Target("G3.lean", "isBivector_bivector"),
    Target("G3.lean", "isTrivector_trivector"),
    Target("G3.lean", "eq_trivector_of_isTrivector"),
    # singles (record sections A.2, B.2)
    Target("Measures.lean", "area_sq_vec"),
    Target("Measures.lean", "normSq_wedge_eq_lagrange"),
    Target("G2.lean", "dual_vec_perp"),
    Target("G2.lean", "vec_mul"),
    Target("G2.lean", "dot_eq_coord_sum"),
    Target("G2.lean", "normSq_wedge_vec"),
    Target("MathlibBridge.lean", "toC_rot_rot"),
    Target("Sandwich.lean", "IsRotor.isEvenVersor"),
    Target("Sandwich.lean", "IsRotor.normSq_eq_one"),
    Target("Sandwich.lean", "mul_reverse_self_of_isRotor"),
    Target("Sandwich.lean", "reverse_mul_self_of_isRotor"),
    Target("Sandwich.lean", "G3.reverse_mul_vec"),
    Target("Rotation2D.lean", "rotor_unit'"),
    # CrossStandardPosition: the projection/rejection half that feeds only itself
    *(Target("CrossStandardPosition.lean", n) for n in (
        "rotYZ_smul", "rotYZ_sub", "rotXZ_sub", "rotYZ_preserves_dot", "proj_rotYZ_equivariant",
        "vecReject_rotXZ_equivariant", "vecReject_rotYZ_equivariant", "proj_reduced",
        "vecReject_reduced",
    )),
    # ProjectionRotation3D: the object-form wrappers nothing uses (record section C.2)
    *(Target("ProjectionRotation3D.lean", n) for n in (
        "wedge_vec_wedge_self", "reject_in_plane_self", "inner_vb_mul_reverse_self",
        "project_onto_in_plane_self", "plane_pythagorean", "project_perp_reject",
        "inplane_perp_reject", "normSq_mul_vec", "normalizeVec_to_mul_versor_eq_bisector",
        "vec_mul_bisector_eq", "normalizeVec_mul_versor_eq_reverse", "versor_mul_project_eq",
        "versor_mul_reject_comm",
    )),
)


def main() -> None:
    """Delete every target and report what matched nothing."""
    by_file: dict[str, list[str]] = {}
    target: Target
    for target in TARGETS:
        by_file.setdefault(target.file, []).append(target.name)
    file: str
    names: list[str]
    for file, names in by_file.items():
        missing: list[str] = delete_from(PROOFS / file, names)
        print(f"{file}: {len(names) - len(missing)} of {len(names)} deleted")
        name: str
        for name in missing:
            print(f"  not found: {name}")
    for gone in ("RotateComponents.lean", "Normalize.lean"):
        path: pathlib.Path = PROOFS / gone
        if path.exists():
            path.unlink()
            print(f"removed file {gone}")


if __name__ == "__main__":
    main()
