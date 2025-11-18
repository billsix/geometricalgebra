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


def test_multivector_add():
    a = mv.MultiVector({(4, 2): 5, (2, 1): 6})
    b = mv.MultiVector({(1,): 5, (2,): 6})
    c = mv.MultiVector({(1,): 7, (2,): 8})

    assert b + c == mv.MultiVector({(1,): 12, (2,): 14})


def test_multivector_absolute_units():
    x: mv.MultiVector = mv.x
    assert x == mv.MultiVector({(1,): 1})
    y: mv.MultiVector = mv.y
    assert y == mv.MultiVector({(2,): 1})
    z: mv.MultiVector = mv.z
    assert z == mv.MultiVector({(3,): 1})

    assert x + y == mv.MultiVector({(1,): 1, (2,): 1})
    assert x + z == mv.MultiVector({(1,): 1, (3,): 1})
    assert y + z == mv.MultiVector({(2,): 1, (3,): 1})

    assert x * 2 == mv.MultiVector({(1,): 2})
    assert 2 * x == mv.MultiVector({(1,): 2})
    assert y * 2 == mv.MultiVector({(2,): 2})
    assert z * 2 == mv.MultiVector({(3,): 2})

    assert (x + y) * 2 == mv.MultiVector({(1,): 2, (2,): 2})


def test_multivector_mult():
    a = 3 * mv.x + 4 * mv.y

    assert a * a == mv.MultiVector({(): 25, (1, 2): 0})

    i = mv.x * mv.y
    assert a * i == -4 * mv.x + 3 * mv.y
    assert (a * i) * i == -3 * mv.x + -4 * mv.y

    a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y")
    vec1 = a_x * mv.x + a_y * mv.y
    vec2 = b_x * mv.x + b_y * mv.y
    assert vec1 * vec2 == mv.MultiVector(
        {(): a_x * b_x + a_y * b_y, (1, 2): a_x * b_y - a_y * b_x}
    )
