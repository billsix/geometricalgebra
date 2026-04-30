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
from collections.abc import Callable, Generator, Sequence
from itertools import chain, combinations
from typing import NamedTuple, TypeIs

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
    def identity() -> MultiVectorFn:
        def i(value: MultiVector) -> MultiVector:
            return value

        return i

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


# doc-region-begin begin define invertible function
@dataclasses.dataclass
class InvertibleFunction:
    # doc-region-end begin define invertible function
    """
    Class that wraps a function and its
    inverse function.  The function takes
    type T as it's argument and it's evaluation
    results in a value of type T.
    """

    # doc-region-begin invertible function members
    func: typing.Callable[[MultiVector], MultiVector]  #: The wrapped function
    inverse: typing.Callable[
        [MultiVector], MultiVector
    ]  #: The inverse of the wrapped function
    latex_repr: str  #: The LaTeX representation of the function
    latex_repr_inv: str  #: The LaTeX representation of the inverse function
    # doc-region-end invertible function members

    # doc-region-begin begin call
    def __call__(self, x: MultiVector) -> MultiVector:
        # doc-region-end begin call
        """
        Execute a function with the given value.

        Args:
            func (typing.Callable[[Vector], Vector]): A function that takes a
                value of type Vector and returns a value of the same type Vector.
            value (Vector): The input value to pass to the function
        Returns:
            Vector: The result of calling func(value).

            Will be the same type as the input value.
        Example:
            >>> from modelviewprojection.mathutils import InvertibleFunction
            >>> from modelviewprojection.mathutils import inverse
            >>> def f(x):
            ...     return 2 + x
            ...
            >>> def f_inv(x):
            ...     return x - 2
            ...
            >>> foo = InvertibleFunction(func=f, inverse=f_inv, latex_repr="", latex_repr_inv="")
            >>> foo # doctest: +ELLIPSIS
            InvertibleFunction(func=<...>, inverse=<...>, latex_repr=..., latex_repr_inv=...)
            >>> foo(5)
            7
            >>> inverse(foo) # doctest: +ELLIPSIS
            InvertibleFunction(func=<...>, inverse=<...>, latex_repr=..., latex_repr_inv=...)
            >>> inverse(foo)(foo(5))
            5
        """
        # doc-region-begin call definition
        return self.func(x)
        # doc-region-end call definition

    def __matmul__(self, f2: "InvertibleFunction") -> "InvertibleFunction":
        """
        Override @ for function composition.  This is abusing the @ symbol,
        which is normally for matrix multiplication.

        Args:
            f2 (mathutils.InvertibleFunction): A function that self is composed with
                and returns a value of the same type Vector.
        Returns:
            InvertibleFunction: The composed function.

        Example:
            >>> from modelviewprojection.mathutils import InvertibleFunction
            >>> from modelviewprojection.mathutils import inverse
            >>> def f(x):
            ...     return 2 + x
            ...
            >>> def f_inv(x):
            ...     return x - 2
            ...
            >>> foo = InvertibleFunction(func=f, inverse=f_inv, latex_repr="", latex_repr_inv="")
            >>> foo(5)
            7
            >>> (foo @ foo)(5)
            9
            >>> inverse(foo @ foo)(5)
            1
            >>> (foo @ inverse(foo))(5)
            5
        """
        return compose([self, f2])

    def __rmatmul__(self, f2: "InvertibleFunction") -> "InvertibleFunction":
        return f2 @ self

    def _repr_latex_(self):
        return "$" + self.latex_repr + "$"


# doc-region-begin begin define inverse
def inverse(f: InvertibleFunction) -> InvertibleFunction:
    # doc-region-end begin define inverse
    """
    Get the inverse of the InvertibleFunction

    Args:
        f: InvertibleFunction: A function with it's associated inverse
            function.
    Returns:
        InvertibleFunction: The Inverse of the function.
    Example:
        >>> from modelviewprojection.mathutils import InvertibleFunction
        >>> from modelviewprojection.mathutils import inverse
        >>> def f(x):
        ...     return 2 + x
        ...
        >>> def f_inv(x):
        ...     return x - 2
        ...
        >>> foo = InvertibleFunction(func=f, inverse=f_inv, latex_repr="", latex_repr_inv="")
        >>> foo # doctest: +ELLIPSIS
        InvertibleFunction(func=<...>, inverse=<...>, latex_repr=..., latex_repr_inv=...)
        >>> foo(5)
        7
        >>> inverse(foo) # doctest: +ELLIPSIS
        InvertibleFunction(func=<...>, inverse=<...>, latex_repr=..., latex_repr_inv=...)
        >>> inverse(foo)(foo(5))
        5
    """

    # doc-region-begin inverse body
    return InvertibleFunction(f.inverse, f.func, f.latex_repr_inv, f.latex_repr)
    # doc-region-end inverse body


