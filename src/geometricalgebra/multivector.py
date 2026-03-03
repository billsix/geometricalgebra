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


import functools
import itertools
import numbers
import typing
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Callable

import numpy as np
import sympy

BladeCoef = dict[tuple[int, ...], numbers.Number]
MultiVectorFn = Callable[["MultiVector"], "MultiVector"]


class MultiVectorABC(ABC):
    @staticmethod
    @abstractmethod
    def from_scalar(scalar: int | float):
        pass

    @staticmethod
    @abstractmethod
    def from_sympy_expr(s: sympy.Expr):
        pass

    @staticmethod
    @abstractmethod
    def unit_pseudoscalar(g: int) -> "MultiVectorABC":
        pass

    @staticmethod
    @abstractmethod
    def unit_pseudoscalar_squared(g: int) -> "MultiVectorABC":
        pass

    @classmethod
    def zero(cls) -> "MultiVectorABC":
        return cls.from_scalar(0)

    @abstractmethod
    def __add__(self, rhs) -> "MultiVectorABC":
        pass

    @abstractmethod
    def __mul__(self, rhs) -> "MultiVectorABC":
        pass

    @abstractmethod
    def __rmul__(self, lhs) -> "MultiVectorABC":
        pass

    @abstractmethod
    def scalar_product(self, other: typing.Self) -> numbers.Number:
        pass

    @abstractmethod
    def r_vector_part(self, r: int) -> "MultiVectorABC":
        pass

    @abstractmethod
    def scalar_part(self) -> numbers.Number:
        pass

    @abstractmethod
    def grades(self) -> list[int]:
        pass

    @abstractmethod
    def reverse(self) -> "MultiVectorABC":
        pass

    @abstractmethod
    def dual(self, g: int) -> "MultiVectorABC":
        pass

    @abstractmethod
    def is_close(self, other: typing.Self) -> bool:
        pass

    @abstractmethod
    def _repr_latex_(self):
        pass

    def __neg__(self) -> "MultiVectorABC":
        return -1 * self

    def __sub__(self, rhs: typing.Self) -> "MultiVectorABC":
        return self + -rhs

    def __abs__(self) -> numbers.Number | sympy.Expr:
        return self.magnitude()

    def magnitude(self) -> numbers.Number | sympy.Expr:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.49
        """
        return sympy.sqrt(self.magnitude_squared())

    def magnitude_squared(self) -> numbers.Number:
        return self.reverse().scalar_product(self)

    def normalize(self) -> "MultiVectorABC":
        return self * (abs(self) ** (-1))  # type: ignore

    def component(self, x: typing.Self) -> numbers.Number:
        # TODO - is this really how I should define it?
        return self.dot(x).scalar_part()

    def inner_product(self, rhs: typing.Self) -> "MultiVectorABC":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.21a, 1.21b, 1.21c
        """

        def inner_product_of_homogenous_multivectors(
            lhs: "MultiVectorABC", rhs: "MultiVectorABC"
        ) -> "MultiVectorABC":
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
            start=type(self).zero(),  # 1.21b
        )

    def dot(self, rhs: typing.Self) -> "MultiVectorABC":
        return self.inner_product(rhs)

    def outer_product(self, rhs: typing.Self) -> "MultiVectorABC":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.22a, 1.22b, 1.22c
        """

        def outer_product_of_homogenous_multivectors(
            lhs: "MultiVectorABC", rhs: "MultiVectorABC"
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
            start=type(self).zero(),
        )

    def wedge(self, rhs: typing.Self) -> "MultiVectorABC":
        return self.outer_product(rhs)

    def __xor__(self, other: typing.Self) -> "MultiVectorABC":
        """
        Python Syntax for the wedge function

        a.wedge(b) = a^b
        """
        return self.wedge(other)

    @staticmethod
    def outer_product_of_vectors(*vectors: "MultiVectorABC") -> "MultiVectorABC":
        return functools.reduce(lambda a, b: a ^ b, vectors)

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
            else (self.inner_product(other) == type(self).zero())
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

    def max_grade(self) -> int:
        return max(self.grades())

    def inverse(self) -> "MultiVectorABC":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Note sure if I'm doing it correctly
        """
        return self.reverse() * (self.magnitude_squared() ** (-1))  # type: ignore

    def even_part(self) -> "MultiVectorABC":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 0],
            start=type(self).zero(),
        )

    def odd_part(self) -> "MultiVectorABC":
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 1],
            start=type(self).zero(),
        )

    def cosine(self, other: "MultiVectorABC") -> numbers.Number:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14,
        equation 1.53b

        """
        return (
            self.reverse().scalar_product(other)
            * (abs(self) ** (-1))  # type: ignore
            * (abs(other) ** (-1))  # type: ignore
        )  # type: ignore

    @staticmethod
    def project(
        onto: "MultiVectorABC" | Sequence["MultiVectorABC"],
    ) -> MultiVectorFn:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18,
        equations 2.9a, 2.9b, 2.9c
        """
        if isinstance(onto, Sequence):
            assert isinstance(onto, Sequence)  # to satisfy type checking
            return MultiVectorABC.project(MultiVectorABC.outer_product(*onto))

        def fn(value: MultiVectorABC) -> MultiVectorABC:
            if value.is_scalar():  # 2.9b
                return value
            elif value.is_r_vector():  # 2.9c
                return (value.dot(onto)) * onto.inverse()
            else:
                return (value.dot(onto)).dot(onto.inverse())  # 2.9a

        return fn

    @staticmethod
    def reject(
        away_from: "MultiVectorABC" | Sequence["MultiVectorABC"],
    ) -> MultiVectorFn:
        """
        page 18
        """

        def r(value: MultiVectorABC) -> MultiVectorABC:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(away_from, MultiVectorABC)  # to satisfy type checking
            return (value.wedge(away_from)) * away_from.inverse()

        match away_from:
            case _ as sequence if isinstance(away_from, Sequence):
                assert isinstance(sequence, Sequence)  # to satisfy type checking
                return MultiVectorABC.reject(MultiVectorABC.outer_product(*sequence))
            case MultiVectorABC() as away_from_vector if away_from_vector.is_vector():
                return r
            case MultiVectorABC() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(away_from))

    @staticmethod
    def reflect(
        across: "MultiVectorABC" | Sequence["MultiVectorABC"],
    ) -> MultiVectorFn:
        components_in_plane: MultiVectorFn = MultiVectorABC.project(across)
        components_exterior_to_plane: MultiVectorFn = MultiVectorABC.reject(across)

        def r(value: MultiVectorABC) -> MultiVectorABC:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(across, MultiVectorABC)  # to satisfy type checking

            return components_in_plane(value) - components_exterior_to_plane(value)

        match across:
            case _ as sequence if isinstance(across, Sequence):
                assert isinstance(sequence, Sequence)  # to satisfy type checking
                return MultiVectorABC.reflect(MultiVectorABC.outer_product(*sequence))
            case MultiVectorABC() as away_from_vector if away_from_vector.is_vector():
                return r
            case MultiVectorABC() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(across))

    @staticmethod
    def rotate(
        from_vector: "MultiVectorABC",
        to_vector: "MultiVectorABC",
        angle_in_radians: None | float = None,
    ) -> MultiVectorFn:
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        plane: MultiVectorABC = from_vector ^ to_vector

        components_in_plane: MultiVectorFn = MultiVectorABC.project(plane)
        components_exterior_to_plane: MultiVectorFn = MultiVectorABC.reject(plane)

        if angle_in_radians is None:

            def r(value: MultiVectorABC) -> MultiVectorABC:
                assert value.is_vector()  # TODO - can this be generalized?
                return (
                    components_in_plane(value) * from_vector * to_vector
                ) + components_exterior_to_plane(value)

            return r
        else:
            c = sympy.cos(angle_in_radians)
            s = sympy.sin(angle_in_radians)

            parallel_in_plane: MultiVectorABC = from_vector.normalize()
            assert parallel_in_plane.is_vector()
            perpendicular_in_plane: MultiVectorABC = MultiVectorABC.reject(
                away_from=from_vector
            )(to_vector).normalize()
            assert perpendicular_in_plane.is_vector()

            def r(value: MultiVectorABC) -> MultiVectorABC:
                assert value.is_vector()  # TODO - can this be generalized?
                return (
                    components_in_plane(value)
                    * parallel_in_plane
                    * (c * parallel_in_plane + s * perpendicular_in_plane)
                ) + components_exterior_to_plane(value)

            return r
