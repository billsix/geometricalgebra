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

"""Frames -- linearly independent sets of vectors -- and their orthogonalization.

from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 27.

A **frame** is a set of vectors ``{a_1, …, a_k}`` whose outer product is nonzero,
``a_1 ∧ a_2 ∧ … ∧ a_k ≠ 0`` -- equivalently, a linearly independent set (a basis
when ``k = n``).  A frame need NOT be orthogonal; the wedge, not orthogonality, is
the defining condition.

The predicates and orthogonalizations are representation-agnostic **free functions**
over :class:`~gacalc.base.MultiVectorBase` vectors (they work on the general ``Gn``
type and on the graded ``Vector_n`` types alike).  :class:`Frame` packages a frame as
an orthogonal set plus the coefficients that rebuild the original vectors from it
(the QR decomposition, with the lengths factored out), and turns it into an
:class:`~gacalc.functions.InvertibleFunction` sending ``e_i`` to ``v_i``.  The math is
in ``tasks/reference/frames-qr-and-reciprocal-frames.md``.
"""

from __future__ import annotations

import dataclasses
import functools
import operator
from collections.abc import Callable, Iterator, Sequence
from itertools import accumulate, pairwise
from typing import Literal

import numpy as np

from gacalc.base import MultiVectorBase, Real
from gacalc.functions import InvertibleFunction, Linearity
from gacalc.transforms import coordinate_along, line_to_line_projection


def are_linearly_independent(
    vectors: Sequence[MultiVectorBase],
    float_close_to_zero: bool = False,
) -> bool:
    """Whether ``vectors`` are linearly independent -- the Hestenes frame condition
    ``a_1 ∧ a_2 ∧ … ∧ a_k ≠ 0`` (H&S p. 27).

    The outer product of the vectors is the (signed) volume of the parallelotope
    they span; it vanishes iff they are linearly dependent.  With
    ``float_close_to_zero=True`` the vanishing test is a tolerant ``np.isclose`` on
    the blade's magnitude (for numeric vectors, where exact zero would not hold
    after rounding); the default is the exact ``≠ 0`` (symbolic vectors, or when
    exactness is wanted).  Mirrors :meth:`MultiVectorBase.is_orthogonal_to`.

    Every input must be a vector (grade 1); a non-vector member is a misuse and
    raises ``ValueError`` -- a frame is a set of *vectors*, and a bivector (say) in
    the list is a category error, not "a dependent frame."  An empty sequence is not
    a frame (returns ``False``).
    """
    if len(vectors) == 0:
        return False
    MultiVectorBase.require_vectors(vectors, "a frame")
    blade: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
    return (
        not bool(np.isclose(float(blade.magnitude()), 0.0, rtol=1e-5, atol=1e-5))
        if float_close_to_zero
        else blade != type(blade).zero()
    )


def is_frame(
    vectors: Sequence[MultiVectorBase],
    float_close_to_zero: bool = False,
) -> bool:
    """Whether ``vectors`` form a frame -- a linearly independent set (H&S p. 27).

    A pass-through to :func:`are_linearly_independent`: a frame *is* a linearly
    independent set of vectors.

    Examples:
        >>> from gacalc.gn import e_1, e_2, e_3
        >>> is_frame([1 * e_1])                            # a single nonzero vector
        True
        >>> is_frame([1 * e_1, 1 * e_2])                   # the 2-D basis
        True
        >>> is_frame([1 * e_1, 1 * e_2, 1 * e_3])          # the 3-D basis
        True
        >>> is_frame([1 * e_1 + 1 * e_2, 1 * e_2])         # oblique, still independent
        True
        >>> is_frame([1 * e_1, 2 * e_1])                   # parallel -> dependent
        False
        >>> is_frame([1 * e_1, 1 * e_2, 1 * e_1 + 1 * e_2])  # dependent: 3rd in span
        False
        >>> is_frame([1 * e_1, 1 * e_2, 1 * e_3, 1 * e_1])  # a repeat in 3-D
        False
        >>> is_frame([])                                   # an empty set is not a frame
        False
    """
    return are_linearly_independent(vectors, float_close_to_zero)


def _scalar_one(vector: MultiVectorBase) -> MultiVectorBase:
    """The scalar 1, in a representation of ``vector``'s algebra that can hold it.

    ``type(vector).one()`` is not enough: a graded ``Vector_n`` type has no scalar
    slot, so its ``one()`` is the zero vector, and a wedge seeded with it is zero.
    ``vector · vector`` is a scalar, so its type is one that holds scalars:
    ``Scalar_n`` for the graded types, and ``Gn`` itself for ``Gn``.
    """
    return type(vector.dot(vector)).one()


