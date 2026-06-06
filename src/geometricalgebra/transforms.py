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

"""Representation-agnostic transform layer.

``InvertibleFunction`` wraps a function and its inverse (plus LaTeX labels) and
composes via ``compose`` / ``@``.  The transform *factories* (``translate``,
``uniform_scale``, ``scale_non_uniform``, ``rotate``, ...) are **representation
preserving**: each derives any basis vectors it needs from the *type of the
value it is applied to* (via the ``AbstractMultiVector`` interchange protocol --
``type(vector).basis_vector(i)``), so a ``G2`` in yields a ``G2`` out, a ``Gn``
in yields a ``Gn`` out, and so on.  Nothing here closes over a specific
representation's basis constants.

This module imports only ``base`` (the abstract base), never a concrete
representation, so it stays free of any single algebra.  ``gn.py`` re-exports
these names for backward compatibility.

The rotations (``rotate_90_degrees`` / ``rotate`` / ``rotate_around``) are
**inherently planar (2D)** -- they act in the e_1 e_2 plane.  The general
vector-to-vector rotation (any plane, any representation) is
``AbstractMultiVector.rotate``; the factories here are the planar 2D
specialization.  (Note the name overlap: ``transforms.rotate`` takes an angle,
``AbstractMultiVector.rotate`` takes a from/to vector pair.)
"""

import dataclasses
import math
import typing

import sympy

from geometricalgebra.base import AbstractMultiVector, MultiVectorFn


@dataclasses.dataclass
class InvertibleFunction:
    """Wraps a function and its inverse function.

    The function takes a value and returns a value of the same type.
    """

    func: typing.Callable[
        [AbstractMultiVector], AbstractMultiVector
    ]  #: The wrapped function
    inverse: typing.Callable[
        [AbstractMultiVector], AbstractMultiVector
    ]  #: The inverse of the wrapped function
    latex_repr: str  #: The LaTeX representation of the function
    latex_repr_inv: str  #: The LaTeX representation of the inverse function

    def __call__(self, x: AbstractMultiVector) -> AbstractMultiVector:
        """Execute the wrapped function on ``x`` (result has the same type as ``x``).

        Example:
            >>> from geometricalgebra.transforms import InvertibleFunction, inverse
            >>> foo = InvertibleFunction(lambda x: 2 + x, lambda x: x - 2, "", "")
            >>> foo  # doctest: +ELLIPSIS
            InvertibleFunction(...)
            >>> foo(5)
            7
            >>> inverse(foo)(foo(5))
            5
        """
        return self.func(x)

    def __matmul__(self, f2: "InvertibleFunction") -> "InvertibleFunction":
        """Override ``@`` for function composition (``self`` after ``f2``).

        Example:
            >>> from geometricalgebra.transforms import InvertibleFunction, inverse
            >>> foo = InvertibleFunction(lambda x: 2 + x, lambda x: x - 2, "", "")
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


def inverse(f: InvertibleFunction) -> InvertibleFunction:
    """Get the inverse of the ``InvertibleFunction``.

    Example:
        >>> from geometricalgebra.transforms import InvertibleFunction, inverse
        >>> foo = InvertibleFunction(lambda x: 2 + x, lambda x: x - 2, "", "")
        >>> inverse(foo)(foo(5))
        5
    """
    return InvertibleFunction(f.inverse, f.func, f.latex_repr_inv, f.latex_repr)


def compose(
    functions: list[InvertibleFunction],
) -> InvertibleFunction:
    r"""Compose a sequence of functions.

    For two functions :math:`f` and :math:`g`, ``compose([f, g])`` is
    :math:`(f \circ g)(x) = f(g(x))` -- i.e. the last function in the list is
    applied first.

    Example:
        >>> from geometricalgebra.transforms import compose, InvertibleFunction
        >>> add2 = InvertibleFunction(lambda x: x + 2, lambda x: x - 2, "", "")
        >>> scale3 = InvertibleFunction(lambda x: x * 3, lambda x: x / 3, "", "")
        >>> fn = compose([scale3, add2])   # scale3(add2(x)) = 3 * (x + 2)
        >>> fn(1)
        9
        >>> inverse(fn)(9)
        1.0
    """

    def composed_fn(x):
        for f in reversed(functions):
            x = f(x)
        return x

    def inv_composed_fn(x):
        for f in functions:
            x = inverse(f)(x)
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
    """Like ``compose``, but returns each of the partial compositions.

    Example:
        >>> from geometricalgebra.transforms import (
        ...     compose_intermediate_fns,
        ...     InvertibleFunction,
        ... )
        >>> add2 = InvertibleFunction(lambda x: x + 2, lambda x: x - 2, "", "")
        >>> scale5 = InvertibleFunction(lambda x: x * 5, lambda x: x / 5, "", "")
        >>> # natural basis: scale5(add2(x))
        >>> fns = compose_intermediate_fns([add2, scale5])
        >>> len(fns)
        3
        >>> [fns[0](1), fns[1](1), fns[2](1)]
        [1, 5, 7]
        >>> # relative basis
        >>> fns = compose_intermediate_fns([add2, scale5], relative_basis=True)
        >>> [fns[0](1), fns[1](1), fns[2](1)]
        [1, 3, 7]
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
    """Like ``compose_intermediate_fns``, paired with the function applied at each step.

    Example:
        >>> from geometricalgebra.transforms import (
        ...     compose_intermediate_fns_and_fn,
        ...     InvertibleFunction,
        ... )
        >>> add2 = InvertibleFunction(lambda x: x + 2, lambda x: x - 2, "", "")
        >>> scale5 = InvertibleFunction(lambda x: x * 5, lambda x: x / 5, "", "")
        >>> for aggregate_fn, current_fn in compose_intermediate_fns_and_fn(
        ...         [add2, scale5]):
        ...     print(aggregate_fn(1), current_fn(1))
        1 5
        5 3
        7 1
    """
    return list(
        zip(
            compose_intermediate_fns(functions, relative_basis=relative_basis),
            [identity()] + functions
            if relative_basis
            else reversed([identity()] + functions),
        )
    )


