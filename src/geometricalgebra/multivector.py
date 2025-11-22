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
import math
import typing
from typing import Protocol

import sympy


class Numeric(Protocol):
    """Generic numeric protocol."""

    def __add__(self, other) -> "Numeric": ...
    # def __radd__(self, other) -> 'Numeric': ...
    # def __sub__(self, other) -> 'Numeric': ...
    # def __rsub__(self, other) -> 'Numeric': ...
    def __mul__(self, other) -> "Numeric": ...
    def __rmul__(self, other) -> "Numeric": ...
    # def __truediv__(self, other) -> 'Numeric': ...
    # def __rtruediv__(self, other) -> 'Numeric': ...
    def __neg__(self) -> "Numeric": ...
    # def __pos__(self) -> 'Numeric': ...
    def __abs__(self) -> "Numeric": ...
    def __pow__(self, other) -> "Numeric": ...

    # def __rpow__(self, other) -> 'Numeric': ...


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
        self.scalar_from_blade = MultiVector.sum_dicts(
            [self.scalar_from_blade, {tuple(): 0}]
        )

    @staticmethod
    def from_scalar(scalar: int | float):
        return MultiVector({tuple(): scalar})

    @staticmethod
    def from_sympy_expr(s: sympy.Expr):
        return MultiVector({tuple(): s})

    @staticmethod
    def pseudoscaler(g: int) -> "MultiVector":
        return math.prod(
            [MultiVector({(x,): 1}) for x in range(1, g + 1)], start=one
        )

    @staticmethod
    def pseudoscaler_squared(g: int) -> "MultiVector":
        return MultiVector.pseudoscaler(g) * MultiVector.pseudoscaler(g)

    @staticmethod
    def sum_dicts(dicts: list[dict[list[int], Numeric]]):
        def sum_2_dicts(
            dict1: dict[list[int], Numeric], dict2: dict[list[int], Numeric]
        ):
            return {
                blade: dict1.get(blade, 0) + dict2.get(blade, 0)
                for blade in dict1.keys() | dict2.keys()
            }

        return functools.reduce(sum_2_dicts, dicts, {})

    def __add__(self, rhs) -> "MultiVector":
        return MultiVector(
            scalar_from_blade={
                blade: self.scalar_from_blade.get(blade, 0)
                + rhs.scalar_from_blade.get(blade, 0)
                for blade in self.scalar_from_blade.keys()
                | rhs.scalar_from_blade.keys()
            }
        )

    def __mul__(self, rhs) -> "MultiVector":
        def mult_blade_list(
            basis_blades: list[int], value: Numeric
        ) -> tuple[list[int], Numeric]:
            match basis_blades:
                case []:
                    return [], value
                case [a]:
                    return [a], value
                case [a, c, *rest] if a == c:
                    return mult_blade_list(rest, value)
                case [a, c, *rest] if a > c:
                    return mult_blade_list([c, a, *rest], -value)
                case [a, c, *rest] if a < c:
                    sorted_rest, new_val = mult_blade_list([c, *rest], value)
                    match sorted_rest:
                        case [b, *_] if a < b:
                            return [a, *sorted_rest], new_val
                        case _:
                            return mult_blade_list([a, *sorted_rest], new_val)
                case _:
                    raise ValueError(
                        "This code should never be able to be excuted - if printed this is a major logic error on my part"
                    )

        def mult_blade(
            basis_blades: list[int], value: Numeric
        ) -> dict[tuple[int, ...], Numeric]:
            sorted_list, new_val = mult_blade_list(list(basis_blades), value)
            return {tuple(sorted_list): new_val}

        match rhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return MultiVector(
                    scalar_from_blade=MultiVector.sum_dicts(
                        [
                            mult_blade(
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

    def __rmul__(self, lhs) -> "MultiVector":
        match lhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return -self.__mul__(lhs)

    def __neg__(self) -> "MultiVector":
        return -1 * self

    def __abs__(self) -> Numeric | sympy.Expr:
        return sympy.sqrt(self.abs_squared())

    def dot(self, rhs) -> "MultiVector":
        return sum(
            [
                (self.r_vector_part(x) * rhs.r_vector_part(y)).r_vector_part(
                    abs(x - y)
                )
                for x, y in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def wedge(self, rhs) -> "MultiVector":
        return sum(
            [
                (self.r_vector_part(x) * rhs.r_vector_part(y)).r_vector_part(
                    x + y
                )
                for x, y in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def r_vector_part(self, r) -> "MultiVector":
        return MultiVector(
            scalar_from_blade={
                blade: self.scalar_from_blade[blade]
                for blade in self.scalar_from_blade.keys()
                if len(blade) == r
            }
        )

    def scalar_part(self) -> Numeric:
        return self.r_vector_part(r=0).scalar_from_blade[tuple()]

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.scalar_from_blade.keys()))

    def max_grade(self) -> int:
        return max(self.grades())

    def reverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5

        to avoid using floats, I subtituted (-1)**(r*(r-1)/2) with an equivalent
        expression
        """
        return sum(
            [
                MultiVector.pseudoscaler_squared(r) * self.r_vector_part(r)
                for r in self.grades()
            ],
            start=zero,
        )

    def simplify(self) -> "MultiVector":
        return MultiVector(
            scalar_from_blade={
                blade: sympy.simplify(self.scalar_from_blade[blade])
                for blade in self.scalar_from_blade.keys()
            }
        )

    def abs_squared(self) -> "MultiVector":
        return (self.reverse() * self).simplify()

    def inverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Note sure if I'm doing it correctly
        """
        return self.reverse().simplify() * (
            self.abs_squared().scalar_part() ** (-1)
        )

    def dual(self, g: int) -> "MultiVector":
        return self * MultiVector.pseudoscaler(g).inverse()


def project(onto_mv: MultiVector):
    """
    page 18
    """

    def value(value: MultiVector):
        return (value.dot(onto_mv)) * onto_mv.inverse()

    return value


def reject(from_mv: MultiVector):
    """
    page 18
    """

    def value(value: MultiVector):
        return (value.wedge(from_mv)) * from_mv.inverse()

    return value


x: MultiVector = MultiVector({(1,): 1})
y: MultiVector = MultiVector({(2,): 1})
z: MultiVector = MultiVector({(3,): 1})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_x, a_y, a_z, b_x, b_y, b_z = sympy.symbols("a_x a_y a_z b_x b_y b_z")

sym_vec2_1: MultiVector = a_x * x + a_y * y
sym_vec2_2: MultiVector = b_x * x + b_y * y

sym_vec3_1: MultiVector = a_x * x + a_y * y + a_z * z
sym_vec3_2: MultiVector = b_x * x + b_y * y + b_z * z

sym_vec_plane: MultiVector = sym_vec3_1 * sym_vec3_2
sym_vec_plane_simplified: MultiVector = sym_vec_plane.simplify()
