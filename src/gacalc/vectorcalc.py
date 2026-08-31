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

r"""Vector calculus in 𝒢₃ -- the familiar calc-3 operations, each a thin name
over geometric-algebra machinery that already computes it:

- :func:`cross` -- the cross product, the **dual of the wedge**:
  ``a × b = (a ∧ b) I₃⁻¹``.
- the **dot product** needs no alias here: it is
  :meth:`gacalc.base.MultiVectorBase.scalar_product` (``a · b = ⟨a b⟩``).
- the **scalar triple product** ``a · (b × c)`` needs no alias either: it is
  :func:`gacalc.measure.signed_volume` -- the 3-D determinant.  The identity is
  gated by ``tests/test_vectorcalc.py``.
- **grad / div / curl** are deliberately absent: they need multivector *fields*
  and a derivative operator (see ``tasks/custom-symbols-and-vector-calc.md``).
"""

from __future__ import annotations

from gacalc.base import MultiVectorBase
from gacalc.measure import _max_basis_index


def cross(a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase:
    r"""The cross product  a × b  =  (a ∧ b) I₃⁻¹  -- the dual of the wedge.

    The wedge ``a ∧ b`` is the oriented parallelogram on ``a`` and ``b``; its
    dual (multiplication by the inverse unit pseudoscalar, :meth:`dual
    <gacalc.base.MultiVectorBase.dual>`) is the **vector** perpendicular to that
    plane, with magnitude ``|a||b| sin θ`` -- the right-hand-rule cross product
    (sign pinned by ``tests/test_vectorcalc.py``):

    >>> from gacalc.g3 import e_1, e_2, e_3
    >>> cross(1 * e_1, 1 * e_2) == 1 * e_3
    True
    >>> cross(1 * e_2, 1 * e_1) == -1 * e_3      # anticommutative
    True
    >>> cross(2 * e_1, 3 * e_1).magnitude()      # parallel -> zero vector
    0

    General symbolic vectors show it *is* the coordinate formula:

    >>> import sympy
    >>> a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    >>> b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
    >>> a = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    >>> b = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    >>> cross(a, b) == (
    ...     (a_2 * b_3 - a_3 * b_2) * e_1
    ...     + (a_3 * b_1 - a_1 * b_3) * e_2
    ...     + (a_1 * b_2 - a_2 * b_1) * e_3
    ... )
    True

    The cross product only exists in 3 dimensions (in general the wedge -- a
    bivector -- is the honest product; only in 𝒢₃ does its dual land on a
    vector), so the ambient dimension must be 3: a fixed-dimension
    representation must be ``g3``'s, and ``Gn`` vectors must use basis indices
    ≤ 3.  Method form: ``a.cross(b)``.

    Raises:
        ValueError: on a non-vector (grade != 1) operand, a fixed-dimension
            representation other than 3-D, or a ``Gn`` vector with a basis
            index above 3.
    """
    for operand in (a, b):
        if not operand.is_vector():
            raise ValueError(
                "cross takes vectors (grade 1); got a non-vector: " + repr(operand)
            )
    wedge: MultiVectorBase = a.wedge(b)
    # Mirror measure.signed_content's dimension logic: a fixed-dimension type
    # declares DIMENSION (and its dual is locked to it -- any other n raises),
    # while the dimension-agnostic Gn is judged by the basis indices it uses.
    dimension: int | None = getattr(type(wedge), "DIMENSION", None)
    if dimension is not None and dimension != 3:
        raise ValueError(
            "the cross product is 3-dimensional; got a "
            f"{dimension}-dimensional representation (use g3, or Gn)"
        )
    if dimension is None and _max_basis_index([a, b]) > 3:
        raise ValueError(
            "the cross product is 3-dimensional; got a vector with a basis "
            f"index above 3 (largest: {_max_basis_index([a, b])})"
        )
    return wedge.dual(3)
