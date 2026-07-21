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
