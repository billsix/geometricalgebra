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

"""Dot and wedge are the parallel/perpendicular faces of the geometric product.

For two vectors ``a`` and ``b``, split ``a`` into its projection onto ``b`` and
its rejection from ``b``:

    a_par  = proj_b(a)   (the part of a parallel to b)
    a_perp = rej_b(a)    (the part of a perpendicular to b)

Then the geometric product of each part with ``b`` isolates one term of the
geometric product ``a b = a·b + a∧b``:

    a_par  b = a·b       (the wedge term vanishes: a_par ∥ b)
    a_perp b = a∧b       (the dot term vanishes:   a_perp ⊥ b)

The symbolic tests are written **explicitly** -- general vectors spelled out as
``a = a_1 e_1 + a_2 e_2``, with the dot product and the wedge asserted against
their exact formulas (so each test reads like the math) -- plus a **numeric**
check over random vectors (float-tolerant ``isclose``).  See
``tasks/reference/dot-wedge-projection-rejection.md`` for the hand proof.
"""

import random
import typing

import pytest
import sympy
from _helpers import random_vector

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.gn import Gn, e_1, e_2, e_3


def test_geometric_product_splits_into_dot_and_wedge_2d() -> None:
    """``ab = a·b + a∧b`` for general 2D vectors -- both parts read off explicitly."""
    a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
    a: Gn = a_1 * e_1 + a_2 * e_2
    b: Gn = b_1 * e_1 + b_2 * e_2
    # the dot product is the symmetric scalar part:
    assert a.dot(b).scalar_part() == a_1 * b_1 + a_2 * b_2
    # the wedge is the antisymmetric bivector part:
    assert a.wedge(b) == (a_1 * b_2 - a_2 * b_1) * (e_1 ^ e_2)
    # together they are the whole geometric product:
    assert a * b == a.dot(b) + a.wedge(b)


def test_geometric_product_splits_into_dot_and_wedge_3d() -> None:
    """``ab = a·b + a∧b`` for general 3D vectors -- the wedge now has three
    bivector components, one per pair of axes."""
    a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")
    a: Gn = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: Gn = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    assert a.dot(b).scalar_part() == a_1 * b_1 + a_2 * b_2 + a_3 * b_3
    assert a.wedge(b) == (
        (a_1 * b_2 - a_2 * b_1) * (e_1 ^ e_2)
        + (a_1 * b_3 - a_3 * b_1) * (e_1 ^ e_3)
        + (a_2 * b_3 - a_3 * b_2) * (e_2 ^ e_3)
    )
    assert a * b == a.dot(b) + a.wedge(b)


def test_projection_and_rejection_split_the_product_2d() -> None:
    """Split ``a`` relative to ``b`` into the part parallel to ``b``
    (``a_par = proj_b(a)``) and the part perpendicular (``a_perp = rej_b(a)``).
    Multiplying each by ``b`` isolates one face of the product: ``a_par b = a·b``
    (parallel, so no wedge), ``a_perp b = a∧b`` (perpendicular, so no dot)."""
    a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
    a: Gn = a_1 * e_1 + a_2 * e_2
    b: Gn = b_1 * e_1 + b_2 * e_2
    a_par: MultiVectorBase = Gn.project(onto=b)(a)  # part of a along b
    a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)  # part of a perp to b
    assert a_par + a_perp == a  # the two parts reconstruct a
    assert a_par * b == a.dot(b)  # parallel part times b is the dot
    assert a_perp * b == a.wedge(b)  # perpendicular part times b is the wedge


def test_projection_and_rejection_split_the_product_3d() -> None:
    """The same projection/rejection split, over general 3D vectors."""
    a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")
    a: Gn = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: Gn = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    a_par: MultiVectorBase = Gn.project(onto=b)(a)
    a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)
    assert a_par + a_perp == a
    assert a_par * b == a.dot(b)
    assert a_perp * b == a.wedge(b)


@pytest.mark.parametrize("dim", [2, 3])
def test_projection_rejection_split_numeric(dim: int) -> None:
    random.seed(20260803)
    tol: float = 1e-9
    for _ in range(100):
        a: Gn = random_vector(dim)
        b: Gn = random_vector(dim)
        a_par: MultiVectorBase = Gn.project(onto=b)(a)
        a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)
        assert (a_par * b).isclose(a.dot(b), rel_tol=tol, abs_tol=tol)
        assert (a_perp * b).isclose(a.wedge(b), rel_tol=tol, abs_tol=tol)
        assert (a_par + a_perp).isclose(a, rel_tol=tol, abs_tol=tol)
        assert (a_par * b + a_perp * b).isclose(a * b, rel_tol=tol, abs_tol=tol)


def test_graded_vector_factories_type_precisely() -> None:
    """On the graded ``Vector_n`` types, project/reject/reflect of a vector across
    a vector stay the concrete vector type -- not the base ``MultiVectorBase`` the
    general ``Gn`` path (above) returns.  ``typing.assert_type`` makes this a
    static check: a regression in the generated overloads fails ``ty check tests``.
    (Runtime is unchanged; ``assert_type`` is a runtime no-op, so the ``isinstance``
    lines below are what this test asserts when executed.)
    """
    v2a: g2.Vector = 2 * g2.Vector.e_1 + 3 * g2.Vector.e_2
    v2b: g2.Vector = 1 * g2.Vector.e_1 + 1 * g2.Vector.e_2
    typing.assert_type(g2.Vector.project(onto=v2b)(v2a), g2.Vector)
    typing.assert_type(g2.Vector.reject(away_from=v2b)(v2a), g2.Vector)
    typing.assert_type(g2.Vector.reflect(across=v2b)(v2a), g2.Vector)

    v3a: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3
    v3b: g3.Vector = 1 * g3.Vector.e_1 + 1 * g3.Vector.e_2
    typing.assert_type(g3.Vector.project(onto=v3b)(v3a), g3.Vector)
    typing.assert_type(g3.Vector.reject(away_from=v3b)(v3a), g3.Vector)
    typing.assert_type(g3.Vector.reflect(across=v3b)(v3a), g3.Vector)

    assert isinstance(g2.Vector.reject(away_from=v2b)(v2a), g2.Vector)
    assert isinstance(g3.Vector.reflect(across=v3b)(v3a), g3.Vector)
