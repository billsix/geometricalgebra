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
# and then rejects `+`/`/`/`**` on it, which broke the generated rotor sandwich.
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
#:   be built via dispatching arithmetic (``Bivector + scalar -> Rotor``),
#:   never via ``from_blade_dict`` on the operand's type (see ``exp``).
BladeCoef = dict[Blade, Coef]
MultiVectorFn = Callable[["MultiVectorBase"], "MultiVectorBase"]

#: Type variable for the operand of a versor sandwich -- the result has the
#: operand's own type (see ``MultiVectorBase.sandwich``).
_OperandT = typing.TypeVar("_OperandT", bound="MultiVectorBase")


def blade_dict_latex(d: BladeCoef) -> str:
    """Render a blade -> coefficient dict as a LaTeX string (the body of
    ``_repr_latex_``, factored out so callers can render a chosen *view*).

    Blades are grade-ordered (``(len, indices)``); a sum coefficient is
    parenthesized; an empty dict renders as ``0``.  ``_repr_latex_`` passes the
    *simplified* dict (display-simplify); ``nbplotutils.show_mult`` passes the
    *expanded* dict, so distribution is visible there without that simplify.
    """

    def add_parens_or_dont(x: Coef) -> str:
        # Parenthesize a sum so its terms bind to the blade; render straight from
        # the sympy/number object (no fragile sympify(str(x)) round-trip).
        if isinstance(x, sympy.Expr) and x.is_Add:
            return "(" + sympy.latex(x) + ")"
        return sympy.latex(x)

    blades: list[str] = [
        add_parens_or_dont(d[blade])
        + " ".join(map(lambda b: r"\mathbf{\vec{e}}_" + str(b), blade))
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

        Raises ``ValueError`` on a non-canonical blade key (indices must be
        strictly increasing -- see ``BladeCoef`` / ``_require_canonical_blades``).
        """

    @abc.abstractmethod
    def to_blade_dict(self) -> BladeCoef:
        """Return this multivector as a canonical blade -> coefficient mapping."""

    @classmethod
    def from_scalar(cls, scalar: int | float) -> typing.Self:
        return cls.from_blade_dict({tuple(): scalar})

    @classmethod
    def from_coef(cls, s: Coef) -> typing.Self:
        return cls.from_blade_dict({tuple(): s})

    @classmethod
    def zero(cls) -> typing.Self:
        return cls.from_scalar(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls.from_scalar(1)

    @classmethod
    def basis_vector(cls, i: int) -> typing.Self:
        """The i-th basis vector e_i of this representation (1-indexed).

        Part of the interchange protocol: lets representation-agnostic code
        (e.g. the transform layer) obtain a basis vector of the *caller's* own
        concrete type, so results stay in that type rather than coercing to Gn.
        """
        return cls.from_blade_dict({(i,): 1})

    @classmethod
    def unit_pseudoscalar(cls, n: int) -> typing.Self:
        """Unit pseudoscalar  i  =  e₁ e₂ … e_n  — the highest-grade unit blade of
        the n-dimensional algebra.
        """
        return math.prod(
            [cls.basis_vector(x) for x in range(1, n + 1)],
            start=cls.one(),
        )

    @classmethod
    def bases(cls, n: int) -> Generator[typing.Self]:
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
        mv: list[MultiVectorBase] = list(cls.bases(n))
        symbols: list[sympy.Symbol] = sympy.symbols(prefix + ":" + str(len(mv)))
        return sum([s * blade for s, blade in zip(symbols, mv)], start=cls.zero())

    @classmethod
    def unit_pseudoscalar_squared(cls, n: int) -> typing.Self:
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
        """

    def __mul__(self, rhs: MultiVectorBase | Coef) -> typing.Self:
        match rhs:
            case int() | float() as n:
                return self._geometric_product(type(self).from_scalar(n))
            case sympy.Expr() as s:
                return self._geometric_product(type(self).from_coef(s))
            case _:
                return self._geometric_product(rhs)

    def __rmul__(self, lhs: MultiVectorBase | Coef) -> typing.Self:
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
        # A bare number is the scalar (grade-0) part -- the generated
        # specialized classes already accept ``mv + 2``; the shared base
        # matches them so e.g. ``bivector * (-s) + c`` builds a rotor in
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
        # addition commutes; gives ``2 + mv`` for free.  ``lhs`` is a bare number,
        # never a multivector: Python only calls ``__radd__`` when the left operand
        # (here a non-multivector) has no ``__add__`` for us -- a multivector left
        # operand uses its own ``__add__``.  Typing it ``Coef`` (not
        # ``MultiVectorBase | Coef``) also matches the generated specialized
        # ``__radd__`` (whose ``lhs`` is a number union), so the override is
        # Liskov-clean at every dimension.
        return self.__add__(lhs)

    def __sub__(self, rhs: typing.Self) -> typing.Self:
        return self + -rhs

    def __neg__(self) -> typing.Self:
        return -1 * self

    def __truediv__(self, rhs: MultiVectorBase | Coef) -> typing.Self:
        """Quotient  A / B  =  A B⁻¹  — division IS multiplication by the
        inverse (right division: order matters in a non-commutative algebra).
        A bare number's inverse is its reciprocal, so ``v / s`` divides every
        coefficient."""
        if isinstance(rhs, (int, float, sympy.Expr)):
            return self * (1 / rhs)
        return self * rhs.inverse()

    def __abs__(self) -> Coef:
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
        """
        d: BladeCoef = self.to_blade_dict()
        yield from (d[key] for key in sorted(d.keys(), key=lambda b: (len(b), b)))

    def magnitude(self) -> Coef:
        """Magnitude  |A|  =  √(Ã ∗ A)  — the positive square root of the scalar
        product of A with its reverse.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.49

        Float input stays a float: ``sympy.sqrt`` always returns a ``sympy.Expr``
        (e.g. ``sqrt(2.0)`` -> ``1.41421356237310`` as a ``sympy.Float``), which
        would leak symbolic objects into purely numeric pipelines (and, downstream,
        produce ``numpy`` ``dtype=object`` arrays).  When ``|A|²`` is a Python
        ``float`` (already inexact) we therefore take ``math.sqrt`` and return a
        ``float``.  An ``int`` |A|² keeps ``sympy.sqrt`` so exactness is preserved
        (``sqrt(25) == 5`` exactly, and a unit blade normalizes to ``Rational``s,
        not floats); symbolic coefficients also stay symbolic.
        """
        magnitude_squared: Coef = self.magnitude_squared()
        if isinstance(magnitude_squared, float):
            return math.sqrt(magnitude_squared)
        return sympy.sqrt(magnitude_squared)

    def magnitude_squared(self) -> Coef:
        """Squared magnitude  |A|²  =  Ã ∗ A  =  ⟨Ã A⟩  (a scalar)."""
        return self.reverse().scalar_product(self)

    def normalize(self) -> typing.Self:
        """Unit multivector  Â  =  A / |A|  — A rescaled to magnitude 1.

        Raises ``ZeroDivisionError`` if ``A`` has zero magnitude (e.g. the zero
        vector), for **any** coefficient kind. A float-zero already raised; without
        this guard an int/symbolic zero silently returned a ``nan``-poisoned value
        (sympy ``0 ** -1`` → ``zoo``, ``0 * zoo`` → ``nan``).
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
        """
        return self._map_coefficients(lambda c: sympy.simplify(c))  # type: ignore

    def expanded(self) -> typing.Self:
        """The same multivector with every coefficient ``sympy.expand``'d.

        Distributes products over sums in each coefficient — the fully *distributed*
        form (e.g. for showing that the geometric product is distributive).  Equal in
        value; only the coefficient form changes.
        """
        return self._map_coefficients(lambda c: sympy.expand(c))

    def inner_product(self, rhs: typing.Self) -> typing.Self:
        """Inner (dot) product  A · B  — the lowest-grade part of the geometric
        product, ⟨A B⟩_|r−s| summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.21a, 1.21b, 1.21c
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
        return self.inner_product(rhs)

    def outer_product(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  — the highest-grade part of the geometric
        product, ⟨A B⟩_(r+s) summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.22a, 1.22b, 1.22c
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
        """
        return (self * other).scalar_part()

    def wedge(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  (alias of ``outer_product``)."""
        return self.outer_product(rhs)

    def __xor__(self, other: typing.Self) -> typing.Self:
        """Operator form of the outer product:  a ^ b  ==  a ∧ b  ==  a.wedge(b)."""
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
        """Operator form of the left contraction:  a < b  ==  a.left_contraction(b)."""
        return self.left_contraction(other)

    def __gt__(self, other: typing.Self) -> typing.Self:
        """Operator form of the right contraction: a > b == a.right_contraction(b)."""
        return self.right_contraction(other)

    @staticmethod
    def outer_product_of_vectors(
        *vectors: MultiVectorBase,
    ) -> MultiVectorBase:
        """Outer product of several vectors  a₁ ∧ a₂ ∧ … ∧ a_r  — a simple r-blade."""
        return functools.reduce(lambda a, b: a ^ b, vectors)

    def r_vector_part(self, r: int) -> typing.Self:
        """Grade-r part  ⟨A⟩ᵣ  — the r-vector (grade-r) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        d: BladeCoef = self.to_blade_dict()
        return type(self).from_blade_dict(
            {blade: d[blade] for blade in d.keys() if len(blade) == r}
        )

    def is_homogeneous_of_grade_r(self, r: int) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4

        The zero multivector has no present blades, so it is trivially homogeneous of
        EVERY grade -- consistent with ``is_scalar(zero) == True``.
        """
        grades: list[int] = self.grades()
        return not grades or (max(grades) == r and self.is_r_vector())

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

    def scalar_part(self) -> Coef:
        """Scalar part  ⟨A⟩  =  ⟨A⟩₀  — the grade-0 (scalar) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self.to_blade_dict().get(tuple(), 0)

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.to_blade_dict().keys()))

    def max_grade(self) -> int:
        # The zero multivector has no present blades; its max grade is 0 (it is
        # homogeneous of every grade -- see is_homogeneous_of_grade_r) rather than a
        # crash on max([]).
        return max(self.grades(), default=0)

    def reverse(self) -> typing.Self:
        """Reverse  Ã  — reverses the order of the vector factors in each blade,
        giving the grade-r part the sign (−1)^(r(r−1)/2).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5,
        equation 1.19
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
        """Inverse  A⁻¹  =  Ã / |A|²  — defined when |A|² ≠ 0.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Not sure if I'm doing it correctly
        """
        # Keep numeric input numeric: a ``float`` |A|² stays a float so the
        # reciprocal doesn't leak sympy into numeric pipelines.  For an ``int``
        # (e.g. a unit blade, |A|² == 1) sympify first, so ``int ** -1`` keeps the
        # exact Rational instead of silently degrading to a float; symbolic |A|²
        # stays symbolic.  (Mirrors the numeric/symbolic split in ``magnitude``.)
        mag_sq: Coef = self.magnitude_squared()
        if not isinstance(mag_sq, float):
            mag_sq = sympy.sympify(mag_sq)
        if mag_sq == 0:
            raise ZeroDivisionError("cannot invert a zero-magnitude multivector")
        return self.reverse() * (mag_sq ** (-1))

    # dual returns MultiVectorBase (not Self) for the same reason as even_part/
    # odd_part below: it maps grade r -> grade n−r, a *different* grade, so a
    # fixed-dimension graded override narrows the return to the resolved type
    # (Bivector.dual -> Vector) -- an override that -> Self would forbid.  The
    # full class G_n keeps -> Self (all grades); Gn inherits this base.
    def dual(self, n: int) -> MultiVectorBase:
        """Dual  A*  =  A I⁻¹  — multiplication by the inverse unit pseudoscalar I,
        mapping a grade-r part to grade n−r.
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
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 0],
            start=type(self).zero(),
        )

    def odd_part(self) -> MultiVectorBase:
        """Odd part  A⁻  =  ⟨A⟩₁ + ⟨A⟩₃ + …  — the sum of the odd-grade parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 1],
            start=type(self).zero(),
        )

    def cosine(self, other: MultiVectorBase) -> Coef:
        """Cosine of the angle between A and B  —  cos θ  =  (Ã ∗ B) / (|A| |B|).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14,
        equation 1.53b
        """
        return (
            self.reverse().scalar_product(other)
            * (abs(self) ** (-1))
            * (abs(other) ** (-1))
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

    # -- named measures (pass-through sugar for gacalc.measure; see that module) ----
    # These delegate to the free functions in ``gacalc.measure`` so the high-school
    # measures are discoverable on a vector (``v.area(w)``).  Deferred imports keep the
    # module graph acyclic (``measure`` imports ``base``).  Only the fixed-arity ones
    # are methods; ``content`` takes a sequence and stays a free function.

    def area(self, other: MultiVectorBase) -> Coef:
        """The area of the parallelogram on ``self`` and ``other`` -- the method form
        of :func:`gacalc.measure.area` (``= |a ∧ b|``).

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
        form of :func:`gacalc.measure.volume`."""
        from gacalc import measure

        return measure.volume(self, b, c)

    def signed_area(self, other: MultiVectorBase) -> Coef:
        """The signed (oriented) area of ``self`` and ``other`` -- the method form of
        :func:`gacalc.measure.signed_area` (the 2-D determinant; needs 2-D vectors).

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
        of :func:`gacalc.measure.signed_volume` (3-D determinant; needs 3-D vectors)."""
        from gacalc import measure

        return measure.signed_volume(self, b, c)

    @staticmethod
    def identity() -> InvertibleFunction[MultiVectorBase]:
        """The identity transform — its own inverse, ``LINEAR``, labelled ``I``."""

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
    def rotor_from_vectors(
        cls,
        from_vector: MultiVectorBase,
        to_vector: MultiVectorBase,
    ) -> MultiVectorBase:
        r"""The rotor ``R`` taking ``from_vector`` toward ``to_vector``, built from
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

        A rotor is the geometric product of two vectors separated by *half* the
        target angle -- so the rotor is the bisector times the from-vector::

            h a  =  (|b| a + |a| b) a
                 =  |b| (a a)  +  |a| (b a)        # a a = |a|^2  (a scalar)
                 =  |b| |a|^2  +  |a| (b a)
                 =  |a| ( |a||b|  +  b a )
                 =  |a| R

        so  R = b a + |a||b| = h a / |a|  -- the leading ``|a|`` is just a
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
        """
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        # |from||to| -- the rotor's scalar part, making it the half-angle rotor.
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
        # scalar + bivector -- the rotor's grade
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
        :meth:`rotor_from_vectors` (which builds the *rotor* from two vectors;
        this builds the *plane*).
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
        ``self * x * self.inverse()`` may *structurally* widen (e.g.
        ``Rotor * Vector`` carries a trivector when ``x`` is off the rotor's
        plane), but for a versor those extra grades are zero, so the result is
        rebuilt as ``type(x)`` — whose ``from_blade_dict`` keeps only ``x``'s
        blades.  ``zero`` conjugates to ``zero`` (no ``is_vector`` assertion,
        unlike the projection-based ``projection_rotation``).

        ``self`` is assumed to be a versor; for a non-versor even element in
        dimension ≥ 4 the conjugation is not grade-preserving and this is lossy.
        """
        conjugated: MultiVectorBase = self * x * self.inverse()
        return type(x).from_blade_dict(conjugated.to_blade_dict())

    def exp(self) -> MultiVectorBase:
        r"""Exponential  e^A  =  Σ Aᵏ/k!  — defined here when A² is a scalar:
        for a scalar, or for a simple (homogeneous) blade, where the Euclidean
        signature closes the series in one trig identity.

        For a grade-r blade,  A² = (−1)^(r(r−1)/2) |A|²  — the *sign of the
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
        A² > 0 (a **vector**).  A positive-square blade would exponentiate by
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
        that can hold the scalar part (Bivector → Rotor; a Bivector cannot
        represent its own exponential).

        >>> import sympy
        >>> from gacalc.g2 import Bivector, Rotor
        >>> (0 * Bivector.e_12).exp()
        g2.Rotor(coeff_scalar=1, coeff_e_12=0)
        >>> (0 * Bivector.e_12).exp() == Rotor(coeff_scalar=1)
        True
        >>> Bivector.e_12.exp()
        g2.Rotor(coeff_scalar=cos(1), coeff_e_12=sin(1))
        >>> Bivector.e_12.exp() == Rotor.e_12 * sympy.sin(1) + sympy.cos(1)
        True
        >>> theta = sympy.Symbol("theta", positive=True)
        >>> (Bivector.e_12 * (-theta / 2)).exp()  # the half-angle rotor
        g2.Rotor(coeff_scalar=cos(theta/2), coeff_e_12=-sin(theta/2))
        >>> R = (Bivector.e_12 * (-theta / 2)).exp()
        >>> R == Rotor.e_12 * -sympy.sin(theta / 2) + sympy.cos(theta / 2)
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
        dimension that the unsuffixed class name (``Vector``, ``Rotor``, ``G``) no
        longer does. (``Gn`` keeps its own dataclass repr — it isn't renamed.)
        Assumes the concrete type is a dataclass, which every representation is.
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
        # Display the simplified view: the lazy classes (G, graded subtypes)
        # don't eager-simplify, so a raw coefficient may not be in lowest terms
        # (e.g. a bivector times its dual whose terms should cancel).  Simplifying
        # only the rendered form leaves the stored fields untouched.  (`Gn` already
        # eager-simplifies, so this is a cheap no-op there; display is not hot.)
        return blade_dict_latex(self.simplified().to_blade_dict())


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
    if isinstance(x, MultiVectorBase):
        return cls.from_blade_dict(x.to_blade_dict())
    if isinstance(x, sympy.Expr):
        return cls.from_coef(x)
    return cls.from_scalar(x)


def _require_canonical_blades(blade_coef: Mapping[Blade, Coef]) -> None:
    """Raise ``ValueError`` on a non-canonical blade key (see ``BladeCoef``).

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
    for blade in blade_coef:
        if any(a >= b for a, b in zip(blade, blade[1:])):
            raise ValueError(
                f"blade key {blade!r} is not canonical: indices must be "
                "strictly increasing -- e.g. e2 e1 = -e1 e2 belongs under "
                "key (1, 2) with a negated coefficient, and a repeated "
                "index contracts (e_i e_i = 1)"
            )
