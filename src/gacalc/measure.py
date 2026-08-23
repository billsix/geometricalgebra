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
        >>> content([e_1, e_2])          # the unit square
        1
        >>> content([e_1, e_1 + e_2])    # sheared: same base and height
        1
        >>> content([e_1, 2 * e_1])      # dependent -> flat
        0

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
        >>> content_by_rejection([e_1, e_1 + e_2]) == content([e_1, e_1 + e_2])
        True

    Raises:
        ValueError: on an empty sequence, a non-vector member, or a linearly
            dependent set (not a frame -- via
            :func:`~gacalc.frame.make_orthogonal_frame`).
    """
    _require_vectors(vectors)
    result: Coef = 1
    for height in make_orthogonal_frame(vectors):
        result = result * height.magnitude()
    return result


def area(a: MultiVectorBase, b: MultiVectorBase) -> Coef:
    """The area of the parallelogram on ``a`` and ``b`` -- ``content([a, b])``
    (Williamson & Trotter pp. 144-145; ``= |a||b| sin θ = |a ∧ b|``).

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> area(3 * e_1, 2 * e_2)
        6
        >>> area(3 * e_1, 2 * e_2) == area(2 * e_2, 3 * e_1)  # unsigned: order-free
        True
    """
    return content([a, b])


def volume(a: MultiVectorBase, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
    """The volume of the parallelepiped on ``a``, ``b``, ``c`` --
    ``content([a, b, c])`` (Williamson & Trotter p. 146).

    Examples:
        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> volume(2 * e_1, e_2, 3 * e_3)
        6
    """
    return content([a, b, c])


def signed_content(vectors: Sequence[MultiVectorBase]) -> Coef:
    """The **signed** (oriented) content -- the determinant -- defined only when the
    vectors span the full space (``k = n``).

    When ``k = n`` the wedge is a multiple of the unit pseudoscalar,
    ``a_1 ∧ … ∧ a_n = (signed content) · I_n``; this returns that scalar.  It is the
    **determinant** of the vectors' coordinates, so it carries the **orientation** --
    the sign flips when two vectors are swapped -- and ``abs(signed_content) ==
    content`` (the unsigned magnitude).  :func:`signed_area` / :func:`signed_volume`
    are the k = 2 / k = 3 aliases.

    For ``k < n`` (e.g. the *area* of two vectors in 3-space) there is **no scalar
    sign** -- the orientation is the wedge bivector's attitude, not a ``±`` -- so this
    raises; use :func:`content` there.  Needs a fixed-dimension type (``g2``/``g3``);
    the general ``Gn`` has no ``DIMENSION`` (no notion of "full space"), so it raises
    too.  A dependent full set gives ``0`` (a flat parallelotope), like
    :func:`content`.

    Raises:
        ValueError: on an empty sequence, a non-vector member, a type with no fixed
            ``DIMENSION`` (e.g. ``Gn``), or when ``len(vectors) != DIMENSION``
            (``k < n``, where no scalar sign exists).
    """
    _require_vectors(vectors)
    representation = type(vectors[0])
    dimension: int | None = getattr(representation, "DIMENSION", None)
    if dimension is None:
        raise ValueError(
            "signed content needs a fixed-dimension type (e.g. g2/g3); the general Gn "
            "has no DIMENSION, so 'full space' -- and thus the sign -- is undefined"
        )
    if len(vectors) != dimension:
        raise ValueError(
            "signed content is only defined when the vectors span the full space "
            f"(k = n = {dimension}); got {len(vectors)}. Use content() (unsigned) for "
            "k < n, where the orientation is a blade, not a scalar sign."
        )
    # When k = n the wedge is a single top-grade blade c·I_n, and gacalc's unit
    # pseudoscalar is +e_(1,…,n); so c -- the signed content, relative to the standard
    # orientation -- is the coefficient of that blade (0 if the set is dependent).
    wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
    pseudoscalar_blade: tuple[int, ...] = tuple(range(1, dimension + 1))
    return wedge.to_blade_dict().get(pseudoscalar_blade, 0)


def signed_area(a: MultiVectorBase, b: MultiVectorBase) -> Coef:
    """The **signed** area of the parallelogram on ``a``, ``b`` --
    ``signed_content([a, b])``, the 2-D determinant ``a_1 b_2 - a_2 b_1`` (needs 2-D
    vectors; see :func:`signed_content`).

    Examples:
        >>> from gacalc.g2 import e_1, e_2
        >>> a = 2 * e_1 + e_2
        >>> b = e_1 + 3 * e_2
        >>> signed_area(a, b)      # determinant 2*3 - 1*1
        5
        >>> signed_area(b, a)      # swapping the two flips the orientation
        -5
    """
    return signed_content([a, b])


def signed_volume(a: MultiVectorBase, b: MultiVectorBase, c: MultiVectorBase) -> Coef:
    """The **signed** volume of the parallelepiped on ``a``, ``b``, ``c`` --
    ``signed_content([a, b, c])``, the 3-D determinant (needs 3-D vectors).

    Examples:
        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> signed_volume(e_1, e_2, e_3)      # right-handed
        1
        >>> signed_volume(e_3, e_2, e_1)      # left-handed after the swap
        -1
    """
    return signed_content([a, b, c])
