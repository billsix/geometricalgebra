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


import dataclasses
import numbers
import typing
from functools import reduce

import sympy


@dataclasses.dataclass
class MultiVector:
    components: dict[tuple[int, ...], typing.Any]

    def __add__(self, other):
        return MultiVector(
            components={
                k: self.components.get(k, 0) + other.components.get(k, 0)
                for k in self.components.keys() | other.components.keys()
            }
        )

    def __mul__(self, other):
        match other:
            case numbers.Number() as n:
                return self * MultiVector({tuple(): n})
            case sympy.Expr() as s:
                return self * MultiVector({tuple(): s})
            case _:
                return MultiVector(
                    components=sum_dicts(
                        [
                            {
                                type(key_left + key_right): sign(
                                    key_left + key_right
                                )
                                * value_left
                                * value_right
                            }
                            for key_left, value_left in self.components.items()
                            for key_right, value_right in other.components.items()
                        ]
                    )
                )

    def __rmul__(self, other):
        return self * other


def type(foo: tuple[int, ...]):
    return sort_types(foo, 1)[0]


def sign(foo: tuple[int, ...]):
    return sort_types(foo, 1)[1]


def sort_types(foo: tuple[int, ...], val):
    def s(foo: list[int, ...], val):
        current_val: int = foo[0]
        for i in range(1, len(foo)):
            if foo[i] < current_val:
                return s(
                    foo[: i - 1] + [foo[i]] + [foo[i - 1]] + foo[i + 1 :], -val
                )
            else:
                current_val = foo[i]
        return foo, val

    foo_sorted, val = s(list(foo), val)
    return remove_same_components(tuple(foo_sorted), val)


def remove_same_components(foo: tuple[int, ...], val):
    def s(foo: list[int, ...], val):
        if foo == list():
            return foo, val
        current_val: int = foo[0]
        for i in range(1, len(foo)):
            if foo[i] == current_val:
                return s(foo[: i - 1] + foo[i + 1 :], val)
            else:
                current_val = foo[i]
        return foo, val

    foo_sorted, val = s(list(foo), val)
    return tuple(foo_sorted), val


def sum_dicts(dicts):
    def sum_2_dicts(a, b):
        return {k: a.get(k, 0) + b.get(k, 0) for k in a.keys() | b.keys()}

    return reduce(sum_2_dicts, dicts, {})


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
