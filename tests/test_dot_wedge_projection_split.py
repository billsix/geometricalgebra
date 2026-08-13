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

Verified here **symbolically** over general 2D and 3D vectors (exact ``==`` on
the eager-simplifying ``Gn`` reference), and **numerically** over random
vectors (float-tolerant ``isclose``).  See
``tasks/reference/dot-wedge-projection-rejection.md`` for the hand proof.
"""

import random
import typing

import pytest

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.gn import (
    Gn,
    e_1,
    e_2,
    e_3,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
)

SYMBOLIC_VECTOR_PAIRS: list[tuple[Gn, Gn]] = [
    (sym_vec2_1, sym_vec2_2),  # general 2D vectors a = a1 e1 + a2 e2, etc.
    (sym_vec3_1, sym_vec3_2),  # general 3D vectors
]


@pytest.mark.parametrize(("a", "b"), SYMBOLIC_VECTOR_PAIRS)
def test_projection_product_is_dot_symbolic(a: Gn, b: Gn) -> None:
    a_par: MultiVectorBase = Gn.project(onto=b)(a)
    assert a_par * b == a.dot(b)


@pytest.mark.parametrize(("a", "b"), SYMBOLIC_VECTOR_PAIRS)
def test_rejection_product_is_wedge_symbolic(a: Gn, b: Gn) -> None:
    a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)
    assert a_perp * b == a.wedge(b)


@pytest.mark.parametrize(("a", "b"), SYMBOLIC_VECTOR_PAIRS)
def test_split_reconstructs_the_vector_symbolic(a: Gn, b: Gn) -> None:
    a_par: MultiVectorBase = Gn.project(onto=b)(a)
    a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)
    assert a_par + a_perp == a


@pytest.mark.parametrize(("a", "b"), SYMBOLIC_VECTOR_PAIRS)
def test_products_sum_to_geometric_product_symbolic(a: Gn, b: Gn) -> None:
    a_par: MultiVectorBase = Gn.project(onto=b)(a)
    a_perp: MultiVectorBase = Gn.reject(away_from=b)(a)
    ab: Gn = a * b  # the full geometric product being decomposed
    # a_par b + a_perp b == a·b + a∧b == a b
    assert a_par * b + a_perp * b == ab
    assert ab == a.dot(b) + a.wedge(b)


def _random_vector(dim: int) -> Gn:
    # random is fine here: these are test vectors, not cryptographic material.
    basis: list[Gn] = [e_1, e_2, e_3][:dim]
    v: Gn = Gn.zero()
    basis_vector: Gn
    for basis_vector in basis:
        v = v + random.uniform(-5.0, 5.0) * basis_vector  # noqa: S311
    return v


@pytest.mark.parametrize("dim", [2, 3])
def test_projection_rejection_split_numeric(dim: int) -> None:
    random.seed(20260803)
    tol: float = 1e-9
    for _ in range(100):
        a: Gn = _random_vector(dim)
        b: Gn = _random_vector(dim)
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
    v2b: g2.Vector = g2.Vector.e_1 + g2.Vector.e_2
    typing.assert_type(g2.Vector.project(onto=v2b)(v2a), g2.Vector)
    typing.assert_type(g2.Vector.reject(away_from=v2b)(v2a), g2.Vector)
    typing.assert_type(g2.Vector.reflect(across=v2b)(v2a), g2.Vector)

    v3a: g3.Vector = g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3
    v3b: g3.Vector = g3.Vector.e_1 + g3.Vector.e_2
    typing.assert_type(g3.Vector.project(onto=v3b)(v3a), g3.Vector)
    typing.assert_type(g3.Vector.reject(away_from=v3b)(v3a), g3.Vector)
    typing.assert_type(g3.Vector.reflect(across=v3b)(v3a), g3.Vector)

    assert isinstance(g2.Vector.reject(away_from=v2b)(v2a), g2.Vector)
    assert isinstance(g3.Vector.reflect(across=v3b)(v3a), g3.Vector)
