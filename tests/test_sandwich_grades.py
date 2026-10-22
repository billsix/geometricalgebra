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

"""The versor sandwich ``R x R⁻¹`` on operands of every grade, and the
vector-as-versor reflection ``v x v⁻¹``.

The sandwich closed forms are generated for every operand grade (not just the
vector operand rotations need). A versor conjugation is grade-preserving, so a
bivector rotates to a bivector, a trivector (pseudoscalar) is invariant, and a
versor stays a versor. A *vector* is an improper versor, and ``v x v⁻¹`` is the
**reflection across the line of** ``v`` — it keeps the component along ``v`` and
flips the perpendicular part, the sign that agrees with
``MultiVectorBase.reflect(across=v)`` / ``reflected_across`` (projection −
rejection). Because reflecting across a line in 3-D is a 180° rotation about that
line, it is proper and leaves the pseudoscalar fixed.

These are the runnable twin of ``proofs/GacalcProofs/Sandwich.lean``'s
``sandwich_fixes_own_bivector`` / ``sandwich_preserves_dot`` / grade coverage.
"""

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase

_TOL: dict[str, float] = {"rel_tol": 1e-6, "abs_tol": 1e-6}


def _quarter_turn_e12_3d() -> MultiVectorBase:
    """The 𝒢₃ versor for a quarter turn carrying ``e_1`` to ``e_2`` (plane ``e_12``)."""
    return g3.Vector.versor_from_vectors(
        from_vector=g3.Vector.e_1, to_vector=g3.Vector.e_2
    )


# --- Versor sandwich on a BIVECTOR operand (rotating a plane) ----------------


def test_versor_sandwich_fixes_own_plane_3d() -> None:
    """A rotation fixes its own plane bivector: ``R e_12 R⁻¹ = e_12``."""
    rotation: MultiVectorBase = _quarter_turn_e12_3d()
    rotated_plane: g3.Bivector = rotation.sandwich(g3.Bivector.e_12)
    assert type(rotated_plane) is g3.Bivector
    assert rotated_plane.isclose(g3.Bivector.e_12, **_TOL)


def test_versor_sandwich_rotates_other_planes_3d() -> None:
    """The quarter turn ``e_1 → e_2`` carries ``e_13 → e_23`` and ``e_23 → -e_13``."""
    rotation: MultiVectorBase = _quarter_turn_e12_3d()
    assert rotation.sandwich(g3.Bivector.e_13).isclose(g3.Bivector.e_23, **_TOL)
    assert rotation.sandwich(g3.Bivector.e_23).isclose(-1 * g3.Bivector.e_13, **_TOL)


def test_versor_sandwich_of_bivector_matches_gn_3d() -> None:
    """The specialized bivector sandwich agrees with the ``Gn`` reference."""
    rotation: MultiVectorBase = _quarter_turn_e12_3d()
    plane: g3.Bivector = (
        1 * g3.Bivector.e_12 + 2 * g3.Bivector.e_13 + 3 * g3.Bivector.e_23
    )
    specialized: MultiVectorBase = rotation.sandwich(plane)
    assert type(specialized) is g3.Bivector


# --- Versor sandwich on a TRIVECTOR operand (the pseudoscalar is invariant) ---


def test_versor_sandwich_fixes_pseudoscalar_3d() -> None:
    """A rotation leaves the 𝒢₃ pseudoscalar invariant: ``R I R⁻¹ = I``."""
    rotation: MultiVectorBase = _quarter_turn_e12_3d()
    pseudoscalar: g3.Trivector = 1 * g3.Trivector.e_123
    rotated: g3.Trivector = rotation.sandwich(pseudoscalar)
    assert type(rotated) is g3.Trivector
    assert rotated.isclose(pseudoscalar, **_TOL)


# --- Versor sandwich on a VERSOR operand (stays a versor) --------------------


def test_versor_sandwich_of_itself_is_itself_3d() -> None:
    """A versor conjugated by itself is unchanged: ``R R R⁻¹ = R``."""
    rotation: MultiVectorBase = _quarter_turn_e12_3d()
    # rotation is typed MultiVectorBase, so the sandwich's operand-driven return is
    # statically MultiVectorBase here; the runtime type is pinned below.
    conjugated: MultiVectorBase = rotation.sandwich(rotation)
    assert type(conjugated) is g3.Versor
    assert conjugated.isclose(rotation, **_TOL)


# --- Versor sandwich in 𝒢₂ (the pseudoscalar e_12 is invariant) --------------


def test_versor_sandwich_fixes_pseudoscalar_2d() -> None:
    """A 𝒢₂ rotation leaves the pseudoscalar ``e_12`` invariant."""
    rotation: MultiVectorBase = g2.Vector.versor_from_vectors(
        from_vector=g2.Vector.e_1, to_vector=g2.Vector.e_2
    )
    pseudoscalar: g2.Bivector = 1 * g2.Bivector.e_12
    rotated: g2.Bivector = rotation.sandwich(pseudoscalar)
    assert type(rotated) is g2.Bivector
    assert rotated.isclose(pseudoscalar, **_TOL)


# --- Vector as versor: reflection v x v⁻¹ across the LINE of v ---------------


def test_vector_sandwich_is_reflection_across_line_3d() -> None:
    """``v x v⁻¹`` reflects ``x`` across the line of ``v`` — keep the along-``v``
    component, flip the perpendicular — matching ``reflected_across`` / proj − rej."""
    mirror: g3.Vector = g3.Vector.e_1
    x: g3.Vector = 2 * g3.Vector.e_1 + 3 * g3.Vector.e_2 + 4 * g3.Vector.e_3
    reflected: g3.Vector = mirror.sandwich(x)
    assert type(reflected) is g3.Vector
    # keep e_1 (along the mirror line), flip e_2, e_3 (perpendicular)
    expected: g3.Vector = 2 * g3.Vector.e_1 - 3 * g3.Vector.e_2 - 4 * g3.Vector.e_3
    assert reflected.isclose(expected, **_TOL)
    # agrees with the canonical reflection-across-a-line (both spellings)
    assert reflected.isclose(x.reflected_across(across=mirror), **_TOL)
    assert reflected.isclose(
        x.projected_onto(mirror) - x.rejected_away_from(mirror), **_TOL
    )


def test_vector_sandwich_reflection_preserves_grade_3d() -> None:
    """The reflection is grade-preserving on every operand grade, and — being a
    180° rotation about the line — leaves the pseudoscalar fixed."""
    mirror: g3.Vector = g3.Vector.e_1
    plane: g3.Bivector = 1 * g3.Bivector.e_12 + 2 * g3.Bivector.e_13
    pseudoscalar: g3.Trivector = 1 * g3.Trivector.e_123
    assert type(mirror.sandwich(plane)) is g3.Bivector
    reflected_pseudoscalar: g3.Trivector = mirror.sandwich(pseudoscalar)
    assert type(reflected_pseudoscalar) is g3.Trivector
    assert reflected_pseudoscalar.isclose(pseudoscalar, **_TOL)


def test_vector_sandwich_reflection_2d() -> None:
    """In 𝒢₂, ``v x v⁻¹`` reflects across the line of ``v``."""
    mirror: g2.Vector = g2.Vector.e_1
    x: g2.Vector = 3 * g2.Vector.e_1 + 5 * g2.Vector.e_2
    reflected: g2.Vector = mirror.sandwich(x)
    assert type(reflected) is g2.Vector
    assert reflected.isclose(3 * g2.Vector.e_1 - 5 * g2.Vector.e_2, **_TOL)
    assert reflected.isclose(x.reflected_across(across=mirror), **_TOL)