def identity() -> InvertibleFunction:
    def f(vector: AbstractMultiVector) -> AbstractMultiVector:
        return vector

    def f_inv(vector: AbstractMultiVector) -> AbstractMultiVector:
        return vector

    return InvertibleFunction(f, f_inv, "I", "I")


def translate(b: AbstractMultiVector) -> InvertibleFunction:
    """Translate by ``b``.  The result has the same representation as ``b``."""

    def f(vector: AbstractMultiVector) -> AbstractMultiVector:
        return vector + b

    def f_inv(vector: AbstractMultiVector) -> AbstractMultiVector:
        return vector - b

    tex_str: str = f"T_{{{b._repr_latex_()[1:-1]}}}"
    inv_str: str = f"T_{{{(-b)._repr_latex_()[1:-1]}}}"
    return InvertibleFunction(f, f_inv, tex_str, inv_str)


def uniform_scale(m: float) -> InvertibleFunction:
    """Scale uniformly by ``m`` (representation preserving -- just ``vector * m``)."""

    def f(vector: AbstractMultiVector) -> AbstractMultiVector:
        return vector * m

    def f_inv(vector: AbstractMultiVector) -> AbstractMultiVector:
        if m == 0.0:
            raise ValueError("Not invertible.  Scaling factor cannot be zero.")

        return vector * (1.0 / m)

    tex_str: str = f"S_{{{m}}}"
    inv_str: str = f"S_{{{-m}}}"
    return InvertibleFunction(f, f_inv, tex_str, inv_str)


