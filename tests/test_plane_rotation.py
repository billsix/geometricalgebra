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

"""plane_rotation: plane established once from two vectors, any angle after.

Covers the design recorded in
tasks/upgrade-rotation-and-ctc-vector-mapping.md (Task 1): grade-1
verification, the wedge-is-zero (parallel) error, from-a-toward-b
orientation, perpendicular-part fixedness, representation and subclass
preservation, inversion, interpolation, symbolic angles, and agreement
with the from/to rotor formulation.
"""

import math
import typing

import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import Coef, MultiVectorBase
from gacalc.gn import Gn, plane_rotation
from gacalc.transforms import (
    InvertibleFunction,
    Linearity,
    inverse,
    rotor_rotation,
)

E1: g2.Vector = g2.Vector.e_1
E2: g2.Vector = g2.Vector.e_2


def test_rotates_a_toward_b() -> None:
    # positive theta turns from a toward b: 90 degrees sends e_1 to e_2.
    f: InvertibleFunction = plane_rotation(E1, E2)(math.radians(90))
    assert f(E1).isclose(E2, rel_tol=1e-5, abs_tol=1e-5)
    # ...and argument order flips the direction.
    g: InvertibleFunction = plane_rotation(E2, E1)(math.radians(90))
    assert g(E1).isclose(-E2, rel_tol=1e-5, abs_tol=1e-5)


def test_angle_values_match_trig() -> None:
    turn: typing.Callable[[Coef], InvertibleFunction] = plane_rotation(E1, E2)
    deg: int
    for deg in (0, 30, 90, 120, 180, 240, -90):
        t: float = math.radians(deg)
        got: MultiVectorBase = turn(t)(g2.Vector(coeff_e_1=1.0, coeff_e_2=0.0))
        want: MultiVectorBase = g2.Vector(coeff_e_1=math.cos(t), coeff_e_2=math.sin(t))
        assert got.isclose(want, rel_tol=1e-5, abs_tol=1e-5), deg


def test_plane_vectors_need_not_be_unit_or_orthogonal() -> None:
    # only the plane (and its orientation) matters; the wedge is normalized.
    a: g2.Vector = g2.Vector(coeff_e_1=3.0, coeff_e_2=0.0)
    b: g2.Vector = g2.Vector(coeff_e_1=1.0, coeff_e_2=2.0)  # oriented like e_1 ^ e_2
    f: InvertibleFunction = plane_rotation(a, b)(math.radians(90))
    assert f(E1).isclose(E2, rel_tol=1e-5, abs_tol=1e-5)


def test_perpendicular_part_fixed_in_g3() -> None:
    f: InvertibleFunction = plane_rotation(g3.Vector.e_1, g3.Vector.e_2)(
        math.radians(37)
    )
    assert f(g3.Vector.e_3).isclose(g3.Vector.e_3, rel_tol=1e-5, abs_tol=1e-5)
    # a mixed vector: in-plane part turns, e_3 part rides along.
    v: g3.Vector = g3.Vector(coeff_e_1=1.0, coeff_e_2=0.0, coeff_e_3=5.0)
    got: MultiVectorBase = f(v)
    t: float = math.radians(37)
    assert got.isclose(
        g3.Vector(coeff_e_1=math.cos(t), coeff_e_2=math.sin(t), coeff_e_3=5.0),
        rel_tol=1e-5,
        abs_tol=1e-5,
    )


def test_representation_preserved() -> None:
    f2: InvertibleFunction = plane_rotation(E1, E2)(1.0)
    assert type(f2(E1)) is g2.Vector
    fn: InvertibleFunction = plane_rotation(Gn.basis_vector(1), Gn.basis_vector(2))(1.0)
    assert type(fn(Gn.basis_vector(1))) is Gn
    f3: InvertibleFunction = plane_rotation(g3.Vector.e_2, g3.Vector.e_3)(1.0)
    assert type(f3(g3.Vector.e_2)) is g3.Vector


def test_zero_rotates_to_zero() -> None:
    f: InvertibleFunction = plane_rotation(E1, E2)(1.0)
    assert f(g2.Vector.zero()).isclose(g2.Vector.zero(), rel_tol=1e-5, abs_tol=1e-5)


