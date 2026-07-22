"""Operators on the generated graded types type *precisely* (added 2026-07-21).

The geometric/outer/inner products and their operators used to be declared
``-> typing.Self`` and cast, so ``v2 * v2`` mistyped as ``Vector2`` though it is a
``Rotor2`` at runtime.  ``@typing.overload`` signatures now give the true type.

``typing.assert_type`` guards the STATIC types (checked by ``ty`` -- a regression
makes ``ty check tests`` fail); the runtime block guards values/runtime types under
pytest.  See ``tasks/typed-product-helper-functions.md``.
"""

import typing

import pytest

from gacalc.g2 import Bivector2, Rotor2, Vector2
from gacalc.g3 import G3, Bivector3, Rotor3, Trivector3, Vector3
from gacalc.scalar import Scalar


def test_operator_static_types() -> None:
    a: Vector2 = Vector2.e_1
    b: Vector2 = Vector2.e_2
    typing.assert_type(a * b, Rotor2)  # geometric: was Vector2, now honest
    typing.assert_type(a ^ b, Bivector2)  # wedge operator
    typing.assert_type(a.outer_product(b), Bivector2)
    typing.assert_type(a.inner_product(b), Scalar)
    typing.assert_type(a * 3, Vector2)  # scalar scaling preserves the type
    u: Vector3 = Vector3.e_1
    v: Vector3 = Vector3.e_2
    typing.assert_type(u * v, Rotor3)
    typing.assert_type(u ^ v, Bivector3)


def test_add_sub_narrow_by_grade() -> None:
    # scalar + bivector spans grades {0, 2} -> the even/Rotor type, in either
    # order (__add__ / __radd__) and for subtraction (__sub__ / __rsub__).
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(3 * i2 + 2, Rotor2)  # __add__ scalar arm
    typing.assert_type(2 + 3 * i2, Rotor2)  # __radd__ (number on the left)
    typing.assert_type(i2 - 2, Rotor2)  # __add__ (subtract a scalar)
    typing.assert_type(2 - i2, Rotor2)  # __rsub__
    typing.assert_type(i2 + i2, Bivector2)  # same grade stays Bivector2


def test_r_vector_part_narrows_by_grade() -> None:
    # r_vector_part(r) with a literal r types precisely to that grade's part:
    # a present grade -> that grade's type, an absent grade -> Scalar (the zero).
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    typing.assert_type(v.r_vector_part(1), Vector2)  # present grade -> itself
    typing.assert_type(v.r_vector_part(0), Scalar)  # absent grade -> Scalar(0)
    typing.assert_type(v.r_vector_part(2), Scalar)
    rotor: Rotor2 = Vector2.e_1 * Vector2.e_2  # grades {0, 2}
    typing.assert_type(rotor.r_vector_part(0), Scalar)  # scalar part
    typing.assert_type(rotor.r_vector_part(2), Bivector2)  # bivector part
    typing.assert_type(rotor.r_vector_part(1), Scalar)  # absent grade -> Scalar(0)


def test_r_vector_part_runtime_types_and_values() -> None:
    rotor: Rotor2 = 5 * Vector2.e_1 * Vector2.e_2 + 7  # 7 + 5 e_12
    assert type(rotor.r_vector_part(2)) is Bivector2
    assert rotor.r_vector_part(2).coeff_e_12 == 5
    assert type(rotor.r_vector_part(0)) is Scalar
    assert rotor.r_vector_part(0).coeff_scalar == 7
    assert type(rotor.r_vector_part(1)) is Scalar  # absent grade -> zero Scalar


def test_even_odd_part_narrow_to_resolved_grade() -> None:
    # even_part/odd_part have no argument to overload on, so the graded override
    # declares its resolved return type directly (base is -> MultiVectorBase).
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    typing.assert_type(v.odd_part(), Vector2)  # a vector is purely odd
    typing.assert_type(v.even_part(), Scalar)  # its even part is the scalar 0
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(i2.even_part(), Bivector2)  # a bivector is purely even
    typing.assert_type(i2.odd_part(), Scalar)
    rotor: Rotor2 = Vector2.e_1 * Vector2.e_2
    typing.assert_type(rotor.even_part(), Rotor2)  # grades {0, 2} are both even
    typing.assert_type(rotor.odd_part(), Scalar)


def test_even_odd_part_runtime_types() -> None:
    i2: Bivector2 = 5 * (Vector2.e_1 ^ Vector2.e_2)
    assert type(i2.even_part()) is Bivector2
    assert i2.even_part().coeff_e_12 == 5
    assert type(i2.odd_part()) is Scalar
    assert type((3 * Vector2.e_1).even_part()) is Scalar  # vector has no even part


