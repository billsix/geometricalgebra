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

"""Unit tests for the code generator's pure logic (tools/).

These exercise the *generator* itself -- blade naming, blade ordering, the
type-resolution registry, and the astbuild DSL invariants -- as opposed to the
*generated* classes, whose behaviour is covered by test_conformance.py /
test_graded.py.  ``tools/`` is not a package and not on the default path, so we
add it here; importing the generator is side-effect-free (``main()`` is guarded
by ``if __name__ == "__main__"``).
"""

import ast
import sys
from pathlib import Path

import sympy

_TOOLS = Path(__file__).resolve().parent.parent / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import astbuild  # noqa: E402
import gen_specialized as gen  # noqa: E402

# --------------------------------------------------------------------------
# Blade <-> name bijection and field naming
# --------------------------------------------------------------------------


def test_blade_label_special_cases() -> None:
    assert gen.blade_label(()) == "scalar"
    assert gen.blade_label((1,)) == "e_1"
    assert gen.blade_label((1, 2)) == "e_12"
    assert gen.blade_label((1, 2, 3)) == "e_123"


def test_blade_label_roundtrips_over_all_blades() -> None:
    n: int
    for n in (1, 2, 3):
        blade: gen.Blade
        for blade in gen.blades_for_dim(n):
            assert gen.blade_of_label(gen.blade_label(blade)) == blade


def test_field_name_is_coeff_prefixed() -> None:
    assert gen.field_name(()) == "coeff_scalar"
    assert gen.field_name((1,)) == "coeff_e_1"
    assert gen.field_name((1, 2)) == "coeff_e_12"


# --------------------------------------------------------------------------
# Canonical blade ordering
# --------------------------------------------------------------------------


def test_blades_for_dim_canonical_order() -> None:
    assert gen.blades_for_dim(2) == [(), (1,), (2,), (1, 2)]
    assert gen.blades_for_dim(3) == [
        (),
        (1,),
        (2,),
        (3,),
        (1, 2),
        (1, 3),
        (2, 3),
        (1, 2, 3),
    ]


def test_blades_for_dim_is_grade_then_index() -> None:
    blades: list[gen.Blade] = gen.blades_for_dim(3)
    assert blades == sorted(blades, key=lambda b: (len(b), b))
    assert len(blades) == 2**3


# --------------------------------------------------------------------------
# term_grade_key -- orders generated sums scalar -> vector -> bivector -> ...
# --------------------------------------------------------------------------


def test_term_grade_key_orders_lower_grade_first() -> None:
    key_vec: tuple[int, gen.Blade, int, gen.Blade] = gen.term_grade_key(
        sympy.Symbol("a_e_2")
    )  # grade 1
    key_biv: tuple[int, gen.Blade, int, gen.Blade] = gen.term_grade_key(
        sympy.Symbol("a_e_12")
    )  # grade 2
    assert key_vec < key_biv
    assert key_vec[0] == 1 and key_biv[0] == 2


def test_term_grade_key_uses_both_operands() -> None:
    # a product of one self (a_) and one rhs (b_) symbol keys on both grades
    key: tuple[int, gen.Blade, int, gen.Blade] = gen.term_grade_key(
        sympy.Symbol("a_e_1") * sympy.Symbol("b_e_2")
    )
    assert key == (1, (1,), 1, (2,))


# --------------------------------------------------------------------------
# Subscript / superscript helpers (used in generated docstrings)
# --------------------------------------------------------------------------


def test_subscript_superscript() -> None:
    assert gen._subscript(0) == "₀"
    assert gen._subscript(12) == "₁₂"
    assert gen._superscript(3) == "³"
    assert gen._superscript(10) == "¹⁰"


# --------------------------------------------------------------------------
# Type registry and resolution -- "the type follows the operation"
# --------------------------------------------------------------------------


def test_registry_for_dim_lists_graded_then_full() -> None:
    names: list[str] = [s.name for s in gen.registry_for_dim(2, "G")]
    assert names == ["Scalar", "Vector", "Bivector", "Versor", "G"]


def test_resolve_smallest_covering_type() -> None:
    assert gen.resolve([()], 2, "G").name == "Scalar"
    assert gen.resolve([(1,), (2,)], 2, "G").name == "Vector"
    assert gen.resolve([(1, 2)], 2, "G").name == "Bivector"
    assert gen.resolve([(), (1, 2)], 2, "G").name == "Versor"


def test_resolve_widens_to_full_when_no_graded_type_covers() -> None:
    # a vector + bivector support spans no single graded type -> the full G_n
    assert gen.resolve([(1,), (1, 2)], 2, "G").name == "G"


# --------------------------------------------------------------------------
# product_result / unary_result -- gen-time result-type determination
# --------------------------------------------------------------------------


def _spec(n: int, name: str) -> gen.TypeSpec:
    by_name: dict[str, gen.TypeSpec] = {
        s.name: s for s in [gen.full_spec(n, "G"), *gen.graded_specs(n)]
    }
    return by_name[name]


