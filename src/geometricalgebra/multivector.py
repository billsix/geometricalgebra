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
from collections.abc import Sequence
from itertools import chain, combinations
from typing import Callable, Generator, NamedTuple, TypeIs

import numpy as np
import sympy

BladeCoef = dict[tuple[int, ...], numbers.Real]
MultiVectorFn = Callable[["MultiVector"], "MultiVector"]


class BladeDictionaryEntry(NamedTuple):
    blade: tuple[int, ...]
    coefficient: numbers.Real

    def as_multivector(self):
        return MultiVector(coefficient_of_blade=dict([(self.blade, self.coefficient)]))


@dataclasses.dataclass
class MultiVector:
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
        return MultiVector({tuple(): typing.cast(numbers.Real, scalar)})

    @staticmethod
    def from_sympy_expr(s: sympy.Expr):
        return MultiVector({tuple(): typing.cast(numbers.Real, s)})

    @staticmethod
    def unit_pseudoscalar(g: int) -> "MultiVector":
        return math.prod(
            [
                MultiVector({(x,): typing.cast(numbers.Real, 1)})
                for x in range(1, g + 1)
            ],
            start=one,
        )

    @staticmethod
    def bases(g: int) -> Generator["MultiVector"]:
        def powerset(iterable: Sequence[int]) -> chain[tuple[int, ...]]:
            s: list[int] = list(iterable)
            # chain.from_iterable flattens the list of combinations
            return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

        yield from (
            math.prod(
                [MultiVector({(x,): typing.cast(numbers.Real, 1)}) for x in b],
                start=one,
            )
            for b in powerset(range(1, g + 1))
        )

    @staticmethod
    def symbolic_multivector(grade: int, prefix: str) -> "MultiVector":
        mv: list[MultiVector] = list(MultiVector.bases(grade))
        symbols: list[sympy.symbol] = sympy.symbols(prefix + ":" + str(len(mv)))
        return sum([s * blade for s, blade in zip(symbols, mv)], start=zero)

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

    def __sub__(self, rhs: typing.Self) -> "MultiVector":
        return self + -rhs

    def __mul__(self, rhs) -> "MultiVector":

        def mul() -> "MultiVector":
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
                                coefficient=typing.cast(
                                    numbers.Real, -(basis_blade.coefficient)
                                ),
                            )
                        )
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
                        raise ValueError("This code should never be able to be excuted")

            def blade_dictionary_entry_to_multivector(
                b: BladeDictionaryEntry,
            ) -> MultiVector:
                return b.as_multivector()

            return sum(
                [
                    blade_dictionary_entry_to_multivector(
                        decrease_grade(
                            BladeDictionaryEntry(
                                blade=(
                                    *blade_left,
                                    *blade_right,
                                ),
                                coefficient=typing.cast(
                                    numbers.Real,
                                    scalar_left * scalar_right,
                                ),
                            )
                        )
                    )
                    for (blade_left, scalar_left), (
                        blade_right,
                        scalar_right,
                    ) in itertools.product(
                        self.coefficient_of_blade.items(),
                        rhs.coefficient_of_blade.items(),
                    )
                ],
                start=zero,
            )

        match rhs:
            case int() as n:
                return self * MultiVector.from_scalar(n)
            case float() as n:
                return self * MultiVector.from_scalar(n)
            case sympy.Expr() as s:
                return self * MultiVector.from_sympy_expr(s)
            case _:
                return mul()

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

    def __abs__(self) -> numbers.Real | sympy.Expr:
        return self.magnitude()

    def __iter__(self):
        yield from (
            MultiVector(BladeCoef({key: value}))
            for key, value in self.coefficient_of_blade.items()
        )

    def magnitude(self) -> numbers.Real | sympy.Expr:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.49
        """
        return sympy.sqrt(self.magnitude_squared())

    def magnitude_squared(self) -> numbers.Real:
        return self.reverse().scalar_product(self)

    def normalize(self) -> "MultiVector":
        return self * (abs(self) ** (-1))

    def component(self, x: typing.Self) -> numbers.Real:
        # TODO - is this really how I should define it?
        return self.dot(x).scalar_part()

    def inner_product(self, rhs: typing.Self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.21a, 1.21b, 1.21c
        """

        def inner_product_of_homogenous_multivectors(
            lhs: "MultiVector", rhs: "MultiVector"
        ) -> "MultiVector":
            # # 1.21b
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(abs(left_grade - right_grade))

        return sum(
            [
                inner_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
                if lg > 0 and rg > 0
            ],
            start=zero,  # 1.21b
        )

    def dot(self, rhs: typing.Self) -> "MultiVector":
        return self.inner_product(rhs)

    def outer_product(self, rhs: typing.Self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.22a, 1.22b, 1.22c
        """

        def outer_product_of_homogenous_multivectors(
            lhs: "MultiVector", rhs: "MultiVector"
        ) -> "MultiVector":
            # 1.22a
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(left_grade + right_grade)

        # 1.22b
        # 1.22c, because unlike the inner_product, we keep grade 0s
        return sum(
            [
                outer_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=zero,
        )

    def scalar_product(self, other: typing.Self) -> numbers.Real:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.44
        """
        return (
            (self * other)
            .r_vector_part(0)
            .coefficient_of_blade.get(tuple(), typing.cast(numbers.Real, 0))
        )

    def wedge(self, rhs: typing.Self) -> "MultiVector":
        return self.outer_product(rhs)

    def __xor__(self, other: typing.Self) -> "MultiVector":
        """
        Python Syntax for the wedge function

        a.wedge(b) = a^b
        """
        return self.wedge(other)

    @staticmethod
    def outer_product_of_vectors(*vectors: "MultiVector") -> "MultiVector":
        return functools.reduce(lambda a, b: a ^ b, vectors)

    def r_vector_part(self, r: int) -> "MultiVector":
        return MultiVector(
            coefficient_of_blade={
                blade: self.coefficient_of_blade[blade]
                for blade in self.coefficient_of_blade.keys()
                if len(blade) == r
            }
        )

    def is_homogeneous_of_grade_r(self, r: int) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self.max_grade() == r and self.is_r_vector()

    def is_scalar(self) -> bool:
        """ """
        return self == self.r_vector_part(0)

    def is_r_vector(self) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self == self.r_vector_part(self.max_grade())

    def is_vector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=1)

    def is_bivector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=2)

    def is_trivector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=3)

    def is_orthogonal_to(
        self, other: typing.Self, float_close_to_zero: bool = False
    ) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 9,
        between equations 1.32 and 1.33
        """

        # TODO - defined for vectors only right now, it's probably defined more
        # generally later in the book
        assert self.is_vector()
        assert other.is_vector()

        return bool(
            np.isclose(
                float(self.inner_product(other).scalar_part()),
                float(0.0),
                rtol=1e-5,
                atol=1e-5,
            )
            if float_close_to_zero
            else (self.inner_product(other) == zero)
        )

    def is_parallel_to(
        self, other: typing.Self, float_close_to_zero: bool = False
    ) -> bool:
        """
        not sure if I'm doing this correctly
        """

        # TODO - defined for vectors only right now, it's probably defined more
        # generally later in the book
        assert self.is_vector()
        assert other.is_vector()

        return bool(
            np.isclose(float(self.cosine(other)), float(1.0), rtol=1e-5, atol=1e-5)
            if float_close_to_zero
            else (self.cosine(other) == 1)
        )

    def scalar_part(self) -> numbers.Real:
        return self.r_vector_part(0).coefficient_of_blade.get(
            tuple(), typing.cast(numbers.Real, 0)
        )

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.coefficient_of_blade.keys()))

    def max_grade(self) -> int:
        return max(self.grades())

    def reverse(self) -> "MultiVector":
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
            start=zero,
        )

    def inverse(self) -> "MultiVector":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Note sure if I'm doing it correctly
        """
        return self.reverse() * (self.magnitude_squared() ** (-1))

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

    def cosine(self, other: "MultiVector") -> numbers.Real:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14,
        equation 1.53b

        """
        return typing.cast(
            numbers.Real,
            self.reverse().scalar_product(other)
            * typing.cast(numbers.Real, abs(self) ** (-1))
            * typing.cast(numbers.Real, (abs(other) ** (-1))),
        )

    @staticmethod
    def project(
        onto: "MultiVector" | Sequence["MultiVector"],
    ) -> MultiVectorFn:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18,
        equations 2.9a, 2.9b, 2.9c
        """
        if isinstance(onto, Sequence):

            def is_multivector_sequence(
                val: Sequence[object],
            ) -> TypeIs[Sequence[MultiVector]]:
                return all(isinstance(x, MultiVector) for x in val)

            if is_multivector_sequence(onto):
                return MultiVector.project(MultiVector.outer_product_of_vectors(*onto))

        def fn(value: MultiVector) -> MultiVector:
            if value.is_scalar():  # 2.9b
                return value
            elif value.is_r_vector():  # 2.9c
                return (value.dot(onto)) * onto.inverse()
            else:
                return (value.dot(onto)).dot(onto.inverse())  # 2.9a

        return fn

    @staticmethod
    def reject(
        away_from: "MultiVector" | Sequence["MultiVector"],
    ) -> MultiVectorFn:
        """
        page 18
        """

        def r(value: MultiVector) -> MultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(away_from, MultiVector)  # to satisfy type checking
            return (value.wedge(away_from)) * away_from.inverse()

        match away_from:
            case _ as sequence if isinstance(away_from, Sequence):
                assert isinstance(sequence, Sequence)  # to satisfy type checking
                return MultiVector.reject(MultiVector.outer_product(*sequence))
            case MultiVector() as away_from_vector if away_from_vector.is_vector():
                return r
            case MultiVector() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(away_from))

    @staticmethod
    def reflect(
        across: "MultiVector" | Sequence["MultiVector"],
    ) -> MultiVectorFn:
        components_in_plane: MultiVectorFn = MultiVector.project(across)
        components_exterior_to_plane: MultiVectorFn = MultiVector.reject(across)

        def r(value: MultiVector) -> MultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(across, MultiVector)  # to satisfy type checking

            return components_in_plane(value) - components_exterior_to_plane(value)

        match across:
            case _ as sequence if isinstance(across, Sequence):
                assert isinstance(sequence, Sequence)  # to satisfy type checking
                return MultiVector.reflect(MultiVector.outer_product(*sequence))
            case MultiVector() as away_from_vector if away_from_vector.is_vector():
                return r
            case MultiVector() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(across))

    @staticmethod
    def rotate(
        from_vector: "MultiVector",
        to_vector: "MultiVector",
    ) -> MultiVectorFn:
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        plane: MultiVector = from_vector ^ to_vector

        components_in_plane: MultiVectorFn = MultiVector.project(plane)
        components_exterior_to_plane: MultiVectorFn = MultiVector.reject(plane)

        def r(value: MultiVector) -> MultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            return (
                components_in_plane(value) * from_vector * to_vector
            ) + components_exterior_to_plane(value)

        return r

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

        def sort_by_grade(a, b):
            print(a)
            print(b)
            print(len(a) > len(b))
            return len(a) > len(b)

        blades = [
            add_parens_or_dont(self.coefficient_of_blade[blade])
            + " ".join(map(lambda b: r"\mathbf{\vec{e}}_" + str(b), blade))
            if blade != tuple()
            else add_parens_or_dont(self.coefficient_of_blade[blade])
            for blade in sorted(
                self.coefficient_of_blade.keys(), key=lambda b: (len(b), str(b))
            )
        ]
        # latex_string = r"$\frac{1}{2}$"
        return "$" + ("0" if (self == zero) else " +  ".join(blades)) + "$"


e_1: MultiVector = MultiVector({(1,): typing.cast(numbers.Real, 1)})
e_2: MultiVector = MultiVector({(2,): typing.cast(numbers.Real, 1)})
e_3: MultiVector = MultiVector({(3,): typing.cast(numbers.Real, 1)})
e_4: MultiVector = MultiVector({(4,): typing.cast(numbers.Real, 1)})
e_5: MultiVector = MultiVector({(5,): typing.cast(numbers.Real, 1)})
e_6: MultiVector = MultiVector({(6,): typing.cast(numbers.Real, 1)})
e_7: MultiVector = MultiVector({(7,): typing.cast(numbers.Real, 1)})
e_8: MultiVector = MultiVector({(8,): typing.cast(numbers.Real, 1)})
e_9: MultiVector = MultiVector({(9,): typing.cast(numbers.Real, 1)})
e_10: MultiVector = MultiVector({(10,): typing.cast(numbers.Real, 1)})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")

sym_vec2_1: MultiVector = a_1 * e_1 + a_2 * e_2
sym_vec2_2: MultiVector = b_1 * e_1 + b_2 * e_2

sym_vec3_1: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
sym_vec3_2: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

sym_vec_plane: MultiVector = sym_vec3_1.wedge(sym_vec3_2)
