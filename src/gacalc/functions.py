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

"""Domain-agnostic composable-function layer -- a **leaf** module.

This module holds the function-composition abstraction, split by *capability*:

* :class:`ComposableFunction` -- a function you can **compose** (via ``@`` /
  :func:`compose`) and **label with LaTeX** (``latex_repr``, ``_repr_latex_``),
  plus a linear/affine/non-linear :class:`Linearity` classification and an
  animation layer (``at`` / ``steps``).  It makes **no** promise of an inverse.
* :class:`InvertibleFunction` -- the ``ComposableFunction`` *subtype* that adds
  an ``inverse`` (and ``latex_repr_inv``).  This is the type consumers that
  require invertibility (e.g. a Cayley-graph edge, traversed backward) must ask
  for; a non-invertible function simply is not one, which is a *type* error at
  that boundary rather than a runtime surprise.

It **imports nothing internal** -- that is what keeps the package's core
dependency graph acyclic and lets ``base.py`` import it (so ``project`` /
``reject`` can return a ``ComposableFunction``).  Consequently its type variable
``V`` is **unbounded** (binding it to ``MultiVectorBase`` would force this module
to import ``base`` and reintroduce a cycle); the abstraction is genuinely
domain-agnostic anyway (the doctests below run it on plain ``int``s).  See the
"Layering" note in ``CLAUDE.md``.
"""

import dataclasses
import typing
from enum import IntEnum

#: Unbounded type variable for the value a function transforms.  Unbounded on
#: purpose: this module must not import ``base`` (see the module docstring), so
#: ``V`` cannot be bound to ``MultiVectorBase``.
V = typing.TypeVar("V")


class Linearity(IntEnum):
    """How structured a transform is, as a total order ``LINEAR < AFFINE <
    NONLINEAR``.  Int-backed so the *join* (the class of a composite) is just
    ``max(...)``: a composite is as general as its most-general part.

    * ``LINEAR``    -- fixes the origin, ``f(x) = A x`` (rotations, scales).
    * ``AFFINE``    -- linear + a translation, ``f(x) = A x + b``.
    * ``NONLINEAR`` -- anything else (e.g. a perspective divide).  Also the
      conservative default for a hand-built function with no declared class.
    """

    LINEAR = 0
    AFFINE = 1
    NONLINEAR = 2


class NotInvertibleError(Exception):
    """Raised when :func:`inverse` is asked for the inverse of a function that
    does not have one -- a bare :class:`ComposableFunction` (e.g. a labelled
    projection or rejection), or a :func:`compose` pipeline containing one.
    Invertibility is a *type* distinction (``InvertibleFunction`` vs
    ``ComposableFunction``); this is the runtime backstop when that distinction
    is bypassed."""


