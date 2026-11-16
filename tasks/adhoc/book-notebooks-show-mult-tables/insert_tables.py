# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
"""Insert the show_mult table cells into the book notebooks (one-shot, idempotent).

Each edit is (notebook, anchor, inserted text, position): the anchor must occur
exactly once; the text goes before or after it. A notebook that already holds the
inserted text is left alone, so a second run changes nothing.
"""

import pathlib
import sys
import typing

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
NOTEBOOKS: pathlib.Path = ROOT / "book" / "docs" / "notebooks"
IMPORT: str = "from gacalc.nbdisplay import show_mult\n"


class Edit(typing.NamedTuple):
    """One insertion: ``text`` goes before or after the unique ``anchor``."""

    notebook: str
    anchor: str
    text: str
    after: bool


EDITS: list[Edit] = [
    # bootstrap-product: a * b concrete, then symbolic.
    Edit(
        "bootstrap-product.py",
        "# %% [markdown]\n# ## The quarter turn is a product\n",
        "# %% [markdown]\n"
        "# ## The same product, term by term\n"
        "#\n"
        "# The multiplication rules give `a * b` the way you multiply `(x + 2) * (x + 3)`:\n"
        "# every term of `a` times every term of `b`, then add. Each row of the table is one\n"
        "# pair of terms. `e_1 * e_1` and `e_2 * e_2` are `1`, and `e_2 * e_1 = -e_12`.\n"
        "# The sum is the product from projection above.\n"
        "\n"
        "# %%\n"
        "show_mult(a, b)\n"
        "\n",
        False,
    ),
    Edit(
        "bootstrap-product.py",
        "projection_symbolic: Vector = b_symbolic.projected_onto(a_symbolic)\n"
        "rejection_symbolic: Vector = b_symbolic.rejected_away_from(a_symbolic)\n",
        "\n"
        "# %% [markdown]\n"
        "# The product by the rules, term by term, for every `a` and `b`:\n"
        "\n"
        "# %%\n"
        "show_mult(a_symbolic, b_symbolic)\n",
        True,
    ),
    # bootstrap-projection-from-product: b * a and (b ^ a) * a^-1, then b * a symbolic.
    Edit(
        "bootstrap-projection-from-product.py",
        "# %%\nb_dot_a: Real = (b * a).scalar_part()\n",
        "# %% [markdown]\n"
        "# `b * a` term by term. Its plain-number part, the sum of the `e_1 * e_1` and\n"
        "# `e_2 * e_2` rows, is `b · a`:\n"
        "\n"
        "# %%\n"
        "show_mult(b, a)\n"
        "\n",
        False,
    ),
    Edit(
        "bootstrap-projection-from-product.py",
        "# %%\nrejection: MultiVectorBase = (b.wedge(a) * a_inverse).simplified()\n",
        "# %% [markdown]\n"
        "# `(b ∧ a) * a⁻¹` term by term: `e_12` times each term of `a⁻¹` is a quarter turn of\n"
        "# that term, so the result is a vector again:\n"
        "\n"
        "# %%\n"
        "show_mult(b.wedge(a), a_inverse)\n"
        "\n",
        False,
    ),
    Edit(
        "bootstrap-projection-from-product.py",
        "# %% [markdown]\n# `a⁻¹ = a / |a|^2`:\n",
        "# %% [markdown]\n"
        "# `b * a` term by term, for every `a` and `b`; its plain-number part is\n"
        "# `a_1 * b_1 + a_2 * b_2`:\n"
        "\n"
        "# %%\n"
        "show_mult(b_symbolic, a_symbolic)\n"
        "\n",
        False,
    ),
    # bootstrap-rotation-from-product: v * unit_product, the sandwich, then symbolic v.
    Edit(
        "bootstrap-rotation-from-product.py",
        "# %%\none_sided: MultiVectorBase = (v * unit_product).simplified()\n",
        "# %% [markdown]\n"
        "# Term by term: each term of `v` times the plain-number part keeps its direction,\n"
        "# and times the `e_12` part turns a quarter turn:\n"
        "\n"
        "# %%\n"
        "show_mult(v, unit_product)\n"
        "\n",
        False,
    ),
    Edit(
        "bootstrap-rotation-from-product.py",
        "# %%\nh: Vector = Scalar(b.magnitude()) * a + Scalar(a.magnitude()) * b\n",
        "# %% [markdown]\n"
        "# The sandwich is two products. First `R * v`, term by term:\n"
        "\n"
        "# %%\n"
        "show_mult(R, v)\n"
        "\n"
        "# %% [markdown]\n"
        "# then that result times `R⁻¹`:\n"
        "\n"
        "# %%\n"
        "show_mult((R * v).simplified(), R.inverse())\n"
        "\n",
        False,
    ),
    Edit(
        "bootstrap-rotation-from-product.py",
        "unit_product_symbolic: Versor = a_symbolic.normalize() * b_symbolic.normalize()\n",
        "\n"
        "# %% [markdown]\n"
        "# The one-sided form term by term for every `v`, with the `a` and `b` set at the top:\n"
        "# each coordinate of the result is a combination of `v_1` and `v_2`.\n"
        "\n"
        "# %%\n"
        "show_mult(v_symbolic, unit_product)\n",
        True,
    ),
    # Part I notebooks: symbolic only (they set no values).
    Edit(
        "product-from-projection.py",
        "# %% [markdown]\n# ## The two parts are the dot and the wedge\n",
        "# %% [markdown]\n"
        "# The same product by the multiplication rules, term by term:\n"
        "\n"
        "# %%\n"
        "show_mult(b, a)\n"
        "\n",
        False,
    ),
    Edit(
        "levels-of-abstraction.py",
        "# %% [markdown]\n# ## Dot product — the grade-0 part\n",
        "# %% [markdown]\n"
        "# The product term by term: the `e_1 * e_1` and `e_2 * e_2` rows make the grade-0\n"
        "# part, the other two rows the grade-2 part.\n"
        "\n"
        "# %%\n"
        "show_mult(a, b)\n"
        "\n",
        False,
    ),
    Edit(
        "geometric-product.py",
        "full_angle_result: Vector = (a * R).simplified()\nfull_angle_result\n",
        "\n"
        "# %% [markdown]\n"
        "# The same product term by term: each coordinate of `a` times `cos(theta)` stays\n"
        "# put, and times `sin(theta) * e_12` turns a quarter turn.\n"
        "\n"
        "# %%\n"
        "show_mult(a, R)\n",
        True,
    ),
    Edit(
        "rotation-from-vectors.py",
        "# %% [markdown]\n# **The rotor carries `a_hat` to `b_hat`.**",
        "# %% [markdown]\n"
        "# The same product term by term. The plain-number rows add to\n"
        "# `cos(α) * cos(β) + sin(α) * sin(β)`, which is `cos(β - α)`, and the `e_12` rows to\n"
        "# `sin(β - α)`: the angle-difference identities, from multiplying.\n"
        "\n"
        "# %%\n"
        "show_mult(a_hat, b_hat)\n"
        "\n",
        False,
    ),
    Edit(
        "three-dimensions.py",
        "\nproduct_3d\n",
        "\n"
        "# %% [markdown]\n"
        "# The product term by term: nine pairs now, three of them a direction times\n"
        "# itself. Those three rows add to the dot; the other six pair up, `e_i * e_j` with\n"
        "# `e_j * e_i`, into the three bivector parts of the wedge.\n"
        "\n"
        "# %%\n"
        "show_mult(p, q)\n",
        True,
    ),
]