def test_inverse_and_composition() -> None:
    turn: typing.Callable[[Coef], InvertibleFunction] = plane_rotation(E1, E2)
    f: InvertibleFunction = turn(0.7)
    v: g2.Vector = g2.Vector(coeff_e_1=2.0, coeff_e_2=-1.0)
    assert inverse(f)(f(v)).isclose(v, rel_tol=1e-5, abs_tol=1e-5)
    assert f.linearity is Linearity.LINEAR
    # rotations in one plane add their angles.
    assert (turn(0.3) @ turn(0.4))(v).isclose(f(v), rel_tol=1e-5, abs_tol=1e-5)


def test_interpolation() -> None:
    turn: typing.Callable[[Coef], InvertibleFunction] = plane_rotation(E1, E2)
    f: InvertibleFunction = turn(math.radians(90))
    assert f.at(0.0)(E1).isclose(E1, rel_tol=1e-5, abs_tol=1e-5)
    assert f.at(0.5)(E1).isclose(turn(math.radians(45))(E1), rel_tol=1e-5, abs_tol=1e-5)
    assert f.at(1.0)(E1).isclose(f(E1), rel_tol=1e-5, abs_tol=1e-5)


def test_symbolic_theta() -> None:
    theta: Coef = sympy.Symbol("theta", real=True)
    f: InvertibleFunction = plane_rotation(E1, E2)(theta)
    got: MultiVectorBase = f(E1).simplified()
    want: dict[tuple[int, ...], Coef] = {
        (1,): sympy.cos(theta),
        (2,): sympy.sin(theta),
    }
    blade: tuple[int, ...]
    expr: Coef
    for blade, expr in want.items():
        assert (
            sympy.simplify(
                sympy.sympify(got.to_blade_dict()[blade]) - sympy.sympify(expr)
            )
            == 0
        )


def test_agrees_with_from_to_rotor_formulation() -> None:
    # rotating BY the angle between from and to, in their plane, is the
    # same rotation rotor_rotation performs.
    t: float = math.radians(40)
    to: g2.Vector = math.cos(t) * E1 + math.sin(t) * E2
    v: g2.Vector = g2.Vector(coeff_e_1=1.0, coeff_e_2=3.0)
    assert plane_rotation(E1, E2)(t)(v).isclose(
        rotor_rotation(E1, to)(v), rel_tol=1e-5, abs_tol=1e-5
    )


def test_numeric_theta_stays_numeric() -> None:
    # the sympy-leak regression (2026-07-09): the int-coefficient basis
    # constants make the unit bivector sympy-exact; a numeric theta must
    # nonetheless yield float rotors and float rotated coefficients, or
    # every downstream game/demo operation drops into sympy object math.
    f: InvertibleFunction = plane_rotation(E1, E2)(math.radians(120))
    got: g2.Vector = f(g2.Vector(coeff_e_1=1.0, coeff_e_2=0.0))
    assert type(got.coeff_e_1) is float
    assert type(got.coeff_e_2) is float


def test_symbolic_theta_stays_exact() -> None:
    # ...while a symbolic theta keeps the exact plane: cos(theta), not
    # 1.0*cos(theta).
    theta: Coef = sympy.Symbol("theta", real=True)
    got: MultiVectorBase = plane_rotation(E1, E2)(theta)(
        g2.Vector(coeff_e_1=1, coeff_e_2=0)
    ).simplified()
    assert got.to_blade_dict() == {
        (1,): sympy.cos(theta),
        (2,): sympy.sin(theta),
    }


def test_latex_label_hooks() -> None:
    turn: typing.Callable[[Coef], InvertibleFunction] = plane_rotation(
        E1,
        E2,
        latex_repr=lambda t: f"RZ_{{<{t}>}}",
        latex_repr_inv=lambda t: f"RZ_{{<{t}>}}^{{-1}}",
    )
    f: InvertibleFunction = turn(1.5)
    assert f.latex_repr == "RZ_{<1.5>}"
    assert f.latex_repr_inv == "RZ_{<1.5>}^{-1}"


def test_non_vector_operands_rejected() -> None:
    with pytest.raises(TypeError, match="grade-1"):
        plane_rotation(g2.Bivector.e_12, E2)
    with pytest.raises(TypeError, match="grade-1"):
        plane_rotation(E1, g2.G(coeff_scalar=1.0, coeff_e_1=1.0))


def test_parallel_vectors_rejected() -> None:
    with pytest.raises(ValueError, match="parallel"):
        plane_rotation(E1, 3 * E1)
    with pytest.raises(ValueError, match="parallel"):
        plane_rotation(E1, -E1)
