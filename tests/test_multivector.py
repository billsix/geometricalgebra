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


import sympy

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

    i: mv.MultiVector = mv.x * mv.y
    assert a * i == -4 * mv.x + 3 * mv.y
    assert (a * i) * i == -3 * mv.x + -4 * mv.y

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y
    assert vec1 * vec2 == mv.MultiVector(
        {(): a_x * b_x + a_y * b_y, (1, 2): a_x * b_y - a_y * b_x}
    )


def test_multivector_mult3d() -> None:
    i: mv.MultiVector = mv.x * mv.y * mv.z

    a_x, a_y, a_z, b_x, b_y, b_z = sympy.symbols("a_x a_y a_z b_x b_y b_z")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y + a_z * mv.z
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y + b_z * mv.z
    assert vec1 * vec2 == mv.MultiVector(
        {
            (): a_x * b_x + a_y * b_y + a_z * b_z,
            (1, 2): a_x * b_y - a_y * b_x,
            (1, 3): a_x * b_z - a_z * b_x,
            (2, 3): a_y * b_z - a_z * b_y,
        }
    )

    # TODO - figure out how to take the dual
    # assert vec1 * vec2 * i == mv.MultiVector(
    #     {(3,): a_x * b_y - a_y * b_x,
    #      (2,): a_z * b_x + a_x * b_z,
    #      (1,): a_y * b_z - a_z * b_y,
    #      }
    # )


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

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y
    assert vec1.dot(vec2) == mv.MultiVector({(): a_x * b_x + a_y * b_y})


def test_multivector_wedge() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.wedge(a) == mv.zero
    c: mv.MultiVector = -4 * mv.x + 3 * mv.y
    assert a.wedge(c) == 25 * mv.x * mv.y

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y
    assert vec1.wedge(vec2) == mv.MultiVector({(1, 2): a_x * b_y - a_y * b_x})


def test_multivector_reverse() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert (a * a).reverse() == a * a

    b: mv.MultiVector = 5 * mv.x + 10 * mv.y
    assert (b * a).reverse() == a * b

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y
    assert (vec2 * vec1).reverse() == vec1 * vec2


def test_multivector_reverse3d() -> None:
    a_x, a_y, a_z, b_x, b_y, b_z = sympy.symbols("a_x a_y a_z b_x b_y b_z")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y + a_z * mv.z
    vec2: mv.MultiVector = b_x * mv.x + b_y * mv.y + b_z * mv.z
    assert (vec2 * vec1).reverse() == vec1 * vec2


def test_multivector_inverse() -> None:
    a: mv.MultiVector = 3 * mv.x + 4 * mv.y
    assert a.inverse() == (1.0 / 25) * a

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1: mv.MultiVector = a_x * mv.x + a_y * mv.y
    assert vec1.inverse() == (a_x**2 + a_y**2) ** -1 * mv.MultiVector(
        scalar_from_blade={
            (1,): a_x,
            (2,): a_y,
            (): 0,
        }
    )
    assert (vec1.inverse() * vec1).simplify().scalar_part() == 1

    a_x, a_y, a_z, b_x, b_y, b_z = sympy.symbols("a_x a_y a_z b_x b_y b_z")
    vec3d_1: mv.MultiVector = a_x * mv.x + a_y * mv.y + a_z * mv.z
    assert vec3d_1.inverse() == (a_x**2 + a_y**2 + a_z**2) ** -1 * mv.MultiVector(
        scalar_from_blade={
            (1,): a_x,
            (2,): a_y,
            (3,): a_z,
            (): 0,
        }
    )

    # assert (vec3d_1.inverse() * vec3d_1).simplify().scalar_part() == 1

    # vec3d_2: mv.MultiVector = b_x * mv.x + b_y * mv.y + b_z * mv.z
    # print((vec3d_1 * vec3d_2).inverse())
    # assert ((vec3d_1 * vec3d_2).inverse() * (vec3d_1 * vec3d_2)).scalar_part() == 1
