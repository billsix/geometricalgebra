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

"""The plane helpers ``bivector_from_vectors`` / ``i`` / ``.i()``.

``bivector_from_vectors(a, b)`` is the raw wedge ``a ∧ b`` (the area bivector);
``i(a, b)`` normalizes it to the plane's unit bivector (``i² = -1``); ``.i()``
gets a bivector's / rotor's own unit plane.  All return a BIVECTOR, never a
rotor.  Design + math: tasks/reference/unit-bivector-and-rotors.md.
"""

import pytest

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.gn import Gn, e_1, e_2

# `bivector_from_vectors` / `i` are on `MultiVectorBase` (or built from it), so they
# are statically typed `MultiVectorBase` even though the runtime value is precise
# (a Bivector on the graded Vector, a Gn on Gn, ...).  Annotate locals accordingly.


def test_bivector_from_vectors_is_the_unnormalized_wedge() -> None:
    # a ∧ b, un-normalized: its magnitude is the parallelogram area.
    biv: MultiVectorBase = Gn.bivector_from_vectors(3 * e_1, 4 * e_2)
    assert biv == 12 * (e_1 ^ e_2)
    assert abs(biv) == 12


def test_bivector_from_vectors_of_parallel_vectors_is_the_zero_bivector() -> None:
    # parallel vectors span no plane -> wedge is zero (this builder does not raise).
    assert Gn.bivector_from_vectors(e_1, 2 * e_1) == Gn.zero()


def test_bivector_from_vectors_rejects_non_vectors() -> None:
    with pytest.raises(TypeError):
        Gn.bivector_from_vectors(e_1 ^ e_2, e_1)  # a bivector is not grade-1


def test_i_is_a_unit_bivector_squaring_to_minus_one() -> None:
    # on Gn, on a full class (G), and on the graded Vector type.
    for i in (
        Gn.i(3 * e_1, 4 * e_2),
        g3.G.i(g3.G.e_1, g3.G.e_3),
        g2.Vector.i(g2.Vector.e_1, g2.Vector.e_2),
    ):
        assert i.is_bivector()  # a BIVECTOR, never a rotor
        assert abs(i) == 1  # unit
        assert (i * i).scalar_part() == -1  # i² = -1


def test_vector_i_is_precisely_typed_as_a_bivector() -> None:
    # on the graded Vector, i(a, b) narrows to the graded Bivector at runtime.
    assert isinstance(g2.Vector.i(g2.Vector.e_1, g2.Vector.e_2), g2.Bivector)
    assert isinstance(g3.Vector.i(g3.Vector.e_1, g3.Vector.e_3), g3.Bivector)


def test_i_of_parallel_vectors_raises() -> None:
    # Parallel vectors span no plane (zero wedge); i raises an explicit ValueError
    # rather than leaking normalize's low-level ZeroDivisionError.
    with pytest.raises(ValueError, match="parallel"):
        Gn.i(e_1, 2 * e_1)


def test_i_method_on_a_bivector_is_it_normalized() -> None:
    b: g2.Bivector = g2.Bivector(coeff_e_12=5)
    assert b.i() == b.normalize()
    assert b.i().is_bivector()


def test_i_method_on_a_rotor_is_its_plane_of_rotation() -> None:
    r: g3.Rotor = g3.Vector.e_1 * g3.Vector.e_2  # vector * vector is a Rotor
    assert r.i() == r.plane_of_rotation()
    assert r.i().is_bivector()


def test_i_from_vectors_composes_the_two_primitives() -> None:
    # i(a, b) builds the plane then takes its unit: == bivector_from_vectors normalized
    a: g3.Vector = g3.Vector.e_1
    b: g3.Vector = g3.Vector.e_3
    plane: MultiVectorBase = g3.Vector.bivector_from_vectors(a, b)
    assert g3.Vector.i(a, b) == plane.normalize()
