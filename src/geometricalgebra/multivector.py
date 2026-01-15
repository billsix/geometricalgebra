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
import numbers
import typing

import sympy

BladeCoef = dict[tuple[int, ...], numbers.Number]


@dataclasses.dataclass
class MultiVector:
    coefficient_of_blade: BladeCoef

    def __post_init__(self):
        # prune zero coefficient_of_blade
        self.coefficient_of_blade = {
            blade: self.coefficient_of_blade[blade]
            for blade in self.coefficient_of_blade.keys()
            if self.coefficient_of_blade[blade] != 0
        }

    @staticmethod
    def from_scalar(scalar: int | float):
        return MultiVector({tuple(): scalar})  # type: ignore

    @staticmethod
    def from_sympy_expr(s: sympy.Expr):
        return MultiVector({tuple(): s})  # type: ignore

    @staticmethod
    def unit_pseudoscalar(g: int) -> "MultiVector":
        return math.prod([MultiVector({(x,): 1}) for x in range(1, g + 1)], start=one)  # type: ignore

    @staticmethod
    def unit_pseudoscalar_squared(g: int) -> "MultiVector":
        unit_pseudoscalar: MultiVector = MultiVector.unit_pseudoscalar(g)
        return unit_pseudoscalar * unit_pseudoscalar

    @staticmethod
    def sum_dicts(dicts: list[BladeCoef]) -> BladeCoef:
        def sum_2_dicts(dict1: BladeCoef, dict2: BladeCoef) -> BladeCoef:
            return {
                blade: dict1.get(blade, 0) + dict2.get(blade, 0)  # type: ignore
                for blade in dict1.keys() | dict2.keys()
            }

        return functools.reduce(sum_2_dicts, dicts, {})

    def __add__(self, rhs) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: (
                    self.coefficient_of_blade.get(blade, 0)
                    + rhs.coefficient_of_blade.get(blade, 0)
                )
                for blade in (
                    self.coefficient_of_blade.keys() | rhs.coefficient_of_blade.keys()
                )
            }
        )

    def __sub__(self, rhs) -> "MultiVector":
        return self + -rhs

    def __mul__(self, rhs) -> "MultiVector":
        def decrease_grade(
            basis_blades: tuple[int, ...], magnitude: numbers.Number
        ) -> tuple[tuple[int, ...], numbers.Number]:
            match basis_blades:
                case ():
                    return (), magnitude
                case (a,):
                    return (a,), magnitude
                case (a, c, *rest) if a == c:
                    return decrease_grade((*rest,), magnitude)
                case (a, c, *rest) if a > c:
                    return decrease_grade((c, a, *rest), -magnitude)  # type: ignore
                case (a, c, *rest) if a < c:
                    sorted_rest, new_mag = decrease_grade((c, *rest), magnitude)
                    match sorted_rest:
                        case (b, *_) if a < b:
                            return (a, *sorted_rest), new_mag
                        case _:
                            return decrease_grade((a, *sorted_rest), new_mag)
                case _:
                    raise ValueError("This code should never be able to be excuted")

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
                            dict(
                                [
                                    decrease_grade(
                                        basis_blades=(*blade_left, *blade_right),
                                        magnitude=scalar_left * scalar_right,  # type: ignore
                                    )
                                ]
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

    def __abs__(self) -> numbers.Number | sympy.Expr:
        return sympy.sqrt(self.abs_squared())

    def dot(self, rhs) -> "MultiVector":
        return sum(
            [
                (self.r(lg) * rhs.r(rg)).r(abs(lg - rg))
                for lg, rg in itertools.product(self.grades(), rhs.grades())
                if lg > 0 and rg > 0
            ],
            start=zero,
        )

    def wedge(self, rhs) -> "MultiVector":
        return sum(
            [
                (self.r(lg) * rhs.r(rg)).r(lg + rg)
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def r(self, part: int) -> "MultiVector":
        return self.r_vector_part(part)

    def r_vector_part(self, r: int) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: self.coefficient_of_blade[blade]
                for blade in self.coefficient_of_blade.keys()
                if len(blade) == r
            }
        )

    def is_homogeneous_of_grade_r(self, r: int) -> bool:
        return self == self.r_vector_part(r)

    def scalar_part(self) -> numbers.Number:
        return self.r(0).coefficient_of_blade.get(tuple(), 0)  # type: ignore

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
            [
                MultiVector.unit_pseudoscalar_squared(g) * self.r(g)
                for g in self.grades()
            ],
            start=zero,
        )

    def simplify(self) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: sympy.simplify(self.coefficient_of_blade[blade])  # type: ignore
                for blade in self.coefficient_of_blade.keys()
            }
        )

    def abs_squared(self) -> numbers.Number:
        return (self.reverse() * self).simplify().scalar_part()

    def inverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Note sure if I'm doing it correctly
        """
        return self.reverse().simplify() * (self.abs_squared() ** (-1))  # type: ignore

    def dual(self, g: int) -> "MultiVector":
        return self * MultiVector.unit_pseudoscalar(g).inverse()

    def even_part(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 0],
            start=zero,
        )

    def odd_part(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 1],
            start=zero,
        )

    def cosine(self, other: "MultiVector") -> numbers.Number:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14

        """
        return (
            (self.reverse() * other).scalar_part()
            * (abs(self) ** (-1))
            * (abs(other) ** (-1))
        )  # type: ignore

    def _repr_latex_(self):
        def add_parens_or_dont(x):
            if isinstance(x, sympy.Expr):
                if x.is_Add:
                    return "(" + sympy.latex(sympy.sympify(str(x))) + ")"
                else:
                    return sympy.latex(sympy.sympify(str(x)))
            else:
                return sympy.latex(sympy.sympify(str(x)))

        blades = [
            add_parens_or_dont(self.coefficient_of_blade[blade])
            + " ".join(map(lambda b: r"\mathbf{\vec{e}}_" + str(b), blade))
            if blade != tuple()
            else add_parens_or_dont(self.coefficient_of_blade[blade])
            for blade in sorted(self.coefficient_of_blade.keys())
        ]
        # latex_string = r"$\frac{1}{2}$"
        return "$" + " +  ".join(blades) + "$"


def project(onto_mv: MultiVector) -> typing.Callable[[MultiVector], MultiVector]:
    """
    page 18
    """

    def value(value: MultiVector) -> MultiVector:
        return (value.dot(onto_mv)) * onto_mv.inverse()

    return value


def reject(from_mv: MultiVector) -> typing.Callable[[MultiVector], MultiVector]:
    """
    page 18
    """

    def value(value: MultiVector) -> MultiVector:
        return (value.wedge(from_mv)) * from_mv.inverse()

    return value


e_1: MultiVector = MultiVector({(1,): 1})  # type: ignore
e_2: MultiVector = MultiVector({(2,): 1})  # type: ignore
e_3: MultiVector = MultiVector({(3,): 1})  # type: ignore
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")

sym_vec2_1: MultiVector = a_1 * e_1 + a_2 * e_2
sym_vec2_2: MultiVector = b_1 * e_1 + b_2 * e_2

sym_vec3_1: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
sym_vec3_2: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

sym_vec_plane: MultiVector = sym_vec3_1 * sym_vec3_2
sym_vec_plane_simplified: MultiVector = sym_vec_plane.simplify()
