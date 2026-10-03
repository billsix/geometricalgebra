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


from __future__ import annotations

import abc
import dataclasses
import functools
import itertools
import math
import typing
from collections.abc import Callable, Generator, Mapping, Sequence
from itertools import chain, combinations
from typing import TypeIs

import numpy as np
import sympy

from gacalc.functions import ComposableFunction, InvertibleFunction, Linearity

# A multivector coefficient: a plain Python number or a sympy expression
# (symbolic mode).  Concrete `int | float | sympy.Expr` rather than the
# `numbers.Real` ABC -- ty turns `numbers.Real` arithmetic into `_ComplexLike`
# and then rejects `+`/`/`/`**` on it, which broke the generated versor sandwich.
Coef = int | float | sympy.Expr
#: A basis blade: a tuple of basis-vector indices, e.g. ``(1, 2)`` ≙ e₁e₂ (``()`` is
#: the scalar blade).  The key type of the ``BladeCoef`` interchange dict.
Blade = tuple[int, ...]
#: THE interchange format of the library.  Every representation (``Gn``,
#: ``G``, the graded subtypes) converts to and from this dict via
#: ``to_blade_dict``/``from_blade_dict``, and all shared arithmetic in this
#: module routes through it.  The contract (pinned by tests/test_blade_dict.py):
#:
#: - **Keys are canonical**: strictly increasing index tuples; ``()`` is the
#:   scalar blade.  ``from_blade_dict`` (every representation, via
#:   ``_require_canonical_blades``) raises ``ValueError`` on a non-canonical
#:   key (``(2, 1)``, duplicates) -- it is NOT read as a signed permutation.
#: - **Readers omit exact-zero coefficients** and a missing blade reads as 0
#:   (``.get(blade, 0)``).  The eager/lazy split shows here: ``Gn`` simplifies
#:   a hidden zero away; the lazy classes prune only a structural ``0``.
#: - **A graded type's ``from_blade_dict`` keeps ONLY its own blades** --
#:   foreign keys are silently dropped, so a result carrying a new grade must
#:   be built via dispatching arithmetic (``Bivector + scalar -> Versor``),
#:   never via ``from_blade_dict`` on the operand's type (see ``exp``).
BladeCoef = dict[Blade, Coef]
MultiVectorFn = Callable[["MultiVectorBase"], "MultiVectorBase"]

#: Type variable for the operand of a versor sandwich -- the result has the
#: operand's own type (see ``MultiVectorBase.sandwich``).
_OperandT = typing.TypeVar("_OperandT", bound="MultiVectorBase")


#: Session-wide blade *display* symbols (blade tuple -> LaTeX string), consulted
#: by ``blade_latex``/``blade_dict_latex`` when no explicit ``symbols`` argument
#: is passed.  Empty by default (standard e-notation).  A module global on
#: purpose: Jupyter invokes ``_repr_latex_()`` with **no arguments**, so plain
#: cell-output rendering can only honor a customization through state the method
#: can reach -- set it once in a notebook setup cell via ``set_blade_symbols``.
#: One map per kernel/process, applying to every algebra at once.  Display only:
#: the blade-tuple interchange format and ``__repr__`` never change.
_blade_display_symbols: dict[Blade, str] = {}


def set_blade_symbols(symbols: Mapping[Blade, str]) -> None:
    r"""Set the session-wide blade **display** symbols -- LaTeX rendering only.

    Meant for a notebook setup cell: every later LaTeX display (a value evaluated
    in a cell, ``show_mult``, plot labels) renders a mapped blade under its custom
    name -- e.g. the calc-3 unit vectors, often paired with the plain-Python
    input aliases ``i, j, k = e_1, e_2, e_3`` (which need no library support).

    Pass ``{}`` to reset.  Keys are canonical blade tuples (strictly increasing
    indices, validated); values are LaTeX.  Rename-only -- a symbol cannot carry
    a sign or reorder indices, and the stored value is untouched (tests pin the
    behavior via the pure ``symbols`` parameter of :func:`blade_dict_latex`,
    which bypasses this session map).

    Args:
        symbols: a canonical blade-tuple -> LaTeX-string map; ``{}`` resets to the
            default e-notation.

    Raises:
        ValueError: on a non-canonical blade key.

    Example:
        >>> from gacalc.gn import e_1, e_2
        >>> set_blade_symbols({(1,): r"\mathbf{i}", (2,): r"\mathbf{j}"})
        >>> (2 * e_1 + 3 * e_2)._repr_latex_()
        '$2\\mathbf{i} +  3\\mathbf{j}$'
        >>> set_blade_symbols({})  # reset to the default e-notation
        >>> (2 * e_1 + 3 * e_2)._repr_latex_()
        '$2\\mathbf{\\vec{e}}_{1} +  3\\mathbf{\\vec{e}}_{2}$'
    """
    _require_canonical_blades(symbols)
    _blade_display_symbols.clear()
    _blade_display_symbols.update(symbols)


def blade_latex(blade: Blade, symbols: Mapping[Blade, str] | None = None) -> str:
    r"""Render one basis blade as LaTeX: its custom symbol when ``blade`` has one,
    else ``\mathbf{\vec{e}}_{b}`` per index (``()``, the scalar blade, is ``1``).

    Args:
        blade: the basis blade to render (a canonical index tuple).
        symbols: a blade -> LaTeX-string map; ``None`` (the default) consults the
            session-wide map set by :func:`set_blade_symbols`.

    Returns:
        str: the LaTeX for the blade.

    Example:
        >>> blade_latex((1,), symbols={(1,): r"\mathbf{i}"})
        '\\mathbf{i}'
        >>> blade_latex((1, 2), symbols={})
        '\\mathbf{\\vec{e}}_{1} \\mathbf{\\vec{e}}_{2}'
        >>> blade_latex((), symbols={})
        '1'
    """
    if symbols is None:
        symbols = _blade_display_symbols
    custom: str | None = symbols.get(blade)
    if custom is not None:
        return custom
    return (
        "1"
        if blade == ()
        else " ".join(r"\mathbf{\vec{e}}_{" + str(b) + "}" for b in blade)
    )


def blade_dict_latex(d: BladeCoef, symbols: Mapping[Blade, str] | None = None) -> str:
    """Render a blade -> coefficient dict as a LaTeX string (the body of
    ``_repr_latex_``, factored out so callers can render a chosen *view*).

    Blades are grade-ordered (``(len, indices)``); a sum coefficient is
    parenthesized; an empty dict renders as ``0``.  ``_repr_latex_`` passes the
    *simplified* dict (display-simplify); ``nbplotutils.show_mult`` passes the
    *expanded* dict, so distribution is visible there without that simplify.

    Each blade renders via :func:`blade_latex`, so ``symbols`` (or, by default,
    the session map set by :func:`set_blade_symbols`) applies here too.

    Args:
        d: the blade -> coefficient mapping to render.
        symbols: a blade -> LaTeX-string map; ``None`` (the default) consults the
            session-wide map set by :func:`set_blade_symbols`.

    Returns:
        str: the LaTeX string (``$...$``; ``$0$`` for an empty dict).
    """

    def add_parens_or_dont(x: Coef) -> str:
        # Parenthesize a sum so its terms bind to the blade; render straight from
        # the sympy/number object (no fragile sympify(str(x)) round-trip).
        return (
            "(" + sympy.latex(x) + ")"
            if isinstance(x, sympy.Expr) and x.is_Add
            else sympy.latex(x)
        )

    blades: list[str] = [
        add_parens_or_dont(d[blade]) + blade_latex(blade, symbols)
        if blade != tuple()
        else add_parens_or_dont(d[blade])
        for blade in sorted(d.keys(), key=lambda b: (len(b), b))
    ]
    return "$" + ("0" if not d else " +  ".join(blades)) + "$"


