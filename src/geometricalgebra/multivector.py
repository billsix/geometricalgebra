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
    scalar_from_blade: dict[tuple[int, ...], typing.Any]

    def __post_init__(self):
        # prune zero scalar_from_blade
        self.scalar_from_blade = {
            blade: self.scalar_from_blade[blade]
            for blade in self.scalar_from_blade.keys()
            if self.scalar_from_blade[blade] != 0
        }
        # excepty for scalar
        self.scalar_from_blade = MultiVector.sum_dicts([self.scalar_from_blade, {tuple(): 0}])

    @staticmethod
    def from_scalar(scalar: numbers.Number):
        return MultiVector({tuple(): scalar})

    @staticmethod
    def from_sympy_expr(s: sympy.Expr):
        return MultiVector({tuple(): s})

    @staticmethod
    def sum_dicts(dicts):
        def sum_2_dicts(dict1, dict2):
            return {
                blade: dict1.get(blade, 0) + dict2.get(blade, 0)
                for blade in dict1.keys() | dict2.keys()
            }

        return functools.reduce(sum_2_dicts, dicts, {})

    def __add__(self, rhs):
        return MultiVector(
            scalar_from_blade={
                blade: self.scalar_from_blade.get(blade, 0) + rhs.scalar_from_blade.get(blade, 0)
                for blade in self.scalar_from_blade.keys() | rhs.scalar_from_blade.keys()
            }
        )

    def __mul__(self, rhs):
        def mult_blade(items: list[int], value):
            match items:
                case []:
                    return [], value
                case [a]:
                    return [a], value
                case [a, b, *rest] if a == b:
                    return mult_blade(rest, value)
                case [a, b, *rest] if a > b:
                    return mult_blade([b, a, *rest], -value)
                case [a, *rest]:
                    sorted_rest, new_val = mult_blade(rest, value)
                    match sorted_rest:
                        case [b, *rest] if a == b:
                            return mult_blade([a, b, *rest], new_val)
                        case [b, *rest] if a > b:
                            return mult_blade([b, a, *rest], -new_val)
                        case _:
                            return [a, *sorted_rest], new_val

        def mult_scalar_from_blade(items: tuple[int], value):
            sorted_list, new_val = mult_blade(list(items), value)
            return {tuple(sorted_list): new_val}

        match rhs:
            case numbers.Number() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return MultiVector(
                    scalar_from_blade=MultiVector.sum_dicts(
                        [
                            mult_scalar_from_blade(
                                [*blade_left, *blade_right],
                                scalar_left * scalar_right,
                            )
                            for (blade_left, scalar_left), (
                                blade_right,
                                scalar_right,
                            ) in itertools.product(
                                self.scalar_from_blade.items(),
                                rhs.scalar_from_blade.items(),
                            )
                        ]
                    )
                )

    def __rmul__(self, lhs):
        return self * lhs

    def __neg__(self):
        return -1 * self

    def dot(self, rhs):
        return sum(
            [
                (self.r_vector_part(x) * rhs.r_vector_part(y)).r_vector_part(abs(x - y))
                for x, y in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def wedge(self, rhs):
        return sum(
            [
                (self.r_vector_part(x) * rhs.r_vector_part(y)).r_vector_part(x + y)
                for x, y in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def r_vector_part(self, r):
        return MultiVector(
            scalar_from_blade={
                blade: self.scalar_from_blade[blade]
                for blade in self.scalar_from_blade.keys()
                if len(blade) == r
            }
        )

    def scalar_part(self):
        return self.r_vector_part(r=0)

    def grades(self):
        return list(set(len(blade) for blade in self.scalar_from_blade.keys()))

    def max_grade(self):
        return max(self.grades())


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)