def prefix_blades(
    vectors: Sequence[MultiVectorBase],
) -> Iterator[MultiVectorBase]:
    """The prefix outer products of a frame -- ``A_0 := 1``, ``A_k := A_{k-1} ∧ v_k``
    (H&S p. 27, eq 3.1).

    Yields ``A_0 = 1`` (the scalar one, in a representation of the operands' algebra
    that holds scalars) first,
    then each prefix wedge: ``A_1 = v_1``, ``A_2 = v_1 ∧ v_2``, …,
    ``A_k = v_1 ∧ … ∧ v_k`` -- ``k + 1`` blades for ``k`` vectors.  The fold reuses the
    blade yielded just before (``accumulate`` carries it), so the whole prefix costs
    ``O(k)`` wedges, not an ``O(k²)`` rebuild of each blade from scratch.

    A representation-agnostic building block (works on ``Gn`` and the graded
    ``Vector_n`` types alike).  Its first consumer is
    :func:`make_orthogonal_frame_hestenes`'s eq-3.2 step, which reads ``A_{k-1}`` and
    ``A_k`` pairwise; the reciprocal frame (H&S p. 27-28) is another natural consumer.
    Lazy -- it returns an iterator.

    Raises:
        ValueError: if ``vectors`` is empty -- there is no operand from which to take
            the representation of the scalar ``A_0 = 1`` (a frame is a nonempty,
            linearly independent set of vectors).
    """
    if len(vectors) == 0:
        raise ValueError(
            "prefix_blades requires a nonempty sequence of vectors (a frame); there "
            "is no operand to take the representation of the scalar A_0 = 1 from"
        )
    # accumulate(seq, ∧, initial=1) folds the wedge over the prefix, seeding with the
    # scalar one: yields A_0 = 1, A_1 = 1 ∧ v_1 = v_1, A_2 = A_1 ∧ v_2, …
    return accumulate(vectors, operator.xor, initial=_scalar_one(vectors[0]))


def make_orthogonal_frame(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """Orthogonalize a frame by **rejection** (H&S p. 27) -- Gram–Schmidt done the
    geometric-algebra way.

    Keep the first vector as-is, reject it out of every vector after it, then
    orthogonalize the rest the same way (recursing on the tail).  By the time a
    vector becomes the head to keep, every vector finalized before it has already
    been rejected out of it, so it is orthogonal to all of them; the result spans
    the same subspace but is mutually orthogonal (``is_orthogonal_to`` between every
    pair).  Each step rejects one already-orthogonal vector at a time, and because
    those vectors are mutually orthogonal, rejecting them one at a time equals
    rejecting their whole span -- so it stays within the grade-1/grade-2 rejections
    gacalc implements.

    The result is **orthogonal, not orthonormal** -- the original lengths are kept
    (the first vector is returned unchanged).  Normalizing each result would give an
    orthonormal frame; that is a separate operation.

    See also :func:`make_orthogonal_frame_hestenes` -- the *same* orthogonalization
    computed a different way (Hestenes' closed-form blade product), kept side by side
    for teaching. The two agree up to a positive scalar per vector
    (``c_k == |A_{k-1}|² * w_k``; proved by ``tests/test_frame.py``). Neither is
    "better", so both stay.

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent -- a later
            vector would reject to zero and the result could not be a frame).
    """
    if not is_frame(vectors):
        raise ValueError(
            "make_orthogonal_frame requires a frame (linearly independent "
            "vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent"
        )

    def orthogonalize(
        remaining: Sequence[MultiVectorBase],
    ) -> list[MultiVectorBase]:
        match list(remaining):
            case []:
                # Base case: no vectors, nothing to orthogonalize.
                return []
            case [v]:
                # A single vector is already an orthogonal frame on its own --
                # there is nothing to reject it out of.
                return [v]
            case [v, *rest]:
                # Two or more: remove from each later vector its component parallel
                # to the first (reject the first out of the rest), keep the first,
                # and recursively orthogonalize the rest.  The first is already
                # orthogonal to every vector finalized before it -- each earlier
                # head was rejected out of it on the way down.
                return [
                    v,
                    *orthogonalize([w.rejected_away_from(v) for w in rest]),
                ]
            case _:
                # Unreachable: [] / [v] / [v, *rest] already cover every list.
                # Kept as the total default because ty does not prove list-pattern
                # exhaustiveness, so the match needs an explicit catch-all.
                return []

    return orthogonalize(vectors)


def make_orthogonal_frame_hestenes(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """Orthogonalize a frame the way Hestenes does it -- the **closed-form blade
    product** (H&S p. 27, eqs 3.1–3.2), the sibling of :func:`make_orthogonal_frame`.

    With the prefix blades ``A_0 := 1``, ``A_k := v_1 ∧ v_2 ∧ … ∧ v_k`` (eq 3.1),
    each orthogonal vector is

    ::

        c_k := reverse(A_{k-1}) * A_k                 (eq 3.2)

    a **closed form**: every ``c_k`` is built directly from the original prefix
    ``v_1 … v_k`` (build the blades, reverse, multiply), so -- unlike
    :func:`make_orthogonal_frame`'s recursive rejection -- the ``c_k`` do not
    reference one another.  ``c_1 = reverse(A_0) A_1 = v_1`` (first vector unchanged).

    **Equivalence, kept side by side for teaching.** This produces the *same
    orthogonal directions* as :func:`make_orthogonal_frame`, scaled by a positive
    scalar per vector: ``c_k == |A_{k-1}|² * w_k`` where ``w_k`` is the rejection
    result and ``|A_{k-1}|² = A_{k-1}.magnitude_squared()`` (so ``c_1 == w_1``, and
    the later ``c_k`` are *longer*).  ``tests/test_frame.py`` verifies this exactly
    (symbolic) and numerically, in 2D and 3D.  Neither method is "better" -- rejection
    reads as the geometric idea, the blade product reads as a closed formula -- so both
    stay.

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent -- some
            ``A_k = 0``, making ``c_k`` degenerate).
    """
    if not is_frame(vectors):
        raise ValueError(
            "make_orthogonal_frame_hestenes requires a frame (linearly independent "
            "vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent"
        )

    # c_k := reverse(A_{k-1}) A_k (eq 3.2), pairing each prefix blade with the
    # one before it.  pairwise(prefix_blades(...)) yields the adjacent
    # (A_{k-1}, A_k) pairs -- (A_0, A_1), (A_1, A_2), … -- the single-pass-safe
    # form of zip(blades, blades[1:]), since prefix_blades is a lazy iterator.
    # c_1 needs no special case: A_0 = 1 and A_1 = 1 ∧ v_1 = v_1, so
    # c_1 = reverse(1) v_1 = v_1.  vectors is nonempty here (the is_frame guard
    # above rejects the empty set).  reverse(A_{k-1}) A_k is grade 1 algebraically;
    # narrow, as base.reject does, to drop any identically-zero widened term.
    return [
        (A_k_minus_1.reverse() * A_k).r_vector_part(1)
        for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))
    ]


