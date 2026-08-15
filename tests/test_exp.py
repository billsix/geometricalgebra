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
holds the properties: the rotor (trig) case and the rejection of the
positive-square (vector) case, the numeric-preservation contract,
inverse-by-negation, the scalar-square guard,
and agreement with ``plane_rotation``'s hand-built half-angle rotor.  The
agreement tests are permanent guards: ``plane_rotation`` keeps its hand-built
rotor ON PURPOSE (a swap onto exp was measured and rejected -- see
tasks/reference/design-decisions.md), and these equalities are what let the
two constructions evolve without drifting apart.
"""

import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.gn import Gn
from gacalc.transforms import plane_rotation


def test_exp_of_zero_is_one() -> None:
    r: g2.Rotor = (0 * g2.Bivector.e_12).exp()
    assert r == g2.Rotor(coeff_scalar=1)


def test_exp_scalar() -> None:
    s: Gn = Gn.from_scalar(2)
    assert s.exp() == Gn.from_coef(sympy.exp(2))


def test_exp_float_stays_float() -> None:
    # the numeric-preservation contract (as magnitude/inverse): float
    # coefficients in, float coefficients out -- no sympy leak.
    r: g2.Rotor = (0.75 * g2.Bivector.e_12).exp()
    assert all(isinstance(coef, float) for coef in r.to_blade_dict().values())
    assert float(r.magnitude()) == pytest.approx(1.0)


def test_exp_int_stays_exact() -> None:
    assert g2.Bivector.e_12.exp() == g2.Rotor.e_12 * sympy.sin(1) + sympy.cos(1)


def test_exp_of_a_vector_is_rejected() -> None:
    # a vector squares to +|v|^2 (A**2 > 0): the series would sum to the
    # hyperbolic cosh + sinh -- a Minkowski boost with no Euclidean meaning, so
    # exp rejects it rather than silently applying a spacetime formula.  (An
    # earlier version returned the hyperbolic form; it was removed.)
    v: g2.Vector = 2 * g2.Vector.e_1
    with pytest.raises(ValueError, match="A\\*\\*2 < 0"):
        v.exp()


def test_exp_trivector_is_trig() -> None:
    # the g3.G pseudoscalar squares to -1, so it exponentiates like a bivector
    # (scalar + trivector has no covering graded type, so the result is a g3.G)
    t: g3.Trivector = g3.Trivector.e_123 * 2
    assert t.exp() == g3.Trivector.e_123 * sympy.sin(2) + sympy.cos(2)


def test_exp_inverse_is_exp_of_negation() -> None:
    b: g2.Bivector = g2.Bivector.e_12 * sympy.Rational(1, 3)
    assert b.exp().inverse() == (-b).exp()


def test_exp_rejects_non_scalar_square() -> None:
    # a rotor (scalar + bivector) has a non-scalar square
    with pytest.raises(ValueError):
        (g2.Rotor.e_12 + 1).exp()
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
    f = plane_rotation(g3.Vector.e_1, g3.Vector.e_2)(theta)
    i: g3.Bivector = g3.Vector.i(g3.Vector.e_1, g3.Vector.e_2)
    r: g3.Rotor = (i * (-theta / 2)).exp()
    v: g3.Vector = 3 * g3.Vector.e_1 + 4 * g3.Vector.e_2 + 5 * g3.Vector.e_3
    assert r.sandwich(v).isclose(f(v), rel_tol=1e-5, abs_tol=1e-5)


def test_exp_agrees_with_plane_rotation_symbolic() -> None:
    # Same identity, symbolic theta.  The symbol is declared POSITIVE on
    # purpose: exp computes |A| = sqrt(theta**2)/2, which collapses to
    # theta/2 only under a sign assumption -- for an unrestricted (complex)
    # symbol the exp-built rotor keeps the sqrt and is NOT syntactically
    # cos(theta/2).  (That limitation is WHY plane_rotation keeps its
    # hand-built rotor -- see tasks/reference/design-decisions.md.)
    theta: sympy.Symbol = sympy.Symbol("theta", positive=True)
    f = plane_rotation(g2.Vector.e_1, g2.Vector.e_2)(theta)
    i: g2.Bivector = g2.Vector.i(g2.Vector.e_1, g2.Vector.e_2)
    r: g2.Rotor = (i * (-theta / 2)).exp()
    # identical coefficient FORM, not merely simplify-equal: the follow-up
    # swap must not change what a notebook renders.
    assert r == g2.Rotor.e_12 * -sympy.sin(theta / 2) + sympy.cos(theta / 2)
    x: sympy.Symbol
    y: sympy.Symbol
    x, y = sympy.symbols("x y")
    v: g2.Vector = g2.Vector.e_1 * x + g2.Vector.e_2 * y
    assert r.sandwich(v) == f(v)
