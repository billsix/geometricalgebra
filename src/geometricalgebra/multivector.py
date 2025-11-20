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
    blades: dict[tuple[int, ...], typing.Any]

    @staticmethod
    def sum_dicts(dicts):
        def sum_2_dicts(a, b):
            return {k: a.get(k, 0) + b.get(k, 0) for k in a.keys() | b.keys()}

        return functools.reduce(sum_2_dicts, dicts, {})

    def __post_init__(self):
        # prune zero blades
        self.blades = {
            k: self.blades[k] for k in self.blades.keys() if self.blades[k] != 0
        }
        # excepty for scalar
        self.blades = MultiVector.sum_dicts([self.blades, {tuple(): 0}])

    def __add__(self, other):
        return MultiVector(
            blades={
                k: self.blades.get(k, 0) + other.blades.get(k, 0)
                for k in self.blades.keys() | other.blades.keys()
            }
        )

    def __mul__(self, other):
        match other:
            case numbers.Number() as n:
                return self * MultiVector({tuple(): n})
            case sympy.Expr() as s:
                return self * MultiVector({tuple(): s})
            case _:

                def mult_blades(tuple_items: tuple[int, ...], val):
                    def canonicalize(items: list[int], value):
                        match items:
                            case []:
                                return [], value
                            case [a]:
                                return [a], value
                            case [a, b, *rest] if a == b:
                                return canonicalize(rest, value)
                            case [a, b, *rest] if a > b:
                                return canonicalize([b, a] + rest, -value)
                            case [a, *rest]:
                                sorted_rest, new_val = canonicalize(rest, value)
                                match sorted_rest:
                                    case [b, *rest] if a == b:
                                        return canonicalize(
                                            [a, b] + rest, new_val
                                        )
                                    case [b, *rest] if a > b:
                                        return canonicalize(
                                            [b, a] + rest, -new_val
                                        )
                                    case _:
                                        return [a] + sorted_rest, new_val

                    sorted_list, new_val = canonicalize(list(tuple_items), val)
                    return {tuple(sorted_list): new_val}

                return MultiVector(
                    blades=MultiVector.sum_dicts(
                        [
                            mult_blades(
                                key_left + key_right, value_left * value_right
                            )
                            for (key_left, value_left), (
                                key_right,
                                value_right,
                            ) in itertools.product(
                                self.blades.items(),
                                other.blades.items(),
                            )
                        ]
                    )
                )

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return -1 * self

    def dot(self, other):
        return sum(
            [
                (self.r_vector_part(x) * other.r_vector_part(y)).r_vector_part(
                    abs(x - y)
                )
                for x, y in itertools.product(self.grades(), other.grades())
            ],
            start=zero,
        )

    def wedge(self, other):
        return sum(
            [
                (self.r_vector_part(x) * other.r_vector_part(y)).r_vector_part(
                    x + y
                )
                for x, y in itertools.product(self.grades(), other.grades())
            ],
            start=zero,
        )

    def r_vector_part(self, r):
        return MultiVector(
            blades={
                k: self.blades[k] for k in self.blades.keys() if len(k) == r
            }
        )

    def scalar_part(self):
        return self.r_vector_part(r=0)

    def grades(self):
        return list(set(len(k) for k in self.blades.keys()))

    def max_grade(self):
        return max(self.grades())


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
zero: MultiVector = MultiVector({tuple(): 0})