def compose(
    functions: list[InvertibleFunction],
) -> InvertibleFunction:
    """
    Compose a sequence of functions.

    If two functions are passed as arguments, named :math:`f` and :math:`g`:

        :math:`(f \\circ g)(x) = f(g(x))`.

    If :math:`n` functions are passed as arguments, :math:`f_1...f_n`:

        :math:`(f_1 \\circ (f_2 \\circ (... f_n )(x) = f_1(f_2...(f_n(x))`.

    Args:
        functions (list[InvertibleFunction]): Variable number of
            InvertibleFunctions to compose.  At least on value must be provided.

    Returns:
        Vector: One function that is the aggregate function.

    Example:
        >>> from modelviewprojection.mathutils import compose
        >>> from modelviewprojection.mathutils import translate as T
        >>> from modelviewprojection.mathutils import uniform_scale as S
        >>> from modelviewprojection.mathutils import Vector2D
        >>> fn = compose([S(2), T(Vector2D(3, 4))])
        >>> fn(Vector2D(1,1))
        Vector2D(x=8, y=10)
    """

    def composed_fn(x):
        for f in reversed(functions):
            x: MultiVector = f(x)
        return x

    def inv_composed_fn(x):
        for f in functions:
            x: MultiVector = inverse(f)(x)
        return x

    tex_str: str = ""
    for f in reversed(functions):
        if tex_str == "":
            tex_str = f.latex_repr
        else:
            tex_str = f.latex_repr + r" \circ " + tex_str

    inv_str: str = ""
    for f in functions:
        if inv_str == "":
            inv_str = inverse(f).latex_repr
        else:
            inv_str = inverse(f).latex_repr + r" \circ " + inv_str

    return InvertibleFunction(composed_fn, inv_composed_fn, tex_str, inv_str)


def compose_intermediate_fns(
    functions: list[InvertibleFunction], relative_basis: bool = False
) -> typing.Iterable[InvertibleFunction]:
    """
    Like compose, but returns a list of all of the partial compositions

    Example:
        >>> from modelviewprojection.mathutils import compose_intermediate_fns
        >>> from modelviewprojection.mathutils import InvertibleFunction
        >>> from modelviewprojection.mathutils import uniform_scale
        >>> from modelviewprojection.mathutils import translate
        >>> from modelviewprojection.mathutils import Vector1D
        >>> from pytest import approx
        >>> m = 5
        >>> b = 2
        >>> # natural basis
        >>> fns: list[InvertibleFunction] = compose_intermediate_fns(
        ...      [translate(Vector1D(b)), uniform_scale(m)]
        ... )
        >>> len(fns)
        3
        >>> fns[0](Vector1D(1))
        Vector1D(x=1)
        >>> fns[1](Vector1D(1))
        Vector1D(x=5)
        >>> fns[2](Vector1D(1))
        Vector1D(x=7)
        >>> # relative basis
        >>> fns: list[InvertibleFunction] = compose_intermediate_fns(
        ...     [translate(Vector1D(b)), uniform_scale(m)], relative_basis=True
        ... )
        >>> len(fns)
        3
        >>> fns[0](Vector1D(1))
        Vector1D(x=1)
        >>> fns[1](Vector1D(1))
        Vector1D(x=3)
        >>> fns[2](Vector1D(1))
        Vector1D(x=7)
    """
    functions_with_identity_fn: list[InvertibleFunction] = (
        [identity()] + functions if relative_basis else functions + [identity()]
    )

    return [
        compose(fs)
        for fs in (
            [
                functions_with_identity_fn[i:]
                for i in reversed(range(len(functions_with_identity_fn)))
            ]
            if not relative_basis
            else [
                functions_with_identity_fn[:i]
                for i in range(1, len(functions_with_identity_fn) + 1)
            ]
        )
    ]


def compose_intermediate_fns_and_fn(
    functions: list[InvertibleFunction], relative_basis: bool = False
) -> list[tuple[InvertibleFunction, InvertibleFunction]]:
    """
    Like compose, but returns a list of all of the partial compositions

    Example:
        >>> from modelviewprojection.mathutils import compose_intermediate_fns_and_fn
        >>> from modelviewprojection.mathutils import InvertibleFunction
        >>> from modelviewprojection.mathutils import uniform_scale
        >>> from modelviewprojection.mathutils import translate
        >>> from modelviewprojection.mathutils import Vector1D
        >>> from pytest import approx
        >>> m = 5
        >>> b = 2
        >>> # natural basis
        >>> for aggregate_fn, current_fn in compose_intermediate_fns_and_fn(
        ...      [translate(Vector1D(b)), uniform_scale(m)]):
        ...      print("agg " + str(aggregate_fn(Vector1D(1))))
        ...      print("current " + str(current_fn(Vector1D(1))))
        ...
        agg Vector1D(x=1)
        current Vector1D(x=5)
        agg Vector1D(x=5)
        current Vector1D(x=3)
        agg Vector1D(x=7)
        current Vector1D(x=1)
        >>> # relative basis
        >>> for aggregate_fn, current_fn in compose_intermediate_fns_and_fn(
        ...      [translate(Vector1D(b)), uniform_scale(m)], relative_basis=True):
        ...      print("agg " + str(aggregate_fn(Vector1D(1))))
        ...      print("current " + str(current_fn(Vector1D(1))))
        ...
        agg Vector1D(x=1)
        current Vector1D(x=1)
        agg Vector1D(x=3)
        current Vector1D(x=3)
        agg Vector1D(x=7)
        current Vector1D(x=5)
    """
    return list(
        zip(
            compose_intermediate_fns(functions, relative_basis=relative_basis),
            [identity()] + functions
            if relative_basis
            else reversed([identity()] + functions),
        )
    )


