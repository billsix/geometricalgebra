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


def test_multivector_add() -> None:
    a: mv.MultiVector = mv.MultiVector({(4, 2): 5, (2, 1): 6})
    b: mv.MultiVector = mv.MultiVector({(1,): 5, (2,): 6})
    c: mv.MultiVector = mv.MultiVector({(1,): 7, (2,): 8})

    assert b + c == mv.MultiVector({(1,): 12, (2,): 14})


def test_multivector_absolute_units() -> None:
    x: mv.MultiVector = mv.x
    assert x == mv.MultiVector({(1,): 1})
    y: mv.MultiVector = mv.y
    assert y == mv.MultiVector({(2,): 1})
    z: mv.MultiVector = mv.z
    assert z == mv.MultiVector({(3,): 1})

    # test addition
    assert x + y == mv.MultiVector({(1,): 1, (2,): 1})
    assert x + z == mv.MultiVector({(1,): 1, (3,): 1})
    assert y + z == mv.MultiVector({(2,): 1, (3,): 1})

    # test scalar multiplication
    assert x * 2 == mv.MultiVector({(1,): 2})
    assert 2 * x == mv.MultiVector({(1,): 2})
    assert y * 2 == mv.MultiVector({(2,): 2})
    assert z * 2 == mv.MultiVector({(3,): 2})

    # test addition on relative units
    assert (x + y) * 2 == mv.MultiVector({(1,): 2, (2,): 2})

    # test permutations
    assert (x * y * z) == mv.MultiVector({(1, 2, 3): 1})
    assert (x * z * y) == -(x * y * z)
    assert (z * x * y) == (x * y * z)
    assert (z * y * x) == -(x * y * z)
    assert (y * x * z) == -(x * y * z)
    assert (y * z * x) == (x * y * z)


def test_multivector_mult() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y

    assert a * a == mv.MultiVector({(): 25, (1, 2): 0})

    i: mv.MultiVector = mv.MultiVector.pseudoscaler(2)
    assert a * i == -4 * mv.x + 3 * mv.y
    assert (a * i) * i == -3 * mv.x + -4 * mv.y

    assert mv.sym_vec2_1 * mv.sym_vec2_2 == mv.MultiVector(
        {(): mv.a_x * mv.b_x + mv.a_y * mv.b_y, (1, 2): mv.a_x * mv.b_y - mv.a_y * mv.b_x}
    )


def test_multivector_mult3d() -> None:
    assert mv.sym_vec3_1 * mv.sym_vec3_2 == mv.MultiVector(
        {
            (): mv.a_x * mv.b_x + mv.a_y * mv.b_y + mv.a_z * mv.b_z,
            (1, 2): mv.a_x * mv.b_y - mv.a_y * mv.b_x,
            (1, 3): mv.a_x * mv.b_z - mv.a_z * mv.b_x,
            (2, 3): mv.a_y * mv.b_z - mv.a_z * mv.b_y,
        }
    )


def test_multivector_dual() -> None:
    assert (mv.sym_vec3_1.wedge(mv.sym_vec3_2)).dual(g=3) == mv.MultiVector(
        {
            (3,): mv.a_x * mv.b_y - mv.a_y * mv.b_x,
            (2,): -mv.a_x * mv.b_z + mv.a_z * mv.b_x,
            (1,): mv.a_y * mv.b_z - mv.a_z * mv.b_y,
        }
    )

    def planewise(plane, vec1, vec2):
        proj = mv.project(plane)
        return proj(vec1).wedge(proj(vec2)).dual(g=3)

    assert (mv.sym_vec3_1.wedge(mv.sym_vec3_2)).dual(g=3) == sum(
        [
            planewise(axis_1.wedge(axis_2), mv.sym_vec3_1, mv.sym_vec3_2)
            for axis_1, axis_2 in itertools.combinations([mv.x, mv.y, mv.z], 2)
        ],
        start=mv.zero,
    )


def test_multivector_grade() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.r_vector_part(0) == mv.zero
    assert a.scalar_part() == 0
    assert a.max_grade() == 1

    b: mv.MultiVector = 3 * mv.x + 4 * mv.y

    assert (b * b).scalar_part() == 25
    assert (b * b).r_vector_part(1) == mv.zero
    assert (b * b).r_vector_part(2) == mv.zero
    assert (b * b).max_grade() == 0

    c: mv.MultiVector = -4 * mv.x + 3 * mv.y
    assert (b * c).scalar_part() == 0
    assert (b * c).r_vector_part(1) == mv.zero
    assert (b * c).r_vector_part(2) == 25 * mv.x * mv.y
    assert (b * c).max_grade() == 2

    i3: mv.MultiVector = mv.x * mv.y * mv.z
    assert i3.scalar_part() == 0
    assert i3.r_vector_part(1) == mv.zero
    assert i3.r_vector_part(2) == mv.zero
    assert i3.r_vector_part(3) == i3
    assert i3.max_grade() == 3