def scale_non_uniform(*factors: float) -> InvertibleFunction:
    """Scale axis ``i`` by ``factors[i]`` (1-indexed e_1, e_2, ...), in any dimension.

    Representation preserving: the basis vectors are taken from the type of the
    value being transformed, so a ``G2``/``G3``/``Gn`` value scales to its own
    type.  ``scale_non_uniform_2d`` is the 2D special case.
    """

    def f(vector: AbstractMultiVector) -> AbstractMultiVector:
        cls: type[AbstractMultiVector] = type(vector)
        return sum(
            (
                m * cls.project(onto=cls.basis_vector(i + 1))(vector)
                for i, m in enumerate(factors)
            ),
            start=cls.zero(),
        )

    def f_inv(vector: AbstractMultiVector) -> AbstractMultiVector:
        if any(m == 0.0 for m in factors):
            raise ValueError("Not invertible.  Scaling factors cannot be zero.")

        cls: type[AbstractMultiVector] = type(vector)
        return sum(
            (
                (1.0 / m) * cls.project(onto=cls.basis_vector(i + 1))(vector)
                for i, m in enumerate(factors)
            ),
            start=cls.zero(),
        )

    forward = "S_{" + ",".join(str(m) for m in factors) + "}"
    inv = "S_{" + ",".join(rf"\frac{{1}}{{{m}}}" for m in factors) + "}"
    return InvertibleFunction(f, f_inv, forward, inv)


def scale_non_uniform_2d(m_x: float, m_y: float) -> InvertibleFunction:
    """2D non-uniform scale (thin wrapper over the n-D ``scale_non_uniform``)."""
    return scale_non_uniform(m_x, m_y)


def rotate_90_degrees() -> InvertibleFunction:
    """Rotate a vector 90 degrees in the e_1 e_2 plane (inherently 2D).

    Representation preserving: the unit bivector e_1 e_2 is built from the type
    of the value being rotated.
    """

    def f(vector: AbstractMultiVector) -> AbstractMultiVector:
        rot_90: AbstractMultiVector = type(vector).from_blade_dict({(1, 2): 1})
        return vector * rot_90

    def f_inv(vector: AbstractMultiVector) -> AbstractMultiVector:
        rot_90: AbstractMultiVector = type(vector).from_blade_dict({(1, 2): 1})
        return vector * rot_90.inverse()

    return InvertibleFunction(f, f_inv, "R_{xy90}", "R_{xy90}^{-1}")


def rotate(angle_in_radians: float) -> InvertibleFunction:
    """Rotate a vector by ``angle_in_radians`` in the e_1 e_2 plane (inherently 2D)."""
    r90: InvertibleFunction = rotate_90_degrees()

    def create_rotate_function(
        perp: InvertibleFunction,
    ) -> typing.Callable[[AbstractMultiVector], AbstractMultiVector]:
        def f(vector: AbstractMultiVector) -> AbstractMultiVector:
            parallel: AbstractMultiVector = math.cos(float(angle_in_radians)) * vector
            perpendicular: AbstractMultiVector = math.sin(
                float(angle_in_radians)
            ) * perp(vector)
            return parallel + perpendicular

        return f

    return InvertibleFunction(
        create_rotate_function(r90),
        create_rotate_function(inverse(r90)),
        f"R_{{{sympy.latex(angle_in_radians)}}}",
        f"R_{{{sympy.latex(-angle_in_radians)}}}",
    )


def rotate_around(
    angle_in_radians: float, center: AbstractMultiVector
) -> InvertibleFunction:
    """Rotate by ``angle_in_radians`` about ``center`` in the e_1 e_2 plane (2D)."""
    return compose([translate(center), rotate(angle_in_radians), translate(-center)])


def is_counter_clockwise(v1: AbstractMultiVector, v2: AbstractMultiVector) -> bool:
    return not is_clockwise(v1, v2)


def is_clockwise(v1: AbstractMultiVector, v2: AbstractMultiVector) -> bool:
    plane: AbstractMultiVector = type(v1).from_blade_dict({(1, 2): 1})
    assert type(v1).project(onto=plane)(v1) == v1
    assert type(v2).project(onto=plane)(v2) == v2
    return float(inverse(rotate_90_degrees())(v1).cosine(v2)) > 0.000001


__all__ = [
    "InvertibleFunction",
    "inverse",
    "compose",
    "compose_intermediate_fns",
    "compose_intermediate_fns_and_fn",
    "identity",
    "translate",
    "uniform_scale",
    "scale_non_uniform",
    "scale_non_uniform_2d",
    "rotate_90_degrees",
    "rotate",
    "rotate_around",
    "is_clockwise",
    "is_counter_clockwise",
    "MultiVectorFn",
]
