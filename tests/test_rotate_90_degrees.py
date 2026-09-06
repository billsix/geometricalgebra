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

"""The 𝒢₂ quarter turn: ``rotate_90_degrees`` IS multiplication by ``e_12``.

Two forms share one generated closed form -- the ``Vector.rotate_90_degrees()``
method and the module-level ``rotate_90_degrees()`` ``InvertibleFunction``
factory.  These pin: the pseudoscalar identity (``v * e_12``), exactness on
integer and symbolic coefficients, the +90° direction (e₁ toward e₂), the
inverse (-90°, ``v * -e_12``), composition (four turns = identity), the
``at(t)`` interpolation law, the grade/type guard, and that the feature is
𝒢₂-only (no ``rotate_90_degrees`` on 𝒢₁ or 𝒢₃).
"""

import math

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.functions import Linearity, inverse
from gacalc.g2 import Vector, e_1, e_2, e_12, rotate_90_degrees
from gacalc.transforms import plane_rotation

V: Vector = 3 * e_1 + 4 * e_2


def test_method_is_multiplication_by_the_pseudoscalar() -> None:
    assert V.rotate_90_degrees() == V * e_12


def test_method_is_exact_on_integer_coefficients() -> None:
    turned: Vector = V.rotate_90_degrees()
    assert turned == Vector(coeff_e_1=-4, coeff_e_2=3)
    assert type(turned) is Vector
    # a closed form, not a rotor: the ints come out as ints, not floats
    assert isinstance(turned.coeff_e_1, int)
    assert isinstance(turned.coeff_e_2, int)


def test_method_is_exact_on_symbolic_coefficients() -> None:
    x, y = sympy.symbols("x y")
    assert (x * e_1 + y * e_2).rotate_90_degrees() == Vector(coeff_e_1=-y, coeff_e_2=x)


def test_direction_is_e1_toward_e2() -> None:
    turn = rotate_90_degrees()
    assert turn(1 * e_1) == 1 * e_2
    assert turn(1 * e_2) == -1 * e_1
    # the same positive sense as the general-angle rotor at theta = pi/2
    assert turn(1 * e_1).isclose(
        plane_rotation(e_1, e_2)(math.pi / 2)(1 * e_1), rel_tol=1e-12, abs_tol=1e-12
    )


def test_factory_agrees_with_method_and_product() -> None:
    turn = rotate_90_degrees()
    assert turn(V) == V.rotate_90_degrees()
    assert turn(V) == V * e_12
    assert turn(V) == -4 * e_1 + 3 * e_2


def test_inverse_is_the_minus_90_turn() -> None:
    turn = rotate_90_degrees()
    assert turn.inverse(V) == V * -e_12
    assert turn.inverse(V) == Vector(coeff_e_1=4, coeff_e_2=-3)
    assert turn.inverse(turn(V)) == V
    assert inverse(turn)(turn(V)) == V
    assert turn(inverse(turn)(V)) == V


def test_composition_two_turns_is_a_half_turn_four_are_the_identity() -> None:
    turn = rotate_90_degrees()
    assert (turn @ turn)(V) == -V
    assert (turn @ turn @ turn @ turn)(V) == V
    # three turns forward equals one turn back
    assert (turn @ turn @ turn)(V) == turn.inverse(V)


def test_interpolation_law() -> None:
    turn = rotate_90_degrees()
    # the endpoints: the identity at 0, the exact turn at 1
    assert turn.at(0)(V).isclose(V, rel_tol=1e-12, abs_tol=1e-12)
    assert turn.at(1)(V) == turn(V)
    assert isinstance(turn.at(1)(V).coeff_e_1, int)
    # midway is the general-angle rotor at pi/4
    half: g2.MultiVectorBase = turn.at(0.5)(1 * e_1)
    expected = math.cos(math.pi / 4) * e_1 + math.sin(math.pi / 4) * e_2
    assert half.isclose(expected, rel_tol=1e-12, abs_tol=1e-12)


def test_metadata() -> None:
    turn = rotate_90_degrees()
    assert turn.linearity is Linearity.LINEAR
    assert turn.latex_repr == r"R_{\pi/2}"
    assert turn.latex_repr_inv == r"R_{-\pi/2}"


def test_rejects_anything_but_a_g2_vector() -> None:
    turn = rotate_90_degrees()
    with pytest.raises(TypeError, match="grade-1 Vector"):
        turn(e_12)  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match="grade-1 Vector"):
        turn(g2.Scalar.from_scalar(2))  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match="grade-1 Vector"):
        turn(g3.e_1)  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match="grade-1 Vector"):
        turn.inverse(e_12)  # ty: ignore[invalid-argument-type]


def test_is_g2_only() -> None:
    assert "rotate_90_degrees" in g2.__all__
    assert not hasattr(g1, "rotate_90_degrees")
    assert not hasattr(g3, "rotate_90_degrees")
    assert not hasattr(g1.Vector, "rotate_90_degrees")
    assert not hasattr(g3.Vector, "rotate_90_degrees")
