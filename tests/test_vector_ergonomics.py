# Copyright (c) 2026 William Emerison Six
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

"""Vector ergonomics added for coordinate-speaking consumers (mvp / ctc).

x/y/z read-only coordinate properties on the grade-1 types (the value types are
frozen/immutable), and the quotient ``A / B = A B**-1`` (division IS
multiplication by the inverse -- Bill's definition, 2026-07-09; a bare number's
inverse is its reciprocal).
See tasks/upgrade-rotation-and-ctc-vector-mapping.md (Task 2).
"""

import dataclasses

import pytest
import sympy

from gacalc.base import Coef, MultiVectorBase
from gacalc.g2 import G2, Bivector2, Rotor2, Scalar2, Vector2
from gacalc.g3 import G3, Vector3
from gacalc.gn import Gn


def test_coordinate_read() -> None:
    v: Vector2 = Vector2(3.0, 4.0)
    assert (v.x, v.y) == (3.0, 4.0)
    w: Vector3 = Vector3(1.0, 2.0, 3.0)
    assert (w.x, w.y, w.z) == (1.0, 2.0, 3.0)


def test_frozen_immutable_rebind_not_mutate() -> None:
    # The generated value types are @dataclass(frozen=True): immutable.  A direct
    # field write raises FrozenInstanceError cleanly.
    v: Vector2 = Vector2(3.0, 4.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.coeff_e_1 = 9.0  # ty: ignore[invalid-assignment]
    # The x/y/z coordinate properties are read-only; assigning is rejected.  (With
    # frozen+slots a *property* write surfaces a Python-internals TypeError rather
    # than FrozenInstanceError -- it is still blocked; see the frozen task doc.)
    with pytest.raises((dataclasses.FrozenInstanceError, TypeError, AttributeError)):
        v.x = 9.0  # ty: ignore[invalid-assignment]
    # "Changing a coordinate" means rebinding a new vector, not mutating in place.
    v = Vector2(9.0, v.y + 1.0)
    assert (v.coeff_e_1, v.coeff_e_2) == (9.0, 5.0)
    assert list(v) == [9.0, 5.0]


def test_coordinates_only_on_grade_1() -> None:
    # x on a rotor / bivector / full multivector would suggest a coordinate
    # tuple those types don't have.
    value: MultiVectorBase
    for value in (
        Rotor2(coeff_scalar=1.0, coeff_e_12=0.0),
        Bivector2.e_12,
        G2(coeff_scalar=1.0),
        Scalar2(coeff_scalar=1.0),
    ):
        assert not hasattr(value, "x")


def test_scalar_division() -> None:
    assert list(Vector2(3.0, 4.0) / 2) == [1.5, 2.0]
    assert list(Vector3(2.0, 4.0, 6.0) / 2.0) == [1.0, 2.0, 3.0]
    assert (G2(coeff_scalar=2.0, coeff_e_1=4.0) / 2).to_blade_dict() == {
        (): 1.0,
        (1,): 2.0,
    }
    assert (G3.from_scalar(6) / 2).scalar_part() == 3
    assert (Scalar2(coeff_scalar=6.0) / 2).coeff_scalar == 3.0
    assert (Gn.from_blade_dict({(1,): 3.0}) / 2).isclose(
        Gn.from_blade_dict({(1,): 1.5}), rel_tol=1e-5, abs_tol=1e-5
    )


def test_division_matches_scaling() -> None:
    v: Vector2 = Vector2(3.0, 4.0)
    assert (v / 2).isclose(v * 0.5, rel_tol=1e-5, abs_tol=1e-5)


def test_symbolic_division() -> None:
    s: Coef = sympy.Symbol("s", positive=True)
    v: Vector2 = Vector2(coeff_e_1=s, coeff_e_2=2 * s)
    got: MultiVectorBase = (v / s).simplified()
    assert got.to_blade_dict() == {(1,): 1, (2,): 2}


def test_division_is_multiplication_by_inverse() -> None:
    # the GA quotient: (a b) / b recovers a for an invertible b.
    a: Vector2 = Vector2(3.0, 4.0)
    b: Vector2 = Vector2(1.0, 2.0)
    assert ((a * b) / b).isclose(a, rel_tol=1e-5, abs_tol=1e-5)
    assert (a / b).isclose(a * b.inverse(), rel_tol=1e-5, abs_tol=1e-5)
    # v / v is 1 (a vector times its own inverse) -- as a Rotor2, the
    # smallest registered type covering the geometric product's grades.
    assert (a / a).isclose(
        Rotor2(coeff_scalar=1.0, coeff_e_12=0.0), rel_tol=1e-5, abs_tol=1e-5
    )


def test_zero_division_raises() -> None:
    with pytest.raises(ZeroDivisionError):
        Vector2(1.0, 2.0) / 0