def make_orthogonal_frame_hestenes_inverse(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """Orthogonalize a frame by the Hestenes closed form, using the **inverse** of each
    prefix blade instead of its reverse -- the variant that lands exactly on the
    rejection frame, with no extra per-vector scaling.

    Identical to :func:`make_orthogonal_frame_hestenes` except ``c_k`` uses
    ``inverse(A_{k-1})`` where that uses ``reverse(A_{k-1})``:

    ::

        c_k := inverse(A_{k-1}) * A_k

    For a blade ``inverse(A) = reverse(A) / |A|^2``, so this divides out the
    ``|A_{k-1}|^2`` factor that makes :func:`make_orthogonal_frame_hestenes`'s result a
    scaled copy of the rejection frame.  The result therefore equals
    :func:`make_orthogonal_frame`'s ``w_k`` **exactly** (same direction *and* length),
    not merely up to a positive scalar -- verified in ``tests/test_frame.py``.
    ``A_0 = 1`` and ``inverse(1) = 1``, so ``c_1 = v_1`` (the first vector
    unchanged), as in both siblings.

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent -- some
            ``A_k = 0``, whose inverse is undefined).
    """
    if not is_frame(vectors):
        raise ValueError(
            "make_orthogonal_frame_hestenes_inverse requires a frame (linearly "
            "independent vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent"
        )

    # c_k := inverse(A_{k-1}) A_k -- the reverse form divided by |A_{k-1}|^2, which
    # cancels the scaling and reproduces the rejection frame w_k exactly.  Same
    # pairwise(prefix_blades(...)) walk and grade-1 narrowing as the reverse variant.
    return [
        (A_k_minus_1.inverse() * A_k).r_vector_part(1)
        for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))
    ]


