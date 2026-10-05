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

"""Extracting ``r``, ``I``, ``θ`` and the conjugate from a versor ``R = r (cos θ + I
sin θ)``
(Macdonald): ``r = R.magnitude()``, ``I = R.plane_of_rotation()``, ``θ = R.angle()``,
``R̄ = R.conjugate()``.  Works on the generated algebras and on ``Gn``, normalized or
not."""

import math

import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
import gacalc.gn as gn
from gacalc.base import MultiVectorBase
from gacalc.gn import Gn


@pytest.mark.parametrize("theta", [0.3, 1.0, math.radians(90), 2.5])
def test_product_of_two_vectors_yields_their_angle_scale_and_plane(
    theta: float,
) -> None:
    u: g2.Vector = 2.0 * g2.Vector.e_1
    v: g2.Vector = 3.0 * (
        math.cos(theta) * g2.Vector.e_1 + math.sin(theta) * g2.Vector.e_2
    )
    r: MultiVectorBase = u * v  # an un-normalized versor: r = |u||v| = 6
    assert math.isclose(r.angle(), theta, rel_tol=1e-12)
    assert math.isclose(r.magnitude(), 6.0, rel_tol=1e-12)
    assert r.plane_of_rotation().isclose(
        1.0 * g2.Bivector.e_12, rel_tol=1e-12, abs_tol=1e-12
    )


def test_versor_reconstructs_from_r_i_theta_numeric() -> None:
    u: g3.Vector = 1.0 * g3.Vector.e_1 + 2.0 * g3.Vector.e_2 + 3.0 * g3.Vector.e_3
    v: g3.Vector = 4.0 * g3.Vector.e_1 + 5.0 * g3.Vector.e_2 + 6.0 * g3.Vector.e_3
    r: MultiVectorBase = u * v
    rebuilt: MultiVectorBase = r.magnitude() * (
        math.cos(r.angle()) + math.sin(r.angle()) * r.plane_of_rotation()
    )
    assert rebuilt.isclose(r, rel_tol=1e-9, abs_tol=1e-9)


def test_versor_reconstructs_from_r_i_theta_symbolic() -> None:
    # R = c + s·I with c, s positive symbols (first quadrant, so sympy can take
    # s/|s| = 1 and cos(atan2(s, c)) = c/sqrt(c² + s²)): the three factors read
    # back and rebuild R symbolically.
    c: sympy.Symbol
    s: sympy.Symbol
    c, s = sympy.symbols("c s", positive=True)
    plane: g2.Bivector = 1 * g2.Bivector.e_12
    versor: MultiVectorBase = c + s * plane
    magnitude: sympy.Expr = sympy.sympify(versor.magnitude())
    assert sympy.simplify(magnitude - sympy.sqrt(c**2 + s**2)) == 0
    assert versor.plane_of_rotation().symbolically_equal(plane)
    angle: sympy.Expr = sympy.sympify(versor.angle())
    assert sympy.simplify(angle - sympy.atan2(s, c)) == 0
    rebuilt: MultiVectorBase = versor.magnitude() * (
        sympy.cos(versor.angle())
        + sympy.sin(versor.angle()) * versor.plane_of_rotation()
    )
    assert rebuilt.symbolically_equal(versor)


def test_angle_is_half_the_rotation_angle_of_the_half_angle_rotor() -> None:
    phi: float = 1.2
    rotor: MultiVectorBase = g2.Vector.rotor_from_vectors(
        1.0 * g2.Vector.e_1,
        math.cos(phi) * g2.Vector.e_1 + math.sin(phi) * g2.Vector.e_2,
    )
    assert math.isclose(rotor.angle(), phi / 2, rel_tol=1e-12)
    assert math.isclose(rotor.magnitude(), 1.0, rel_tol=1e-12)


def test_conjugate_is_the_reverse_and_multiplies_to_magnitude_squared() -> None:
    r: MultiVectorBase = (1.0 * g3.Vector.e_1 + 2.0 * g3.Vector.e_3) * (
        3.0 * g3.Vector.e_2 + 1.0 * g3.Vector.e_1
    )
    assert r.conjugate() == r.reverse()
    product: MultiVectorBase = r * r.conjugate()
    assert product.is_scalar()
    assert math.isclose(product.scalar_part(), r.magnitude_squared(), rel_tol=1e-12)


def test_works_on_gn() -> None:
    theta: float = 0.7
    u: Gn = 1.0 * gn.e_1
    v: Gn = math.cos(theta) * gn.e_1 + math.sin(theta) * gn.e_2
    r: Gn = u * v
    assert math.isclose(r.angle(), theta, rel_tol=1e-12)
    assert r.plane_of_rotation().isclose(
        1.0 * (gn.e_1 ^ gn.e_2), rel_tol=1e-12, abs_tol=1e-12
    )
    assert r.conjugate() == r.reverse()


def test_angle_and_conjugate_reject_non_versors() -> None:
    with pytest.raises(ValueError):
        (1.0 * g3.Vector.e_1 + 2.0 * g3.Bivector.e_12).angle()
    with pytest.raises(ValueError):
        (1.0 * g3.G.e_123 + 1.0).conjugate()
