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

"""bivector_rotation: the bivector-first (`i`-first) sibling of plane_rotation.

Covers subtask 2 of tasks/archive/2026/08/15/redo-exp-book-referenced.md: take
the plane's bivector directly, normalize it internally, and return angle ->
half-angle rotor sandwich.  Checks agreement with plane_rotation on the same
plane, the internal normalization (a non-unit bivector rotates by the right
angle), grade-2 / zero validation, orientation, perpendicular-part fixedness,
inversion, interpolation, and that a symbolic angle keeps the clean
cos(theta/2) form (the reason it is built directly, not via exp).
"""

import math

import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.transforms import bivector_rotation, plane_rotation

_TOL: dict[str, float] = {"rel_tol": 1e-9, "abs_tol": 1e-9}


def test_agrees_with_plane_rotation_on_the_same_plane() -> None:
    # bivector_rotation(i(a, b)) is the same rotation as plane_rotation(a, b).
    i = g3.Vector.i(g3.Vector.e_1, g3.Vector.e_2)
    by_bivector = bivector_rotation(i)(math.radians(50))
    by_vectors = plane_rotation(g3.Vector.e_1, g3.Vector.e_2)(math.radians(50))
    v = 3 * g3.Vector.e_1 + 4 * g3.Vector.e_2 + 5 * g3.Vector.e_3
    assert by_bivector(v).isclose(by_vectors(v), **_TOL)


def test_quarter_turn_maps_e1_to_e2_and_fixes_perpendicular() -> None:
    turn = bivector_rotation(g3.Vector.i(g3.Vector.e_1, g3.Vector.e_2))
    quarter = turn(math.radians(90))
    assert quarter(g3.Vector.e_1).isclose(g3.Vector.e_2, rel_tol=1e-6, abs_tol=1e-6)
    # e_3 is perpendicular to the e_1 e_2 plane -> left fixed.
    assert quarter(g3.Vector.e_3).isclose(g3.Vector.e_3, rel_tol=1e-6, abs_tol=1e-6)


def test_normalizes_the_bivector_internally() -> None:
    # A bivector scaled off unit length must still rotate by the given angle:
    # the builder normalizes it, so the magnitude does not leak into the angle.
    i = g3.Vector.i(g3.Vector.e_1, g3.Vector.e_2)
    unit_result = bivector_rotation(i)(math.radians(30))
    scaled_result = bivector_rotation(5 * i)(math.radians(30))
    v = 2 * g3.Vector.e_1 + g3.Vector.e_3
    assert scaled_result(v).isclose(unit_result(v), **_TOL)


def test_inverse_undoes_the_rotation() -> None:
    f = bivector_rotation(g3.Vector.i(g3.Vector.e_1, g3.Vector.e_3))(1.1)
    v = 7 * g3.Vector.e_1 + 2 * g3.Vector.e_2 - g3.Vector.e_3
    assert f.inverse(f(v)).isclose(v, rel_tol=1e-6, abs_tol=1e-6)


def test_interpolation_is_a_fraction_of_the_angle() -> None:
    turn = bivector_rotation(g3.Vector.i(g3.Vector.e_1, g3.Vector.e_2))
    half = turn(math.radians(80)).at(0.5)
    direct = turn(math.radians(40))
    v = g3.Vector.e_1 + g3.Vector.e_2 + g3.Vector.e_3
    assert half(v).isclose(direct(v), **_TOL)


def test_symbolic_angle_keeps_clean_half_angle_form() -> None:
    # The whole reason it is built directly (cos(theta/2) - sin(theta/2) i) and
    # NOT via exp: a symbolic angle must render cos(theta/2), never
    # cos(sqrt(theta**2)/2).  Same guarantee plane_rotation gives.
    theta: sympy.Symbol = sympy.Symbol("theta", positive=True)
    i = g2.Vector.i(g2.Vector.e_1, g2.Vector.e_2)
    rotor = bivector_rotation(i)(theta)
    # apply to e_1 and read the coefficient forms back
    rotated = rotor(g2.Vector.e_1)
    expected = sympy.cos(theta) * g2.Vector.e_1 + sympy.sin(theta) * g2.Vector.e_2
    assert rotated == expected


def test_rejects_a_non_bivector() -> None:
    with pytest.raises(TypeError, match="grade-2"):
        bivector_rotation(g3.Vector.e_1)  # a vector, not a bivector


def test_rejects_the_zero_bivector() -> None:
    with pytest.raises(ValueError, match="zero"):
        bivector_rotation(g3.Bivector.zero())