# doc-region-begin define identity
def identity() -> InvertibleFunction:
    def f(vector: MultiVector) -> MultiVector:
        return vector

    def f_inv(vector: MultiVector) -> MultiVector:
        return vector

    tex_str: str = "I"
    inv_str: str = "I"
    return InvertibleFunction(f, f_inv, tex_str, inv_str)
    # doc-region-end define identity


# doc-region-begin define translate
def translate(b: MultiVector) -> InvertibleFunction:
    def f(vector: MultiVector) -> MultiVector:
        return vector + b

    def f_inv(vector: MultiVector) -> MultiVector:
        return vector - b

    tex_str: str = f"T_{{<{b._repr_latex_()[1:-1]}>}}"
    inv_str: str = f"T_{{<{(-b)._repr_latex_()[1:-1]}>}}"
    return InvertibleFunction(f, f_inv, tex_str, inv_str)
    # doc-region-end define translate


# doc-region-begin define uniform scale
def uniform_scale(m: float) -> InvertibleFunction:
    def f(vector: MultiVector) -> MultiVector:
        return vector * m

    def f_inv(vector: MultiVector) -> MultiVector:
        if m == 0.0:
            raise ValueError("Not invertible.  Scaling factor cannot be zero.")

        return vector * (1.0 / m)

    tex_str: str = f"S_{{{m}}}"
    inv_str: str = f"S_{{{-m}}}"
    return InvertibleFunction(f, f_inv, tex_str, inv_str)
    # doc-region-end define uniform scale


def scale_non_uniform_2d(m_x: float, m_y: float) -> InvertibleFunction:
    def f(vector: MultiVector) -> MultiVector:
        return m_x * MultiVector.project(onto=e_1)(vector) + m_y * MultiVector.project(
            onto=e_2
        )(vector)

    def f_inv(vector: MultiVector) -> MultiVector:
        if m_x == 0.0 or m_y == 0.0:
            raise ValueError("Note invertible.  Scaling factors cannot be zero.")

        return (m_x) ** (-1) * MultiVector.project(onto=e_1)(vector) + (m_y) ** (
            -1
        ) * MultiVector.project(onto=e_2)(vector)

    return InvertibleFunction(
        f,
        f_inv,
        f"S_{{<{m_x},{m_y}>}}",
        f"S_{{<\\\frac{{1}}{{{m_x}}},\\\frac{{1}}{{{m_y}>}}",
    )


# doc-region-begin define rotate
def rotate_90_degrees() -> InvertibleFunction:
    rot_90: MultiVector = e_1 * e_2

    def f(vector: MultiVector) -> MultiVector:
        return vector * rot_90

    def f_inv(vector: MultiVector) -> MultiVector:
        return vector * rot_90.inverse()

    return InvertibleFunction(f, f_inv, "R_{<xy90>}", "R_{<xy90>}^{-1}")


def rotate(angle_in_radians: float) -> InvertibleFunction:
    r90: InvertibleFunction = rotate_90_degrees()

    def create_rotate_function(
        perp: InvertibleFunction,
    ) -> typing.Callable[[MultiVector], MultiVector]:
        def f(vector: MultiVector) -> MultiVector:
            parallel: MultiVector = math.cos(float(angle_in_radians)) * vector
            perpendicular: MultiVector = math.sin(float(angle_in_radians)) * perp(
                vector
            )
            return parallel + perpendicular

        return f

    return InvertibleFunction(
        create_rotate_function(r90),
        create_rotate_function(inverse(r90)),
        f"R_{{<{sympy.latex(angle_in_radians)}>}}",
        f"R_{{<{sympy.latex(-angle_in_radians)}>}}",
    )
    # doc-region-end define rotate


# doc-region-begin define rotate around
def rotate_around(angle_in_radians: float, center: MultiVector) -> InvertibleFunction:
    return compose([translate(center), rotate(angle_in_radians), translate(-center)])
    # doc-region-end define rotate around


# doc-region-begin counter clockwise
def is_counter_clockwise(v1: MultiVector, v2: MultiVector) -> bool:
    return not is_clockwise(v1, v2)
    # doc-region-end counter clockwise


# doc-region-begin clockwise
def is_clockwise(v1: MultiVector, v2: MultiVector) -> bool:
    assert MultiVector.project(onto=e_1 * e_2)(v1) == v1
    assert MultiVector.project(onto=e_1 * e_2)(v2) == v2
    return float(inverse(rotate_90_degrees())(v1).cosine(v2)) > 0.000001  # type: ignore
    # doc-region-end clockwise