def test_contraction_static_types() -> None:
    # left/right contraction resolve their grade like the other products:
    # left keeps grade m-k (right-left), right keeps k-m; a negative grade -> Scalar.
    a: Vector2 = Vector2.e_1
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(a.left_contraction(a), Scalar)  # vector ⌋ vector = dot (grade 0)
    typing.assert_type(a.left_contraction(i2), Vector2)  # vector ⌋ bivector (grade 1)
    typing.assert_type(i2.left_contraction(a), Scalar)  # bivector ⌋ vector -> 0
    typing.assert_type(i2.right_contraction(a), Vector2)  # bivector ⌊ vector (grade 1)
    typing.assert_type(a.right_contraction(i2), Scalar)  # vector ⌊ bivector -> 0
    # the < / > operators carry the same precise overloads
    typing.assert_type(a < a, Scalar)
    typing.assert_type(a < i2, Vector2)
    typing.assert_type(i2 > a, Vector2)


def test_contraction_runtime_types_and_values() -> None:
    a: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    i2: Bivector2 = 5 * (Vector2.e_1 ^ Vector2.e_2)
    # vector ⌋ vector is the dot product: 3*3 + 4*4 = 25
    assert type(a.left_contraction(a)) is Scalar
    assert a.left_contraction(a).coeff_scalar == 25
    assert (a < a).coeff_scalar == 25  # operator agrees
    # e_1 ⌋ (5 e_12) = 5 e_2 ;  contraction asymmetry: (5 e_12) ⌋ e_1 == 0
    assert type(Vector2.e_1.left_contraction(i2)) is Vector2
    assert Vector2.e_1.left_contraction(i2).coeff_e_2 == 5
    assert type(i2.left_contraction(Vector2.e_1)) is Scalar  # grade -1 -> Scalar(0)
    assert (i2 > Vector2.e_1).coeff_e_2 == -5  # bivector ⌊ vector = -5 e_2


def test_dual_narrows_by_grade() -> None:
    # dual has no argument to overload on (its grade n−r is fixed by the operand
    # grade + dimension), so like even/odd_part the graded override *declares*
    # the resolved grade type -- no unsound Self cast.
    v3: Vector3 = 3.0 * Vector3.e_1
    typing.assert_type(v3.dual(), Bivector3)  # grade 1 -> grade 2 in 3D
    i3: Bivector3 = 5.0 * Bivector3.e_23
    typing.assert_type(i3.dual(), Vector3)  # grade 2 -> grade 1 in 3D
    t3: Trivector3 = 7.0 * Trivector3.e_123
    typing.assert_type(t3.dual(), Scalar)  # grade 3 -> grade 0
    r3: Rotor3 = 1 + 2.0 * Bivector3.e_12
    typing.assert_type(r3.dual(), G3)  # {0,2} -> {3,1} = odd, no covering type

    # 2D duals: grade n−r with n=2.
    v2: Vector2 = 3 * Vector2.e_1
    typing.assert_type(v2.dual(), Vector2)  # grade 1 -> grade 1
    i2: Bivector2 = 5 * Bivector2.e_12
    typing.assert_type(i2.dual(), Scalar)  # grade 2 -> grade 0
    rotor2: Rotor2 = 1 + 2 * Bivector2.e_12
    typing.assert_type(rotor2.dual(), Rotor2)  # {0,2} -> {2,0} = {0,2}


def test_dual_runtime_types_and_values() -> None:
    # e_23* = e_1 (Bivector3.dual really returns a Vector3 -- the whole point).
    n: Vector3 = Bivector3.e_23.dual()
    assert type(n) is Vector3
    assert n.coeff_e_1 == 1
    assert type(Trivector3.e_123.dual()) is Scalar
    assert Trivector3.e_123.dual().coeff_scalar == 1
    assert type(Bivector2.e_12.dual()) is Scalar
    # a fixed-dimension type's dual is at its own dimension: a mismatched n raises.
    with pytest.raises(ValueError, match="fixed at dimension 3"):
        Bivector3.e_23.dual(2)
    Bivector3.e_23.dual(3)  # the dimension itself is fine


def test_operator_runtime_types_and_values() -> None:
    a: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    b: Vector2 = Vector2.e_1 + 2 * Vector2.e_2
    # the runtime type has always been correct; here we pin it next to the static one
    assert type(a * b) is Rotor2
    assert type(a ^ b) is Bivector2
    assert type(a.inner_product(b)) is Scalar
    assert type(a * 3) is Vector2
    # value equals the wedge coefficient e_1 e_2:  3*2 - 4*1 = 2
    assert (a ^ b).coeff_e_12 == 2
    # and the geometric product carries both scalar and bivector parts
    product: Rotor2 = a * b
    assert product.coeff_scalar == 11  # 3*1 + 4*2
    assert product.coeff_e_12 == 2
