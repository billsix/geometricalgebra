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

import sympy


@dataclasses.dataclass
class MultiVector:
    components: dict[tuple[int, ...], typing.Any]

    def __add__(self, other):
        return MultiVector(
            components={
                k: self.components.get(k, 0) + other.components.get(k, 0)
                for k in [*self.components.keys(), *other.components.keys()]
            }
        )

    def __mul__(self, other):
        if isinstance(other, numbers.Number) or isinstance(other, sympy.Expr):
            return MultiVector(
                components={
                    k: other * self.components[k]
                    for k in self.components.keys()
                }
            )
        else:
            combined_dict = {}
            for key_left, value_left in self.components.items():
                for key_right, value_right in other.components.items():
                    my_type, sign = sort_types(key_left + key_right, 1)
                    combined_dict[my_type] = (
                        combined_dict.get(my_type, 0)
                        + sign * value_left * value_right
                    )
            return MultiVector(components=combined_dict)

    def __rmul__(self, other):
        return self * other


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


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
