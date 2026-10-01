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

"""Fixed-grade (bound-grade) reading of the dot and wedge products of vectors.

Hestenes defines the inner/outer products as graded PARTS of the geometric
product: ``a·b = ⟨ab⟩_|r−s|`` and ``a∧b = ⟨ab⟩_(r+s)`` (H&S p. 6, eqs. 1.21/1.22).
For two VECTORS (grade 1) the selected grade is a fixed literal — dot is the
grade-0 (scalar) part ``⟨ab⟩_0``, wedge is the grade-2 (bivector) part ``⟨ab⟩_2``.
These tests pin that this *bound-grade* reading (``(a*b).r_vector_part(0)`` /
``.r_vector_part(2)``) equals the canonical ``inner_product`` / ``outer_product``
(which pick the grade dynamically from each homogeneous pair).  This is the
middle "fixed-grade" rung of the levels-of-abstraction theme — coordinate →
fixed-grade → coordinate-free — proved equal.  See
``tasks/archive/2026/10/01/per-type-fixed-grade-dot-wedge-sine-cosine.md``.
"""

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.gn import (
    MultiVector,
    a_1,
    a_2,
    a_3,
    b_1,
    b_2,
    b_3,
    e_1,
    e_2,
    e_3,
)

# The bound grades for a grade-1 × grade-1 product: dot picks |1−1| = 0, wedge 1+1 = 2.
_DOT_GRADE: int = 0
_WEDGE_GRADE: int = 2


def test_fixed_grade_equals_canonical_2d_symbolic() -> None:
    a: MultiVector = a_1 * e_1 + a_2 * e_2
    b: MultiVector = b_1 * e_1 + b_2 * e_2
    product: MultiVector = a * b
    assert product.r_vector_part(_DOT_GRADE) == a.inner_product(b)
    assert product.r_vector_part(_WEDGE_GRADE) == a.outer_product(b)


def test_fixed_grade_equals_canonical_3d_symbolic() -> None:
    a: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    product: MultiVector = a * b
    assert product.r_vector_part(_DOT_GRADE) == a.inner_product(b)
    assert product.r_vector_part(_WEDGE_GRADE) == a.outer_product(b)


def test_product_is_dot_plus_wedge_2d_symbolic() -> None:
    # The two bound-grade parts reassemble the whole product: ab = a·b + a∧b.
    a: MultiVector = a_1 * e_1 + a_2 * e_2
    b: MultiVector = b_1 * e_1 + b_2 * e_2
    product: MultiVector = a * b
    assert product == product.r_vector_part(_DOT_GRADE) + product.r_vector_part(
        _WEDGE_GRADE
    )


def test_fixed_grade_equals_canonical_g2_generated() -> None:
    # Same identity on the fast generated 𝒢₂ classes (numeric).
    a: g2.Vector = 3.0 * g2.e_1 + 4.0 * g2.e_2
    b: g2.Vector = 1.0 * g2.e_1 + 2.0 * g2.e_2
    product: MultiVectorBase = a * b
    assert product.r_vector_part(_DOT_GRADE) == a.inner_product(b)
    assert product.r_vector_part(_WEDGE_GRADE) == a.outer_product(b)


def test_fixed_grade_equals_canonical_g3_generated() -> None:
    a: g3.Vector = 1.0 * g3.e_1 + 2.0 * g3.e_2 + 3.0 * g3.e_3
    b: g3.Vector = 4.0 * g3.e_1 + 5.0 * g3.e_2 + 6.0 * g3.e_3
    product: MultiVectorBase = a * b
    assert product.r_vector_part(_DOT_GRADE) == a.inner_product(b)
    assert product.r_vector_part(_WEDGE_GRADE) == a.outer_product(b)
