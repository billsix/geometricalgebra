# Copyright (c) 2025 William Emerison Six
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


import itertools

import geometricalgebra.multivector as mv
from geometricalgebra.multivector import (
    MultiVector,
    a_1,
    a_2,
    a_3,
    b_1,
    b_2,
    b_3,
    e_1,
    e_2,
    e_3,
    project,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
    sym_vec_plane_simplified,
    zero,
)


def test_multivector_add() -> None:
    a: MultiVector = 5 * e_1 + 6 * e_2
    b: MultiVector = 7 * e_1 + 8 * e_2
    assert (a + b) == (12 * e_1 + 14 * e_2)

    c: MultiVector = 7 * e_1 + 2 * e_2
    d: MultiVector = 1 * e_1 + 3 * e_3
    assert (c + d) == (8 * e_1 + 2 * e_2 + 3 * e_3)

def test_multivector_subtract() -> None:
    a: MultiVector = 5 * e_1 + 6 * e_2
    b: MultiVector = 7 * e_1 + 9 * e_2
    # doc-region-end test add
    assert (b - a) == (2 * e_1 + 3 * e_2)

def test_multivector_absolute_units() -> None:
    # test addition
    assert (e_1 + e_2) == (e_2 + e_1)

    # test scalar multiplication
    assert (e_1 * 2) == (e_1 + e_1)
    assert (2 * e_1) == (e_1 + e_1)
    assert (e_2 * 2) == (e_2 + e_2)
    assert (2 * e_2) == (e_2 + e_2)

    # test addition on relative units
    assert ((e_1 + e_2) * 2) == ((e_1 + e_2) + (e_1 + e_2))

    # test permutations
    assert (e_1 * e_2 * e_3).abs_squared() == 1
    assert (e_1 * e_3 * e_2) == -1 * (e_1 * e_2 * e_3)
    assert (e_3 * e_1 * e_2) == (e_1 * e_2 * e_3)
    assert (e_3 * e_2 * e_1) == -1 * (e_1 * e_2 * e_3)
    assert (e_2 * e_1 * e_3) == -1 * (e_1 * e_2 * e_3)
    assert (e_2 * e_3 * e_1) == (e_1 * e_2 * e_3)


def test_multivector_mult() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.abs_squared() == 25

    assert (a * a) == MultiVector.from_scalar(25)

    i: MultiVector = MultiVector.unit_pseudoscalar(2)
    assert (a * i) == (-4 * e_1 + 3 * e_2)
    assert ((a * i) * i) == -3 * e_1 + -4 * e_2

    assert (sym_vec2_1 * sym_vec2_2) == (
        MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2)
        + (a_1 * b_2 - a_2 * b_1) * e_1 * e_2
    )

    assert (sym_vec2_1 * sym_vec2_2) == (
        sym_vec2_1.dot(sym_vec2_2) + (sym_vec2_1 * i).dot(sym_vec2_2) * i
    )


def planewise_wedge(plane, vec1, vec2):
    proj = project(plane)
    return proj(vec1).wedge(proj(vec2))


def test_multivector_mult3d() -> None:
    assert (sym_vec3_1 * sym_vec3_2) == (
        MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2 + a_3 * b_3)
        + (a_1 * b_2 - a_2 * b_1) * e_1 * e_2
        + (a_2 * b_3 - a_3 * b_2) * e_2 * e_3
        + (a_3 * b_1 - a_1 * b_3) * e_3 * e_1
    )

    assert (sym_vec3_1 * sym_vec3_2) == sum(
        [
            sym_vec3_1.dot(sym_vec3_2),
            *[
                planewise_wedge(plane=axis_1 * axis_2, vec1=sym_vec3_1, vec2=sym_vec3_2)
                for axis_1, axis_2 in itertools.combinations([e_1, e_2, e_3], 2)
            ],
        ],
        start=zero,
    )

    assert sym_vec3_1.dot(sym_vec3_2) == sym_vec3_1.dot(sym_vec3_2)

    assert (sym_vec3_1.wedge(sym_vec3_2)) == sum(
        [
            planewise_wedge(plane=axis_1 * axis_2, vec1=sym_vec3_1, vec2=sym_vec3_2)
            for axis_1, axis_2 in itertools.combinations([e_1, e_2, e_3], 2)
        ],
        start=zero,
    )