def add_import(source: str) -> str:
    """``source`` with the ``show_mult`` import after its last gacalc import."""
    lines: list[str] = source.splitlines(keepends=True)
    last: int = max(
        i
        for i, line in enumerate(lines)
        if line.startswith(("from gacalc", "import gacalc"))
    )
    while lines[last].rstrip().endswith("("):
        last = next(i for i in range(last, len(lines)) if lines[i].startswith(")"))
    return "".join([*lines[: last + 1], IMPORT, *lines[last + 1 :]])


def main() -> int:
    """Apply every edit; return 1 if an anchor is missing or not unique."""
    status: int = 0
    name: str
    for name in sorted({edit.notebook for edit in EDITS}):
        path: pathlib.Path = NOTEBOOKS / name
        source: str = path.read_text()
        edit: Edit
        for edit in (e for e in EDITS if e.notebook == name):
            if edit.text in source:
                continue
            count: int = source.count(edit.anchor)
            if count != 1:
                print(f"{name}: anchor found {count} times: {edit.anchor!r}")  # noqa: T201
                status = 1
                continue
            replacement: str = (
                edit.anchor + edit.text if edit.after else edit.text + edit.anchor
            )
            source = source.replace(edit.anchor, replacement)
        if "show_mult(" in source and IMPORT not in source:
            source = add_import(source)
        path.write_text(source)
    return status


if __name__ == "__main__":
    sys.exit(main())