@dataclasses.dataclass
class ComposableFunction(typing.Generic[V]):
    """A composable, LaTeX-labelled function ``V -> V`` with **no** inverse.

    Compose with ``@`` / :func:`compose`, render with ``_repr_latex_``,
    interpolate with :meth:`at`, flatten with :meth:`steps`.  ``InvertibleFunction``
    extends this with an inverse; anything that only needs "compose + label"
    (e.g. a labelled ``project`` / ``reject``) is exactly this base type.
    """

    func: typing.Callable[[V], V]  #: The wrapped function
    latex_repr: str  #: The LaTeX representation of the function
    #: Optional interpolation law: maps ``t`` in ``[0, 1]`` to the
    #: partially-applied function, with ``at(0)`` the identity and ``at(1)``
    #: this function.  Bound by the transform primitives; ``None`` otherwise.
    interpolate: typing.Callable[[float], "ComposableFunction[V]"] | None = (
        dataclasses.field(default=None, kw_only=True)
    )
    #: For composites built by :func:`compose`: the constituent functions, in
    #: application order (lets :meth:`at` / :meth:`steps` recurse).
    components: typing.Sequence["ComposableFunction[V]"] | None = dataclasses.field(
        default=None, kw_only=True
    )
    #: linear / affine / non-linear classification (see :class:`Linearity`).
    linearity: Linearity = dataclasses.field(default=Linearity.NONLINEAR, kw_only=True)

    def __call__(self, x: V) -> V:
        """Execute the wrapped function on ``x`` (result has the same type as ``x``).

        Example:
            >>> from gacalc.functions import ComposableFunction
            >>> double = ComposableFunction(lambda x: 2 * x, "D")
            >>> double(5)
            10
        """
        return self.func(x)

    def __matmul__(self, f2: "ComposableFunction[V]") -> "ComposableFunction[V]":
        """Override ``@`` for function composition (``self`` after ``f2``).

        Example:
            >>> from gacalc.functions import InvertibleFunction, inverse
            >>> foo = InvertibleFunction(lambda x: 2 + x, "", lambda x: x - 2, "")
            >>> (foo @ foo)(5)
            9
            >>> inverse(foo @ foo)(5)
            1
            >>> (foo @ inverse(foo))(5)
            5
        """
        return compose([self, f2])

    def __rmatmul__(self, f2: "ComposableFunction[V]") -> "ComposableFunction[V]":
        return f2 @ self

    def _repr_latex_(self) -> str:
        return "$" + self.latex_repr + "$"

    def at(self, t: float) -> "ComposableFunction[V]":
        """The function interpolated at parameter ``t`` in ``[0, 1]``, where
        ``at(0)`` is the identity and ``at(1)`` is the function itself.

        Resolution order: a primitive carries an :attr:`interpolate` law -> use
        it; a composite (from :func:`compose`) has no law -> recurse into its
        :attr:`components`, interpolating each and re-composing; otherwise (a
        hand-built function with neither) -> a step: the identity until
        ``t >= 1``, then the function itself.

        Example:
            >>> from gacalc.transforms import translate, compose, uniform_scale
            >>> from gacalc.g3 import Vector3
            >>> T = translate(10 * Vector3.e_1)
            >>> T.at(0.5)(Vector3.zero()).is_close(5 * Vector3.e_1)
            True
        """
        if self.interpolate is not None:
            return self.interpolate(t)
        if self.components is not None:
            return compose([c.at(t) for c in self.components])
        return self if t >= 1.0 else identity()

    def steps(self) -> "typing.Iterator[ComposableFunction[V]]":
        """Yield the leaf primitives in application order, flattening nested
        compositions.  A primitive yields itself; a composite yields its
        components' leaves recursively.

        Example:
            >>> from gacalc.transforms import compose, translate, uniform_scale
            >>> from gacalc.g3 import Vector3
            >>> f = compose([translate(Vector3.e_1), uniform_scale(2.0)])
            >>> len(list(f.steps()))
            2
        """
        if self.components is None:
            yield self
        else:
            for c in self.components:
                yield from c.steps()


@dataclasses.dataclass
class InvertibleFunction(ComposableFunction[V]):
    """A :class:`ComposableFunction` that also carries an ``inverse``.

    Same interface as the base (compose, label, ``at`` / ``steps``), plus a real
    inverse -- so it is the type to require where a function must be reversible
    (a Cayley-graph edge walked backward, an animation played in reverse).

    Note the constructor is keyword-friendliest as
    ``InvertibleFunction(func=..., latex_repr=..., inverse=..., latex_repr_inv=...)``;
    positionally the order is ``(func, latex_repr, inverse, latex_repr_inv)`` with
    ``linearity`` / ``interpolate`` / ``components`` keyword-only.
    """

    inverse: typing.Callable[[V], V]  #: The inverse of the wrapped function
    latex_repr_inv: str  #: The LaTeX representation of the inverse

    def at(self, t: float) -> "InvertibleFunction[V]":
        """Interpolate — narrower return than the base: an invertible function's
        interpolation (its law, its inverted components, or the identity) is
        itself invertible, so callers can keep inverting without a cast."""
        return typing.cast("InvertibleFunction[V]", super().at(t))

    @typing.overload
    def __matmul__(self, f2: "InvertibleFunction[V]") -> "InvertibleFunction[V]": ...
    @typing.overload
    def __matmul__(self, f2: "ComposableFunction[V]") -> "ComposableFunction[V]": ...
    def __matmul__(self, f2: "ComposableFunction[V]") -> "ComposableFunction[V]":
        """Compose — same narrowing as :meth:`at`, and the operator form of what
        :func:`compose` already promises via *its* overloads: invertible @
        invertible is invertible.  Without this, ``a @ b`` on two
        ``InvertibleFunction``s typed as a bare ``ComposableFunction``, so
        assigning it to an ``InvertibleFunction`` was a type error even though
        the value returned at runtime *is* invertible (``__matmul__`` delegates
        to ``compose``, which resolves invertibility from the parts).  Composing
        with a non-invertible function still yields a ``ComposableFunction``.

        Example:
            >>> from gacalc.functions import InvertibleFunction, inverse
            >>> foo = InvertibleFunction(lambda x: 2 + x, "", lambda x: x - 2, "")
            >>> isinstance(foo @ foo, InvertibleFunction)
            True
            >>> inverse(foo @ foo)(9)
            5
        """
        return super().__matmul__(f2)


