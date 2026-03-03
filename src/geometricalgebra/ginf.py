# Copyright (c) 2025-2026 William Emerison Six
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
from typing import NamedTuple

import numpy as np
import sympy

from geometricalgebra.multivector import (
    MultiVectorABC,
)


class BladeDictionaryEntry(NamedTuple):
    blade: tuple[int, ...]
    coefficient: numbers.Number


@dataclasses.dataclass
class MultiVector(MultiVectorABC):
    coefficient_of_blade: BladeCoef

    def __post_init__(self):
        # simplify all coefficients
        self.coefficient_of_blade = {
            blade: sympy.simplify(self.coefficient_of_blade[blade])  # type: ignore
            for blade in self.coefficient_of_blade.keys()
        }
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

    def __mul__(self, rhs) -> "MultiVector":
        match rhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:

                def decrease_grade(
                    basis_blade: BladeDictionaryEntry,
                ) -> BladeDictionaryEntry:
                    match basis_blade.blade:
                        case ():
                            return basis_blade
                        case (a,):
                            return basis_blade
                        case (a, c, *rest) if a == c:
                            return decrease_grade(
                                BladeDictionaryEntry(
                                    blade=(*rest,), coefficient=basis_blade.coefficient
                                )
                            )
                        case (a, c, *rest) if a > c:
                            return decrease_grade(
                                BladeDictionaryEntry(
                                    blade=(c, a, *rest),
                                    coefficient=-(basis_blade.coefficient),  # type: ignore
                                )
                            )  # type: ignore
                        case (a, c, *rest) if a < c:
                            sortedBladeDictionyEntriy: BladeDictionaryEntry = (
                                decrease_grade(
                                    BladeDictionaryEntry(
                                        blade=(c, *rest),
                                        coefficient=basis_blade.coefficient,
                                    )
                                )
                            )
                            match sortedBladeDictionyEntriy.blade:
                                case (b, *_) if a < b:
                                    return BladeDictionaryEntry(
                                        blade=(a, *sortedBladeDictionyEntriy.blade),
                                        coefficient=sortedBladeDictionyEntriy.coefficient,
                                    )
                                case _:
                                    return decrease_grade(
                                        BladeDictionaryEntry(
                                            blade=(a, *sortedBladeDictionyEntriy.blade),
                                            coefficient=sortedBladeDictionyEntriy.coefficient,
                                        )
                                    )
                        case _:
                            raise ValueError(
                                "This code should never be able to be excuted"
                            )

                # make order the absolute units in a way that would
                # be considered positive in a full space.
                # For instance, e_1 * e_3 should be reprented as a negative
                # value, because e_1 * e_2 * e_3 = 1,
                # therefore e_1 * e_3 * e_2 = -1,
                def make_positive(
                    basis_blade: BladeDictionaryEntry,
                ) -> BladeDictionaryEntry:
                    if len(basis_blade.blade) <= 1:
                        return basis_blade
                    else:
                        missing_directions: tuple[int, ...] = sorted(
                            list(
                                set(list(range(1, max(basis_blade.blade))))
                                - set(basis_blade.blade)
                            )
                        )

                        has_positive_orientation: bool = (
                            1
                            == decrease_grade(
                                BladeDictionaryEntry(
                                    blade=(*basis_blade.blade, *missing_directions),
                                    coefficient=1,  # type: ignore
                                )
                            ).coefficient
                        )

                        return (
                            basis_blade
                            if has_positive_orientation
                            else BladeDictionaryEntry(
                                (basis_blade.blade[1],)
                                + (basis_blade.blade[0],)
                                + basis_blade.blade[2:],
                                -(basis_blade.coefficient),  # type: ignore
                            )
                        )

                def sum_dicts(dicts: list[BladeCoef]) -> BladeCoef:
                    def sum_2_dicts(dict1: BladeCoef, dict2: BladeCoef) -> BladeCoef:
                        return {
                            blade: dict1.get(blade, 0) + dict2.get(blade, 0)  # type: ignore
                            for blade in dict1.keys() | dict2.keys()
                        }

                    return functools.reduce(sum_2_dicts, dicts, {})

                return MultiVector(
                    coefficient_of_blade=sum_dicts(
                        [
                            dict(
                                [
                                    make_positive(
                                        decrease_grade(
                                            BladeDictionaryEntry(
                                                blade=(
                                                    *blade_left,
                                                    *blade_right,
                                                ),
                                                coefficient=scalar_left * scalar_right,  # type: ignore
                                            )
                                        )
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

    def __rmul__(self, lhs) -> "MultiVectorABC":
        match lhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return -self.__mul__(lhs)

    def scalar_product(self, other: typing.Self) -> numbers.Number:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.44
        """
        return (self * other).r_vector_part(0).coefficient_of_blade.get(tuple(), 0)  # type: ignore

    def r_vector_part(self, r: int) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: self.coefficient_of_blade[blade]
                for blade in self.coefficient_of_blade.keys()
                if len(blade) == r
            }
        )

    def scalar_part(self) -> numbers.Number:
        return self.r_vector_part(0).coefficient_of_blade.get(tuple(), 0)  # type: ignore

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.coefficient_of_blade.keys()))

    def reverse(self) -> "MultiVectorABC":
        pass
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5,
        equation 1.19

        to avoid using floats, I subtituted (-1)**(r*(r-1)/2) with an equivalent
        expression
        """

        # supposedly, 1.19 works for simple r-vectors, but because of linearity
        # of the grade operator, it works for all multivectors
        return sum(
            [
                MultiVector.unit_pseudoscalar_squared(g) * self.r_vector_part(g)
                for g in self.grades()
            ],
            start=MultiVector.zero(),
        )

    def dual(self, g: int) -> "MultiVectorABC":
        return self * MultiVector.unit_pseudoscalar(g).inverse()

    def is_close(self, other: typing.Self) -> bool:
        return all(
            [
                np.isclose(
                    float(self.coefficient_of_blade.get(blade, 0)),
                    float(other.coefficient_of_blade.get(blade, 0)),
                    rtol=1e-5,
                    atol=1e-5,
                )
                for blade in (
                    self.coefficient_of_blade.keys() | other.coefficient_of_blade.keys()
                )
            ]
        )

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


e_1: MultiVector = MultiVector({(1,): 1})  # type: ignore
e_2: MultiVector = MultiVector({(2,): 1})  # type: ignore
e_3: MultiVector = MultiVector({(3,): 1})  # type: ignore
e_4: MultiVector = MultiVector({(4,): 1})  # type: ignore
e_5: MultiVector = MultiVector({(5,): 1})  # type: ignore
e_6: MultiVector = MultiVector({(6,): 1})  # type: ignore
e_7: MultiVector = MultiVector({(7,): 1})  # type: ignore
e_8: MultiVector = MultiVector({(8,): 1})  # type: ignore
e_9: MultiVector = MultiVector({(9,): 1})  # type: ignore
e_10: MultiVector = MultiVector({(10,): 1})  # type: ignore
one: MultiVector = MultiVector.from_scalar(1)

a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")

sym_vec2_1: MultiVector = a_1 * e_1 + a_2 * e_2
sym_vec2_2: MultiVector = b_1 * e_1 + b_2 * e_2

sym_vec3_1: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
sym_vec3_2: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

sym_vec_plane: MultiVector = sym_vec3_1.wedge(sym_vec3_2)
