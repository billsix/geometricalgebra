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

"""Standard-position (frame-reduction) project/reject (``gacalc.standardposition``).

The ``project_sp`` / ``reject_sp`` rotate ``b`` onto the ``e_1`` axis with elementary
plane rotations, project/reject there, and rotate back.  These tests are the runnable
twin of the Lean equivariance/alignment proofs
(``proofs/GacalcProofs/StandardPosition.lean``: ``proj_rotXY_equivariant`` /
``proj_rotXZ_equivariant`` / ``rotate_b_to_e1``): they assert the standard-position
result equals the canonical Hestenes ``projected_onto`` / ``rejected_away_from``,
numerically and symbolically.  See the reference doc
``tasks/reference/reduction-to-standard-position.md``.
"""

import numpy as np
import sympy

from gacalc.g3 import Vector, e_1, e_2, e_3
from gacalc.standardposition import project_sp, reject_sp


def _coords(v: Vector) -> np.ndarray:
    # iteration yields the coefficient values in blade order = the coordinates
    return np.array(list(v), dtype=float)


def test_project_sp_matches_canonical_numeric() -> None:
    a: Vector = 1.5 * e_1 + (-2.0) * e_2 + 0.5 * e_3
    b: Vector = 0.25 * e_1 + 4.0 * e_2 + (-1.0) * e_3
    assert np.allclose(_coords(project_sp(a, b)), _coords(a.projected_onto(b)))


def test_reject_sp_matches_canonical_numeric() -> None:
    a: Vector = 1.5 * e_1 + (-2.0) * e_2 + 0.5 * e_3
    b: Vector = 0.25 * e_1 + 4.0 * e_2 + (-1.0) * e_3
    assert np.allclose(_coords(reject_sp(a, b)), _coords(a.rejected_away_from(b)))


def test_project_plus_reject_is_identity_numeric() -> None:
    a: Vector = 3.0 * e_1 + 1.0 * e_2 + (-2.0) * e_3
    b: Vector = 1.0 * e_1 + 2.0 * e_2 + 2.0 * e_3
    assert np.allclose(_coords(project_sp(a, b) + reject_sp(a, b)), _coords(a))


# A Pythagorean quadruple: k = sqrt(3^2+4^2) = 5 and |b| = sqrt(3^2+4^2+12^2) = 13
# are both exact (no sqrt symbols), so BOTH plane rotations are non-trivial and the
# rotation coefficients stay rational -- keeping the symbolic comparison tractable.
_B_EXACT: Vector = 3 * e_1 + 4 * e_2 + 12 * e_3


def test_project_sp_matches_canonical_symbolic() -> None:
    """Symbolic ``a`` with an exact-magnitude ``b`` (k = 5, |b| = 13): the
    standard-position projection equals the canonical Hestenes projection."""
    a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    a: Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    difference: Vector = project_sp(a, _B_EXACT) - a.projected_onto(_B_EXACT)
    assert all(
        sympy.simplify(sympy.sympify(coefficient)) == 0 for coefficient in difference
    )


def test_reject_sp_matches_canonical_symbolic() -> None:
    a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    a: Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    difference: Vector = reject_sp(a, _B_EXACT) - a.rejected_away_from(_B_EXACT)
    assert all(
        sympy.simplify(sympy.sympify(coefficient)) == 0 for coefficient in difference
    )
