# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

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


def test_blade_label_special_cases():
    assert gen.blade_label(()) == "scalar"
    assert gen.blade_label((1,)) == "e_1"
    assert gen.blade_label((1, 2)) == "e_12"
    assert gen.blade_label((1, 2, 3)) == "e_123"


def test_blade_label_roundtrips_over_all_blades():
    for n in (1, 2, 3):
        for blade in gen.blades_for_dim(n):
            assert gen.blade_of_label(gen.blade_label(blade)) == blade


def test_field_name_is_coeff_prefixed():
    assert gen.field_name(()) == "coeff_scalar"
    assert gen.field_name((1,)) == "coeff_e_1"
    assert gen.field_name((1, 2)) == "coeff_e_12"


# --------------------------------------------------------------------------
# Canonical blade ordering
# --------------------------------------------------------------------------


def test_blades_for_dim_canonical_order():
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


def test_blades_for_dim_is_grade_then_index():
    blades = gen.blades_for_dim(3)
    assert blades == sorted(blades, key=lambda b: (len(b), b))
    assert len(blades) == 2**3


# --------------------------------------------------------------------------
# term_grade_key -- orders generated sums scalar -> vector -> bivector -> ...
# --------------------------------------------------------------------------


def test_term_grade_key_orders_lower_grade_first():
    key_vec = gen.term_grade_key(sympy.Symbol("a_e_2"))  # grade 1
    key_biv = gen.term_grade_key(sympy.Symbol("a_e_12"))  # grade 2
    assert key_vec < key_biv
    assert key_vec[0] == 1 and key_biv[0] == 2


def test_term_grade_key_uses_both_operands():
    # a product of one self (a_) and one rhs (b_) symbol keys on both grades
    key = gen.term_grade_key(sympy.Symbol("a_e_1") * sympy.Symbol("b_e_2"))
    assert key == (1, (1,), 1, (2,))


# --------------------------------------------------------------------------
# Subscript / superscript helpers (used in generated docstrings)
# --------------------------------------------------------------------------


def test_subscript_superscript():
    assert gen._subscript(0) == "₀"
    assert gen._subscript(12) == "₁₂"
    assert gen._superscript(3) == "³"
    assert gen._superscript(10) == "¹⁰"


# --------------------------------------------------------------------------
# Type registry and resolution -- "the type follows the operation"
# --------------------------------------------------------------------------


def test_registry_for_dim_lists_graded_then_full():
    names = [s.name for s in gen.registry_for_dim(2, "G2")]
    assert names == ["Scalar", "Vector2", "Bivector2", "Rotor2", "G2"]


def test_resolve_smallest_covering_type():
    assert gen.resolve([()], 2, "G2").name == "Scalar"
    assert gen.resolve([(1,), (2,)], 2, "G2").name == "Vector2"
    assert gen.resolve([(1, 2)], 2, "G2").name == "Bivector2"
    assert gen.resolve([(), (1, 2)], 2, "G2").name == "Rotor2"


def test_resolve_widens_to_full_when_no_graded_type_covers():
    # a vector + bivector support spans no single graded type -> the full G_n
    assert gen.resolve([(1,), (1, 2)], 2, "G2").name == "G2"


# --------------------------------------------------------------------------
# product_result / unary_result -- gen-time result-type determination
# --------------------------------------------------------------------------


def _spec(n, name):
    by_name = {s.name: s for s in [gen.full_spec(n, f"G{n}"), *gen.graded_specs(n)]}
    return by_name[name]


def test_product_result_geometric_vector_times_vector_is_rotor():
    v2 = _spec(2, "Vector2")
    result_spec, _ = gen.product_result(v2, v2, lambda a, b: a * b, 2, "G2")
    assert result_spec.name == "Rotor2"


def test_product_result_outer_vector_wedge_vector_is_bivector():
    v2 = _spec(2, "Vector2")
    result_spec, _ = gen.product_result(
        v2, v2, lambda a, b: a.outer_product(b), 2, "G2"
    )
    assert result_spec.name == "Bivector2"


def test_product_result_bivector_times_bivector_is_scalar():
    b2 = _spec(2, "Bivector2")
    result_spec, _ = gen.product_result(b2, b2, lambda a, b: a * b, 2, "G2")
    assert result_spec.name == "Scalar"


def test_unary_result_reverse_preserves_grade():
    v2 = _spec(2, "Vector2")
    result_spec, _ = gen.unary_result(v2, lambda a: a.reverse(), 2, "G2")
    assert result_spec.name == "Vector2"


def test_unary_result_dual_of_vector3_is_bivector3():
    v3 = _spec(3, "Vector3")
    result_spec, _ = gen.unary_result(v3, lambda a: a.dual(3), 3, "G3")
    assert result_spec.name == "Bivector3"


# --------------------------------------------------------------------------
# astbuild DSL invariants
# --------------------------------------------------------------------------


def test_module_source_roundtrip():
    src = astbuild.module_source([ast.Expr(astbuild.dot("self", "e_1"))])
    assert src == "self.e_1"


def test_symbol_to_attr_rewrites_operand_symbols():
    tree = astbuild.parse_expr("a_e_1 + b_e_2")
    rename = {"a_e_1": ("self", "e_1"), "b_e_2": ("rhs", "e_2")}
    out = ast.fix_missing_locations(astbuild.SymbolToAttr(rename).visit(tree))
    assert ast.unparse(out) == "self.e_1 + rhs.e_2"


def test_cast_coef_skips_bare_and_negated_fields():
    bare = astbuild.dot("self", "coeff_e_1")
    assert astbuild.cast_coef(bare) is bare
    negated = ast.UnaryOp(ast.USub(), astbuild.dot("self", "coeff_e_1"))
    assert astbuild.cast_coef(negated) is negated


def test_cast_coef_wraps_compound_expression():
    compound = ast.BinOp(astbuild.nm("a"), ast.Add(), astbuild.nm("b"))
    wrapped = astbuild.cast_coef(compound)
    assert ast.unparse(wrapped) == "typing.cast(Coef, a + b)"
