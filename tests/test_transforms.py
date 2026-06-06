# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Transform-layer tests: representation-preserving (type round-trip) + values.

The factories in ``geometricalgebra.transforms`` derive any basis vectors they
need from the *type of the value* (``cls.basis_vector(i)``), so a G1/G2/G3/Gn
value in yields the **same concrete type** out.  These tests pin that, plus a few
known values, invertibility, and the non-invertible error paths.

Rotations / 2-D scale are inherently planar (the e_1 e_2 plane), so their *values*
are exercised only on planar (e_1, e_2) vectors and on the G2 / Gn / G3 reps.
Equality on the specialized classes is simplify-aware, but these use numeric
coefficients, so ``is_close`` (float-tolerant) is the right comparison.
"""

import math

import pytest

from geometricalgebra.g1 import G1
from geometricalgebra.g2 import G2
from geometricalgebra.g3 import G3
from geometricalgebra.gn import Gn
from geometricalgebra.transforms import (
    compose,
    identity,
    inverse,
    rotate,
    rotate_90_degrees,
    rotate_around,
    scale_non_uniform,
    scale_non_uniform_2d,
    translate,
    uniform_scale,
)


def vec(cls, *coords):
    """Build a vector of representation ``cls`` from its e_1.. components."""
    return sum(
        (c * cls.basis_vector(i + 1) for i, c in enumerate(coords)),
        start=cls.zero(),
    )


# (rep, a vector of that rep's natural dimension)
DIM_GENERAL = [(Gn, (1, 2, 3)), (G1, (3,)), (G2, (3, 4)), (G3, (1, 2, 3))]
# reps on which the planar (e_1 e_2) transforms preserve type
PLANAR_REPS = [Gn, G2, G3]


@pytest.mark.parametrize("cls", [Gn, G1, G2, G3])
def test_basis_vector_e1_is_unit(cls):
    assert cls.basis_vector(1) == cls.from_blade_dict({(1,): 1})


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_basis_vector_e2_is_unit(cls):
    assert cls.basis_vector(2) == cls.from_blade_dict({(2,): 1})


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_dimension_general_transforms_preserve_type(cls, coords):
    v = vec(cls, *coords)
    b = vec(cls, *coords)  # translate target must be the same representation
    factors = tuple(range(2, 2 + len(coords)))  # (2,) / (2,3) / (2,3,4)
    fns = [
        translate(b),
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        identity(),
        compose([uniform_scale(2.0), translate(b)]),
    ]
    for fn in fns:
        assert type(fn(v)) is cls


@pytest.mark.parametrize("cls", PLANAR_REPS)
def test_planar_transforms_preserve_type(cls):
    v = vec(cls, 3, 4)  # lies in the e_1 e_2 plane
    center = vec(cls, 1, 1)
    fns = [
        rotate_90_degrees(),
        rotate(math.pi / 3),
        rotate_around(math.pi / 4, center),
        scale_non_uniform_2d(2.0, 3.0),
    ]
    for fn in fns:
        assert type(fn(v)) is cls


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_known_values(cls):
    v = vec(cls, 3, 4)
    # rotate 90 degrees in e_1 e_2:  3 e_1 + 4 e_2  ->  -4 e_1 + 3 e_2
    assert rotate_90_degrees()(v).is_close(vec(cls, -4, 3))
    # rotate(pi/2) (float trig) lands on the same result within tolerance
    assert rotate(math.pi / 2)(v).is_close(vec(cls, -4, 3))
    # non-uniform 2-D scale
    assert scale_non_uniform_2d(2.0, 3.0)(vec(cls, 1, 1)).is_close(vec(cls, 2, 3))
    # uniform scale
    assert uniform_scale(2.0)(v).is_close(vec(cls, 6, 8))


def test_nd_scale_preserves_type_and_value():
    for cls in (Gn, G3):
        v = vec(cls, 1, 1, 1)
        scaled = scale_non_uniform(2.0, 3.0, 4.0)(v)
        assert type(scaled) is cls
        assert scaled.is_close(vec(cls, 2, 3, 4))


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_invertibility(cls, coords):
    v = vec(cls, *coords)
    factors = tuple(range(2, 2 + len(coords)))
    for fn in [
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        translate(vec(cls, *coords)),
    ]:
        assert inverse(fn)(fn(v)).is_close(v)
    c = compose([uniform_scale(2.0), translate(vec(cls, *coords))])
    assert inverse(c)(c(v)).is_close(v)


def test_non_invertible_scales_raise():
    v = vec(Gn, 1, 1)
    # the forward of a zero scale is fine; the *inverse* is undefined and raises
    with pytest.raises(ValueError):
        inverse(uniform_scale(0.0))(v)
    with pytest.raises(ValueError):
        inverse(scale_non_uniform(2.0, 0.0))(v)