def pseudoscalar_squared_sign(r: int) -> int:
    """The sign (``+1`` / ``−1``) of a grade-``r`` blade's square in Euclidean 𝒢ₙ.

    A grade-``r`` blade ``A`` satisfies ``A² = (−1)^(r(r−1)/2) · |A|²``; this is
    that sign factor — equivalently the reversion sign for grade ``r``, and the
    sign of the ``r``-dimensional unit pseudoscalar squared. Named so ``reverse`` /
    ``exp`` (and the generator's emitted ``reverse``) read as what they mean.

    Uses the closed form ``(−1)^(r(r−1)/2)``, proven equal to actually squaring the
    ``r``-dimensional unit pseudoscalar. For a hand-counted proof (grades 1–5,
    move-by-move) see ``tasks/reference/pseudoscalar-square-sign.md``; the
    equivalence is gated permanently by ``tests/test_pseudoscalar_square_sign.py``.
    Cost falls only on the two *non-generated* runtime callers, ``Gn.reverse`` and
    ``exp`` — the generator bakes this value as a compile-time constant into each
    generated ``reverse``, so the specialized classes pay nothing.

    Args:
        r: the grade of the blade.

    Returns:
        int: the sign factor ``(−1)^(r(r−1)/2)`` (``+1`` or ``−1``).
    """
    # Proven equal to squaring the unit pseudoscalar the slow, obviously-correct way
    # — the SAME calculation, kept here as a comment so it reads as a proof for a
    # student.  Phase 1 (2026-08-15) computed exactly this value like so, which
    # needed a deferred ``from gacalc.gn import Gn`` (a graded type can't build the
    # grade-1 vectors the pseudoscalar is made of, so only the full algebra Gn can):
    #
    #     from gacalc.gn import Gn
    #     return int(Gn.unit_pseudoscalar_squared(r).scalar_part())
    #
    # The closed form drops that base→gn coupling and is O(1).  The reversion swap
    # count for a grade-r blade is the triangular number r(r−1)/2 (see the proof).
    return (-1) ** ((r * (r - 1)) // 2)


def pseudoscalar_squared_is_positive(r: int) -> bool:
    """Whether a grade-``r`` blade squares to a *positive* scalar (``A² > 0``).

    ``pseudoscalar_squared_sign(r) == 1``.  ``exp`` uses it to reject the
    positive-square (vector) case, which has no Euclidean exponential.

    Args:
        r: the grade of the blade.

    Returns:
        bool: ``True`` iff a grade-``r`` blade squares to a positive scalar.
    """
    return pseudoscalar_squared_sign(r) == 1


class MultiVectorBase(abc.ABC):
    """Abstract base class for an element (multivector) of a geometric algebra.

    Concrete representations (Gn, and later G) implement a tiny interchange
    protocol -- ``from_blade_dict`` / ``to_blade_dict`` -- plus the core
    ``_geometric_product``.  The blade dict (``BladeCoef``, documented at its
    definition above) is **the canonical interchange representation**: every
    type converts through it, and all the shared arithmetic below routes
    through it.  Every representation-independent method here is
    written against that protocol, constructing results of the caller's own
    concrete type via ``type(self)``.  This is the abstraction boundary: only
    methods that touch the raw representation are reimplemented per subclass.
    """

    # No instance state of its own; empty slots so slotted subclasses (Gn,
    # G with ``slots=True``) don't inherit a __dict__ from the base.
    __slots__ = ()

    # ------------------------------------------------------------------
    # interchange protocol + construction (concrete subclasses implement
    # from_blade_dict / to_blade_dict; the rest is shared)
    # ------------------------------------------------------------------
    @classmethod
    @abc.abstractmethod
    def from_blade_dict(cls, blade_coef: Mapping[Blade, Coef]) -> typing.Self:
        """Build an instance of this representation from a blade->coef mapping.

        Args:
            blade_coef: a canonical blade -> coefficient mapping (keys are
                strictly-increasing index tuples; see ``BladeCoef``).

        Returns:
            Self: an instance of this concrete representation holding those
            coefficients.

        Raises:
            ValueError: on a non-canonical blade key (indices must be strictly
                increasing -- see ``_require_canonical_blades``).
        """

    @abc.abstractmethod
    def to_blade_dict(self) -> BladeCoef:
        """Return this multivector as a canonical blade -> coefficient mapping.

        Returns:
            BladeCoef: the blade -> coefficient interchange dict (canonical keys,
            exact-zero coefficients omitted).
        """

    @classmethod
    def from_scalar(cls, scalar: int | float) -> typing.Self:
        """The scalar (grade-0) multivector  ⟨A⟩₀ = scalar  — every other blade zero.

        For a symbolic coefficient use ``from_coef``; this takes a plain number.

        Args:
            scalar: the grade-0 coefficient (a plain Python number).

        Returns:
            Self: the multivector whose scalar part is ``scalar`` and whose every
            other blade coefficient is zero.
        """
        return cls.from_blade_dict({tuple(): scalar})

    @classmethod
    def from_coef(cls, s: Coef) -> typing.Self:
        """The scalar (grade-0) multivector whose coefficient is ``s`` — like
        ``from_scalar`` but also accepts a symbolic ``sympy.Expr`` coefficient.

        Args:
            s: the grade-0 coefficient (a number or a ``sympy.Expr``).

        Returns:
            Self: the multivector whose scalar part is ``s``, every other blade
            zero.
        """
        return cls.from_blade_dict({tuple(): s})

    @classmethod
    def zero(cls) -> typing.Self:
        """The additive identity  0  — every blade coefficient zero.

        Returns:
            Self: the multivector with every coefficient zero.
        """
        return cls.from_scalar(0)

    @classmethod
    def one(cls) -> typing.Self:
        """The multiplicative identity  1  — the unit scalar (grade-0).

        Returns:
            Self: the unit scalar (scalar part 1, every other blade zero).
        """
        return cls.from_scalar(1)

    @classmethod
    def basis_vector(cls, i: int) -> typing.Self:
        """The i-th basis vector e_i of this representation (1-indexed).

        Part of the interchange protocol: lets representation-agnostic code
        (e.g. the transform layer) obtain a basis vector of the *caller's* own
        concrete type, so results stay in that type rather than coercing to Gn.

        Args:
            i: the 1-indexed basis-vector index (``1`` gives e₁).

        Returns:
            Self: the unit basis vector eᵢ of this representation.
        """
        return cls.from_blade_dict({(i,): 1})

    @classmethod
    def unit_pseudoscalar(cls, n: int) -> typing.Self:
        """Unit pseudoscalar  i  =  e₁ e₂ … e_n  — the highest-grade unit blade of
        the n-dimensional algebra.

        Args:
            n: the dimension of the algebra (the pseudoscalar is the product of
                e₁ through e_n).

        Returns:
            Self: the unit pseudoscalar e₁e₂…e_n.
        """
        return math.prod(
            [cls.basis_vector(x) for x in range(1, n + 1)],
            start=cls.one(),
        )

    @classmethod
    def bases(cls, n: int) -> Generator[typing.Self]:
        """Yield the  2ⁿ  basis blades of 𝒢ₙ, one multivector each, from the scalar
        1 through the pseudoscalar e₁e₂…e_n (the powerset of {e₁, …, e_n}, ordered
        by grade).  This is the linear basis every multivector is a sum over.

        Args:
            n: the dimension of the algebra (yields 2ⁿ blades).

        Yields:
            Self: each unit basis blade of 𝒢ₙ in grade order, from the scalar 1
            to the pseudoscalar.
        """

        def powerset(iterable: Sequence[int]) -> chain[Blade]:
            s: list[int] = list(iterable)
            # chain.from_iterable flattens the list of combinations
            return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

        yield from (
            math.prod(
                [cls.basis_vector(x) for x in b],
                start=cls.one(),
            )
            for b in powerset(range(1, n + 1))
        )

    @classmethod
    def symbolic_multivector(cls, n: int, prefix: str) -> typing.Self:
        """A general multivector of 𝒢ₙ with a distinct symbolic coefficient on every
        basis blade — ``prefix0``·1 + ``prefix1``·e₁ + … over all  2ⁿ  blades.

        The workhorse for proving an identity symbolically: build one of these,
        run the operation, and check the result simplifies to the expected form.

        Args:
            n: the dimension of the algebra (gives 2ⁿ symbolic coefficients).
            prefix: the base name for the generated ``sympy`` symbols (``"a"``
                gives ``a0``, ``a1``, …).

        Returns:
            Self: a multivector carrying one distinct symbol per basis blade.
        """
        mv: list[MultiVectorBase] = list(cls.bases(n))
        symbols: list[sympy.Symbol] = sympy.symbols(prefix + ":" + str(len(mv)))
        return sum([s * blade for s, blade in zip(symbols, mv)], start=cls.zero())

    @classmethod
    def unit_pseudoscalar_squared(cls, n: int) -> typing.Self:
        """The square of the unit pseudoscalar,  i²  — the scalar
        :func:`~gacalc.base.pseudoscalar_squared_sign` (of the dimension ``n``;
        ``= (−1)^(n(n−1)/2)``) in Euclidean 𝒢ₙ (see
        ``tasks/reference/pseudoscalar-square-sign.md``); ±1, and the sign that
        decides whether i is a "complex/quaternionic" imaginary.

        Args:
            n: the dimension of the algebra.

        Returns:
            Self: the scalar multivector ``i²`` whose value is
            :func:`~gacalc.base.pseudoscalar_squared_sign` (``±1``).
        """
        unit_pseudoscalar: MultiVectorBase = cls.unit_pseudoscalar(n)
        return unit_pseudoscalar * unit_pseudoscalar

    # ------------------------------------------------------------------
    # core product: scalar dispatch is shared, the multivector*multivector
    # case is the representation-specific primitive _geometric_product
    # ------------------------------------------------------------------
    @abc.abstractmethod
    def _geometric_product(self, rhs: MultiVectorBase) -> typing.Self:
        """Geometric product  A B  (juxtaposition) — the fundamental product of the
        algebra, from which the inner product  A · B  and outer product  A ∧ B  are
        derived.  This is the representation-specific primitive.

        Args:
            rhs: the right operand (another multivector of a compatible
                representation).

        Returns:
            Self: the geometric product ``self * rhs``.
        """

    def __mul__(self, rhs: MultiVectorBase | Coef) -> typing.Self:
        """Geometric product  A B  (``*``).  A bare number on the right is lifted to a
        scalar first, so ``A * 2`` scales; otherwise this is the full product of the
        algebra, dispatched to the representation's ``_geometric_product``.

        Args:
            rhs: the right operand — a multivector, or a bare number / ``sympy``
                expression (lifted to the scalar part first).

        Returns:
            Self: the geometric product ``self * rhs``.
        """
        match rhs:
            case int() | float() as n:
                return self._geometric_product(type(self).from_scalar(n))
            case sympy.Expr() as s:
                return self._geometric_product(type(self).from_coef(s))
            case _:
                return self._geometric_product(rhs)

    def __rmul__(self, lhs: MultiVectorBase | Coef) -> typing.Self:
        """Reflected geometric product  (number) A  — gives ``2 * A`` for a bare number
        on the left.  A multivector left operand is handled by its own ``__mul__``; any
        other left type returns ``NotImplemented`` so Python raises ``TypeError``.

        Args:
            lhs: the left operand — a bare number or ``sympy`` expression (lifted
                to the scalar part).

        Returns:
            Self: the geometric product ``lhs * self``, or ``NotImplemented`` for
            an unsupported left type.
        """
        match lhs:
            case int() | float() as n:
                return self._geometric_product(type(self).from_scalar(n))
            case sympy.Expr() as s:
                return self._geometric_product(type(self).from_coef(s))
            case _:
                # multivector*multivector is handled by __mul__; any other left
                # operand is unsupported -- defer so Python raises a clean
                # TypeError (the previous `-self._geometric_product(lhs)` was dead
                # and wrongly negated: the geometric product is not anticommutative).
                return NotImplemented

    # ------------------------------------------------------------------
    # shared arithmetic, all built on the interchange + primitives
    # ------------------------------------------------------------------
    def __add__(self, rhs: MultiVectorBase | Coef) -> typing.Self:
        """Sum  A + B  — coefficient-wise over the union of both multivectors' blades.
        A bare number adds to the scalar (grade-0) part, so ``bivector + c`` builds
        the versor  c + B  in every representation.

        Args:
            rhs: the right operand — a multivector, or a bare number / ``sympy``
                expression (added to the scalar part).

        Returns:
            Self: the coefficient-wise sum ``self + rhs``.
        """
        # A bare number is the scalar (grade-0) part -- the generated
        # specialized classes already accept ``mv + 2``; the shared base
        # matches them so e.g. ``bivector * (-s) + c`` builds a versor in
        # every representation.
        if isinstance(rhs, (int, float, sympy.Expr)):
            rhs = type(self).from_blade_dict({(): rhs})
        left: BladeCoef = self.to_blade_dict()
        right: BladeCoef = rhs.to_blade_dict()
        return type(self).from_blade_dict(
            {
                blade: (left.get(blade, 0) + right.get(blade, 0))
                for blade in (left.keys() | right.keys())
            }
        )

    def __radd__(self, lhs: Coef) -> typing.Self:
        """Reflected sum  (number) + A  — addition commutes, so this gives ``2 + A``
        for free.  ``lhs`` is always a bare number (a multivector left operand uses
        its own ``__add__``).

        Args:
            lhs: the left operand — a bare number or ``sympy`` expression.

        Returns:
            Self: the sum ``lhs + self``.
        """
        # addition commutes; gives ``2 + mv`` for free.  ``lhs`` is a bare number,
        # never a multivector: Python only calls ``__radd__`` when the left operand
        # (here a non-multivector) has no ``__add__`` for us -- a multivector left
        # operand uses its own ``__add__``.  Typing it ``Coef`` (not
        # ``MultiVectorBase | Coef``) also matches the generated specialized
        # ``__radd__`` (whose ``lhs`` is a number union), so the override is
        # Liskov-clean at every dimension.
        return self.__add__(lhs)

    def __sub__(self, rhs: typing.Self) -> typing.Self:
        """Difference  A − B  =  A + (−B).

        Args:
            rhs: the multivector to subtract.

        Returns:
            Self: the difference ``self - rhs``.
        """
        return self + -rhs

    def __neg__(self) -> typing.Self:
        """Negation  −A — every coefficient sign-flipped (scalar factor −1).

        Returns:
            Self: ``self`` with every coefficient negated.
        """
        return -1 * self

    def __truediv__(self, rhs: MultiVectorBase | Coef) -> typing.Self:
        """Quotient  A / B  =  A B⁻¹  — division IS multiplication by the
        inverse (right division: order matters in a non-commutative algebra).
        A bare number's inverse is its reciprocal, so ``v / s`` divides every
        coefficient.

        Args:
            rhs: the divisor — a multivector (right-multiplied by its inverse) or
                a bare number / ``sympy`` expression (its reciprocal).

        Returns:
            Self: the quotient ``self * rhs.inverse()`` (or ``self * (1 / rhs)``
            for a number).

        Raises:
            ZeroDivisionError: if ``rhs`` is a zero-magnitude multivector (via
                ``inverse``) or a zero number.
        """
        return (
            self * (1 / rhs)
            if isinstance(rhs, (int, float, sympy.Expr))
            else self * rhs.inverse()
        )

    def __abs__(self) -> Coef:
        """Magnitude  \\|A\\|  =  ``abs(A)``  — the norm √⟨A A˜⟩; see ``magnitude``.

        Returns:
            Coef: the magnitude ``|A|`` (see :meth:`magnitude`).
        """
        return self.magnitude()

    def __iter__(self):
        # Return intentionally left unannotated: typing it ``Generator[Coef]``
        # makes ty treat a MultiVectorBase as a destructurable iterable, so the
        # ``case [*sequence]:`` patterns in project/reject/reflect then also match
        # a lone multivector and widen the bound element type -- a false positive
        # (at runtime a multivector is not a Sequence).  The docstring already
        # documents that iteration yields the coefficient values.
        """Iterate the coefficient values in blade order (a value/coordinate tuple).

        ``list(v)`` / ``tuple(v)`` / ``np.array([list(v), ...])`` give the numeric
        components, so a multivector reads as the numbers it holds.  To decompose
        into one single-blade multivector per term instead, iterate
        ``to_blade_dict()``.

        Yields:
            Coef: each coefficient value, in grade-then-index blade order.
        """
        d: BladeCoef = self.to_blade_dict()
        yield from (d[key] for key in sorted(d.keys(), key=lambda b: (len(b), b)))

    def magnitude(self) -> Coef:
        """Magnitude  ``|A|``  =  √(Ã ∗ A)  — the positive square root of the scalar
        product of A with its reverse.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.49

        Float input stays a float: ``sympy.sqrt`` always returns a ``sympy.Expr``
        (e.g. ``sqrt(2.0)`` -> ``1.41421356237310`` as a ``sympy.Float``), which
        would leak symbolic objects into purely numeric pipelines (and, downstream,
        produce ``numpy`` ``dtype=object`` arrays).  When ``|A|²`` is a Python
        ``float`` (already inexact) we therefore take ``math.sqrt`` and return a
        ``float``.  An ``int`` ``|A|²`` keeps ``sympy.sqrt`` so exactness is preserved
        (``sqrt(25) == 5`` exactly, and a unit blade normalizes to ``Rational`` values,
        not floats); symbolic coefficients also stay symbolic.

        Returns:
            Coef: the magnitude ``|A|`` — a ``float`` for float input, otherwise
            an exact ``sympy`` value.
        """
        magnitude_squared: Coef = self.magnitude_squared()
        return (
            math.sqrt(magnitude_squared)
            if isinstance(magnitude_squared, float)
            else sympy.sqrt(magnitude_squared)
        )

    def magnitude_squared(self) -> Coef:
        """Squared magnitude  ``|A|²``  =  Ã ∗ A  =  ⟨Ã A⟩  (a scalar).

        Returns:
            Coef: the scalar ``|A|²`` (the scalar product of the reverse with A).
        """
        return self.reverse().scalar_product(self)

    def normalize(self) -> typing.Self:
        """Unit multivector  Â  =  A / ``|A|``  — A rescaled to magnitude 1.

        Raises ``ZeroDivisionError`` if ``A`` has zero magnitude (e.g. the zero
        vector), for **any** coefficient kind. A float-zero already raised; without
        this guard an int/symbolic zero silently returned a ``nan``-poisoned value
        (sympy ``0 ** -1`` → ``zoo``, ``0 * zoo`` → ``nan``).

        Returns:
            Self: the unit multivector ``A / |A|`` (magnitude 1).

        Raises:
            ZeroDivisionError: if ``A`` has zero magnitude (for any coefficient
                kind).
        """
        if self.magnitude_squared() == 0:
            raise ZeroDivisionError("cannot normalize a zero-magnitude multivector")
        return self * (abs(self) ** (-1))

    def coefficient(self, blade: typing.Self) -> Coef:
        """The coefficient this multivector stores on the unit basis ``blade``.

        A thin reader convenience: it reads the stored value straight from the
        blade-dict interchange — no geometric product — and is correct for any
        grade.  ``blade`` is a unit basis blade: a class constant like
        ``g2.Vector.e_1`` / ``g2.Bivector.e_12`` / ``g3.G.e_123``, or a module constant
        like ``gn.e_1``.  (Not from Hestenes/Sobczyk — a convenience over
        ``to_blade_dict()``.  For the scalar part or a whole grade, use
        ``scalar_part`` / ``r_vector_part``.)

        Args:
            blade: a unit basis blade — a class constant like ``g2.Vector.e_1`` /
                ``g2.Bivector.e_12``, or a module constant like ``gn.e_1``.

        Returns:
            Coef: the coefficient stored on ``blade`` (0 if absent).

        Example:
            >>> from gacalc.g2 import Vector
            >>> (3 * Vector.e_1 + 4 * Vector.e_2).coefficient(Vector.e_1)
            3
        """
        (key,) = blade.to_blade_dict()  # the single blade of a unit basis blade
        return self.to_blade_dict().get(key, 0)

    def _map_coefficients(self, op: Callable[[Coef], Coef]) -> typing.Self:
        """Return a new multivector with ``op`` applied to each coefficient.

        The same value, with its blade coefficients transformed (e.g. by a sympy
        rewrite).  Works on any representation via the blade-dict interchange, so
        ``Gn``/``G`` and the graded subtypes all inherit it.

        Args:
            op: a coefficient -> coefficient function applied to each stored
                coefficient.

        Returns:
            Self: a new multivector with ``op`` applied to every coefficient.
        """
        return type(self).from_blade_dict(
            {blade: op(coef) for blade, coef in self.to_blade_dict().items()}
        )

    def simplified(self) -> typing.Self:
        """The same multivector with every coefficient ``sympy.simplify``'d.

        The specialized/graded classes don't eager-simplify (the lazy policy), so a
        symbolic result can carry uncombined or uncancelled coefficients — e.g. a
        bivector times its dual whose terms should cancel.  ``simplified()`` returns
        an equal value with each coefficient in lowest terms, for display/inspection;
        the stored fields are untouched.  (``Gn`` already eager-simplifies, so this
        is a no-op there.)

        Returns:
            Self: an equal multivector with every coefficient ``sympy.simplify``'d.
        """
        return self._map_coefficients(lambda c: sympy.simplify(c))  # type: ignore

    def expanded(self) -> typing.Self:
        """The same multivector with every coefficient ``sympy.expand``'d.

        Distributes products over sums in each coefficient — the fully *distributed*
        form (e.g. for showing that the geometric product is distributive).  Equal in
        value; only the coefficient form changes.

        Returns:
            Self: an equal multivector with every coefficient ``sympy.expand``'d.
        """
        return self._map_coefficients(lambda c: sympy.expand(c))

    def inner_product(self, rhs: typing.Self) -> typing.Self:
        """Inner (dot) product  A · B  — the lowest-grade part of the geometric
        product, ⟨A B⟩_|r−s| summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.21a, 1.21b, 1.21c

        Args:
            rhs: the right operand.

        Returns:
            Self: the inner product ``A · B`` (the lowest-grade part of the
            geometric product).
        """

        def inner_product_of_homogenous_multivectors(
            lhs: MultiVectorBase, rhs: MultiVectorBase
        ) -> MultiVectorBase:
            # # 1.21b
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(abs(left_grade - right_grade))

        inner: MultiVectorBase = sum(
            [
                inner_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
                if lg > 0 and rg > 0
            ],
            start=type(self).zero(),  # 1.21b
        )
        return typing.cast(typing.Self, inner)

    def dot(self, rhs: typing.Self) -> typing.Self:
        """Inner (dot) product  A · B  — a spelling of ``inner_product``.

        This is the Hestenes inner product, which EXCLUDES grade 0 (so it differs
        from the grade-0-including left/right contractions on scalar operands); see
        ``tasks/reference/contraction-and-dot-definitions.md``.

        Args:
            rhs: the right operand.

        Returns:
            Self: the inner product ``A · B`` (see :meth:`inner_product`).
        """
        return self.inner_product(rhs)

    def outer_product(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  — the highest-grade part of the geometric
        product, ⟨A B⟩_(r+s) summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.22a, 1.22b, 1.22c

        Args:
            rhs: the right operand.

        Returns:
            Self: the outer product ``A ∧ B`` (the highest-grade part of the
            geometric product).
        """

        def outer_product_of_homogenous_multivectors(
            lhs: MultiVectorBase, rhs: MultiVectorBase
        ) -> MultiVectorBase:
            # 1.22a
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(left_grade + right_grade)

        # 1.22b
        # 1.22c, because unlike the inner_product, we keep grade 0s
        outer: MultiVectorBase = sum(
            [
                outer_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, outer)

    def scalar_product(self, other: typing.Self) -> Coef:
        """Scalar product  A ∗ B  =  ⟨A B⟩  — the grade-0 (scalar) part of the
        geometric product.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.44

        Args:
            other: the right operand.

        Returns:
            Coef: the scalar product ``⟨A B⟩`` (the grade-0 part of the product).
        """
        return (self * other).scalar_part()

    def wedge(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  (alias of ``outer_product``).

        Args:
            rhs: the right operand.

        Returns:
            Self: the outer product ``A ∧ B`` (see :meth:`outer_product`).
        """
        return self.outer_product(rhs)

    def __xor__(self, other: typing.Self) -> typing.Self:
        """Operator form of the outer product:  a ^ b  ==  a ∧ b  ==  a.wedge(b).

        Args:
            other: the right operand.

        Returns:
            Self: the outer product ``a ∧ b``.
        """
        return self.wedge(other)

    def left_contraction(self, rhs: typing.Self) -> typing.Self:
        """Left contraction  A ⌋ B  — for homogeneous grade-k (left) and grade-m
        (right) parts, the grade-(m−k) part of the geometric product ⟨A_k B_m⟩_(m−k),
        summed bilinearly; zero whenever m − k < 0.

        from M.D. Taylor, An Introduction to Geometric Algebra and Geometric
        Calculus, 2021, page 103.  (galgebra 0.6.0 agrees: its
        _LeftContractFunction keeps grade grade2 − grade1.)

        Grade-0 caveat: UNLIKE the Hestenes dot product (``inner_product``), the
        loop over source components INCLUDES grade 0 — Taylor (and galgebra's
        contraction) do; Hestenes' dot is undefined for scalars.  Taylor also calls
        grade 0 part of the plain dot product, which conflicts with Hestenes; this
        discrepancy may warrant further investigation (see
        tasks/investigate-dot-product-grade-0.md).

        Args:
            rhs: the right operand.

        Returns:
            Self: the left contraction ``A ⌋ B`` (grade m−k per homogeneous
            part; zero where m−k < 0).
        """

        def left_contraction_of_homogenous_multivectors(
            lhs: MultiVectorBase, rhs: MultiVectorBase
        ) -> MultiVectorBase:
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            # grade m − k; r_vector_part of a negative grade is zero
            return (lhs * rhs).r_vector_part(right_grade - left_grade)

        contraction: MultiVectorBase = sum(
            [
                left_contraction_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, contraction)

    def right_contraction(self, rhs: typing.Self) -> typing.Self:
        """Right contraction  A ⌊ B  — for homogeneous grade-k (left) and grade-m
        (right) parts, the grade-(k−m) part of the geometric product ⟨A_k B_m⟩_(k−m),
        summed bilinearly; zero whenever k − m < 0.

        from M.D. Taylor, An Introduction to Geometric Algebra and Geometric
        Calculus, 2021, page 103.  (galgebra 0.6.0 agrees: its
        _RightContractFunction keeps grade grade1 − grade2.)

        Grade-0 caveat: like the left contraction, the loop INCLUDES grade 0,
        unlike the Hestenes dot (``inner_product``) — see ``left_contraction`` and
        tasks/investigate-dot-product-grade-0.md.

        Args:
            rhs: the right operand.

        Returns:
            Self: the right contraction ``A ⌊ B`` (grade k−m per homogeneous
            part; zero where k−m < 0).
        """

        def right_contraction_of_homogenous_multivectors(
            lhs: MultiVectorBase, rhs: MultiVectorBase
        ) -> MultiVectorBase:
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            # grade k − m; r_vector_part of a negative grade is zero
            return (lhs * rhs).r_vector_part(left_grade - right_grade)

        contraction: MultiVectorBase = sum(
            [
                right_contraction_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, contraction)

    def __lt__(self, other: typing.Self) -> typing.Self:
        """Operator form of the left contraction:  a < b  ==  a.left_contraction(b).

        Args:
            other: the right operand.

        Returns:
            Self: the left contraction ``a ⌋ b``.
        """
        return self.left_contraction(other)

    def __gt__(self, other: typing.Self) -> typing.Self:
        """Operator form of the right contraction: a > b == a.right_contraction(b).

        Args:
            other: the right operand.

        Returns:
            Self: the right contraction ``a ⌊ b``.
        """
        return self.right_contraction(other)

    @staticmethod
    def outer_product_of_vectors(
        *vectors: MultiVectorBase,
    ) -> MultiVectorBase:
        """Outer product of several vectors  a₁ ∧ a₂ ∧ … ∧ a_r  — a simple r-blade.

        Args:
            *vectors: the grade-1 vectors to wedge together.

        Returns:
            MultiVectorBase: the simple r-blade ``a₁ ∧ … ∧ a_r``.
        """
        return functools.reduce(lambda a, b: a ^ b, vectors)

    def r_vector_part(self, r: int) -> typing.Self:
        """Grade-r part  ⟨A⟩ᵣ  — the r-vector (grade-r) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4

        Args:
            r: the grade to extract.

        Returns:
            Self: the grade-``r`` part of A (zero if A has no grade-``r`` blades).
        """
        d: BladeCoef = self.to_blade_dict()
        return type(self).from_blade_dict(
            {blade: d[blade] for blade in d.keys() if len(blade) == r}
        )

    def is_homogeneous_of_grade_r(self, r: int) -> bool:
        """True iff A is homogeneous of grade ``r`` (all present blades have grade r).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4

        The zero multivector has no present blades, so it is trivially homogeneous of
        EVERY grade -- consistent with ``is_scalar(zero) == True``.

        Args:
            r: the grade to test for.

        Returns:
            bool: ``True`` iff every present blade has grade ``r`` (``zero`` is
            homogeneous of every grade).
        """
        grades: list[int] = self.grades()
        return not grades or (max(grades) == r and self.is_r_vector())

    def is_scalar(self) -> bool:
        """True iff A is a scalar (grade 0) — equal to its own grade-0 part.

        Returns:
            bool: ``True`` iff A has only a grade-0 (scalar) part (``zero``
            qualifies).
        """
        return self == self.r_vector_part(0)

    def is_r_vector(self) -> bool:
        """True iff A is homogeneous of some single grade (an r-vector) — equal to
        its own top-grade part.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4

        Returns:
            bool: ``True`` iff A is homogeneous of a single grade (``zero``
            qualifies).
        """
        return self == self.r_vector_part(self.max_grade())

    def is_vector(self) -> bool:
        """True iff A is homogeneous of grade 1 (a vector); ``zero`` qualifies.

        Returns:
            bool: ``True`` iff A is homogeneous of grade 1.
        """
        return self.is_homogeneous_of_grade_r(r=1)

    def is_bivector(self) -> bool:
        """True iff A is homogeneous of grade 2 (a bivector); ``zero`` qualifies.

        Returns:
            bool: ``True`` iff A is homogeneous of grade 2.
        """
        return self.is_homogeneous_of_grade_r(r=2)

    def is_trivector(self) -> bool:
        """True iff A is homogeneous of grade 3 (a trivector); ``zero`` qualifies.

        Returns:
            bool: ``True`` iff A is homogeneous of grade 3.
        """
        return self.is_homogeneous_of_grade_r(r=3)

    def is_orthogonal_to(
        self, other: typing.Self, float_close_to_zero: bool = False
    ) -> bool:
        """True iff vectors A and B are orthogonal (perpendicular) — the cosine of
        the angle between them is zero.

        For a geometry/trig student: perpendicular vectors meet at a right angle, so
        ``cos θ = 0`` (see :meth:`cosine`).  The test is implemented with the inner
        product ``A · B`` — the robust, division-free primitive — because
        ``cos θ = 0 ⟺ A · B = 0`` for (nonzero) vectors, without ``cosine``'s 0/0
        edge case.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 9,
        between equations 1.32 and 1.33

        Args:
            other: the other vector.
            float_close_to_zero: when ``True``, test the inner product with a
                ``numpy`` floating-point tolerance instead of exact equality.

        Returns:
            bool: ``True`` iff ``A · B`` is (approximately) zero.

        Raises:
            ValueError: if either operand is the zero vector — the angle is undefined,
                so orthogonality is too (matches the Lean proofs' nonzero hypothesis).
            AssertionError: if either operand is not a vector (grade 1).
        """

        if self == type(self).zero() or other == type(other).zero():
            raise ValueError(
                "orthogonality (the angle) is undefined for the zero vector"
            )

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
        """True iff vectors A and B are parallel — the sine of the angle between
        them is zero (equivalently, their outer product ``A ∧ B`` is zero: they are
        linearly dependent).

        For a geometry/trig student: parallel vectors point the same way (or exactly
        opposite), so they enclose no angle and ``sin θ = 0`` (see :meth:`abs_sin`).
        The test is implemented with the outer product ``A ∧ B`` — the robust,
        division-free primitive — since ``sin θ = 0 ⟺ A ∧ B = 0``.  ``A ∧ B = 0``
        iff A and B span no area, so this holds for both same-direction and
        anti-parallel vectors. The equivalence ``A ∧ B = 0 ⟺ A ∥ B`` is
        machine-checked in ``proofs/GacalcProofs/Predicates3D.lean``.

        Args:
            other: the other vector.
            float_close_to_zero: when ``True``, test the wedge with a ``numpy``
                floating-point tolerance instead of exact equality.

        Returns:
            bool: ``True`` iff ``A ∧ B`` is (approximately) zero.

        Raises:
            ValueError: if either operand is the zero vector — parallelism is framed via
                the angle (sine 0), which is undefined there (matches the Lean proofs'
                nonzero hypothesis).
            AssertionError: if either operand is not a vector (grade 1).
        """

        if self == type(self).zero() or other == type(other).zero():
            raise ValueError("parallelism (the angle) is undefined for the zero vector")

        # TODO - defined for vectors only right now, it's probably defined more
        # generally later in the book
        assert self.is_vector()
        assert other.is_vector()

        wedge: typing.Self = self.outer_product(other)
        if float_close_to_zero:
            return wedge.isclose(type(self).zero(), rel_tol=1e-5, abs_tol=1e-5)
        return bool(wedge == type(self).zero())

    def scalar_part(self) -> Coef:
        """Scalar part  ⟨A⟩  =  ⟨A⟩₀  — the grade-0 (scalar) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4

        Returns:
            Coef: the grade-0 coefficient of A (0 if absent).
        """
        return self.to_blade_dict().get(tuple(), 0)

    def grades(self) -> list[int]:
        """The distinct grades present in A — the set of blade lengths that carry a
        nonzero coefficient (e.g. a versor gives ``[0, 2]``).  Empty for ``zero``.

        Returns:
            list[int]: the distinct grades present (blade lengths with a nonzero
            coefficient); empty for ``zero``.
        """
        return list(set(len(blade) for blade in self.to_blade_dict().keys()))

    def max_grade(self) -> int:
        """The highest grade present in A (its top blade's grade); 0 for ``zero``.

        Returns:
            int: the highest grade present (0 for ``zero``).
        """
        # The zero multivector has no present blades; its max grade is 0 (it is
        # homogeneous of every grade -- see is_homogeneous_of_grade_r) rather than a
        # crash on max([]).
        return max(self.grades(), default=0)

    def reverse(self) -> typing.Self:
        """Reverse  Ã  — reverses the order of the vector factors in each blade,
        giving the grade-``r`` part the reversion sign
        :func:`~gacalc.base.pseudoscalar_squared_sign` (of the grade ``r``;
        ``= (−1)^(r(r−1)/2)``).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5,
        equation 1.19

        Returns:
            Self: the reverse ``Ã`` (each grade-``r`` part scaled by
            :func:`~gacalc.base.pseudoscalar_squared_sign`).
        """

        # supposedly, 1.19 works for simple r-vectors, but because of linearity
        # of the grade operator, it works for all multivectors
        return sum(
            [
                pseudoscalar_squared_sign(r) * self.r_vector_part(r)
                for r in self.grades()
            ],
            start=type(self).zero(),
        )

    def inverse(self) -> typing.Self:
        """Inverse  A⁻¹  =  Ã / ``|A|²``  — for a **blade or versor** (see scope).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Scope (this is NOT the general multivector inverse): the formula
        ``Ã/|A|²`` is exact only when ``Ã A`` is a **scalar** — true for a
        **blade** (a grade-pure simple element: scalar, vector, bivector, or
        trivector/pseudoscalar) and for a **versor** (a product of invertible
        vectors, e.g. a rotor), where ``(Ã/|A|²) A = Ã A / |A|² = 1``.  For a
        **general mixed-grade multivector**, ``Ã A`` has non-scalar parts, so
        this returns a WRONG "inverse".  A general low-dimensional closed form
        does exist (Hitzer & Sangwine 2017, via the grade involutions) but is
        not implemented here — it is tracked in
        ``tasks/lean-general-multivector-inverse.md``.  ``A A⁻¹ = 1`` is
        machine-checked for the vector, versor, bivector and trivector cases in
        the Lean proof layer (``proofs/GacalcProofs/``).

        (This replaces the older "not sure if I'm doing this correctly" flag:
        the method is correct for the subset above; the general case is
        unimplemented and now **guarded** — a mixed-grade ``A`` raises
        ``RuntimeError`` instead of returning a wrong answer.  The guard is the
        exact condition "``Ã A`` is a scalar", which subsumes scalar/vector/blade/
        versor in every dimension — unlike a grade-shape test, which cannot spot a
        versor and would wrongly accept a non-simple grade-pure element in 𝒢₄/𝒢₅.
        A good alternative NOT used: trust the graded subtypes — a ``Vector``/
        ``Bivector``/``Trivector``/``Versor`` is a blade/versor by construction, so
        no runtime check is needed on those types; only a raw mixed-grade ``Gn``/
        ``G`` is unsafe.  The general low-dim closed form is tracked in
        ``tasks/lean-general-multivector-inverse.md``.)

        Returns:
            Self: the inverse ``A⁻¹ = Ã / |A|²`` (valid for a blade or versor).

        Raises:
            ZeroDivisionError: if ``|A|²`` is zero (A has no inverse).
            RuntimeError: if ``A`` is a mixed-grade multivector (``Ã A`` not a
                scalar) — the general inverse is not implemented.
        """
        # Compute the full product Ã A once — reverse on the LEFT, matching
        # :meth:`magnitude_squared` (= ``self.reverse().scalar_product(self)`` = ⟨Ã A⟩)
        # and the returned inverse ``Ã / |A|²``.  We keep the *whole* product rather
        # than just its scalar part so the non-scalar part is available for the gate
        # below; its scalar part (via :meth:`scalar_part`) is exactly ``|A|²``, and
        # ``a_reverse`` is reused for the returned inverse.
        a_reverse: typing.Self = self.reverse()
        reverse_times_self: typing.Self = a_reverse * self
        # Gate: ``Ã / |A|²`` is a genuine inverse iff ``Ã A`` is a scalar — then
        # ``A⁻¹ A = Ã A / |A|² = 1`` — which holds for a blade or versor.  A non-scalar
        # product means A is a mixed-grade element whose (general) inverse is not
        # implemented.  See :meth:`is_scalar`.
        if not reverse_times_self.is_scalar():
            raise RuntimeError(
                "inverse() supports a blade or versor (where Ã A is a scalar); the "
                "general mixed-grade multivector inverse is not implemented "
                "(see tasks/lean-general-multivector-inverse.md)"
            )
        # Keep numeric input numeric: a ``float`` |A|² stays a float so the
        # reciprocal doesn't leak sympy into numeric pipelines.  For an ``int``
        # (e.g. a unit blade, |A|² == 1) sympify first, so ``int ** -1`` keeps the
        # exact Rational instead of silently degrading to a float; symbolic |A|²
        # stays symbolic.  (Mirrors the numeric/symbolic split in ``magnitude``.)
        mag_sq: Coef = reverse_times_self.scalar_part()
        if not isinstance(mag_sq, float):
            mag_sq = sympy.sympify(mag_sq)
        if mag_sq == 0:
            raise ZeroDivisionError("cannot invert a zero-magnitude multivector")
        return a_reverse * (mag_sq ** (-1))

    # dual returns MultiVectorBase (not Self) for the same reason as even_part/
    # odd_part below: it maps grade r -> grade n−r, a *different* grade, so a
    # fixed-dimension graded override narrows the return to the resolved type
    # (Bivector.dual -> Vector) -- an override that -> Self would forbid.  The
    # full class G_n keeps -> Self (all grades); Gn inherits this base.
    def dual(self, n: int) -> MultiVectorBase:
        """Dual  A*  =  A I⁻¹  — multiplication by the inverse unit pseudoscalar I,
        mapping a grade-r part to grade n−r.

        Args:
            n: the dimension of the algebra (fixes the pseudoscalar I).

        Returns:
            MultiVectorBase: the dual ``A I⁻¹`` (grade r ↦ grade n−r).
        """
        return self * type(self).unit_pseudoscalar(n).inverse()

    # even_part/odd_part return MultiVectorBase (not Self): the even/odd part of a
    # single-grade type is a *different* grade (e.g. a vector's even part is the
    # scalar 0), so the generated graded overrides narrow the return to that
    # resolved type (Vector.even_part -> Scalar) -- an override that -> Self
    # would forbid.  Gn/the full class G_n stay their own type via their overrides.
    def even_part(self) -> MultiVectorBase:
        """Even part  A⁺  =  ⟨A⟩₀ + ⟨A⟩₂ + …  — the sum of the even-grade parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        Returns:
            MultiVectorBase: the sum of the even-grade (0, 2, …) parts of A.
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 0],
            start=type(self).zero(),
        )

    def odd_part(self) -> MultiVectorBase:
        """Odd part  A⁻  =  ⟨A⟩₁ + ⟨A⟩₃ + …  — the sum of the odd-grade parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8

        Returns:
            MultiVectorBase: the sum of the odd-grade (1, 3, …) parts of A.
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 1],
            start=type(self).zero(),
        )

    def cosine(self, other: MultiVectorBase) -> Coef:
        """Cosine of the angle between A and B:  cos θ  =  (Ã ∗ B) / (``|A|`` ``|B|``).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14,
        equation 1.53b

        Args:
            other: the other multivector.

        Returns:
            Coef: the cosine ``cos θ = (Ã ∗ B) / (|A| |B|)``.

        Raises:
            ValueError: if ``self`` or ``other`` is the zero vector — the angle (hence
                its cosine) is undefined there; mirrors the Lean proofs' nonzero
                hypothesis on the sine/cosine theorems.
        """
        if self == type(self).zero() or other == type(other).zero():
            raise ValueError("cosine (the angle) is undefined for the zero vector")
        return (
            self.reverse().scalar_product(other)
            * (abs(self) ** (-1))
            * (abs(other) ** (-1))
        )

    def abs_sin(self, other: MultiVectorBase) -> Coef:
        """Unsigned sine of the angle between A and B:  ``|A ∧ B|`` / (``|A|`` ``|B|``).

        The non-negative, any-dimension companion to :meth:`cosine`.  By Lagrange's
        identity ``‖A ∧ B‖² = ‖A‖²‖B‖² − (A ∗ B)²`` the two satisfy
        ``cosine² + abs_sin² == 1`` for vectors
        (<https://en.wikipedia.org/wiki/Lagrange%27s_identity>; the Hestenes dot/
        magnitude relation ``|A ∧ B| = |A| |B| sin θ`` is the companion of
        ``cosine``'s H&S p. 14, eq. 1.53b).  Float input stays a float; int and
        symbolic stay exact (via :meth:`magnitude`).

        The *signed* (oriented) sine exists only in 𝒢₂, where two vectors have a
        single turn direction; see the plotting helper ``nbplotutils.sine``.

        Args:
            other: the other multivector.

        Returns:
            Coef: the unsigned sine ``|A ∧ B| / (|A| |B|)``.

        Raises:
            ValueError: if ``self`` or ``other`` is the zero vector — the angle (hence
                its sine) is undefined there (matches :meth:`cosine` and the Lean
                proofs' nonzero hypothesis).
        """
        if self == type(self).zero() or other == type(other).zero():
            raise ValueError("abs_sin (the angle) is undefined for the zero vector")
        return (
            abs(self.outer_product(other)) * (abs(self) ** (-1)) * (abs(other) ** (-1))
        )

    @classmethod
    def project(
        cls,
        onto: MultiVectorBase | Sequence[MultiVectorBase],
    ) -> ComposableFunction[MultiVectorBase]:
        """Projection  P_B(A)  =  (A · B) B⁻¹  — the component of A lying in the
        subspace represented by the blade B (``onto``).

        A projection discards the rejected part, so it is **not invertible**: this
        returns a :class:`~gacalc.functions.ComposableFunction` (labelled, composable
        into a pipeline) — not an ``InvertibleFunction``.  The return is typed at
        ``MultiVectorBase`` (the closure acts generically); a caller wanting the
        concrete type (``ComposableFunction[Vector]``) can cast at the use site.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18,
        equations 2.9a, 2.9b, 2.9c

        Args:
            onto: the blade B to project onto — a multivector, or a sequence of
                vectors (wedged into a blade first).

        Returns:
            gacalc.functions.ComposableFunction[MultiVectorBase]: the
            (non-invertible) projection ``A ↦ (A · B) B⁻¹``.
        """
        if isinstance(onto, Sequence):

            def is_multivector_sequence(
                val: Sequence[object],
            ) -> TypeIs[Sequence[MultiVectorBase]]:
                return all(isinstance(x, MultiVectorBase) for x in val)

            if is_multivector_sequence(onto):
                return cls.project(cls.outer_product_of_vectors(*onto))

        def fn(value: MultiVectorBase) -> MultiVectorBase:
            if value.is_scalar():  # 2.9b
                return value
            elif value.is_r_vector():  # 2.9c
                projected: MultiVectorBase = (value.dot(onto)) * onto.inverse()
                # P_B(A) preserves A's grade r, so the result is a grade-r blade.
                # The generic product type can widen (e.g. Vector * Bivector ->
                # G, since vector * bivector *could* carry a grade-3 part -- which
                # is identically zero for a projection): keep grade r and stay in
                # A's own type.
                grades: list[int] = list(value.grades())
                r: int = max(grades) if grades else 0
                return type(value).from_blade_dict(
                    projected.r_vector_part(r).to_blade_dict()
                )
            else:
                return (value.dot(onto)).dot(onto.inverse())  # 2.9a

        return ComposableFunction(
            fn,
            latex_repr="P_{" + onto._repr_latex_().strip("$") + "}",
            linearity=Linearity.LINEAR,
        )

    @classmethod
    def reject(
        cls,
        away_from: MultiVectorBase | Sequence[MultiVectorBase],
    ) -> ComposableFunction[MultiVectorBase]:
        """Rejection  P_B^⊥(A)  =  (A ∧ B) B⁻¹  — the component of A orthogonal to
        the subspace represented by the blade B (``away_from``).

        Like :meth:`project`, a rejection discards information and is **not
        invertible**: it returns a :class:`~gacalc.functions.ComposableFunction`.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Args:
            away_from: the blade B to reject from — a multivector, or a sequence
                of vectors (wedged into a blade first).

        Returns:
            gacalc.functions.ComposableFunction[MultiVectorBase]: the
            (non-invertible) rejection ``A ↦ (A ∧ B) B⁻¹``.

        Raises:
            Exception: if ``away_from`` is neither a vector nor a bivector.
        """

        def r(value: MultiVectorBase) -> MultiVectorBase:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(away_from, MultiVectorBase)  # to satisfy type checking
            rejected: MultiVectorBase = (value.wedge(away_from)) * away_from.inverse()
            # Rejection of a vector is a vector, but the raw product widens the
            # container in 3D+ (e.g. Vector wedge Vector -> Bivector, times a
            # vector inverse -> the odd part G with an identically-zero grade-3
            # term).  Narrow back to the operand's grade and rebuild as its type --
            # the same grade-preservation base.project does -- so reject stays in
            # the operand's type (Vector, not G) as documented.
            return type(value).from_blade_dict(
                rejected.r_vector_part(1).to_blade_dict()
            )

        def rejection(blade: MultiVectorBase) -> ComposableFunction[MultiVectorBase]:
            return ComposableFunction(
                r,
                latex_repr="P^{\\perp}_{" + blade._repr_latex_().strip("$") + "}",
                linearity=Linearity.LINEAR,
            )

        match away_from:
            case [*sequence]:
                return cls.reject(cls.outer_product_of_vectors(*sequence))
            case MultiVectorBase() as away_from_vector if away_from_vector.is_vector():
                return rejection(away_from_vector)
            case MultiVectorBase() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return rejection(away_from_bivector)
            case _:
                raise Exception("TODO - implement project for " + str(away_from))

    @classmethod
    def reflect(
        cls,
        across: MultiVectorBase | Sequence[MultiVectorBase],
    ) -> InvertibleFunction[MultiVectorBase]:
        """Reflection across the subspace (blade) ``across``  —  the projection
        minus the rejection,  P_B(A) − P_B^⊥(A).

        A reflection is an **involution** (reflecting twice is the identity), so
        unlike :meth:`project` / :meth:`reject` it *is* invertible: this returns an
        :class:`~gacalc.functions.InvertibleFunction` whose inverse is itself.

        Args:
            across: the blade to reflect across — a multivector, or a sequence of
                vectors (wedged into a blade first).

        Returns:
            gacalc.functions.InvertibleFunction[MultiVectorBase]: the reflection
            ``P_B(A) − P_B^⊥(A)``, an involution (its own inverse).

        Raises:
            Exception: if ``across`` is neither a vector nor a bivector.
        """
        components_in_plane: ComposableFunction[MultiVectorBase] = cls.project(across)
        components_exterior_to_plane: ComposableFunction[MultiVectorBase] = cls.reject(
            across
        )

        def r(value: MultiVectorBase) -> MultiVectorBase:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(across, MultiVectorBase)  # to satisfy type checking

            return components_in_plane(value) - components_exterior_to_plane(value)

        def reflection(blade: MultiVectorBase) -> InvertibleFunction[MultiVectorBase]:
            label: str = "\\mathrm{refl}_{" + blade._repr_latex_().strip("$") + "}"
            # an involution: r is its own inverse, same label for both directions.
            return InvertibleFunction(
                func=r,
                latex_repr=label,
                inverse=r,
                latex_repr_inv=label,
                linearity=Linearity.LINEAR,
            )

        match across:
            case [*sequence]:
                return cls.reflect(cls.outer_product_of_vectors(*sequence))
            case MultiVectorBase() as across_vector if across_vector.is_vector():
                return reflection(across_vector)
            case MultiVectorBase() as across_bivector if across_bivector.is_bivector():
                return reflection(across_bivector)
            case _:
                raise Exception("TODO - implement project for " + str(across))

    # -- project/reject/reflect pass-through sugar (apply the factory to this value) --
    # ``project``/``reject``/``reflect`` are *factories* returning a function; these
    # apply that function to ``self`` in one call, so ``v.rejected_away_from(b)`` reads
    # better than ``type(v).reject(away_from=b)(v)`` at a one-shot call site.  The
    # factories stay for compose/label/pipeline/Cayley uses.  Typed ``->
    # MultiVectorBase`` here; the generated vector types narrow the return to the
    # concrete vector type (grade-preserving) via @overload -- see
    # tools/gen_specialized.py ``passthrough_method_overrides``.
    def projected_onto(
        self, onto: MultiVectorBase | Sequence[MultiVectorBase]
    ) -> MultiVectorBase:
        """Project this value onto the blade ``onto`` — sugar for
        ``project(onto)(self)`` (see :meth:`project`).

        Args:
            onto: the blade to project onto (a multivector or a sequence of
                vectors).

        Returns:
            MultiVectorBase: the projection of ``self`` onto ``onto``.
        """
        return type(self).project(onto)(self)

    def rejected_away_from(
        self, away_from: MultiVectorBase | Sequence[MultiVectorBase]
    ) -> MultiVectorBase:
        """Reject this value from the blade ``away_from`` — sugar for
        ``reject(away_from)(self)`` (see :meth:`reject`).

        Args:
            away_from: the blade to reject from (a multivector or a sequence of
                vectors).

        Returns:
            MultiVectorBase: the rejection of ``self`` from ``away_from``.
        """
        return type(self).reject(away_from)(self)

    def reflected_across(
        self, across: MultiVectorBase | Sequence[MultiVectorBase]
    ) -> MultiVectorBase:
        """Reflect this value across the blade ``across`` — sugar for
        ``reflect(across)(self)`` (see :meth:`reflect`).

        Args:
            across: the blade to reflect across (a multivector or a sequence of
                vectors).

        Returns:
            MultiVectorBase: ``self`` reflected across ``across``.
        """
        return type(self).reflect(across)(self)

    # -- named measures (pass-through sugar for gacalc.measure; see that module) ----
    # These delegate to the free functions in ``gacalc.measure`` so the high-school
    # measures are discoverable on a vector (``v.area(w)``).  Deferred imports keep the
    # module graph acyclic (``measure`` imports ``base``).  Only the fixed-arity ones
    # are methods; ``content`` takes a sequence and stays a free function.

    def area(self, other: MultiVectorBase) -> Coef:
        """The area of the parallelogram on ``self`` and ``other`` -- the student's
        ``|a| |b| sin θ`` (see :meth:`abs_sin`), computed as ``|a ∧ b|`` (the method
        form of :func:`gacalc.measure.area`).

        Args:
            other: the second vector spanning the parallelogram.

        Returns:
            Coef: the (unsigned) area ``|a ∧ b|``.

        Example:
            >>> from gacalc.g2 import e_1, e_2
            >>> (3 * e_1).area(2 * e_2)
            6
            >>> (3 * e_1).area(2 * e_2) == (2 * e_2).area(3 * e_1)  # unsigned
            True
        """
        from gacalc import measure

        return measure.area(self, other)

    def volume(self, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
        """The volume of the parallelepiped on ``self``, ``b``, ``c`` -- the method
        form of :func:`gacalc.measure.volume`.

        Args:
            b: the second edge vector.
            c: the third edge vector.

        Returns:
            Coef: the (unsigned) volume of the parallelepiped.
        """
        from gacalc import measure

        return measure.volume(self, b, c)

    def signed_area(self, other: MultiVectorBase) -> Coef:
        """The signed (oriented) area of ``self`` and ``other`` -- the method form of
        :func:`gacalc.measure.signed_area` (the 2-D determinant; needs 2-D vectors).

        Args:
            other: the second vector.

        Returns:
            Coef: the signed area (the 2-D determinant; negative when ``other`` is
            clockwise from ``self``).

        Example:
            >>> from gacalc.g2 import e_1, e_2
            >>> a = 2 * e_1 + 1 * e_2
            >>> b = 1 * e_1 + 3 * e_2
            >>> a.signed_area(b)
            5
            >>> b.signed_area(a)
            -5
        """
        from gacalc import measure

        return measure.signed_area(self, other)

    def signed_volume(self, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
        """The signed (oriented) volume of ``self``, ``b``, ``c`` -- the method form
        of :func:`gacalc.measure.signed_volume` (3-D determinant; needs 3-D vectors).

        Args:
            b: the second edge vector.
            c: the third edge vector.

        Returns:
            Coef: the signed volume (the 3-D determinant).
        """
        from gacalc import measure

        return measure.signed_volume(self, b, c)

    # -- vector calculus (pass-through sugar for gacalc.vectorcalc) -----------------

    def cross(self, other: MultiVectorBase) -> MultiVectorBase:
        """The cross product ``self × other`` -- the method form of
        :func:`gacalc.vectorcalc.cross` (``= (self ∧ other) I₃⁻¹``; 3-D vectors).

        Args:
            other: the second vector.

        Returns:
            MultiVectorBase: the cross product ``self × other`` (a 3-D vector).

        Example:
            >>> from gacalc.g3 import e_1, e_2, e_3
            >>> (1 * e_1).cross(1 * e_2) == 1 * e_3
            True
        """
        from gacalc import vectorcalc

        return vectorcalc.cross(self, other)

    @staticmethod
    def identity() -> InvertibleFunction[MultiVectorBase]:
        """The identity transform — its own inverse, ``LINEAR``, labelled ``I``.

        Returns:
            gacalc.functions.InvertibleFunction[MultiVectorBase]: the identity map
            (its own inverse).
        """

        def i(value: MultiVectorBase) -> MultiVectorBase:
            return value

        return InvertibleFunction(
            func=i,
            latex_repr="I",
            inverse=i,
            latex_repr_inv="I",
            linearity=Linearity.LINEAR,
        )

    @classmethod
    def versor_from_vectors(
        cls,
        from_vector: MultiVectorBase,
        to_vector: MultiVectorBase,
    ) -> MultiVectorBase:
        r"""The versor ``R`` taking ``from_vector`` toward ``to_vector``, built from
        the angle bisector.  (Geometric products are juxtaposition, as elsewhere;
        ``A B`` is *not* an inner product.)

        Derivation (write ``a = from_vector``, ``b = to_vector``).  Scale each
        input by the *other's* length and add -- this is the half-angle, or
        angle-bisector, vector::

            h  =  |b| a  +  |a| b

        Both ``|b| a`` and ``|a| b`` have length ``|a||b|``, so their sum ``h``
        bisects the a->b angle -- it sits the same angle θ/2 from each of ``a``
        and ``b`` (drawn with ``h`` straight up, ``a`` and ``b`` mirror-imaged;
        their lengths may differ, only the directions matter here)::

                            ^   h = |b| a + |a| b
            b = to  \       |       / a = from
                     \      |      /
                      \     |     /
                       \θ/2 |θ/2 /
                        \   |   /
                         \  |  /
                          \ | /
                           \|/
                            O

        A versor is the geometric product of two vectors separated by *half* the
        target angle -- so the versor is the bisector times the from-vector::

            h a  =  (|b| a + |a| b) a
                 =  |b| (a a)  +  |a| (b a)        # a a = |a|^2  (a scalar)
                 =  |b| |a|^2  +  |a| (b a)
                 =  |a| ( |a||b|  +  b a )
                 =  |a| R

        so  ``R = b a + |a||b|`` = ``h a / |a|``  -- the leading ``|a|`` is just a
        positive scale that cancels in the sandwich.  And because
        ``|a||b| = |b a|`` (the magnitude of a product of two vectors is the
        product of their magnitudes), this is the compact ``product + |product|``
        form built below -- but that form hides the bisector ``h`` it came from.

        ``R`` is thus the (un-normalized) even multivector ``|a||b| + b a``
        (scalar + bivector): a vector ``v`` rotates by ``R v R.inverse()``, which
        equals ``projection_rotation(from, to)(v)`` (in ``transforms``).  Because
        ``R`` is un-normalized, the bare
        ``R v R.reverse()`` would also *scale* by ``R.magnitude_squared()``;
        ``R.inverse()`` (= ``R.reverse() / |R|^2``) divides that out, leaving a
        pure rotation.

        (Assumes ``from``/``to`` are not antiparallel; the construction
        degenerates only on that measure-zero case.)

        Args:
            from_vector: the vector the versor rotates *from*.
            to_vector: the vector the versor rotates *toward*.

        Returns:
            MultiVectorBase: the un-normalized versor ``|a||b| + b a`` (scalar +
            bivector); apply it with ``R v R.inverse()``.

        Raises:
            AssertionError: if either argument is not a vector (grade 1).
        """
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        # |from||to| -- the versor's scalar part, making it the half-angle versor.
        # Kept as the *product of two magnitudes* (two simple sqrts), NOT
        # |to from| = sqrt(|to|^2 |from|^2): the latter is mathematically equal
        # but sympy leaves it as a nested radical it cannot simplify through the
        # sandwich, breaking the symbolic R v R^-1 == projection_rotation
        # identity.  No cast
        # needed now that magnitude() is typed Coef (int | float | sympy.Expr).
        # (Why the two are equal -- |ab| = |a||b| via |a^b| = |a||b|sin θ -- is
        # demonstrated in notebooks/displayg2.py and displayg3.py; that the
        # |to from| form regresses this identity was re-confirmed empirically.)
        scale: Coef = from_vector.magnitude() * to_vector.magnitude()
        # scalar + bivector -- the versor's grade
        product: MultiVectorBase = to_vector * from_vector
        return product + type(product).from_coef(scale)

    @classmethod
    def bivector_from_vectors(
        cls,
        a: MultiVectorBase,
        b: MultiVectorBase,
    ) -> MultiVectorBase:
        r"""The bivector ``a`` ∧ ``b`` -- the oriented plane the two vectors span.

        Its magnitude is the area of the parallelogram on ``a`` and ``b``.  Its
        *normalized* form is the plane's **unit bivector** ``i`` (with
        ``i * i == -1``), built by the ``i(a, b)`` classmethod on the concrete
        classes (Gn, G2, G3, Vector).  Parallel vectors span no plane, so their
        wedge is the **zero** bivector -- this builder does not raise on that;
        the ``i`` builder does, when it normalizes.  Companion to
        :meth:`versor_from_vectors` (which builds the *rotor* from two vectors;
        this builds the *plane*).

        Args:
            a: the first vector.
            b: the second vector.

        Returns:
            MultiVectorBase: the bivector ``a ∧ b`` (the zero bivector if ``a``
            and ``b`` are parallel).

        Raises:
            TypeError: if either argument is not a vector (grade 1).
        """
        if not (a.is_vector() and b.is_vector()):
            raise TypeError(
                "bivector_from_vectors takes two vectors (grade-1); "
                f"got grades {a.grades()} and {b.grades()}"
            )
        return a.outer_product(b)

    def sandwich(self, x: _OperandT) -> _OperandT:
        r"""Versor conjugation  :math:`R\,x\,R^{-1}`  — apply the versor ``self``
        to ``x``, returning a value of ``x``'s own type.

        For a *versor* ``R`` (a geometric product of invertible vectors — every
        invertible even element of 𝒢₂/𝒢₃ is one, up to scale), the conjugation
        ``R x R⁻¹`` is **grade-preserving**: a vector goes to a vector, a
        bivector to a bivector, and so on.  The raw product
        ``self * x * self.inverse()`` carries the higher grade *structurally*
        (e.g. ``Versor * Vector`` carries a trivector when ``x`` is off the
        versor's plane — in 𝒢₃ that is the named ``Odd_3`` type, elsewhere it
        widens to the full ``G_n``), but for a versor those extra grades are
        zero, so the result is rebuilt as ``type(x)`` — whose ``from_blade_dict``
        keeps only ``x``'s blades.  ``zero`` conjugates to ``zero`` (no
        ``is_vector`` assertion, unlike the projection-based
        ``projection_rotation``).

        ``self`` is assumed to be a versor; for a non-versor even element in
        dimension ≥ 4 the conjugation is not grade-preserving and this is lossy.

        Args:
            x: the operand to conjugate; the result is rebuilt as ``type(x)``.

        Returns:
            _OperandT: the conjugate ``R x R⁻¹``, of ``x``'s own type.
        """
        conjugated: MultiVectorBase = self * x * self.inverse()
        return type(x).from_blade_dict(conjugated.to_blade_dict())

    def exp(self) -> MultiVectorBase:
        r"""Exponential  e^A  =  Σ Aᵏ/k!  — defined here when A² is a scalar:
        for a scalar, or for a simple (homogeneous) blade, where the Euclidean
        signature closes the series in one trig identity.

        For a grade-``r`` blade,  ``A² = pseudoscalar_squared_sign(r) · |A|²``
        (:func:`~gacalc.base.pseudoscalar_squared_sign`) — the *sign of the
        square is decided by the grade*, never by inspecting a (possibly
        symbolic) coefficient, so no branch hint is ever needed (galgebra's
        ``hint`` parameter exists only for signatures this library doesn't
        have).  The series then sums to:

        * scalar ``s``                              →  e^s
        * A² < 0  (a bivector; the 𝒢₃ pseudoscalar) →  cos|A| + sin|A| Â

        This is the **exponential map onto the rotors** (Dorst, Fontijne &
        Mann, *Geometric Algebra for Computer Science*, §7.4): for a unit
        bivector ``i`` (an oriented plane),  ``exp(−(θ/2) i)``  is exactly the
        half-angle rotor that ``transforms.plane_rotation`` /
        ``transforms.bivector_rotation`` build — "a rotor is the exponential of
        a bivector" — and it is automatically unit (cos² + sin² = 1).

        Defined **only** for the scalar and negative-square (A² < 0) cases;
        raises ``ValueError`` otherwise.  That covers A² not scalar at all (a
        rotor, or a non-simple bivector of 𝒢ₙ for n ≥ 4) and — deliberately —
        A² > 0 (a **vector**, the case
        :func:`~gacalc.base.pseudoscalar_squared_is_positive` guards).  A
        positive-square blade would exponentiate by
        the hyperbolic ``cosh|A| + sinh|A| Â``, which is a *Minkowski boost*: it
        has no meaning in this Euclidean library (early Hestenes; no
        conformal / projective / spacetime signature), so ``exp`` rejects it
        rather than silently applying a spacetime formula to a Euclidean vector.
        (An earlier version returned the hyperbolic form for vectors; it was
        lifted from galgebra with no Euclidean justification and was removed.)

        Follows the numeric-preservation convention of ``magnitude`` /
        ``inverse``: float coefficients use ``math`` trig and stay float; int
        coefficients go through sympy exactly; symbolic stays symbolic.

        The result is built with *dispatching arithmetic* (``A·k + c``), never
        ``from_blade_dict``, so a graded operand returns the resolved type
        that can hold the scalar part (Bivector → Versor; a Bivector cannot
        represent its own exponential).

        Returns:
            MultiVectorBase: e^A — a scalar for a scalar A, otherwise the rotor
            ``cos|A| + sin|A| Â`` (a bivector / the 𝒢₃ pseudoscalar).

        Raises:
            ValueError: if A² is not a scalar (a rotor or a non-simple bivector),
                or if A² > 0 (a vector — the hyperbolic/boost case, meaningless in
                this Euclidean library).

        Example:
            >>> import sympy
            >>> from gacalc.g2 import Bivector, Versor
            >>> (0 * Bivector.e_12).exp()
            g2.Versor(coeff_scalar=1, coeff_e_12=0)
            >>> (0 * Bivector.e_12).exp() == Versor(coeff_scalar=1)
            True
            >>> Bivector.e_12.exp()
            g2.Versor(coeff_scalar=cos(1), coeff_e_12=sin(1))
            >>> Bivector.e_12.exp() == Versor.e_12 * sympy.sin(1) + sympy.cos(1)
            True
            >>> theta = sympy.Symbol("theta", positive=True)
            >>> (Bivector.e_12 * (-theta / 2)).exp()  # the half-angle rotor
            g2.Versor(coeff_scalar=cos(theta/2), coeff_e_12=-sin(theta/2))
            >>> R = (Bivector.e_12 * (-theta / 2)).exp()
            >>> R == Versor.e_12 * -sympy.sin(theta / 2) + sympy.cos(theta / 2)
            True
        """
        if self.is_scalar():
            s: Coef = self.scalar_part()
            exp_s: Coef = math.exp(s) if isinstance(s, float) else sympy.exp(s)
            # zero() + exp_s routes through the dispatching add (see docstring)
            return type(self).zero() + exp_s
        if not self.is_r_vector() or not (self * self).is_scalar():
            raise ValueError(
                "exp is defined when A**2 is a scalar: a scalar or a simple "
                f"(homogeneous) blade; got grades {sorted(self.grades())}"
            )
        r: int = self.max_grade()
        if pseudoscalar_squared_is_positive(r):
            # A**2 > 0 (a vector, or any positive-square blade): the series
            # would sum to the hyperbolic cosh|A| + sinh|A| Â -- the Minkowski
            # boost, meaningful only in a spacetime metric this Euclidean
            # library does not have.  Rejected rather than silently applied
            # (see the docstring); exp needs A**2 < 0.
            raise ValueError(
                f"exp is not defined for a grade-{r} blade: its square is "
                "positive (A**2 > 0, the hyperbolic/boost case), which has no "
                "Euclidean meaning; exp needs A**2 < 0 (a bivector or the 𝒢₃ "
                f"pseudoscalar). got grades {sorted(self.grades())}"
            )
        # the one remaining case: A**2 < 0 (bivector / pseudoscalar) -> a rotor.
        theta: Coef = self.magnitude()
        numeric: bool = isinstance(theta, float)
        cos_t: Coef = math.cos(theta) if numeric else sympy.cos(theta)
        sin_t: Coef = math.sin(theta) if numeric else sympy.sin(theta)
        #   Â sin|A| + cos|A|   with   Â = A / |A|
        return self * (sin_t / theta) + cos_t

    def isclose(
        self, other: typing.Self, rel_tol: float = 0.0, abs_tol: float = 0.0
    ) -> bool:
        """Approximate **floating-point** equality, blade by blade: the symmetric
        PEP 485 / ``math.isclose`` test
        ``abs(a - b) <= max(rel_tol * max(|a|, |b|), abs_tol)`` over the union of
        present blades (a blade absent on one side counts as ``0``).

        Floating-point only.  A symbolic (non-numeric) coefficient raises a
        ``TypeError`` -- use ``==`` for exact/symbolic equality.  **Both
        tolerances default to ``0.0``**, so with no arguments this is *exact*
        equality; a caller states the tolerance it wants (``rel_tol`` for the
        general case, ``abs_tol`` for values near zero -- a rotated basis
        vector's off-axis components, a product that cancels to 0, ...).  Every
        in-tree caller passes ``rel_tol=1e-5, abs_tol=1e-5``.

        Args:
            other: the multivector to compare against.
            rel_tol: relative tolerance (default ``0.0`` — exact).
            abs_tol: absolute tolerance, for values near zero (default ``0.0``).

        Returns:
            bool: ``True`` iff every blade coefficient is within tolerance.

        Raises:
            TypeError: if any coefficient is symbolic (non-numeric) — use ``==``
                for exact/symbolic equality.
        """
        left: BladeCoef = self.to_blade_dict()
        right: BladeCoef = other.to_blade_dict()
        # ``blade`` is a genexpr var (separate scope) so it stays inferred.
        return all(
            math.isclose(
                _require_float(left.get(blade, 0)),
                _require_float(right.get(blade, 0)),
                rel_tol=rel_tol,
                abs_tol=abs_tol,
            )
            for blade in (left.keys() | right.keys())
        )

    def __repr__(self) -> str:
        """A module-qualified repr, e.g. ``g2.Vector(coeff_e_1=1.5, coeff_e_2=2.0)``.

        The generated value types are ``@dataclass(repr=False)`` and inherit this,
        so the module short name (``g1``/``g2``/``g3``) carries the algebra's
        dimension that the unsuffixed class name (``Vector``, ``Versor``, ``G``) no
        longer does. (``Gn`` keeps its own dataclass repr — it isn't renamed.)
        Assumes the concrete type is a dataclass, which every representation is.

        Returns:
            str: a module-qualified constructor-style repr.
        """
        module: str = type(self).__module__.rsplit(".", 1)[-1]
        # every concrete representation is a dataclass; base itself is abstract, so
        # cast past dataclasses.fields' DataclassInstance bound.
        instance: typing.Any = self
        fields: str = ", ".join(
            f"{f.name}={getattr(self, f.name)!r}" for f in dataclasses.fields(instance)
        )
        return f"{module}.{type(self).__name__}({fields})"

    def _repr_latex_(self) -> str:
        """Render A as LaTeX for Jupyter's rich display (the name Jupyter looks up).

        Shows the simplified view so the lazy classes don't display un-reduced
        coefficients; the stored fields are left untouched.

        Returns:
            str: the LaTeX rendering of the simplified value (``$...$``).
        """
        # Display the simplified view: the lazy classes (G, graded subtypes)
        # don't eager-simplify, so a raw coefficient may not be in lowest terms
        # (e.g. a bivector times its dual whose terms should cancel).  Simplifying
        # only the rendered form leaves the stored fields untouched.  (`Gn` already
        # eager-simplifies, so this is a cheap no-op there; display is not hot.)
        return blade_dict_latex(self.simplified().to_blade_dict())


def _coef_eq(left: Coef, right: Coef) -> bool:
    """Coefficient equality: exact for plain numbers, ``simplify``-backed for symbols.

    Native ``==`` settles *both* plain-number outcomes on its own -- equal numbers
    are equal, and ``simplify`` can never turn two *unequal* numbers into equal
    ones -- so when neither side is symbolic the answer is already known and the
    sympy branch is pure cost.  That cost is not small: a differing numeric
    comparison (``Vector(3.0, 4.0) == Vector(1.5, -2.0)``) measured 48 us against
    0.018 us for the equivalent tuple comparison, and dominated a
    modelviewprojection game profile (2026-09-06).

    sympy is therefore reached only when at least one side is a symbolic
    expression, where structurally-different-but-equal forms (``(x + 1)**2`` vs
    ``x**2 + 2*x + 1``) must still compare equal.  Float ``==`` stays EXACT on
    purpose (``0.1 + 0.2 != 0.3``); tolerance is ``isclose``'s job, not ``==``'s.

    Shared by every generated ``__eq__`` -- the same-type field comparison and the
    cross-type blade-dict fallback both call it (``tools/gen_specialized.py``,
    ``eq_method``), so the rule lives in one hand-written, gate-checked place
    rather than being emitted twice as inline AST.
    """
    if left == right:
        return True
    if not (isinstance(left, sympy.Basic) or isinstance(right, sympy.Basic)):
        return False
    return bool(sympy.simplify(sympy.sympify(left) - sympy.sympify(right)) == 0)


def _require_float(coef: Coef) -> float:
    """A coefficient as a ``float`` for ``isclose``; raise a clear
    error on a symbolic (non-numeric) coefficient.

    ``isclose`` is floating-point only, so a coefficient carrying a
    free symbol (``x``, ``2*t``, ...) has no meaningful float value.  Numeric
    sympy (``Integer``/``Rational``/``Float``/``sqrt(2)``) is ``float``-able and
    passes through; only a genuinely symbolic expression raises -- and it raises
    *here*, with a message that names the value, instead of the opaque
    ``TypeError`` a bare ``float(expr)`` would throw.
    """
    if isinstance(coef, sympy.Expr) and not coef.is_number:
        raise TypeError(
            "isclose is floating-point only; got the symbolic "
            f"coefficient {coef!r} -- use == for exact/symbolic equality"
        )
    return float(coef)


def _coerce[T: MultiVectorBase](x: MultiVectorBase | Coef, cls: type[T]) -> T:
    """Coerce a scalar or multivector to ``cls`` (the full type).

    The shared widen helper for the generated dispatch methods' ``case _:``
    fallback arms (g1/g2/g3 import it): an operand no closed-form arm matched
    is rebuilt in the algebra's full class via the blade-dict interchange, and
    a bare number/``sympy.Expr`` becomes the scalar part.  (One definition
    here rather than a copy per generated module.)
    """
    match x:
        case MultiVectorBase():
            return cls.from_blade_dict(x.to_blade_dict())
        case sympy.Expr():
            return cls.from_coef(x)
        case _:
            return cls.from_scalar(x)


def _require_canonical_blades(blade_coef: Mapping[Blade, object]) -> None:
    """Raise ``ValueError`` on a non-canonical blade key (see ``BladeCoef``).
    Only the keys are read, so any blade-keyed mapping qualifies (a ``BladeCoef``,
    or ``set_blade_symbols``'s blade -> LaTeX-string map).

    A canonical key's indices are strictly increasing (``(1, 2)``, never
    ``(2, 1)`` or ``(1, 1)``).  ``e₂e₁`` is a legal algebra *element* but not
    a legal *key*: it equals ``−e₁e₂``, so it belongs under the sorted key
    with the sign folded into the coefficient (and a repeated index contracts
    away entirely, ``eᵢeᵢ = 1``).  Shared by every representation's
    ``from_blade_dict`` (the generated modules import it), replacing two old
    *silent* failure modes -- ``Gn`` storing the bad key raw, the specialized
    classes dropping it -- with one loud error (decision (a) of
    tasks/validate-blade-dict-keys.md, 2026-07-29).
    """
    blade: Blade
    for blade in blade_coef:
        if any(a >= b for a, b in zip(blade, blade[1:])):
            raise ValueError(
                f"blade key {blade!r} is not canonical: indices must be "
                "strictly increasing -- e.g. e2 e1 = -e1 e2 belongs under "
                "key (1, 2) with a negated coefficient, and a repeated "
                "index contracts (e_i e_i = 1)"
            )