def test_product_result_geometric_vector_times_vector_is_versor() -> None:
    v2: gen.TypeSpec = _spec(2, "Vector")
    result_spec: gen.TypeSpec
    result_spec, _ = gen.product_result(v2, v2, lambda a, b: a * b, 2, "G")
    assert result_spec.name == "Versor"


def test_product_result_outer_vector_wedge_vector_is_bivector() -> None:
    v2: gen.TypeSpec = _spec(2, "Vector")
    result_spec: gen.TypeSpec
    result_spec, _ = gen.product_result(v2, v2, lambda a, b: a.outer_product(b), 2, "G")
    assert result_spec.name == "Bivector"


def test_product_result_bivector_times_bivector_is_scalar() -> None:
    b2: gen.TypeSpec = _spec(2, "Bivector")
    result_spec: gen.TypeSpec
    result_spec, _ = gen.product_result(b2, b2, lambda a, b: a * b, 2, "G")
    assert result_spec.name == "Scalar"


def test_unary_result_reverse_preserves_grade() -> None:
    v2: gen.TypeSpec = _spec(2, "Vector")
    result_spec: gen.TypeSpec
    result_spec, _ = gen.unary_result(v2, lambda a: a.reverse(), 2, "G")
    assert result_spec.name == "Vector"


def test_unary_result_dual_of_vector3_is_bivector3() -> None:
    v3: gen.TypeSpec = _spec(3, "Vector")
    result_spec: gen.TypeSpec
    result_spec, _ = gen.unary_result(v3, lambda a: a.dual(3), 3, "G")
    assert result_spec.name == "Bivector"


# --------------------------------------------------------------------------
# astbuild DSL invariants
# --------------------------------------------------------------------------


def test_module_source_roundtrip() -> None:
    src: str = astbuild.module_source([ast.Expr(astbuild.attribute("self", "e_1"))])
    assert src == "self.e_1"


def test_symbol_to_attr_rewrites_operand_symbols() -> None:
    tree: ast.expr = astbuild.parse_expr("a_e_1 + b_e_2")
    rename: dict[str, tuple[str, str]] = {
        "a_e_1": ("self", "e_1"),
        "b_e_2": ("rhs", "e_2"),
    }
    out: ast.AST = ast.fix_missing_locations(astbuild.SymbolToAttr(rename).visit(tree))
    assert ast.unparse(out) == "self.e_1 + rhs.e_2"


def test_cast_coef_skips_bare_and_negated_fields() -> None:
    bare: ast.expr = astbuild.attribute("self", "coeff_e_1")
    assert astbuild.cast_coef(bare) is bare
    negated: ast.UnaryOp = ast.UnaryOp(
        ast.USub(), astbuild.attribute("self", "coeff_e_1")
    )
    assert astbuild.cast_coef(negated) is negated


def test_cast_coef_wraps_compound_expression() -> None:
    compound: ast.BinOp = ast.BinOp(
        astbuild.name_ref("a"), ast.Add(), astbuild.name_ref("b")
    )
    wrapped: ast.expr = astbuild.cast_coef(compound)
    assert ast.unparse(wrapped) == "typing.cast(Real, a + b)"


def test_header_comment_renders_at_the_end_of_the_def_line() -> None:
    # A header_comment decorator becomes a trailing comment on the `def` line.
    function: ast.stmt = ast.parse("def f(x):\n    return x\n").body[0]
    assert isinstance(function, ast.FunctionDef)
    function.decorator_list.append(astbuild.header_comment("ty: ignore[some-rule]"))
    source: str = astbuild.module_source([function])
    assert source.splitlines()[0] == "def f(x):  # ty: ignore[some-rule]"
    assert "@@" not in source


def test_mark_graded_return_overrides_marks_only_conflicting_overrides() -> None:
    # A graded override conflicts with the base's `-> Self` when its own-type
    # overload returns another type (Vector.wedge(Vector) -> Bivector), or, for an
    # any-operand method, when its implementation returns another type.  An
    # own-type overload returning the class itself (Scalar.wedge) does not.
    module: ast.Module = ast.parse(
        "import typing\n"
        "class G:\n"
        "    def __mul__(self, rhs) -> MultiVectorBase: ...\n"
        "class Vector:\n"
        "    @typing.overload\n"
        "    def wedge(self, rhs: Vector) -> Bivector: ...\n"
        "    def wedge(self, rhs) -> MultiVectorBase: ...\n"
        "    def __mul__(self, rhs) -> MultiVectorBase: ...\n"
        "    def r_vector_part(self, r) -> Vector: ...\n"
        "class Scalar:\n"
        "    @typing.overload\n"
        "    def wedge(self, rhs: Scalar) -> Scalar: ...\n"
        "    def wedge(self, rhs) -> MultiVectorBase: ...\n"
    )
    gen.mark_graded_return_overrides(module.body, "G")
    source: str = astbuild.module_source(module.body)
    suppression: str = "  # ty: ignore[invalid-method-override]"
    marked: list[str] = [
        line.strip().removesuffix(suppression)
        for line in source.splitlines()
        if line.endswith(suppression)
    ]
    assert marked == [
        "def wedge(self, rhs) -> MultiVectorBase:",
        "def __mul__(self, rhs) -> MultiVectorBase:",
    ]
