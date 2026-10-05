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

"""``rotor_from_vectors`` -- the versor of ``versor_from_vectors``, normalized -- is a
unit rotor, and its REVERSE sandwich ``R̂ v R̂~`` is the versor's INVERSE sandwich
``R v R⁻¹`` (hence ``projection_rotation``).  The Python mirror of
``proofs/GacalcProofs/Rotor.lean``, proven *symbolically* with sympy where it can be.

The piece that needs Lagrange: ``normalize`` divides by ``sqrt(|R|²)`` with ``|R|²``
the raw polynomial ``(|a||b| + a·b)² + |a∧b|²``.  Lagrange's identity (<https://en.wikipedia.org/wiki/Lagrange%27s_identity>)
``(a·b)² + |a∧b|² = |a|²|b|²`` collapses it to ``2|a||b|(|a||b| + a·b)``, and for unit
vectors at angle θ that is ``2 + 2cos θ = 4cos²(θ/2)`` -- which is how the normalized
versor turns out to be the half-angle rotor ``cos(θ/2) - sin(θ/2)·i``.  Parametrizing by
``(c, s) = (cos(θ/2), sin(θ/2))`` with ``s² → 1 - c²`` lets sympy take that square root.
"""

import math

import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import Coef, MultiVectorBase, SymbolicSubstitution
from gacalc.functions import InvertibleFunction
from gacalc.transforms import plane_rotation, projection_rotation


def _lagrange_closed_form(a: MultiVectorBase, b: MultiVectorBase) -> Coef:
    """``2|a||b|(|a||b| + a·b)`` -- the versor's squared magnitude by Lagrange."""
    ab: Coef = a.magnitude() * b.magnitude()
    return 2 * ab * (ab + a.scalar_product(b))


def test_versor_magnitude_squared_has_the_lagrange_closed_form_2d_symbolic() -> None:
    a1: sympy.Symbol
    a2: sympy.Symbol
    b1: sympy.Symbol
    b2: sympy.Symbol
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2", real=True, positive=True)
    a: g2.Vector = a1 * g2.Vector.e_1 + a2 * g2.Vector.e_2
    b: g2.Vector = b1 * g2.Vector.e_1 + b2 * g2.Vector.e_2
    r: MultiVectorBase = g2.Vector.versor_from_vectors(from_vector=a, to_vector=b)
    assert (
        sympy.simplify(
            sympy.sympify(r.magnitude_squared()) - _lagrange_closed_form(a, b)
        )
        == 0
    )


def test_versor_magnitude_squared_has_the_lagrange_closed_form_3d_symbolic() -> None:
    syms: list[sympy.Symbol] = list(
        sympy.symbols("a1 a2 a3 b1 b2 b3", real=True, positive=True)
    )
    a: g3.Vector = (
        syms[0] * g3.Vector.e_1 + syms[1] * g3.Vector.e_2 + syms[2] * g3.Vector.e_3
    )
    b: g3.Vector = (
        syms[3] * g3.Vector.e_1 + syms[4] * g3.Vector.e_2 + syms[5] * g3.Vector.e_3
    )
    r: MultiVectorBase = g3.Vector.versor_from_vectors(from_vector=a, to_vector=b)
    assert (
        sympy.simplify(
            sympy.sympify(r.magnitude_squared()) - _lagrange_closed_form(a, b)
        )
        == 0
    )


def test_rotor_from_vectors_is_a_unit_versor_2d_symbolic() -> None:
    a1: sympy.Symbol
    a2: sympy.Symbol
    b1: sympy.Symbol
    b2: sympy.Symbol
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2", real=True, positive=True)
    a: g2.Vector = a1 * g2.Vector.e_1 + a2 * g2.Vector.e_2
    b: g2.Vector = b1 * g2.Vector.e_1 + b2 * g2.Vector.e_2
    rhat: MultiVectorBase = g2.Vector.rotor_from_vectors(from_vector=a, to_vector=b)
    assert type(rhat) is g2.Versor  # the generated narrowing: a Versor of this algebra
    assert sympy.simplify(sympy.sympify(rhat.magnitude_squared()) - 1) == 0
    assert (rhat * rhat.reverse()).symbolically_equal(
        g2.Versor(coeff_scalar=1, coeff_e_12=0)
    )  # R̂ R̂~ = 1: the inverse IS the reverse


def test_rotor_reverse_sandwich_is_versor_inverse_sandwich_2d_symbolic() -> None:
    # the bridge (Rotor.lean `rotorSandwich_normalize`): (R/|R|) v (R/|R|)~ = R v R⁻¹,
    # and both are projection_rotation -- a symbolic proof over general 2D vectors
    syms: list[sympy.Symbol] = list(
        sympy.symbols("a1 a2 b1 b2 v1 v2", real=True, positive=True)
    )
    a: g2.Vector = syms[0] * g2.Vector.e_1 + syms[1] * g2.Vector.e_2
    b: g2.Vector = syms[2] * g2.Vector.e_1 + syms[3] * g2.Vector.e_2
    v: g2.Vector = syms[4] * g2.Vector.e_1 + syms[5] * g2.Vector.e_2
    r: MultiVectorBase = g2.Vector.versor_from_vectors(from_vector=a, to_vector=b)
    rhat: MultiVectorBase = g2.Vector.rotor_from_vectors(from_vector=a, to_vector=b)
    rotor_sandwich: MultiVectorBase = rhat * v * rhat.reverse()
    assert rotor_sandwich.symbolically_equal(r * v * r.inverse())
    assert rotor_sandwich.symbolically_equal(rhat.sandwich(v))
    assert rotor_sandwich.symbolically_equal(
        projection_rotation(from_vector=a, to_vector=b)(v)
    )


