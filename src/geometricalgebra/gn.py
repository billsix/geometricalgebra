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
import itertools
import math
import numbers
import typing
from typing import NamedTuple

import sympy

from geometricalgebra.base import AbstractMultiVector, BladeCoef


class BladeDictionaryEntry(NamedTuple):
    blade: tuple[int, ...]
    coefficient: numbers.Real

    def as_multivector(self):
        return Gn(coefficient_of_blade=dict([(self.blade, self.coefficient)]))


@dataclasses.dataclass
class Gn(AbstractMultiVector):
    """An element (multivector) of 𝒢ₙ, the geometric algebra of n-dimensional
    Euclidean space ℝⁿ (Hestenes' notation).

    𝒢ₙ has 2ⁿ basis blades.  This is the general, dimension-agnostic
    representation, storing a dict from blade (a tuple of basis-vector indices,
    e.g. ``(1, 2)`` ≙ e₁e₂) to coefficient.  G2 and G3 will be specialized,
    faster representations of 𝒢₂ and 𝒢₃.

    Terminology: 𝒢ₙ denotes the *algebra*; an instance of this class is an
    *element of* 𝒢ₙ.  The class is named after its algebra as a shorthand.

    This representation eagerly ``sympy.simplify``s every coefficient in
    ``__post_init__``.  That is the dominant cost (profiling shows ~100%), and
    it is kept here on purpose: Gn is allowed to be slow.  The specialized
    G2/G3 simplify lazily instead.
    """

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

    @classmethod
    def from_blade_dict(cls, blade_coef) -> "Gn":
        return cls(coefficient_of_blade=dict(blade_coef))

    def to_blade_dict(self) -> BladeCoef:
        return self.coefficient_of_blade

    def _geometric_product(self, rhs: "AbstractMultiVector") -> typing.Self:
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
                    sortedBladeDictionyEntriy: BladeDictionaryEntry = decrease_grade(
                        BladeDictionaryEntry(
                            blade=(c, *rest),
                            coefficient=basis_blade.coefficient,
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
        ) -> AbstractMultiVector:
            return b.as_multivector()

        product: "AbstractMultiVector" = sum(
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
                    rhs.to_blade_dict().items(),
                )
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, product)


# Backward-compatible alias: ``MultiVector`` is the general representation Gn.
# (Gn is the canonical name; AbstractMultiVector is the shared base type.)
MultiVector = Gn


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
            >>> foo = InvertibleFunction(f, f_inv, "", "")
            >>> foo  # doctest: +ELLIPSIS
            InvertibleFunction(...)
            >>> foo(5)
            7
            >>> inverse(foo)  # doctest: +ELLIPSIS
            InvertibleFunction(...)
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
            >>> foo = InvertibleFunction(f, f_inv, "", "")
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
        >>> foo = InvertibleFunction(f, f_inv, "", "")
        >>> foo  # doctest: +ELLIPSIS
        InvertibleFunction(...)
        >>> foo(5)
        7
        >>> inverse(foo)  # doctest: +ELLIPSIS
        InvertibleFunction(...)
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

    tex_str: str = f"T_{{{b._repr_latex_()[1:-1]}}}"
    inv_str: str = f"T_{{{(-b)._repr_latex_()[1:-1]}}}"
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
        return typing.cast(
            MultiVector,
            m_x * MultiVector.project(onto=e_1)(vector)
            + m_y * MultiVector.project(onto=e_2)(vector),
        )

    def f_inv(vector: MultiVector) -> MultiVector:
        if m_x == 0.0 or m_y == 0.0:
            raise ValueError("Note invertible.  Scaling factors cannot be zero.")

        return typing.cast(
            MultiVector,
            (m_x) ** (-1) * MultiVector.project(onto=e_1)(vector)
            + (m_y) ** (-1) * MultiVector.project(onto=e_2)(vector),
        )

    return InvertibleFunction(
        f,
        f_inv,
        f"S_{{{m_x},{m_y}}}",
        f"S_{{\\\frac{{1}}{{{m_x}}},\\\frac{{1}}{{{m_y}}}",
    )


# doc-region-begin define rotate
def rotate_90_degrees() -> InvertibleFunction:
    rot_90: MultiVector = e_1 * e_2

    def f(vector: MultiVector) -> MultiVector:
        return vector * rot_90

    def f_inv(vector: MultiVector) -> MultiVector:
        return vector * rot_90.inverse()

    return InvertibleFunction(f, f_inv, "R_{xy90}", "R_{xy90}^{-1}")


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
        f"R_{{{sympy.latex(angle_in_radians)}}}",
        f"R_{{{sympy.latex(-angle_in_radians)}}}",
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
    return float(inverse(rotate_90_degrees())(v1).cosine(v2)) > 0.000001
    # doc-region-end clockwise
