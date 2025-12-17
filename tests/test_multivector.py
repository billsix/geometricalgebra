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
from geometricalgebra.multivector import e_1, e_2, e_3


def test_multivector_add() -> None:
    a: mv.MultiVector = 5 * e_1 + 6 * e_2
    b: mv.MultiVector = 7 * e_1 + 8 * e_2

    assert a + b == 12 * e_1 + 14 * e_2


def test_multivector_absolute_units() -> None:
    # test addition
    assert e_1 + e_2 == e_2 + e_1

    # test scalar multiplication
    assert e_1 * 2 == e_1 + e_1
    assert 2 * e_1 == e_1 + e_1
    assert e_2 * 2 == e_2 + e_2
    assert 2 * e_2 == e_2 + e_2

    # test addition on relative units
    assert (e_1 + e_2) * 2 == (e_1 + e_2) + (e_1 + e_2)

    # test permutations
    assert (e_1 * e_2 * e_3).abs_squared() == mv.MultiVector.from_scalar(1)
    assert (e_1 * e_3 * e_2) == -(e_1 * e_2 * e_3)
    assert (e_3 * e_1 * e_2) == (e_1 * e_2 * e_3)
    assert (e_3 * e_2 * e_1) == -(e_1 * e_2 * e_3)
    assert (e_2 * e_1 * e_3) == -(e_1 * e_2 * e_3)
    assert (e_2 * e_3 * e_1) == (e_1 * e_2 * e_3)


def test_multivector_mult() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert a.abs_squared() == mv.MultiVector.from_scalar(25)

    assert a * a == mv.MultiVector.from_scalar(25)

    i: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(2)
    assert a * i == -4 * e_1 + 3 * e_2
    assert (a * i) * i == -3 * e_1 + -4 * e_2

    assert (
        mv.sym_vec2_1 * mv.sym_vec2_2
        == mv.MultiVector.from_scalar(mv.a_x * mv.b_x + mv.a_y * mv.b_y)
        + (mv.a_x * mv.b_y - mv.a_y * mv.b_x) * e_1 * e_2
    )

    assert mv.sym_vec2_1 * mv.sym_vec2_2 == (
        mv.sym_vec2_1.dot(mv.sym_vec2_2) + (mv.sym_vec2_1 * i).dot(mv.sym_vec2_2) * i
    )


def planewise_wedge(plane, vec1, vec2):
    proj = mv.project(plane)
    return proj(vec1).wedge(proj(vec2))


def test_multivector_mult3d() -> None:
    assert (
        mv.sym_vec3_1 * mv.sym_vec3_2
        == mv.MultiVector.from_scalar(
            mv.a_x * mv.b_x + mv.a_y * mv.b_y + mv.a_z * mv.b_z
        )
        + (mv.a_x * mv.b_y - mv.a_y * mv.b_x) * e_1 * e_2
        + (mv.a_y * mv.b_z - mv.a_z * mv.b_y) * e_2 * e_3
        + (mv.a_z * mv.b_x - mv.a_x * mv.b_z) * e_3 * e_1
    )

    assert mv.sym_vec3_1 * mv.sym_vec3_2 == sum(
        [
            mv.sym_vec3_1.dot(mv.sym_vec3_2),
            *[
                planewise_wedge(
                    plane=axis_1 * axis_2, vec1=mv.sym_vec3_1, vec2=mv.sym_vec3_2
                )
                for axis_1, axis_2 in itertools.combinations([e_1, e_2, e_3], 2)
            ],
        ],
        start=mv.zero,
    )

    assert mv.sym_vec3_1.dot(mv.sym_vec3_2) == mv.sym_vec3_1.dot(mv.sym_vec3_2)

    assert (mv.sym_vec3_1.wedge(mv.sym_vec3_2)) == sum(
        [
            planewise_wedge(
                plane=axis_1 * axis_2, vec1=mv.sym_vec3_1, vec2=mv.sym_vec3_2
            )
            for axis_1, axis_2 in itertools.combinations([e_1, e_2, e_3], 2)
        ],
        start=mv.zero,
    )


def test_multivector_dual() -> None:
    assert mv.sym_vec2_1.dual(g=2) == sum(
        [mv.a_y * e_1, -mv.a_x * e_2],
        start=mv.zero,
    )

    assert mv.sym_vec3_1.dual(g=3) == sum(
        [-mv.a_z * e_1 * e_2, -mv.a_y * e_3 * e_1, -mv.a_x * e_2 * e_3],
        start=mv.zero,
    )


def test_multivector_grade() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert a.r_vector_part(0) == mv.zero
    assert a.scalar_part() == 0
    assert a.max_grade() == 1

    b: mv.MultiVector = 3 * e_1 + 4 * e_2

    assert (b * b).scalar_part() == 25
    assert (b * b).r_vector_part(1) == mv.zero
    assert (b * b).r_vector_part(2) == mv.zero
    assert (b * b).max_grade() == 0

    c: mv.MultiVector = -4 * e_1 + 3 * e_2
    assert (b * c).scalar_part() == 0
    assert (b * c).r_vector_part(1) == mv.zero
    assert (b * c).r_vector_part(2) == 25 * e_1 * e_2
    assert (b * c).max_grade() == 2

    i3: mv.MultiVector = e_1 * e_2 * e_3
    assert i3.scalar_part() == 0
    assert i3.r_vector_part(1) == mv.zero
    assert i3.r_vector_part(2) == mv.zero
    assert i3.r_vector_part(3) == i3
    assert i3.max_grade() == 3