def test_rotor_reverse_sandwich_is_versor_inverse_sandwich_3d() -> None:
    # 3D with concrete vectors (the magnitudes are irrational, so compare by simplify)
    a: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3
    b: g3.Vector = 4 * g3.Vector.e_1 + 5 * g3.Vector.e_2 + 6 * g3.Vector.e_3
    v: g3.Vector = 7 * g3.Vector.e_1 + 1 * g3.Vector.e_2 + 2 * g3.Vector.e_3
    r: MultiVectorBase = g3.Vector.versor_from_vectors(from_vector=a, to_vector=b)
    rhat: MultiVectorBase = g3.Vector.rotor_from_vectors(from_vector=a, to_vector=b)
    assert type(rhat) is g3.Versor
    assert sympy.simplify(sympy.sympify(rhat.magnitude_squared()) - 1) == 0
    rotor_sandwich: MultiVectorBase = rhat * v * rhat.reverse()
    assert rotor_sandwich.symbolically_equal(r * v * r.inverse())
    assert rotor_sandwich.symbolically_equal(
        projection_rotation(from_vector=a, to_vector=b)(v)
    )
    # carries a to b, scaled to |a|: R̂ a R̂~ = (|a|/|b|) b
    assert (rhat * a * rhat.reverse()).symbolically_equal(
        (a.magnitude() / b.magnitude()) * b
    )


def test_rotor_from_unit_vectors_is_the_half_angle_rotor_symbolic() -> None:
    # Parametrize the angle θ from e_1 to b by its HALF: c = cos(θ/2), s = sin(θ/2),
    # so b = cos θ e_1 + sin θ e_2 = (2c² − 1) e_1 + 2sc e_2.  The versor is
    # b·e_1 + 1 = 2c² − 2sc e_12 = 2c (c − s e_12), with |R|² = 4c²(c² + s²) = 4c²;
    # Lagrange is what makes that square root collapse: sqrt(|R|²) = 2c once sympy
    # is told s² = 1 − c².  Normalizing then gives exactly the half-angle rotor
    # c − s e_12 that transforms.plane_rotation builds -- the step the earlier
    # attempt got stuck on.
    c: sympy.Symbol
    s: sympy.Symbol
    c, s = sympy.symbols("c s", real=True, positive=True)
    pythagoras: SymbolicSubstitution = {s**2: 1 - c**2}
    a: g2.Vector = 1 * g2.Vector.e_1
    b: g2.Vector = (2 * c**2 - 1) * g2.Vector.e_1 + (2 * s * c) * g2.Vector.e_2
    r: MultiVectorBase = g2.Vector.versor_from_vectors(from_vector=a, to_vector=b)
    # |b| arrives as sqrt(4c²s² + (2c² − 1)²); it is 1 only once sympy knows
    # s² = 1 − c²
    assert r.symbolically_equal(
        g2.Versor(coeff_scalar=2 * c**2, coeff_e_12=-2 * s * c), subs=pythagoras
    )
    r_norm_sq: sympy.Expr = sympy.sympify(r.magnitude_squared()).subs(pythagoras)
    assert sympy.simplify(r_norm_sq - 4 * c**2) == 0
    rhat: MultiVectorBase = g2.Vector.rotor_from_vectors(from_vector=a, to_vector=b)
    half_angle_rotor: g2.Versor = g2.Versor(coeff_scalar=c, coeff_e_12=-s)
    assert rhat.symbolically_equal(half_angle_rotor, subs=pythagoras)


def test_rotor_from_unit_vectors_matches_plane_rotation_numerically() -> None:
    # the same identity at sample angles, against the half-angle rotor factory
    v: g2.Vector = g2.Vector(coeff_e_1=1.0, coeff_e_2=3.0)
    rotate_in_plane: InvertibleFunction[g2.Vector]
    theta: float
    for theta in (0.3, 1.0, math.radians(90), 2.5):
        b: g2.Vector = math.cos(theta) * g2.Vector.e_1 + math.sin(theta) * g2.Vector.e_2
        rhat: MultiVectorBase = g2.Vector.rotor_from_vectors(
            from_vector=1.0 * g2.Vector.e_1, to_vector=b
        )
        expected: g2.Versor = g2.Versor(
            coeff_scalar=math.cos(theta / 2), coeff_e_12=-math.sin(theta / 2)
        )
        assert rhat.isclose(expected, rel_tol=1e-9, abs_tol=1e-9)
        rotate_in_plane = plane_rotation(1.0 * g2.Vector.e_1, 1.0 * g2.Vector.e_2)(
            theta
        )
        assert (rhat * v * rhat.reverse()).isclose(
            rotate_in_plane(v), rel_tol=1e-9, abs_tol=1e-9
        )
