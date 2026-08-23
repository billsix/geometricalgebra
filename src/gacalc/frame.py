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

These are representation-agnostic **free functions** over
:class:`~gacalc.base.MultiVectorBase` vectors (they work on the general ``Gn`` type
and on the graded ``Vector_n`` types alike), so no ``Frame`` class is needed to use
them.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from gacalc.base import MultiVectorBase


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
    for v in vectors:
        if not v.is_vector():
            raise ValueError(
                "a frame is a set of vectors (grade 1); got a non-vector: " + repr(v)
            )
    blade: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
    if float_close_to_zero:
        return not bool(np.isclose(float(blade.magnitude()), 0.0, rtol=1e-5, atol=1e-5))
    return blade != type(blade).zero()


def is_frame(
    vectors: Sequence[MultiVectorBase],
    float_close_to_zero: bool = False,
) -> bool:
    """Whether ``vectors`` form a frame -- a linearly independent set (H&S p. 27).

    A pass-through to :func:`are_linearly_independent`: a frame *is* a linearly
    independent set of vectors.
    """
    return are_linearly_independent(vectors, float_close_to_zero)


def make_orthogonal_frame(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """Orthogonalize a frame by **rejection** (H&S p. 27) -- Gram–Schmidt done the
    geometric-algebra way.

    Keep the first vector as-is; each subsequent vector has the span of the ones
    before it rejected out, so the result spans the same subspace but is mutually
    orthogonal (``is_orthogonal_to`` between every pair).  The rejection is applied
    one prior vector at a time -- ``reject(… reject(v_{k+1}, w_1) …, w_k)`` -- which,
    because the ``w_j`` are already mutually orthogonal, equals rejecting the whole
    span; doing it pairwise only ever rejects from a single vector, so it stays
    within the grade-1/grade-2 rejections gacalc implements.

    The result is **orthogonal, not orthonormal** -- the original lengths are kept
    (the first vector is returned unchanged).  Normalizing each result would give an
    orthonormal frame; that is a separate operation.

    See also :func:`make_orthogonal_frame_hestenes` -- the *same* orthogonalization
    computed a different way (Hestenes' closed-form blade product), kept side by side
    for teaching. The two agree up to a positive scalar per vector
    (``c_k == |A_{k-1}|² · w_k``; proved by ``tests/test_frame.py``). Unlike the
    archived blade-square-sign task -- where one form was strictly optimal and replaced
    the other -- neither is "better" here, so both stay.

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent -- a later
            vector would reject to zero and the result could not be a frame).
    """
    if not is_frame(vectors):
        raise ValueError(
            "make_orthogonal_frame requires a frame (linearly independent "
            "vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent"
        )
    orthogonal: list[MultiVectorBase] = []
    for v in vectors:
        w: MultiVectorBase = v
        for prior in orthogonal:
            w = type(w).reject(away_from=prior)(w)
        orthogonal.append(w)
    return orthogonal


def make_orthogonal_frame_hestenes(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """Orthogonalize a frame the way Hestenes does it -- the **closed-form blade
    product** (H&S p. 27, eqs 3.1–3.2), the sibling of :func:`make_orthogonal_frame`.

    With the prefix blades ``A_0 := 1``, ``A_k := v_1 ∧ v_2 ∧ … ∧ v_k`` (eq 3.1),
    each orthogonal vector is

    ::

        c_k := reverse(A_{k-1}) · A_k                 (eq 3.2)

    a **closed form**: every ``c_k`` is built directly from the original prefix
    ``v_1 … v_k`` (build the blades, reverse, multiply), so -- unlike
    :func:`make_orthogonal_frame`'s recursive rejection -- the ``c_k`` do not
    reference one another.  ``c_1 = reverse(A_0) A_1 = v_1`` (first vector unchanged).

    **Equivalence, kept side by side for teaching.** This produces the *same
    orthogonal directions* as :func:`make_orthogonal_frame`, scaled by a positive
    scalar per vector: ``c_k == |A_{k-1}|² · w_k`` where ``w_k`` is the rejection
    result and ``|A_{k-1}|² = A_{k-1}.magnitude_squared()`` (so ``c_1 == w_1``, and
    the later ``c_k`` are *longer*).  ``tests/test_frame.py`` verifies this exactly
    (symbolic) and numerically, in 2D and 3D.  Neither method is "better" -- rejection
    reads as the geometric idea, the blade product reads as a closed formula -- so both
    stay (contrast the blade-square-sign task, which optimized to one form).

    Raises:
        ValueError: if ``vectors`` is not a frame (linearly dependent -- some
            ``A_k = 0``, making ``c_k`` degenerate).
    """
    if not is_frame(vectors):
        raise ValueError(
            "make_orthogonal_frame_hestenes requires a frame (linearly independent "
            "vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent"
        )
    orthogonal: list[MultiVectorBase] = []
    for k in range(1, len(vectors) + 1):
        if k == 1:
            orthogonal.append(vectors[0])  # c_1 = reverse(A_0=1) A_1 = v_1
            continue
        a_prev: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(
            *vectors[: k - 1]
        )
        a_k: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors[:k])
        # reverse(A_{k-1}) A_k is grade 1 algebraically; narrow, as base.reject does,
        # to drop any identically-zero widened term.
        orthogonal.append((a_prev.reverse() * a_k).r_vector_part(1))
    return orthogonal