def test_multivector_dot() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert a.dot(a) == mv.MultiVector.from_scalar(25)
    c: mv.MultiVector = -4 * e_1 + 3 * e_2
    assert a.dot(c) == mv.zero

    assert mv.sym_vec2_1.dot(mv.sym_vec2_2) == mv.MultiVector.from_scalar(
        mv.a_x * mv.b_x + mv.a_y * mv.b_y
    )


def test_multivector_wedge() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert a.wedge(a) == mv.zero
    c: mv.MultiVector = -4 * e_1 + 3 * e_2
    assert a.wedge(c) == 25 * e_1 * e_2

    assert (
        mv.sym_vec2_1.wedge(mv.sym_vec2_2)
        == mv.MultiVector.from_scalar(mv.a_x * mv.b_y - mv.a_y * mv.b_x) * e_1 * e_2
    )


def test_multivector_unit_pseudoscalar() -> None:
    assert mv.MultiVector.unit_pseudoscalar(1) == e_1
    assert mv.MultiVector.unit_pseudoscalar(2) == e_1 * e_2
    assert mv.MultiVector.unit_pseudoscalar(3) == e_1 * e_2 * e_3

    i1: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(1)
    i2: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(2)
    i3: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(3)
    i4: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(4)
    i5: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(5)
    i6: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(6)
    i7: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(7)
    i8: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(8)
    i9: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(9)
    i10: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(10)
    i11: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(11)
    i12: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(12)
    i13: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(13)
    i14: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(14)
    i15: mv.MultiVector = mv.MultiVector.unit_pseudoscalar(14)

    assert i1 * i1 == mv.MultiVector.from_scalar(1)
    assert mv.MultiVector.unit_pseudoscalar_squared(1) == mv.MultiVector.from_scalar(1)
    assert i2 * i2 == mv.MultiVector.from_scalar(-1)
    assert mv.MultiVector.unit_pseudoscalar_squared(2) == mv.MultiVector.from_scalar(-1)
    assert i3 * i3 == mv.MultiVector.from_scalar(-1)
    assert i4 * i4 == mv.MultiVector.from_scalar(1)
    assert i5 * i5 == mv.MultiVector.from_scalar(1)
    assert i6 * i6 == mv.MultiVector.from_scalar(-1)
    assert i7 * i7 == mv.MultiVector.from_scalar(-1)
    assert i8 * i8 == mv.MultiVector.from_scalar(1)
    assert i9 * i9 == mv.MultiVector.from_scalar(1)
    assert i10 * i10 == mv.MultiVector.from_scalar(-1)
    assert i11 * i11 == mv.MultiVector.from_scalar(-1)
    assert i12 * i12 == mv.MultiVector.from_scalar(1)
    assert i13 * i13 == mv.MultiVector.from_scalar(1)
    assert i14 * i14 == mv.MultiVector.from_scalar(-1)
    assert i15 * i15 == mv.MultiVector.from_scalar(-1)


def test_multivector_reverse() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert (a * a).reverse() == a * a

    b: mv.MultiVector = 5 * e_1 + 10 * e_2
    assert (b * a).reverse() == a * b

    assert (mv.sym_vec2_2 * mv.sym_vec2_1).reverse() == mv.sym_vec2_1 * mv.sym_vec2_2


def test_multivector_reverse_3d() -> None:
    assert (mv.sym_vec3_2 * mv.sym_vec3_1).reverse() == mv.sym_vec3_1 * mv.sym_vec3_2


def test_multivector_inverse() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert a.abs_squared() == mv.MultiVector.from_scalar(25)
    assert a.abs_squared() * a.inverse() == a

    assert mv.sym_vec2_1.abs_squared() * mv.sym_vec2_1.inverse() == mv.sym_vec2_1
    assert (mv.sym_vec2_1.inverse() * mv.sym_vec2_1).simplify().scalar_part() == 1

    assert mv.sym_vec3_1.abs_squared() * mv.sym_vec3_1.inverse() == mv.sym_vec3_1
    assert (
        mv.sym_vec3_1.inverse() * mv.sym_vec3_1
    ).simplify() == mv.MultiVector.from_scalar(1)

    plane: mv.MultiVector = mv.sym_vec_plane_simplified
    assert (plane * plane.inverse()).simplify() == mv.one
    assert (plane.inverse() * plane).simplify() == mv.one


def test_project_and_reject() -> None:
    a: mv.MultiVector = 3 * e_1 + 4 * e_2
    assert mv.project(onto_mv=e_1)(a) == 3 * e_1
    assert mv.reject(from_mv=e_1)(a) == 4 * e_2

    assert mv.project(onto_mv=e_1)(2 * a) == 6 * e_1
    assert mv.reject(from_mv=e_1)(2 * a) == 8 * e_2

    assert mv.project(onto_mv=2 * e_1)(a) == 3 * e_1
    assert mv.reject(from_mv=2 * e_1)(a) == 4 * e_2

    parallel_to_vec1: mv.MultiVector = mv.project(onto_mv=mv.sym_vec2_1)(mv.sym_vec2_2)
    perp_to_vec1: mv.MultiVector = mv.reject(from_mv=mv.sym_vec2_1)(mv.sym_vec2_2)
    assert mv.sym_vec2_2 == (parallel_to_vec1 + perp_to_vec1).simplify()
