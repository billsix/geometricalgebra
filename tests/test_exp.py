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

"""Properties of the exponential map (``MultiVectorBase.exp``).

Representation agreement lives in test_conformance (``test_exp``); the graded
return type in test_graded (``test_exp_narrows_bivector_to_rotor``).  This file
holds the properties: the trig/hyperbolic split by grade, the
numeric-preservation contract, inverse-by-negation, the scalar-square guard,
and agreement with ``plane_rotation``'s hand-built half-angle rotor.  The
agreement tests are permanent guards: ``plane_rotation`` keeps its hand-built
rotor ON PURPOSE (a swap onto exp was measured and rejected -- see
tasks/reference/design-decisions.md), and these equalities are what let the
two constructions evolve without drifting apart.
"""

import pytest
import sympy

from gacalc.g2 import Bivector2, Rotor2, Vector2
from gacalc.g3 import Bivector3, Rotor3, Trivector3, Vector3
from gacalc.gn import Gn
from gacalc.transforms import plane_rotation


def test_exp_of_zero_is_one() -> None:
    r: Rotor2 = (0 * Bivector2.e_12).exp()
    assert r == Rotor2(coeff_scalar=1)


def test_exp_scalar() -> None:
    s: Gn = Gn.from_scalar(2)
    assert s.exp() == Gn.from_coef(sympy.exp(2))


def test_exp_float_stays_float() -> None:
    # the numeric-preservation contract (as magnitude/inverse): float
    # coefficients in, float coefficients out -- no sympy leak.
    r: Rotor2 = (0.75 * Bivector2.e_12).exp()
    assert all(isinstance(coef, float) for coef in r.to_blade_dict().values())
    assert float(r.magnitude()) == pytest.approx(1.0)


def test_exp_int_stays_exact() -> None:
    assert Bivector2.e_12.exp() == Rotor2.e_12 * sympy.sin(1) + sympy.cos(1)


def test_exp_vector_is_hyperbolic() -> None:
    # a vector squares to +|v|^2, so the series sums to cosh + sinh
    v: Vector2 = 2 * Vector2.e_1
    assert v.exp() == Vector2.e_1 * sympy.sinh(2) + sympy.cosh(2)


def test_exp_trivector_is_trig() -> None:
    # the G3 pseudoscalar squares to -1, so it exponentiates like a bivector
    # (scalar + trivector has no covering graded type, so the result is a G3)
    t: Trivector3 = Trivector3.e_123 * 2
    assert t.exp() == Trivector3.e_123 * sympy.sin(2) + sympy.cos(2)


def test_exp_inverse_is_exp_of_negation() -> None:
    b: Bivector2 = Bivector2.e_12 * sympy.Rational(1, 3)
    assert b.exp().inverse() == (-b).exp()


def test_exp_rejects_non_scalar_square() -> None:
    # a rotor (scalar + bivector) has a non-scalar square
    with pytest.raises(ValueError):
        (Rotor2.e_12 + 1).exp()
    # a NON-SIMPLE homogeneous bivector (dim >= 4, Gn only): e12 + e34
    # squares to -2 + 2 e1234, not a scalar -- the guard must catch it even
    # though the operand is homogeneous of grade 2.
    e12: Gn = Gn.from_blade_dict({(1, 2): 1})
    e34: Gn = Gn.from_blade_dict({(3, 4): 1})
    with pytest.raises(ValueError):
        (e12 + e34).exp()


def test_exp_agrees_with_plane_rotation_numeric() -> None:
    # exp((-theta/2) i) IS plane_rotation's half-angle rotor -- numeric theta
    theta: float = 1.234
    f = plane_rotation(Vector3.e_1, Vector3.e_2)(theta)
    i: Bivector3 = (Vector3.e_1 ^ Vector3.e_2).normalize()
    r: Rotor3 = (i * (-theta / 2)).exp()
    v: Vector3 = 3 * Vector3.e_1 + 4 * Vector3.e_2 + 5 * Vector3.e_3
    assert r.sandwich(v).is_close(f(v))


def test_exp_agrees_with_plane_rotation_symbolic() -> None:
    # Same identity, symbolic theta.  The symbol is declared POSITIVE on
    # purpose: exp computes |A| = sqrt(theta**2)/2, which collapses to
    # theta/2 only under a sign assumption -- for an unrestricted (complex)
    # symbol the exp-built rotor keeps the sqrt and is NOT syntactically
    # cos(theta/2).  (That limitation is WHY plane_rotation keeps its
    # hand-built rotor -- see tasks/reference/design-decisions.md.)
    theta: sympy.Symbol = sympy.Symbol("theta", positive=True)
    f = plane_rotation(Vector2.e_1, Vector2.e_2)(theta)
    i: Bivector2 = (Vector2.e_1 ^ Vector2.e_2).normalize()
    r: Rotor2 = (i * (-theta / 2)).exp()
    # identical coefficient FORM, not merely simplify-equal: the follow-up
    # swap must not change what a notebook renders.
    assert r == Rotor2.e_12 * -sympy.sin(theta / 2) + sympy.cos(theta / 2)
    x: sympy.Symbol
    y: sympy.Symbol
    x, y = sympy.symbols("x y")
    v: Vector2 = Vector2.e_1 * x + Vector2.e_2 * y
    assert r.sandwich(v) == f(v)
