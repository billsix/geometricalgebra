"""The ``Odd_3`` graded type (the odd part {1,3} of 𝒢₃) and its opt-in cast API.

``typing.assert_type`` pins the STATIC types (checked by ``ty`` -- a regression fails
``ty check tests``); the runtime types/values are checked with plain asserts.

The three geometric cases are built the **dual-of-wedge** way: for a plane ``B = a ^ b``,
``(a ^ b).dual()`` is a vector **perpendicular** to the plane (the cross-product
direction), ``a`` is **in** the plane, and ``a + perp`` **mixes** both -- so ``B * <that>``
lands in grade 1, grade 3, or {1,3} respectively.  Background:
``tasks/reference/graded-subspaces-vs-subalgebras.md``, ``tasks/model-odd-graded-type.md``.
"""

import typing

import pytest
import sympy

import gacalc.g3 as g3

# A non-axis-aligned plane B = a ^ b, and the three operand vectors.
_a: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2
_b: g3.Vector = 3 * g3.Vector.e_1 + 1 * g3.Vector.e_2 + 1 * g3.Vector.e_3
_B: g3.Bivector = _a ^ _b  # the plane bivector
_perp: g3.Vector = (_a ^ _b).dual()  # dual of the wedge: perpendicular to the plane
_in_plane: g3.Vector = _a  # lies in the plane
_mixed: g3.Vector = _a + _perp  # in-plane + perpendicular


def test_odd3_product_types_static() -> None:
    # Vector * Bivector spans the odd part {1,3} -> Odd_3 (was G3 before Odd_3 existed).
    typing.assert_type(g3.Vector.e_1 * g3.Bivector.e_12, g3.Odd_3)
    typing.assert_type(g3.Bivector.e_12 * g3.Vector.e_1, g3.Odd_3)
    rotor: g3.Rotor = g3.Vector.e_1 * g3.Vector.e_2
    typing.assert_type(rotor * g3.Vector.e_1, g3.Odd_3)
    typing.assert_type(rotor * g3.Trivector.e_123, g3.Odd_3)
    # odd * odd = even -> Rotor: Odd_3 is a SUBSPACE, not a subalgebra.
    odd: g3.Odd_3 = g3.Bivector.e_12 * g3.Vector.e_1
    typing.assert_type(odd * odd, g3.Rotor)


def test_odd3_product_types_runtime() -> None:
    assert type(g3.Vector.e_1 * g3.Bivector.e_12) is g3.Odd_3
    odd = g3.Bivector.e_12 * g3.Vector.e_1
    assert type(odd * odd) is g3.Rotor  # odd * odd = even


def test_cast_in_plane_is_vector() -> None:
    r = _B * _in_plane
    assert type(r) is g3.Odd_3 and r.grades() == [1]
    typing.assert_type(r.to_vector(), g3.Vector)
    v = r.to_vector()
    assert type(v) is g3.Vector
    assert (v.coeff_e_1, v.coeff_e_2, v.coeff_e_3) == (
        r.coeff_e_1, r.coeff_e_2, r.coeff_e_3,
    )
    with pytest.raises(ValueError):
        r.to_trivector()


def test_cast_perpendicular_is_trivector() -> None:
    r = _B * _perp
    assert type(r) is g3.Odd_3 and r.grades() == [3]
    typing.assert_type(r.to_trivector(), g3.Trivector)
    t = r.to_trivector()
    assert type(t) is g3.Trivector
    assert t.coeff_e_123 == r.coeff_e_123
    with pytest.raises(ValueError):
        r.to_vector()


def test_cast_mixed_raises_both() -> None:
    r = _B * _mixed
    assert type(r) is g3.Odd_3 and r.grades() == [1, 3]
    with pytest.raises(ValueError):
        r.to_vector()
    with pytest.raises(ValueError):
        r.to_trivector()


def test_query_predicates() -> None:
    # the "query" half of query+cast is the inherited is_vector/is_trivector/grades
    assert (_B * _in_plane).is_vector()
    assert not (_B * _in_plane).is_trivector()
    assert (_B * _perp).is_trivector()
    assert not (_B * _perp).is_vector()
    assert not (_B * _mixed).is_vector()
    assert not (_B * _mixed).is_trivector()


def test_sandwich_result_is_odd3_static() -> None:
    # The rotor sandwich R v R⁻¹ as PLAIN products (not the derived sandwich() op)
    # types as Odd_3: Rotor*Vector = Odd_3, then Odd_3*Rotor = Odd_3.
    rotor: g3.Rotor = g3.Vector.e_1 * g3.Vector.e_2
    typing.assert_type(rotor * g3.Vector.e_1 * rotor.inverse(), g3.Odd_3)


def test_sandwich_grade_preservation_is_one_coefficient() -> None:
    """Odd_3 makes rotor-sandwich grade-preservation a ONE-coefficient proof.

    ``R v R⁻¹`` (as plain products) types as ``Odd_3`` -- support {1,3} -- so proving
    it is a vector reduces to showing its single grade-3 coefficient vanishes, rather
    than clearing the several non-grade-1 parts of the old ``G3`` form.  It holds for a
    GENERAL symbolic rotor, not just a unit one (the versor is grade-preserving).
    """
    a, b, c, d = sympy.symbols("a b c d", real=True)
    x, y, z = sympy.symbols("x y z", real=True)
    rotor = a + b * g3.Bivector.e_12 + c * g3.Bivector.e_13 + d * g3.Bivector.e_23
    v = x * g3.Vector.e_1 + y * g3.Vector.e_2 + z * g3.Vector.e_3
    conjugated = rotor * v * rotor.inverse()
    assert type(conjugated) is g3.Odd_3  # a named type now, not G3
    assert sympy.simplify(conjugated.coeff_e_123) == 0  # grade-3 vanishes -> a vector