def test_multivector_dual() -> None:
    assert sym_vec2_1.dual(g=2) == sum(
        [a_2 * e_1, -a_1 * e_2],
        start=zero,
    )

    assert sym_vec3_1.dual(g=3) == sum(
        [-a_3 * e_1 * e_2, -a_2 * e_3 * e_1, -a_1 * e_2 * e_3],
        start=zero,
    )


def test_multivector_grade() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.r_vector_part(0) == zero
    assert a.scalar_part() == 0
    assert a.max_grade() == 1

    b: MultiVector = 3 * e_1 + 4 * e_2

    assert (b * b).scalar_part() == 25
    assert (b * b).r_vector_part(1) == zero
    assert (b * b).r_vector_part(2) == zero
    assert (b * b).max_grade() == 0

    c: MultiVector = -4 * e_1 + 3 * e_2
    assert (b * c).scalar_part() == 0
    assert (b * c).r_vector_part(1) == zero
    assert (b * c).r_vector_part(2) == 25 * e_1 * e_2
    assert (b * c).max_grade() == 2

    i3: MultiVector = e_1 * e_2 * e_3
    assert i3.scalar_part() == 0
    assert i3.r_vector_part(1) == zero
    assert i3.r_vector_part(2) == zero
    assert i3.r_vector_part(3) == i3
    assert i3.max_grade() == 3


def test_is_homogeneous_of_grade_r() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.is_homogeneous_of_grade_r(1)
    assert (a * a).is_homogeneous_of_grade_r(0)
    assert not (a * a).is_homogeneous_of_grade_r(1)
    assert not (a * a).is_homogeneous_of_grade_r(2)

    b: MultiVector = -4 * e_1 + 3 * e_2

    assert (a * b).is_homogeneous_of_grade_r(2)
    assert (a.wedge(b)).is_homogeneous_of_grade_r(2)

    c: MultiVector = 0 * e_1 + 5 * e_2
    assert not (a * c).is_homogeneous_of_grade_r(2)
    assert (a.wedge(c)).is_homogeneous_of_grade_r(2)


def test_even_part_odd_part() -> None:
    assert (sym_vec3_1).odd_part() == sym_vec3_1
    assert (sym_vec3_1).even_part() == zero
    assert (sym_vec3_1 * sym_vec3_2).odd_part() == zero
    assert (sym_vec3_1 * sym_vec3_2).even_part() == sym_vec3_1 * sym_vec3_2

    assert (sym_vec3_1 * sym_vec3_2) == (sym_vec3_1 * sym_vec3_2).odd_part() + (
        sym_vec3_1 * sym_vec3_2
    ).even_part()


def test_multivector_dot() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.dot(a) == MultiVector.from_scalar(25)
    c: MultiVector = -4 * e_1 + 3 * e_2
    assert a.dot(c) == zero

    assert sym_vec2_1.dot(sym_vec2_2) == MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2)


def test_multivector_cosine() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.cosine(a) == 1
    b: MultiVector = -4 * e_1 + 3 * e_2
    assert a.cosine(b) == 0

    # print(sym_vec2_1.cosine(sym_vec2_2) * abs(sym_vec2_1) * abs(sym_vec2_2))
    assert MultiVector.from_scalar(
        sym_vec2_1.cosine(sym_vec2_2) * abs(sym_vec2_1) * abs(sym_vec2_2)
    ) == sym_vec2_1.dot(sym_vec2_2)


def test_multivector_wedge() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.wedge(a) == zero
    c: MultiVector = -4 * e_1 + 3 * e_2
    assert a.wedge(c) == 25 * e_1 * e_2

    assert (
        sym_vec2_1.wedge(sym_vec2_2)
        == MultiVector.from_scalar(a_1 * b_2 - a_2 * b_1) * e_1 * e_2
    )