def kronecker_delta(k: int, j: int) -> int:
    """The Kronecker delta ``δ^k_j``: ``1`` when ``j = k`` and ``0`` when ``j ≠ k``.

    The notation of H&S p. 28, eq 3.5, where the reciprocal frame is defined by
    ``a^k · a_j = δ^k_j``: ``k`` is the upper index (the reciprocal vector), ``j``
    the lower (the frame vector).  The value is symmetric, ``δ^k_j = δ^j_k``.

    Examples:
        >>> kronecker_delta(2, 2)
        1
        >>> kronecker_delta(1, 2)
        0
        >>> kronecker_delta(3, 1) == kronecker_delta(1, 3) == 0  # symmetric
        True
        >>> [[kronecker_delta(k, j) for j in range(1, 4)] for k in range(1, 4)]
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    """
    return 1 if j == k else 0


def all_wedged_except_the_kth(
    vectors: Sequence[MultiVectorBase],
    k: int,
) -> MultiVectorBase:
    """The outer product of every vector but the ``k``-th, in order --
    ``a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n`` (H&S p. 28, eq 3.7), where ``ǎ_k`` means "leave ``a_k``
    out".

    ``k`` counts from 1, as the book does.  For a frame this is the face of the
    parallelotope opposite ``a_k``, the (n−1)-blade :func:`reciprocal_frame` turns into
    ``a^k``.  With a single vector, leaving it out gives the empty wedge, the scalar 1.

    Examples:
        >>> from gacalc.gn import e_1, e_2, e_3
        >>> frame = [1 * e_1, 1 * e_2, 1 * e_3]
        >>> all_wedged_except_the_kth(frame, 1) == e_2 ^ e_3
        True
        >>> all_wedged_except_the_kth(frame, 2) == e_1 ^ e_3
        True
        >>> all_wedged_except_the_kth(frame, 3) == e_1 ^ e_2
        True

    Raises:
        ValueError: if ``k`` is not between 1 and ``len(vectors)`` (there is no
            ``k``-th vector to leave out).
    """
    if not 1 <= k <= len(vectors):
        raise ValueError(
            f"all_wedged_except_the_kth needs 1 <= k <= {len(vectors)} (the number of "
            f"vectors); got k = {k}"
        )
    others: list[MultiVectorBase] = [*vectors[: k - 1], *vectors[k:]]
    return functools.reduce(operator.xor, others, _scalar_one(vectors[0]))