def test_multivector_dot() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.dot(a) == mv.MultiVector({tuple(): 25})
    c: mv.MultiVector = -4 * mv.x + 3 * mv.y
    assert a.dot(c) == mv.zero

    assert mv.sym_vec2_1.dot(mv.sym_vec2_2) == mv.MultiVector(
        {(): mv.a_x * mv.b_x + mv.a_y * mv.b_y}
    )


def test_multivector_wedge() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.wedge(a) == mv.zero
    c: mv.MultiVector = -4 * mv.x + 3 * mv.y
    assert a.wedge(c) == 25 * mv.x * mv.y

    assert mv.sym_vec2_1.wedge(mv.sym_vec2_2) == mv.MultiVector(
        {(1, 2): mv.a_x * mv.b_y - mv.a_y * mv.b_x}
    )


def test_multivector_pseudoscalar() -> None:
    assert mv.MultiVector.pseudoscaler(1) == mv.x
    assert mv.MultiVector.pseudoscaler(2) == mv.x * mv.y
    assert mv.MultiVector.pseudoscaler(3) == mv.x * mv.y * mv.z

    i1: mv.MultiVector = mv.MultiVector.pseudoscaler(1)
    i2: mv.MultiVector = mv.MultiVector.pseudoscaler(2)
    i3: mv.MultiVector = mv.MultiVector.pseudoscaler(3)
    i4: mv.MultiVector = mv.MultiVector.pseudoscaler(4)
    i5: mv.MultiVector = mv.MultiVector.pseudoscaler(5)
    i6: mv.MultiVector = mv.MultiVector.pseudoscaler(6)
    i7: mv.MultiVector = mv.MultiVector.pseudoscaler(7)
    i8: mv.MultiVector = mv.MultiVector.pseudoscaler(8)
    i9: mv.MultiVector = mv.MultiVector.pseudoscaler(9)
    i10: mv.MultiVector = mv.MultiVector.pseudoscaler(10)
    i11: mv.MultiVector = mv.MultiVector.pseudoscaler(11)
    i12: mv.MultiVector = mv.MultiVector.pseudoscaler(12)
    i13: mv.MultiVector = mv.MultiVector.pseudoscaler(13)
    i14: mv.MultiVector = mv.MultiVector.pseudoscaler(14)
    i15: mv.MultiVector = mv.MultiVector.pseudoscaler(14)

    assert i1 * i1 == mv.MultiVector.from_scalar(1)
    assert mv.MultiVector.pseudoscaler_squared(1) == mv.MultiVector.from_scalar(1)
    assert i2 * i2 == mv.MultiVector.from_scalar(-1)
    assert mv.MultiVector.pseudoscaler_squared(2) == mv.MultiVector.from_scalar(-1)
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
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert (a * a).reverse() == a * a

    b: mv.MultiVector = 5 * mv.x + 10 * mv.y
    assert (b * a).reverse() == a * b

    assert (mv.sym_vec2_2 * mv.sym_vec2_1).reverse() == mv.sym_vec2_1 * mv.sym_vec2_2


def test_multivector_reverse3d() -> None:
    assert (mv.sym_vec3_2 * mv.sym_vec3_1).reverse() == mv.sym_vec3_1 * mv.sym_vec3_2


def test_multivector_inverse() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.abs_squared() == mv.MultiVector.from_scalar(25)
    assert a.abs_squared() * a.inverse() == a

    assert mv.sym_vec2_1.abs_squared() * mv.sym_vec2_1.inverse() == mv.sym_vec2_1
    assert (mv.sym_vec2_1.inverse() * mv.sym_vec2_1).simplify().scalar_part() == 1

    assert mv.sym_vec3_1.abs_squared() * mv.sym_vec3_1.inverse() == mv.sym_vec3_1
    assert (mv.sym_vec3_1.inverse() * mv.sym_vec3_1).simplify() == mv.MultiVector.from_scalar(1)

    plane: mv.MultiVector = mv.sym_vec_plane_simplified
    assert (plane * plane.inverse()).simplify() == mv.one
    assert (plane.inverse() * plane).simplify() == mv.one


def test_project_and_reject() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert mv.project(onto_mv=mv.x)(a) == 3 * mv.x
    assert mv.reject(from_mv=mv.x)(a) == 4 * mv.y

    assert mv.project(onto_mv=mv.x)(2 * a) == 6 * mv.x
    assert mv.reject(from_mv=mv.x)(2 * a) == 8 * mv.y

    assert mv.project(onto_mv=2 * mv.x)(a) == 3 * mv.x
    assert mv.reject(from_mv=2 * mv.x)(a) == 4 * mv.y

    parallel_to_vec1: mv.MultiVector = mv.project(onto_mv=mv.sym_vec2_1)(mv.sym_vec2_2)
    perp_to_vec1: mv.MultiVector = mv.reject(from_mv=mv.sym_vec2_1)(mv.sym_vec2_2)
    assert mv.sym_vec2_2 == (parallel_to_vec1 + perp_to_vec1).simplify()
