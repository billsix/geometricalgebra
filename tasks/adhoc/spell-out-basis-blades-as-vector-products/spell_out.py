#!/usr/bin/env python3
"""Spell out the unit planes of the book and notebooks as products of basis vectors.

Rewrites ``\\mathbf{e}_{12}`` (and ``_{13}``, ``_{23}``, ``_{123}``) in typeset math to
``\\vec{\\mathbf{e}}_1 * \\vec{\\mathbf{e}}_2`` (and the matching products) in the book pages
and in the notebooks, following the rules of
``tasks/spell-out-basis-blades-as-vector-products.md``:

- after ``* `` the product follows a coefficient plainly (``y * e_1 * e_2``) and is
  parenthesized after a vector (``a * (e_1 * e_2)``);
- as the left factor, after ``\\cdot`` or before ``{}^2`` it is parenthesized;
- bare after ``=`` it is ``1 * e_1 * e_2``; elsewhere (a role in a sentence) it is the
  bare product.

A line that names the blade itself (a product rule ``e_1 * e_2 = e_12``, "call it", the list
of blades) keeps the name; those lines are in ``KEEP``. Pages and notebooks whose only uses are
plane names or subscripts are not processed at all (``SKIP``).

The ``C-same`` code lines (the constant ``e_12`` where the product has the same type) are
rewritten by ``CODE_EDITS``. Matching is on text, never on a line number; running the script
twice changes nothing.

Usage: ``python tasks/adhoc/spell-out-basis-blades-as-vector-products/spell_out.py``
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
E: str = r"\vec{\mathbf{e}}"
PRODUCT: dict[str, str] = {
    "12": f"{E}_1 * {E}_2",
    "13": f"{E}_1 * {E}_3",
    "23": f"{E}_2 * {E}_3",
    "123": f"{E}_1 * {E}_2 * {E}_3",
}
BLADE: re.Pattern[str] = re.compile(r"\\mathbf\{e\}_\{(12|13|23|123)\}")
VECTOR_TAIL: re.Pattern[str] = re.compile(
    r"\\(?:vec|hat)\{\\mathbf\{[a-z]\}\}(?:_\{?\w+\}?)?\Z"
)
BLADE_GROUP_TAIL: re.Pattern[str] = re.compile(
    r"\(\\vec\{\\mathbf\{e\}\}_1 \* [^()]*\)\Z"
)

# Pages and notebooks whose uses are plane names, subscripts or figure labels (class P/X),
# or already written in the target form.
SKIP: frozenset[str] = frozenset(
    {
        "book/docs/cheat-sheet-2d.rst",
        "book/docs/cheat-sheet-3d.rst",
        "book/docs/cheat-sheet-gn.rst",
        "book/docs/proof-cross.rst",
        "book/docs/projection-rejection-3d.rst",
        "notebooks/projection-rejection-3d.py",
        "notebooks/proof-cross.py",
        "notebooks/proof-projection-3d.py",
        "notebooks/reflection-3d.py",
        "notebooks/frame-qr-3d.py",
        "notebooks/displaygraded.py",
        "notebooks/displayrotations.py",
    }
)

# A match on a line containing one of these strings keeps the name (class N).
KEEP: tuple[str, ...] = (
    "call it",
    "The blades are constants",
    "to the arrow it names",
    "object :math:`\\mathbf{e}_{12} = ",
    "$\\mathbf{e}_{12} = \\vec",
    "behave like the complex numbers",
    "$\\mathbf{e}_{12}, \\mathbf{e}_{13}, \\mathbf{e}_{23}$, one for each pair",
    "$\\mathbf{e}_{123} = \\vec",
    "like the plane's $\\mathbf{e}_{12}$ in `displayg2.py`",
    "written $\\mathbf{e}_{12}$",
    "unit volume $\\mathbf{e}_{123}$",
    "# $\\mathbf{e}_{123}$.",
    "of plane $\\mathbf{e}_{12}$",
    "is the unit plane $\\mathbf{e}_{12}$",
    "grade 2.",
    'note(at=0.5 * (P_E1 + P_E2), text=r"$\\mathbf{e}_{12}$"',
)


@dataclass(frozen=True)
class CodeEdit:
    """One rewrite of a code line that uses the constant ``e_12``.

    Attributes:
        path: File to edit, relative to the repository root.
        old: Exact text to replace; must occur in the file unless already rewritten.
        new: Its replacement.
    """

    path: str
    old: str
    new: str


CODE_EDITS: tuple[CodeEdit, ...] = (
    CodeEdit(
        "notebooks/bootstrap-product.py",
        "Scalar(measured.coefficient(e_2)) * e_12)",
        "Scalar(measured.coefficient(e_2)) * (e_1 * e_2))",
    ),
    CodeEdit(
        "notebooks/bootstrap-product.py",
        "quarter_turn: MultiVectorBase = b * e_12",
        "quarter_turn: MultiVectorBase = b * (e_1 * e_2)",
    ),
    CodeEdit(
        "notebooks/bootstrap-product.py",
        "Scalar(sympy.sin(beta - alpha)) * e_12",
        "Scalar(sympy.sin(beta - alpha)) * (e_1 * e_2)",
    ),
    CodeEdit("notebooks/defining-g2.py", "\ne_12 * e_12\n", "\n(e_1 * e_2) * (e_1 * e_2)\n"),
    CodeEdit(
        "notebooks/defining-g2.py",
        "Scalar(sympy.sin(theta)) * e_12",
        "Scalar(sympy.sin(theta)) * (e_1 * e_2)",
    ),
    CodeEdit("notebooks/defining-g2.py", "type(a * e_12).__name__", "type(a * (e_1 * e_2)).__name__"),
    CodeEdit("notebooks/dual.py", "\ne_12 * I_inverse\n", "\n(e_1 * e_2) * I_inverse\n"),
    CodeEdit(
        "notebooks/geometric-product.py",
        "quarter_turn: Vector = a * Bivector.e_12",
        "quarter_turn: Vector = a * (Vector.e_1 * Vector.e_2)",
    ),
    CodeEdit(
        "notebooks/geometric-product.py",
        "Scalar(sympy.sin(theta)) * Bivector.e_12",
        "Scalar(sympy.sin(theta)) * (Vector.e_1 * Vector.e_2)",
    ),
    CodeEdit(
        "notebooks/product-from-projection.py",
        "Scalar(y) * Bivector.e_12)",
        "Scalar(y) * (Vector.e_1 * Vector.e_2))",
    ),
    CodeEdit(
        "notebooks/product-from-projection.py",
        "Scalar(b.magnitude() * y) * Bivector.e_12)",
        "Scalar(b.magnitude() * y) * (Vector.e_1 * Vector.e_2))",
    ),
)


# Hand-written rewrites that no rule covers: the e_31 / e_13 note of finding 3 in three
# places (written as e_3 * e_1 = -e_1 * e_3), and the sentence of displayg2.py that
# `tasks/prune-unneeded-cancellation-checks.md` left with a plain `\\mathbf{e}_1`.
TEXT_EDITS: tuple[CodeEdit, ...] = (
    CodeEdit(
        "book/docs/projection-rejection-3d.rst",
        "   The third plane is written :math:`\\mathbf{e}_{31}` (cyclically, like :math:`\\mathbf{e}_{12}` and\n"
        "   :math:`\\mathbf{e}_{23}`); gacalc spells the same blade :math:`\\mathbf{e}_{13} = -\\mathbf{e}_{31}`.\n",
        "   The third plane is written :math:`\\mathbf{e}_{31}` (cyclically, like :math:`\\mathbf{e}_{12}` and\n"
        "   :math:`\\mathbf{e}_{23}`); gacalc writes its product the other way round, and\n"
        "   :math:`\\vec{\\mathbf{e}}_3 * \\vec{\\mathbf{e}}_1 = -\\vec{\\mathbf{e}}_1 * \\vec{\\mathbf{e}}_3` is the same plane.\n",
    ),
    CodeEdit(
        "notebooks/projection-rejection-3d.py",
        "# Onto the $\\mathbf{e}_{31}$ plane (gacalc writes it\n"
        "# $\\mathbf{e}_{13} = -\\mathbf{e}_{31}$; the sign does not change which plane it is), the\n",
        "# Onto the $\\mathbf{e}_{31}$ plane (gacalc writes its product the other way round,\n"
        "# $\\vec{\\mathbf{e}}_3 * \\vec{\\mathbf{e}}_1 = -\\vec{\\mathbf{e}}_1 * \\vec{\\mathbf{e}}_3$;\n"
        "# the sign does not change which plane it is), the\n",
    ),
    CodeEdit(
        "book/figures/epix/proj3d_e31.py",
        "# book writes this plane $\\mathbf{e}_{31}$, cyclically; gacalc's blade constant is\n"
        "# $\\mathbf{e}_{13}=-\\mathbf{e}_{31}$.) Built with the `epix` package;\n",
        "# book writes this plane $\\mathbf{e}_{31}$, cyclically; gacalc writes its product the other\n"
        "# way round, $\\vec{\\mathbf{e}}_3 * \\vec{\\mathbf{e}}_1 = -\\vec{\\mathbf{e}}_1 * \\vec{\\mathbf{e}}_3$.)\n"
        "# Built with the `epix` package;\n",
    ),
    CodeEdit(
        "notebooks/displayg2.py",
        "product $\\mathbf{e}_1 * \\mathbf{e}_2$.",
        "product $\\vec{\\mathbf{e}}_1 * \\vec{\\mathbf{e}}_2$.",
    ),
)


def replacement_for(text: str, match: re.Match[str]) -> str | None:
    """The spelled-out form of one ``\\mathbf{e}_{..}`` occurrence.

    Args:
        text: The whole file.
        match: The occurrence.

    Returns:
        str | None: the replacement, or None to leave the occurrence alone.
    """
    product: str = PRODUCT[match.group(1)]
    before: str = text[: match.start()]
    after: str = text[match.end() :]
    line_start: int = text.rfind("\n", 0, match.start()) + 1
    line_end: int = text.find("\n", match.end())
    line: str = text[line_start : line_end if line_end >= 0 else len(text)]
    if any(marker in line for marker in KEEP):
        return None
    if before.endswith("_{"):
        return None
    if re.search(rf"{re.escape(E)}_1 \* {re.escape(E)}_2 = -?\Z", before):
        return None  # the naming equation e_1 * e_2 = e_12 keeps the name
    if after.startswith("{}^2"):
        return f"({product})"
    star: re.Match[str] | None = re.search(r"\*\s+\Z", before)
    if star is not None:
        prior: str = before[: star.start()].rstrip()
        after_vector: bool = VECTOR_TAIL.search(prior) is not None
        after_product: bool = (
            BLADE_GROUP_TAIL.search(prior) is not None or BLADE.search(prior[-24:]) is not None
        )
        return f"({product})" if after_vector or after_product else product
    if re.match(r"\s*\*", after) or re.search(r"\\cdot\s+\Z", before):
        return f"({product})"
    if re.search(rf"{re.escape(E)}_2 \* {re.escape(E)}_1 = -\Z", before):
        return product
    if re.search(r"=\s*\Z", before) or re.search(r"=\s*-\Z", before):
        return f"1 * {product}"
    return product


def rewrite_text(text: str) -> str:
    """Spell out every eligible blade name in ``text``.

    Args:
        text: The whole file.

    Returns:
        str: the text with each eligible ``\\mathbf{e}_{12}`` and its relatives rewritten.
    """
    pieces: list[str] = []
    cursor: int = 0
    match: re.Match[str]
    for match in BLADE.finditer(text):
        new: str | None = replacement_for(text, match)
        if new is None:
            continue
        pieces.append(text[cursor : match.start()])
        pieces.append(new)
        cursor = match.end()
    pieces.append(text[cursor:])
    return "".join(pieces)


def target_files() -> list[pathlib.Path]:
    """The book pages and notebooks that are rewritten.

    Returns:
        list[pathlib.Path]: every page and notebook not in ``SKIP``.
    """
    paths: list[pathlib.Path] = sorted(
        [*(REPO / "book" / "docs").glob("*.rst"), *(REPO / "notebooks").glob("*.py")]
    )
    return [p for p in paths if str(p.relative_to(REPO)) not in SKIP]


def main() -> None:
    """Rewrite the blade names, then the code lines, and report what changed."""
    changed: int = 0
    path: pathlib.Path
    for path in target_files():
        original: str = path.read_text()
        updated: str = rewrite_text(original)
        if updated != original:
            path.write_text(updated)
            changed += 1
            print(f"spelled out: {path.relative_to(REPO)}")
    edit: CodeEdit
    for edit in (*CODE_EDITS, *TEXT_EDITS):
        target: pathlib.Path = REPO / edit.path
        text: str = target.read_text()
        if edit.old not in text:
            print(f"  already done or absent: {edit.path}: {edit.old.strip()[:50]}")
            continue
        target.write_text(text.replace(edit.old, edit.new))
        changed += 1
        print(f"code: {edit.path}: {edit.old.strip()[:50]}")
    print(f"{changed} files or lines changed")


if __name__ == "__main__":
    main()