# Why x_i = a^i · y reads off a coordinate (similar right triangles standing on the
# face opposite a_i): tasks/reference/frames-qr-and-reciprocal-frames.md, "Why one
# dot product reads off an oblique coordinate: similar right triangles".
def reciprocal_frame(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """The **reciprocal frame** ``a^1 … a^n`` of the frame ``a_1 … a_n`` (H&S p. 28).

    The reciprocal vectors are defined by the property (eq 3.5)

    ::

        a^k · a_j = δ^k_j

    the Kronecker delta (:func:`kronecker_delta`): ``1`` when ``j = k`` and ``0`` when
    ``j ≠ k``.  Each ``a^k``
    is perpendicular to every frame vector except ``a_k``, and its projection on
    ``a_k`` is 1.  So the coordinates of a vector ``y`` in the frame are dot products,
    ``y = Σ_k (a^k · y) * a_k``, with no system to solve.  (The upper index names the
    reciprocal; it is not an exponent.)

    Hestenes and Sobczyk build them from the frame's pseudoscalar, eqs 3.6 and 3.7:

    ::

        A_n := a_1 ∧ a_2 ∧ … ∧ a_n                              (eq 3.6)
        a^k := (-1)^(k-1) * (a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n) * A_n⁻¹        (eq 3.7)

    where ``ǎ_k`` means "leave ``a_k`` out" and the product with ``A_n⁻¹`` is the
    geometric product.  The wedge of the others is the face of the parallelotope
    opposite ``a_k``; multiplying it by ``A_n⁻¹`` gives the vector perpendicular to
    that face with length face / volume = 1 / (the height of ``a_k`` above the face);
    ``(-1)^(k-1)`` makes ``a^k · a_k`` come out ``+1``.  Because the face lies inside
    the space of ``A_n``, the product is a pure vector (``tests/test_frame.py`` checks
    that it has no other grade).

    The face is :func:`all_wedged_except_the_kth`.  The result is a list, like the
    frame: ``result[k - 1]`` is ``a^k``.  For ``k``
    vectors in a larger space it is the reciprocal frame within their span.

    Machine-checked for ``n = 2`` and ``3`` in
    ``proofs/GacalcProofs/ReciprocalFrame2D.lean`` / ``ReciprocalFrame3D.lean``: each
    ``a^k`` is a vector (``isVector_recip*``), ``a^k · a_j`` is the Kronecker delta
    (``dot_recip_kronecker``), ``y = Σ (a^k · y) * a_k`` (``reconstruct``), and
    ``a^i = m / (m · a_i)`` for any ``m`` perpendicular to the other frame vectors
    (``recip*_eq_normal_div``).

    Examples:
        The oblique frame ``a_1 = 2 * e_1``, ``a_2 = 1 * e_1 + 3 * e_2``:

        >>> import sympy
        >>> from gacalc.gn import e_1, e_2
        >>> frame = [2 * e_1, 1 * e_1 + 3 * e_2]
        >>> reciprocal = reciprocal_frame(frame)
        >>> reciprocal == [sympy.Rational(1, 2) * e_1 - sympy.Rational(1, 6) * e_2,
        ...                sympy.Rational(1, 3) * e_2]
        True
        >>> [[a_upper.dot(a).scalar_part() for a in frame] for a_upper in reciprocal]
        [[1, 0], [0, 1]]

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent, empty, or
            containing a non-vector), so that ``A_n = 0`` has no inverse.
    """
    if not is_frame(vectors):
        raise ValueError(
            "reciprocal_frame requires a frame (linearly independent vectors: "
            "a_1 ∧ … ∧ a_n ≠ 0); the given vectors are dependent"
        )
    # A_n⁻¹, the inverse of the wedge of every frame vector (eq 3.6).
    A_n_inverse: MultiVectorBase = functools.reduce(
        operator.xor, vectors, _scalar_one(vectors[0])
    ).inverse()
    # eq 3.7: enumerate(start=1) makes the loop variable the book's k, so the sign is
    # literally (-1)^(k-1).
    return [
        (-1) ** (k - 1) * all_wedged_except_the_kth(vectors, k) * A_n_inverse
        for k, _ in enumerate(vectors, start=1)
    ]


def _has_float(vectors: Sequence[MultiVectorBase]) -> bool:
    """True if any coefficient of ``vectors`` is a ``float``: the "on the line" checks
    then need :func:`~gacalc.transforms.coordinate_along`'s tolerance."""
    return any(isinstance(coefficient, float) for v in vectors for coefficient in v)


@dataclasses.dataclass(frozen=True)
class Frame:
    """A frame ``v_1 … v_k`` (H&S p. 27), held together with its **orthogonal** set.

    The constructor takes the frame's vectors and keeps two things:

    - ``vectors`` -- the original ``v_1 … v_k``, as a tuple.  Iterating a ``Frame``
      (``iter(frame)``, ``list(frame)``) yields them.
    - ``orthogonal_vectors`` -- ``w_1 … w_k``, the frame orthogonalized by rejection
      (:func:`make_orthogonal_frame`): each ``w_i`` is ``v_i`` with the span of the
      earlier vectors rejected out of it.

    :meth:`coefficients` gives the table that rebuilds each ``v_i`` from the
    ``w_j``, ``coefficients()[i][j] = (w_j · v_i) / |w_j|²`` with
    ``v_i = Σ_j coefficients()[i][j] * w_j``.  It is zero above its diagonal and one
    on it: ``v_i`` needs only ``w_1 … w_i``, and its component along its own ``w_i``
    is exactly ``w_i``.

    This is the **QR decomposition** of the matrix whose columns are the ``v_i``,
    with the lengths factored out of ``Q``: the orthonormal ``u_j = w_j / |w_j|``
    are ``Q``'s columns (:meth:`orthonormal_vectors`), and ``R``'s entries are
    ``coefficients()[i][j] * |w_j|``.  The orthogonal set is kept rather than the
    orthonormal one because normalizing introduces a square root of every
    ``|w_j|²``; dividing by ``|w_j|²`` instead keeps every value a rational function
    of the inputs, which sympy can verify exactly in 3D (see
    ``tasks/reference/frames-qr-and-reciprocal-frames.md``, "Why gacalc's ``Frame``
    is stored orthogonal, not orthonormal").  Float input is subject to the usual
    Gram–Schmidt rounding.

    Examples:
        >>> from gacalc.gn import e_1, e_2
        >>> frame = Frame([2 * e_1, 1 * e_1 + 3 * e_2])
        >>> frame.orthogonal_vectors == (2 * e_1, 3 * e_2)
        True
        >>> frame.coefficients()
        ((1, 0), (1/2, 1))
        >>> list(frame) == [2 * e_1, 1 * e_1 + 3 * e_2]
        True

    Raises:
        ValueError: if the vectors are not a frame (linearly dependent, empty, or
            containing a non-vector).
    """

    vectors: Sequence[MultiVectorBase]
    orthogonal_vectors: tuple[MultiVectorBase, ...] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        # make_orthogonal_frame raises ValueError on a non-frame.
        orthogonal_vectors: tuple[MultiVectorBase, ...] = tuple(
            make_orthogonal_frame(self.vectors)
        )
        # A frozen dataclass sets its fields through object.__setattr__; the
        # vectors are stored as a tuple whatever sequence was passed.
        object.__setattr__(self, "vectors", tuple(self.vectors))
        object.__setattr__(self, "orthogonal_vectors", orthogonal_vectors)

    def __iter__(self) -> Iterator[MultiVectorBase]:
        """The original frame vectors ``v_1 … v_k``.

        Yields:
            MultiVectorBase: each ``v_i``, in the order the frame was given.
        """
        return iter(self.vectors)

    def __len__(self) -> int:
        """The number of vectors ``k`` in the frame."""
        return len(self.vectors)

    def coefficients(self) -> tuple[tuple[Real, ...], ...]:
        """The table rebuilding each ``v_i`` from the orthogonal set -- ``R`` of QR,
        with the lengths factored out.

        ``coefficients()[i][j]`` is how many copies of ``w_j`` the projection of
        ``v_i`` onto ``w_j`` is (in coordinates ``(w_j · v_i) / |w_j|²``), so that
        ``v_i = Σ_j coefficients()[i][j] * w_j``.  Zero above the diagonal, one on it.

        Returns:
            tuple[tuple[Real, ...], ...]: one row per original vector, one entry per
            orthogonal vector.
        """
        return tuple(
            tuple(
                coordinate_along(
                    v.projected_onto(w),
                    along=w,
                    float_close_to_zero=_has_float((v, w)),
                )
                for w in self.orthogonal_vectors
            )
            for v in self.vectors
        )

    def orthonormal_vectors(self) -> tuple[MultiVectorBase, ...]:
        """The orthonormal set ``u_j = w_j / |w_j|`` -- the columns of ``Q`` in QR.

        Computed on demand (it introduces square roots); the frame itself stores the
        orthogonal ``w_j``.

        Returns:
            tuple[MultiVectorBase, ...]: ``u_1 … u_k``, unit length and mutually
            orthogonal.
        """
        return tuple(w.normalize() for w in self.orthogonal_vectors)

    def reciprocal_vectors(self) -> tuple[MultiVectorBase, ...]:
        """The reciprocal frame ``v¹ … vᵏ`` (H&S p. 28): ``vⁱ · v_j = δⁱ_j``.

        Computed on demand by :func:`reciprocal_frame`.

        Returns:
            tuple[MultiVectorBase, ...]: ``v¹ … vᵏ``, in frame order.
        """
        return tuple(reciprocal_frame(self.vectors))

    def to_invertible_function(
        self,
        *,
        inverse_method: Literal["reciprocal", "peel"] = "reciprocal",
    ) -> InvertibleFunction[MultiVectorBase]:
        """The linear map sending each standard basis vector ``e_i`` to ``v_i``.

        Forward: project the input onto ``e_1 … e_k`` and use the components as
        weights on the frame vectors, ``f(x) = Σ_i (x · e_i) * v_i``.

        Inverse: given ``y = f(x) = Σ_i x_i * v_i``, recover the coordinates
        ``x_1 … x_k``.  ``inverse_method`` chooses how; both give the same
        coordinates (the solution is unique for a frame), which
        ``tests/test_frame_class.py`` checks symbolically.

        Both read a coordinate the same way.  If a vector ``n`` is perpendicular to
        every frame vector except ``v_i``, projecting ``y`` onto ``n`` sees only the
        ``x_i * v_i`` term: ``P_n(y) = x_i * P_n(v_i)``.  The point on ``v_i``'s line
        whose projection onto ``n`` is ``P_n(y)`` is therefore ``x_i * v_i``; that is
        the inverse of :func:`~gacalc.transforms.line_to_line_projection` from
        ``v_i`` to ``n``, and :func:`~gacalc.transforms.coordinate_along` reads
        ``x_i`` off it.  (In coordinates ``x_i = (n · y) / (n · v_i)``: two heights,
        one divided by the other.)  The methods differ in which ``n`` they use.

        ``inverse_method="reciprocal"`` (the default) uses the **reciprocal frame**
        ``v¹ … vᵏ`` (:meth:`reciprocal_vectors`, H&S p. 28): ``vⁱ`` is perpendicular
        to every ``v_j`` with ``j ≠ i`` (eq 3.5), so ``n = vⁱ`` reads ``x_i``
        directly, and the coordinates are independent of one another.  The
        reciprocal vectors are computed once, when the map is built.

        ``inverse_method="peel"`` **peels the frame from its last vector**, using the
        stored orthogonal set.  Each step:

        1. **Read the last coordinate.**  ``w_k`` is ``v_k`` with the span of
           ``v_1 … v_{k-1}`` rejected out of it, so it is perpendicular to every
           earlier frame vector: ``n = w_k`` gives the last term, ``x_k * v_k``.
        2. **Remove it.**  ``y - x_k * v_k`` equals ``Σ_{i < k} x_i * v_i``: a vector
           in the span of the first ``k - 1`` frame vectors.
        3. **Repeat on the smaller frame.**  That remainder is the same problem for
           ``v_1 … v_{k-1}``, whose last orthogonal vector ``w_{k-1}`` is again
           perpendicular to every vector before it, so step 1 applies to it.  The
           recursion stops when no vectors remain.

        Worked example, the frame ``v_1 = 2 * e_1``, ``v_2 = 1 * e_1 + 3 * e_2``
        (orthogonal set ``w_1 = 2 * e_1``, ``w_2 = 3 * e_2``) and
        ``y = 3 * e_1 + 3 * e_2``: ``P_{w_2}(y) = 3 * e_2``, and the point on
        ``v_2``'s line with that projection is ``1 * v_2``, so ``x_2 = 1``; the
        remainder is ``y - 1 * v_2 = 2 * e_1``, which is ``1 * v_1``, so ``x_1 = 1``.
        The reciprocal frame ``v¹ = 1/2 * e_1 - 1/6 * e_2``, ``v² = 1/3 * e_2`` gives
        the same ``x = 1 * e_1 + 1 * e_2``.

        The peel's order is forced: with the frame orthogonalized first-to-last, only
        the last orthogonal vector is perpendicular to *all* the others, so the first
        coordinate that can be read off directly is the last one.  This is
        back-substitution (``x = R⁻¹ * Qᵀ * y`` in QR terms), read geometrically, with
        no row reduction and no coefficient table; see
        ``tasks/reference/frames-qr-and-reciprocal-frames.md``, "The peel inverse, step
        by step".

        Machine-checked for ``n = 2`` and ``3``
        (``proofs/GacalcProofs/ReciprocalFrame2D.lean`` / ``ReciprocalFrame3D.lean``):
        both inverses undo the forward map on both sides (``invReciprocal_frameMap``,
        ``frameMap_invReciprocal``, ``invPeel_frameMap``, ``frameMap_invPeel``) and
        agree (``invReciprocal_eq_invPeel``); the peel's last reciprocal vector is the
        last rejection over its squared length (``recip2_eq_reject_div`` /
        ``recip3_eq_reject_div``).

        The frame must span the whole space (``k = n``), or the forward map would
        discard the components along ``e_{k+1} …`` and could not be inverted.  ``n``
        is the class's ``DIMENSION`` for the specialized types; ``Gn`` has no fixed
        dimension, so there ``n`` is the highest basis index the frame vectors use.

        Args:
            inverse_method: how the inverse recovers the coordinates:
                ``"reciprocal"`` (default; read through each ``vⁱ``) or ``"peel"``
                (back-substitution from the last frame vector).  Keyword-only.

        Returns:
            InvertibleFunction[MultiVectorBase]: the map ``e_i ↦ v_i`` and its
            inverse, tagged ``LINEAR``.

        Every dot product here is between two vectors (the frame's own, or the
        argument, which both directions check), so ``a.dot(b).scalar_part()`` is the
        familiar dot product read out as a number.

        Raises:
            ValueError: if ``k ≠ n`` (the frame does not span the space), or
                ``inverse_method`` is not one of the two names.  The returned map and
                its inverse raise ``ValueError`` when called on a non-vector: they are
                defined on vectors only.

        Examples:
            >>> from gacalc.gn import e_1, e_2
            >>> f = Frame([2 * e_1, 1 * e_1 + 3 * e_2]).to_invertible_function()
            >>> f(1 * e_1 + 1 * e_2) == 3 * e_1 + 3 * e_2
            True
            >>> f.inverse(3 * e_1 + 3 * e_2) == 1 * e_1 + 1 * e_2
            True
            >>> g = Frame([2 * e_1, 1 * e_1 + 3 * e_2]).to_invertible_function(
            ...     inverse_method="peel"
            ... )
            >>> g.inverse(3 * e_1 + 3 * e_2) == 1 * e_1 + 1 * e_2
            True
        """
        # n is the dimension of the space.  type(self.vectors[0]) is the frame's
        # representation: a specialized type fixes n as its DIMENSION; Gn has none, so
        # the getattr default gives the smallest dimension holding every frame vector.
        n: int = getattr(
            type(self.vectors[0]),
            "DIMENSION",
            max(v.implied_minimal_number_of_dimensions() for v in self.vectors),
        )
        if len(self.vectors) != n:
            raise ValueError(
                f"to_invertible_function needs a frame that spans the space (k = n); "
                f"got k = {len(self.vectors)} vectors in n = {n} dimensions"
            )

        def forward(x: MultiVectorBase) -> MultiVectorBase:
            MultiVectorBase.require_vector(x, "a frame's map")
            cls: type[MultiVectorBase] = type(x)
            # basis_vector numbers the basis from 1, hence enumerate(start=1).
            return sum(
                (
                    x.coefficient(cls.basis_vector(i)) * v
                    for i, v in enumerate(self.vectors, start=1)
                ),
                start=cls.zero(),
            )

        # Why one dot product per coordinate is enough (similar right triangles):
        # tasks/reference/frames-qr-and-reciprocal-frames.md, "Why one dot product
        # reads off an oblique coordinate: similar right triangles".
        def term_and_coordinate(
            y: MultiVectorBase, v: MultiVectorBase, m: MultiVectorBase
        ) -> tuple[MultiVectorBase, Real]:
            # y's term along v, x * v, and its coordinate x, for an m perpendicular to
            # every frame vector but v: the point on v's line whose projection onto m
            # matches y's.  Float input checks "on the line" with a tolerance.
            tolerant: bool = _has_float((y, v, m))
            term: MultiVectorBase = line_to_line_projection(
                from_vector=v, to_vector=m, float_close_to_zero=tolerant
            ).inverse(y.projected_onto(m))
            return term, coordinate_along(term, along=v, float_close_to_zero=tolerant)

        def backward_by_reciprocal(y: MultiVectorBase) -> MultiVectorBase:
            MultiVectorBase.require_vector(y, "a frame's map")
            cls: type[MultiVectorBase] = type(y)
            # Read x_i through vⁱ.  reciprocal_vectors is bound in the match below,
            # which runs before this can be called.  basis_vector numbers the basis
            # from 1, hence enumerate(start=1).
            return sum(
                (
                    term_and_coordinate(y, v=v, m=v_upper)[1] * cls.basis_vector(i)
                    for i, (v, v_upper) in enumerate(
                        zip(self.vectors, reciprocal_vectors, strict=True), start=1
                    )
                ),
                start=cls.zero(),
            )

        def backward_by_peel(y: MultiVectorBase) -> MultiVectorBase:
            def peel(
                remaining: Sequence[tuple[MultiVectorBase, MultiVectorBase]],
                y: MultiVectorBase,
            ) -> list[Real]:
                match remaining:
                    case []:
                        # No vectors left: nothing to solve.
                        return []
                    case [*earlier, (w, v)]:
                        # One or more vectors.  w is perpendicular to every vector in
                        # earlier, so it reads this vector's term of y.  Subtracting
                        # the term leaves a y built from the earlier vectors alone;
                        # solve those coordinates the same way, and put this one
                        # after them.
                        term: MultiVectorBase
                        x_last: Real
                        term, x_last = term_and_coordinate(y, v=v, m=w)
                        return [*peel(earlier, y - term), x_last]
                    case _:
                        # Unreachable: [] and [*earlier, last] cover every list.  Kept
                        # as the total default because ty does not prove list-pattern
                        # exhaustiveness, so the match needs an explicit catch-all.
                        return []

            MultiVectorBase.require_vector(y, "a frame's map")
            cls: type[MultiVectorBase] = type(y)
            # basis_vector numbers the basis from 1, hence enumerate(start=1).  The
            # tuple(zip(...)) argument to peel is the pairs: each orthogonal vector
            # with the frame vector it came from, (w_i, v_i), in frame order; peel
            # consumes them from the end.
            return sum(
                (
                    x_i * cls.basis_vector(i)
                    for i, x_i in enumerate(
                        peel(
                            tuple(
                                zip(self.orthogonal_vectors, self.vectors, strict=True)
                            ),
                            y,
                        ),
                        start=1,
                    )
                ),
                start=cls.zero(),
            )

        backward: Callable[[MultiVectorBase], MultiVectorBase]
        match inverse_method:
            case "reciprocal":
                # Built once, here, so each call to the inverse is k dot products.
                reciprocal_vectors: tuple[MultiVectorBase, ...] = (
                    self.reciprocal_vectors()
                )
                backward = backward_by_reciprocal
            case "peel":
                backward = backward_by_peel
            case _:
                raise ValueError(
                    "inverse_method must be 'reciprocal' or 'peel'; "
                    f"got {inverse_method!r}"
                )

        return InvertibleFunction(
            func=forward,
            latex_repr="F",
            inverse=backward,
            latex_repr_inv="F^{-1}",
            linearity=Linearity.LINEAR,
        )
