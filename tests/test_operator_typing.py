"""Operators on the generated graded types type *precisely* (added 2026-07-21).

The geometric/outer/inner products and their operators used to be declared
``-> typing.Self`` and cast, so ``v2 * v2`` mistyped as ``Vector2`` though it is a
``Rotor2`` at runtime.  ``@typing.overload`` signatures now give the true type.

``typing.assert_type`` guards the STATIC types (checked by ``ty`` -- a regression
makes ``ty check tests`` fail); the runtime block guards values/runtime types under
pytest.  See ``tasks/typed-product-helper-functions.md``.
"""

import typing

from gacalc.g2 import Bivector2, Rotor2, Vector2
from gacalc.g3 import Bivector3, Rotor3, Vector3
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
