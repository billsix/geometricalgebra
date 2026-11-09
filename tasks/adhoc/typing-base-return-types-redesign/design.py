# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

"""Toy model of gacalc's typing: base, full class, graded types, generic transforms."""

from __future__ import annotations

import typing
from collections.abc import Callable
from typing import Protocol, Self, overload

Real = int | float


class Base:
    # Honest base: a number times x keeps x's type; a product with another
    # multivector is only known to be *some* multivector.
    @overload
    def __mul__(self, rhs: Real) -> Self: ...
    @overload
    def __mul__(self, rhs: Base) -> Base: ...
    def __mul__(self, rhs: Real | Base) -> Self | Base:
        return self

    def __rmul__(self, lhs: Real) -> Self:
        return self

    @overload
    def __add__(self, rhs: Self) -> Self: ...
    @overload
    def __add__(self, rhs: Base | Real) -> Base: ...
    def __add__(self, rhs: Base | Real) -> Self | Base:
        return self

    def reverse(self) -> Self:  # a grade-preserving map really is Self
        return self


class Gn(Base):
    # The reference representation: every operation with a Gn stays a Gn.
    if typing.TYPE_CHECKING:

        @overload
        def __mul__(self, rhs: Real) -> Self: ...
        @overload
        def __mul__(self, rhs: Base) -> Gn: ...
        def __mul__(self, rhs: Real | Base) -> Self | Gn: ...

        @overload
        def __add__(self, rhs: Self) -> Self: ...
        @overload
        def __add__(self, rhs: Base | Real) -> Gn: ...
        def __add__(self, rhs: Base | Real) -> Self | Gn: ...


class Versor(Base): ...


class Scalar(Base): ...


class G(Base):
    @overload
    def __mul__(self, rhs: Real) -> G: ...
    @overload
    def __mul__(self, rhs: Gn) -> Gn: ...
    @overload
    def __mul__(self, rhs: Base) -> G: ...
    def __mul__(self, rhs: Real | Base) -> Base:
        return self


@typing.final
class Vector(Base):
    @overload
    def __mul__(self, rhs: Real) -> Vector: ...
    @overload
    def __mul__(self, rhs: Vector) -> Versor: ...
    @overload
    def __mul__(self, rhs: Base) -> Base: ...
    def __mul__(self, rhs: Real | Base) -> Base:
        return self

    @overload
    def __add__(self, rhs: Vector) -> Vector: ...
    @overload
    def __add__(self, rhs: Base | Real) -> G: ...
    def __add__(self, rhs: Base | Real) -> Base:
        return self


# --- a Protocol for the operations that keep a type closed: the linear-space ones
class LinearSpace(Protocol):
    def __add__(self, rhs: Self, /) -> Self: ...
    def __rmul__(self, lhs: Real, /) -> Self: ...


def translate[V: LinearSpace](b: V) -> Callable[[V], V]:
    def f(v: V) -> V:
        return v + b

    return f


def uniform_scale[V: LinearSpace](m: Real) -> Callable[[V], V]:
    def f(v: V) -> V:
        return m * v

    return f


# --- uses
v: Vector = Vector()
w: Vector = v + v
R: Versor = v * v
s: Vector = 2 * v
g: Gn = Gn() * Gn()
t: Vector = translate(v)(v)
u: Gn = translate(Gn())(Gn())
z: Vector = uniform_scale(3)(v)
