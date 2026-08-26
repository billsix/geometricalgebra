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

"""Named measures -- ``area``, ``volume``, and the general ``content``.

The high-school-legible measure of the parallelotope a set of vectors spans:
length -> area -> volume -> **content** (the k-dimensional generalization). From
**Williamson & Trotter, Multivariable Mathematics, 2nd ed., 1979**: "content" is
defined on **p. 308**; the recursive height construction on **p. 146**; the
parallelogram area (``|a||b| sin θ``) on **pp. 144-145**. See
``tasks/reference/content-area-volume.md`` for the source notes and the connection
to frames.

``content`` is the **unsigned scalar magnitude** of the wedge, computable two equal
ways -- both kept for teaching (:func:`content` and :func:`content_by_rejection`):

    content([a_1, …, a_k]) = |a_1 ∧ … ∧ a_k|   (magnitude of the wedge blade)
                           = ∏_j |h_j|           (product of rejected heights, p. 146)

The **signed** (oriented) content -- the determinant -- is available as
:func:`signed_content` / :func:`signed_area` / :func:`signed_volume`, but only when
the vectors span the full space (``k = n``); for ``k < n`` there is no scalar sign
(see those docstrings).

These are representation-agnostic free functions over
:class:`~gacalc.base.MultiVectorBase` vectors, like the frame functions.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from gacalc.base import Coef, MultiVectorBase
from gacalc.frame import make_orthogonal_frame


def _require_vectors(vectors: Sequence[MultiVectorBase]) -> None:
    """Raise unless ``vectors`` is a non-empty sequence of grade-1 vectors."""
    if len(vectors) == 0:
        raise ValueError("area/volume/content need at least one vector")
    for v in vectors:
        if not v.is_vector():
            raise ValueError(
                "area/volume/content take vectors (grade 1); got a non-vector: "
                + repr(v)
            )


def _max_basis_index(vectors: Sequence[MultiVectorBase]) -> int:
    """The largest basis-vector index appearing in ``vectors`` (``0`` if all zero).

    For the dimension-agnostic ``Gn`` this is the dimension of the smallest coordinate
    space containing the vectors -- the ``n`` a signed (oriented) ``n``-volume lives in.
    """
    return max(
        (
            index
            for vector in vectors
            for blade in vector.to_blade_dict()
            for index in blade
        ),
        default=0,
    )


def content(vectors: Sequence[MultiVectorBase]) -> Coef:
    """The k-dimensional **content** of the parallelotope on ``vectors`` -- the
    high-school length/area/volume generalized (Williamson & Trotter p. 308).

    Computed as ``|a_1 ∧ … ∧ a_k|``, the magnitude of the wedge (``= √det(Gram)``);
    an **unsigned scalar**.  ``content([a]) == |a|`` (length), ``content([a, b])`` is
    an area, ``content([a, b, c])`` a volume.  A linearly **dependent** set spans a
    degenerate parallelotope, so its content is ``0`` (the wedge vanishes) -- unlike
    :func:`content_by_rejection`, which is defined only on a frame.

    :func:`content_by_rejection` computes the *same* value W&T's way (product of
    rejected heights); the two are kept side by side for teaching and their
    equivalence is proved in ``tests/test_measure.py``.

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> content([1 * e_1, 1 * e_2])          # the unit square
        1
        >>> content([1 * e_1, 1 * e_1 + 1 * e_2])    # sheared: same base and height
        1
        >>> content([1 * e_1, 2 * e_1])      # dependent -> flat
        0

        General symbolic vectors show the formula — the magnitude of the determinant:

        >>> import sympy
        >>> a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
        >>> content([a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2])
        sqrt((a_1*b_2 - a_2*b_1)**2)

    Raises:
        ValueError: on an empty sequence, or any non-vector (grade != 1) member.
    """
    _require_vectors(vectors)
    return MultiVectorBase.outer_product_of_vectors(*vectors).magnitude()


def content_by_rejection(vectors: Sequence[MultiVectorBase]) -> Coef:
    """The content computed **Hestenes/Williamson-Trotter's way** -- the product of
    rejected heights, ``∏_j |h_j|`` (W&T p. 146), the sibling of :func:`content`.

    Each height ``h_j`` is ``v_j`` rejected from the span of the ones before it, i.e.
    the orthogonalized ``w_j`` from :func:`~gacalc.frame.make_orthogonal_frame`; so
    this returns ``∏_j |w_j|``.  On a **frame** this equals :func:`content`
    (``∏|w_j| = |wedge| = √det(Gram)``) -- proved in ``tests/test_measure.py``, exactly
    (symbolic) and numerically, in 2D and 3D.  Kept alongside :func:`content` for
    teaching (contrast the blade-square-sign task, which optimized to one form).

    Defined only on a **frame** -- a dependent set has a zero height and no full
    parallelotope, so this raises there; use :func:`content` (which returns ``0``) for
    the degenerate case.

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> vectors = [1 * e_1, 1 * e_1 + 1 * e_2]
        >>> content_by_rejection(vectors) == content(vectors)
        True

    Raises:
        ValueError: on an empty sequence, a non-vector member, or a linearly
            dependent set (not a frame -- via
            :func:`~gacalc.frame.make_orthogonal_frame`).
    """
    _require_vectors(vectors)
    return math.prod(
        (
            perpendicular_vector.magnitude()
            for perpendicular_vector in make_orthogonal_frame(vectors)
        ),
        start=1,
    )


def area(a: MultiVectorBase, b: MultiVectorBase) -> Coef:
    """The area of the parallelogram on ``a`` and ``b`` -- ``content([a, b])``
    (Williamson & Trotter pp. 144-145; ``= |a||b| sin θ = |a ∧ b|``).

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> area(3 * e_1, 2 * e_2)
        6
        >>> area(3 * e_1, 2 * e_2) == area(2 * e_2, 3 * e_1)  # unsigned: order-free
        True

        General symbolic vectors show the formula — the magnitude of the determinant:

        >>> import sympy
        >>> a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
        >>> area(a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2)
        sqrt((a_1*b_2 - a_2*b_1)**2)
    """
    return content([a, b])


def volume(a: MultiVectorBase, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
    """The volume of the parallelepiped on ``a``, ``b``, ``c`` --
    ``content([a, b, c])`` (Williamson & Trotter p. 146).

    Examples:
        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> volume(2 * e_1, 1 * e_2, 3 * e_3)
        6
    """
    return content([a, b, c])


def signed_content(vectors: Sequence[MultiVectorBase]) -> Coef:
    """The **signed** (oriented) content -- the determinant -- of ``n`` vectors that
    span the full ``n``-dimensional space.

    The wedge of ``n`` spanning vectors is a multiple of the unit pseudoscalar,
    ``a_1 ∧ … ∧ a_n = c · I_n``; this returns that scalar ``c`` -- the **determinant**
    of the vectors' coordinates.  It carries the **orientation** (the sign flips when
    two vectors are swapped) and ``abs(signed_content) == content`` (the unsigned
    magnitude).  :func:`signed_area` / :func:`signed_volume` are the ``k = 2`` /
    ``k = 3`` aliases.

    Works for **any** representation, including the dimension-agnostic ``Gn``.  The
    ambient dimension ``n`` comes from:

    - a **fixed-dimension** type's own ``DIMENSION`` (``g2`` -> 2, ``g3`` -> 3); or
    - for ``Gn``, the **largest basis index** the vectors use -- the smallest coordinate
      space containing them.

    Signed content is a scalar only for **exactly ``n`` vectors** (``k = n``).  The
    implementation is the pseudoscalar **dual** of the wedge:
    ``dual(a_1 ∧ … ∧ a_k, n)`` is a *scalar* iff the wedge is top-grade, i.e. iff the
    vectors span the full space, so a scalar result *is* that proof.  A dependent set of
    the right count (``k = n`` but parallel/coplanar) wedges to ``0`` and returns ``0``
    -- a flat parallelotope, like :func:`content`.

    The **wrong count** has no scalar sign and raises: too few (``k < n`` -- e.g. the
    *area* of two vectors in 3-space, whose orientation is a bivector's attitude, not a
    ``±``) or too many (``k > n``, over-determined).  Use :func:`content` (unsigned)
    there.

    Examples:
        >>> import gacalc.gn as gn  # signed content works on the general Gn now
        >>> signed_content([1 * gn.e_1, 1 * gn.e_2])          # oriented unit square
        1
        >>> signed_content([1 * gn.e_2, 1 * gn.e_1])          # swap flips the sign
        -1

    Raises:
        ValueError: on an empty sequence or a non-vector member (via
            :func:`_require_vectors`), or when ``len(vectors) != n`` -- the wrong number
            of vectors to span the space (too few, or too many / over-determined).
    """
    _require_vectors(vectors)
    representation = type(vectors[0])
    dimension: int | None = getattr(representation, "DIMENSION", None)
    # A fixed type declares the ambient dimension (and its dual is locked to it); the
    # dimension-agnostic Gn takes the smallest space containing the vectors.
    n: int = dimension if dimension is not None else _max_basis_index(vectors)
    if len(vectors) != n:
        raise ValueError(
            "signed content is the oriented n-volume: it needs exactly n vectors "
            f"to span the n-dimensional space (k = n); got k = {len(vectors)}, "
            f"n = {n}. Use content() (unsigned) for k != n."
        )
    # k = n: the wedge is c·I_n (or 0 when the vectors are dependent), so its dual by
    # I_n is the scalar c -- the signed content.  A non-scalar dual would mean the
    # vectors don't span the full space; is_scalar() states that invariant (it holds
    # for k = n, and is correct on the zero/degenerate case, where max_grade() raises).
    wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
    oriented: MultiVectorBase = wedge.dual(n)
    if not oriented.is_scalar():
        raise ValueError(
            "signed content is a scalar only when the vectors span the full "
            f"space; got a grade-{oriented.max_grade()} orientation."
        )
    return oriented.scalar_part()


def signed_area(a: MultiVectorBase, b: MultiVectorBase) -> Coef:
    """The **signed** area of the parallelogram on ``a``, ``b`` --
    ``signed_content([a, b])``, the 2-D determinant ``a_1 b_2 - a_2 b_1`` (needs 2-D
    vectors; see :func:`signed_content`).

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> a = 2 * e_1 + 1 * e_2
        >>> b = 1 * e_1 + 3 * e_2
        >>> signed_area(a, b)      # determinant 2*3 - 1*1
        5
        >>> signed_area(b, a)      # swapping the two flips the orientation
        -5

        General symbolic vectors show it *is* the 2x2 determinant:

        >>> import sympy
        >>> a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
        >>> signed_area(a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2)
        a_1*b_2 - a_2*b_1
    """
    return signed_content([a, b])


def signed_volume(a: MultiVectorBase, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
    """The **signed** volume of the parallelepiped on ``a``, ``b``, ``c`` --
    ``signed_content([a, b, c])``, the 3-D determinant (needs 3-D vectors).

    Examples:
        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> signed_volume(1 * e_1, 1 * e_2, 1 * e_3)      # right-handed
        1
        >>> signed_volume(1 * e_3, 1 * e_2, 1 * e_1)      # left-handed after the swap
        -1

        General symbolic vectors show it *is* the 3x3 determinant (cofactor expansion):

        >>> import sympy
        >>> a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
        >>> b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
        >>> c_1, c_2, c_3 = sympy.symbols("c_1 c_2 c_3")
        >>> a = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
        >>> b = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
        >>> c = c_1 * e_1 + c_2 * e_2 + c_3 * e_3
        >>> signed_volume(a, b, c)
        c_1*(a_2*b_3 - a_3*b_2) - c_2*(a_1*b_3 - a_3*b_1) + c_3*(a_1*b_2 - a_2*b_1)
    """
    return signed_content([a, b, c])
