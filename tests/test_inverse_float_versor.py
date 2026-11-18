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


"""``inverse()`` on a float versor whose ``Ã * A`` carries rounding residue.

A 𝒢₃ versor built from float vectors has ``Ã * A`` equal to a scalar plus a bivector
coefficient of about 1e-16; ``inverse()`` treats that residue as zero
(``base._is_scalar_up_to_rounding``) instead of rejecting the versor, so
``versor_rotation`` works on float 3D vectors.  A genuinely mixed-grade float
element is still rejected, and exact input is still held to exact equality.
"""

import pytest

from gacalc.functions import InvertibleFunction
from gacalc.g3 import Vector, Versor, e_1, e_2, e_3
from gacalc.transforms import versor_rotation

FROM: Vector = 2.0 * e_1 + 1.0 * e_2 + 0.5 * e_3
TO: Vector = 0.5 * e_1 + 3.0 * e_2 + 1.0 * e_3


def test_float_versor_inverts() -> None:
    """The versor from two float vectors inverts: ``R * R⁻¹`` is 1."""
    R: Versor = FROM.versor_from_vectors(from_vector=FROM, to_vector=TO)
    assert (R * R.inverse()).isclose(Versor.from_real(1.0), abs_tol=1e-12)


def test_float_versor_rotation_round_trips() -> None:
    """``versor_rotation`` on float 3D vectors rotates and inverts back."""
    rotation: InvertibleFunction[Vector] = versor_rotation(
        from_vector=FROM, to_vector=TO
    )
    x: Vector = 1.0 * e_3
    assert rotation.inverse(rotation(x)).isclose(x, abs_tol=1e-12)
    assert rotation(FROM).isclose(
        TO * (FROM.magnitude() / TO.magnitude()), rel_tol=1e-12, abs_tol=1e-12
    )


def test_float_mixed_grade_still_raises() -> None:
    """A scalar plus a vector is not a versor; its inverse is not implemented."""
    with pytest.raises(RuntimeError):
        (1.0 + 1.0 * e_1).inverse()


def test_exact_input_stays_exact() -> None:
    """Exact input skips the tolerance path: ``R⁻¹`` keeps exact coefficients."""
    R: Versor = (1 * e_1).versor_from_vectors(from_vector=1 * e_1, to_vector=1 * e_2)
    assert all(not isinstance(c, float) for c in R.inverse())
