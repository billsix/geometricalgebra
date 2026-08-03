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

import pytest

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
