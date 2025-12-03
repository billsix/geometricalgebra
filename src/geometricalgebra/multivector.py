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
    coefficient_of_blade: dict[tuple[int, ...], Numeric]

    def __post_init__(self):
        # prune zero coefficient_of_blade
        self.coefficient_of_blade = {
            blade: self.coefficient_of_blade[blade]
            for blade in self.coefficient_of_blade.keys()
            if self.coefficient_of_blade[blade] != 0
        }

    @staticmethod
    def from_scalar(scalar: int | float):
        return MultiVector({tuple(): scalar})

    @staticmethod
    def from_sympy_expr(s: sympy.Expr):
        return MultiVector({tuple(): s})

    @staticmethod
    def unit_pseudoscalar(g: int) -> "MultiVector":
        return math.prod([MultiVector({(x,): 1}) for x in range(1, g + 1)], start=one)

    @staticmethod
    def unit_pseudoscalar_squared(g: int) -> "MultiVector":
        unit_pseudoscalar: MultiVector = MultiVector.unit_pseudoscalar(g)
        return unit_pseudoscalar * unit_pseudoscalar

    @staticmethod
    def sum_dicts(dicts: list[dict[tuple[int], Numeric]]):
        def sum_2_dicts(
            dict1: dict[tuple[int], Numeric],
            dict2: dict[tuple[int], Numeric],
        ):
            return {blade: dict1.get(blade, 0) + dict2.get(blade, 0) for blade in dict1.keys() | dict2.keys()}

        return functools.reduce(sum_2_dicts, dicts, {})

    def __add__(self, rhs) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: self.coefficient_of_blade.get(blade, 0) + rhs.coefficient_of_blade.get(blade, 0)
                for blade in self.coefficient_of_blade.keys() | rhs.coefficient_of_blade.keys()
            }
        )

    def __mul__(self, rhs) -> "MultiVector":
        def decrease_grade_list(magnitude: Numeric, basis_blades: list[int]) -> tuple[Numeric, list[int]]:
            match basis_blades:
                case []:
                    return magnitude, []
                case [a]:
                    return magnitude, [a]
                case [a, c, *rest] if a == c:
                    return decrease_grade_list(magnitude, rest)
                case [a, c, *rest] if a > c:
                    return decrease_grade_list(-magnitude, [c, a, *rest])
                case [a, c, *rest] if a < c:
                    new_mag, sorted_rest = decrease_grade_list(magnitude, [c, *rest])
                    match sorted_rest:
                        case [b, *_] if a < b:
                            return new_mag, [a, *sorted_rest]
                        case _:
                            return decrease_grade_list(new_mag, [a, *sorted_rest])
                case _:
                    raise ValueError(
                        "This code should never be able to be excuted - if printed this is a major logic error on my part"
                    )

        def decrease_grade(
            magnitude: Numeric,
            basis_blades: list[int],
        ) -> dict[tuple[int, ...], Numeric]:
            new_mag, sorted_list = decrease_grade_list(magnitude, list(basis_blades))
            return {tuple(sorted_list): new_mag}

        def increase_grade(blade_left: tuple[int, ...], blade_right: tuple[int, ...]) -> list[int]:
            return [*blade_left, *blade_right]

        match rhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return MultiVector(
                    coefficient_of_blade=MultiVector.sum_dicts(
                        [
                            decrease_grade(
                                scalar_left * scalar_right,
                                increase_grade(blade_left, blade_right),
                            )
                            for (blade_left, scalar_left), (
                                blade_right,
                                scalar_right,
                            ) in itertools.product(
                                self.coefficient_of_blade.items(),
                                rhs.coefficient_of_blade.items(),
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

    def dot(lhs, rhs) -> "MultiVector":
        return sum(
            [
                (lhs.r_vector_part(left_grade) * rhs.r_vector_part(right_grade)).r_vector_part(
                    abs(left_grade - right_grade)
                )
                for left_grade, right_grade in itertools.product(lhs.grades(), rhs.grades())
                if left_grade > 0 and right_grade > 0
            ],
            start=zero,
        )

    def wedge(lhs, rhs) -> "MultiVector":
        return sum(
            [
                (lhs.r_vector_part(left_grade) * rhs.r_vector_part(right_grade)).r_vector_part(left_grade + right_grade)
                for left_grade, right_grade in itertools.product(lhs.grades(), rhs.grades())
            ],
            start=zero,
        )

    def r_vector_part(self, r) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: self.coefficient_of_blade[blade] for blade in self.coefficient_of_blade.keys() if len(blade) == r
            }
        )

    def scalar_part(self) -> Numeric:
        return self.r_vector_part(r=0).coefficient_of_blade.get(tuple(), 0)

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.coefficient_of_blade.keys()))

    def max_grade(self) -> int:
        return max(self.grades())

    def reverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5

        to avoid using floats, I subtituted (-1)**(r*(r-1)/2) with an equivalent
        expression
        """
        return sum(
            [MultiVector.unit_pseudoscalar_squared(g) * self.r_vector_part(g) for g in self.grades()],
            start=zero,
        )

    def simplify(self) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: sympy.simplify(self.coefficient_of_blade[blade]) for blade in self.coefficient_of_blade.keys()
            }
        )

    def abs_squared(self) -> "MultiVector":
        return (self.reverse() * self).simplify()

    def inverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Note sure if I'm doing it correctly
        """
        return self.reverse().simplify() * (self.abs_squared().scalar_part() ** (-1))

    def dual(self, g: int) -> "MultiVector":
        return self * MultiVector.unit_pseudoscalar(g).inverse()

    def _repr_latex_(self):
        blades = [
            "("
            + sympy.latex(sympy.sympify(str(self.coefficient_of_blade[blade])))
            + ")"
            + sympy.latex(sympy.sympify(sympy.symbols("e_" + "".join(map(str, blade)), bold=True)))
            if blade != tuple()
            else "(" + sympy.latex(sympy.sympify(str(self.coefficient_of_blade[blade]))) + ")"
            for blade in self.coefficient_of_blade.keys()
        ]
        # latex_string = r"$\frac{1}{2}$"
        return "$" + " +  ".join(blades) + "$"


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


e_1: MultiVector = MultiVector({(1,): 1})
e_2: MultiVector = MultiVector({(2,): 1})
e_3: MultiVector = MultiVector({(3,): 1})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_x, a_y, a_z, b_x, b_y, b_z = sympy.symbols("a_x a_y a_z b_x b_y b_z")

sym_vec2_1: MultiVector = a_x * e_1 + a_y * e_2
sym_vec2_2: MultiVector = b_x * e_1 + b_y * e_2

sym_vec3_1: MultiVector = a_x * e_1 + a_y * e_2 + a_z * e_3
sym_vec3_2: MultiVector = b_x * e_1 + b_y * e_2 + b_z * e_3

sym_vec_plane: MultiVector = sym_vec3_1 * sym_vec3_2
sym_vec_plane_simplified: MultiVector = sym_vec_plane.simplify()
