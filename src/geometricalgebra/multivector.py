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
import functools
import itertools
import numbers
import typing

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
                            for (key_left, value_left), (
                                key_right,
                                value_right,
                            ) in itertools.product(
                                self.components.items(),
                                other.components.items(),
                            )
                        ]
                    )
                )

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return -1 * self


def type(foo: tuple[int, ...]):
    return sort_types(foo, 1)[0]


def sign(foo: tuple[int, ...]):
    return sort_types(foo, 1)[1]


def sort_types(tuple_items: tuple[int, ...], val):
    def sort(items: list[int], value):
        match items:
            case []:
                return items, value
            case [single]:
                return items, value
            case [a, b, *rest] if a == b:
                return sort(rest, value)
            case [a, b, *rest] if a > b:
                return sort([b, a] + rest, -value)
            case [a, *rest]:
                tail, new_val = sort(rest, value)
                match tail:
                    case []:
                        return [a], new_val
                    case [single]:
                        return [a, single], new_val
                    case [first, *rest] if a == first:
                        return sort(rest, new_val)
                    case [first, *rest] if a > first:
                        return sort([first, a] + rest, -new_val)
                    case _:
                        return [a] + tail, new_val

    sorted_list, new_val = sort(list(tuple_items), val)
    return tuple(sorted_list), new_val


def sum_dicts(dicts):
    def sum_2_dicts(a, b):
        return {k: a.get(k, 0) + b.get(k, 0) for k in a.keys() | b.keys()}

    return functools.reduce(sum_2_dicts, dicts, {})


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