def test_multivector_unit_pseudoscalar() -> None:
    assert MultiVector.unit_pseudoscalar(1) == e_1
    assert MultiVector.unit_pseudoscalar(2) == e_1 * e_2
    assert MultiVector.unit_pseudoscalar(3) == e_1 * e_2 * e_3

    i1: MultiVector = MultiVector.unit_pseudoscalar(1)
    assert i1 * i1 == MultiVector.from_scalar(1)
    assert MultiVector.unit_pseudoscalar_squared(1) == MultiVector.from_scalar(1)
    i2: MultiVector = MultiVector.unit_pseudoscalar(2)
    assert i2 * i2 == MultiVector.from_scalar(-1)
    assert MultiVector.unit_pseudoscalar_squared(2) == MultiVector.from_scalar(-1)
    i3: MultiVector = MultiVector.unit_pseudoscalar(3)
    assert i3 * i3 == MultiVector.from_scalar(-1)
    i4: MultiVector = MultiVector.unit_pseudoscalar(4)
    assert i4 * i4 == MultiVector.from_scalar(1)
    i5: MultiVector = MultiVector.unit_pseudoscalar(5)
    assert i5 * i5 == MultiVector.from_scalar(1)
    i6: MultiVector = MultiVector.unit_pseudoscalar(6)
    assert i6 * i6 == MultiVector.from_scalar(-1)
    i7: MultiVector = MultiVector.unit_pseudoscalar(7)
    assert i7 * i7 == MultiVector.from_scalar(-1)
    i8: MultiVector = MultiVector.unit_pseudoscalar(8)
    assert i8 * i8 == MultiVector.from_scalar(1)
    i9: MultiVector = MultiVector.unit_pseudoscalar(9)
    assert i9 * i9 == MultiVector.from_scalar(1)
    i10: MultiVector = MultiVector.unit_pseudoscalar(10)
    assert i10 * i10 == MultiVector.from_scalar(-1)
    i11: MultiVector = MultiVector.unit_pseudoscalar(11)
    assert i11 * i11 == MultiVector.from_scalar(-1)
    i12: MultiVector = MultiVector.unit_pseudoscalar(12)
    assert i12 * i12 == MultiVector.from_scalar(1)
    i13: MultiVector = MultiVector.unit_pseudoscalar(13)
    assert i13 * i13 == MultiVector.from_scalar(1)
    i14: MultiVector = MultiVector.unit_pseudoscalar(14)
    assert i14 * i14 == MultiVector.from_scalar(-1)
    i15: MultiVector = MultiVector.unit_pseudoscalar(14)
    assert i15 * i15 == MultiVector.from_scalar(-1)


def test_multivector_reverse() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert (a * a).reverse() == a * a

    b: MultiVector = 5 * e_1 + 10 * e_2
    assert (b * a).reverse() == a * b

    assert (sym_vec2_2 * sym_vec2_1).reverse() == sym_vec2_1 * sym_vec2_2


def test_multivector_reverse_3d() -> None:
    assert (sym_vec3_2 * sym_vec3_1).reverse() == sym_vec3_1 * sym_vec3_2


def test_multivector_inverse() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.abs_squared() == 25
    assert a.abs_squared() * a.inverse() == a

    assert sym_vec2_1.abs_squared() * sym_vec2_1.inverse() == sym_vec2_1
    assert (sym_vec2_1.inverse() * sym_vec2_1).simplify().scalar_part() == 1

    assert sym_vec3_1.abs_squared() * sym_vec3_1.inverse() == sym_vec3_1
    assert (sym_vec3_1.inverse() * sym_vec3_1).simplify() == MultiVector.from_scalar(1)

    plane: MultiVector = sym_vec_plane_simplified
    assert (plane * plane.inverse()).simplify() == mv.one
    assert (plane.inverse() * plane).simplify() == mv.one


def test_project_and_reject() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert mv.project(onto_mv=e_1)(a) == 3 * e_1
    assert mv.reject(from_mv=e_1)(a) == 4 * e_2

    assert mv.project(onto_mv=e_1)(2 * a) == 6 * e_1
    assert mv.reject(from_mv=e_1)(2 * a) == 8 * e_2

    assert mv.project(onto_mv=2 * e_1)(a) == 3 * e_1
    assert mv.reject(from_mv=2 * e_1)(a) == 4 * e_2

    parallel_to_vec1: MultiVector = mv.project(onto_mv=sym_vec2_1)(sym_vec2_2)
    perp_to_vec1: MultiVector = mv.reject(from_mv=sym_vec2_1)(sym_vec2_2)
    assert sym_vec2_2 == (parallel_to_vec1 + perp_to_vec1).simplify()