def inverse(f: InvertibleFunction[V]) -> InvertibleFunction[V]:
    """Get the inverse of an :class:`InvertibleFunction`.

    Raises :class:`NotInvertibleError` if ``f`` is a bare
    :class:`ComposableFunction` (no inverse) -- e.g. a labelled projection, or a
    :func:`compose` pipeline that contains one.

    Example:
        >>> from gacalc.functions import InvertibleFunction, inverse
        >>> foo = InvertibleFunction(lambda x: 2 + x, "", lambda x: x - 2, "")
        >>> inverse(foo)(foo(5))
        5
    """
    if not isinstance(f, InvertibleFunction):
        raise NotInvertibleError(
            f"{getattr(f, 'latex_repr', f)!r} is not invertible; it has no inverse "
            "(a bare ComposableFunction, or a pipeline containing one)"
        )
    f_inverse: InvertibleFunction[V] = InvertibleFunction(
        func=f.inverse,
        latex_repr=f.latex_repr_inv,
        inverse=f.func,
        latex_repr_inv=f.latex_repr,
        linearity=f.linearity,
    )
    # Make inverse commute with at():  inverse(f).at(t) == inverse(f.at(t)) for
    # all t.  A primitive carries its law (inverted); a composite carries its
    # components reversed and each inverted -- the inverse-of-a-composition rule
    # -- so interpolation/iteration recurse correctly through an inverse.
    if f.interpolate is not None:
        law = f.interpolate  # bind the narrowed (non-None) law for the closure
        f_inverse.interpolate = lambda t: inverse(
            typing.cast("InvertibleFunction[V]", law(t))
        )
    if f.components is not None:
        f_inverse.components = [
            inverse(typing.cast("InvertibleFunction[V]", c))
            for c in reversed(f.components)
        ]
    return f_inverse


@typing.overload
def compose(functions: "list[InvertibleFunction[V]]") -> "InvertibleFunction[V]": ...
@typing.overload
def compose(functions: "list[ComposableFunction[V]]") -> "ComposableFunction[V]": ...
def compose(
    functions: "list[ComposableFunction[V]]",
) -> "ComposableFunction[V]":
    r"""Compose a sequence of functions.

    For two functions :math:`f` and :math:`g`, ``compose([f, g])`` is
    :math:`(f \circ g)(x) = f(g(x))` -- i.e. the last function in the list is
    applied first.  The result is an :class:`InvertibleFunction` **iff every part
    is invertible**; if any part is a bare :class:`ComposableFunction` the
    composite is one too (it has no inverse).

    Example:
        >>> from gacalc.functions import compose, InvertibleFunction, inverse
        >>> add2 = InvertibleFunction(lambda x: x + 2, "", lambda x: x - 2, "")
        >>> scale3 = InvertibleFunction(lambda x: x * 3, "", lambda x: x / 3, "")
        >>> fn = compose([scale3, add2])   # scale3(add2(x)) = 3 * (x + 2)
        >>> fn(1)
        9
        >>> inverse(fn)(9)
        1.0
    """
    fns: list[ComposableFunction[V]] = list(functions)

    def composed_fn(x: V) -> V:
        f: ComposableFunction[V]
        for f in reversed(fns):
            x = f(x)
        return x

    tex_str: str = ""
    f: ComposableFunction[V]
    for f in reversed(fns):
        tex_str = f.latex_repr if not tex_str else f.latex_repr + r" \circ " + tex_str
    linearity: Linearity = max((f.linearity for f in fns), default=Linearity.LINEAR)

    inv_fns: list[InvertibleFunction[V]] = [
        f for f in fns if isinstance(f, InvertibleFunction)
    ]
    if len(inv_fns) != len(fns):
        # some part has no inverse -> the whole composite has none
        return ComposableFunction(
            composed_fn, tex_str, components=list(fns), linearity=linearity
        )

    def inv_composed_fn(x: V) -> V:
        f: InvertibleFunction[V]
        for f in inv_fns:
            x = inverse(f)(x)
        return x

    inv_str: str = ""
    invertible_fn: InvertibleFunction[V]
    for invertible_fn in inv_fns:
        step: str = inverse(invertible_fn).latex_repr
        inv_str = step if not inv_str else step + r" \circ " + inv_str

    return InvertibleFunction(
        func=composed_fn,
        latex_repr=tex_str,
        inverse=inv_composed_fn,
        latex_repr_inv=inv_str,
        components=list(fns),
        linearity=linearity,
    )


def identity() -> InvertibleFunction[V]:
    """The identity function -- its own inverse, ``LINEAR``, labelled ``I``."""

    def f(vector: V) -> V:
        return vector

    return InvertibleFunction(
        func=f,
        latex_repr="I",
        inverse=f,
        latex_repr_inv="I",
        interpolate=lambda t: identity(),
        linearity=Linearity.LINEAR,
    )
