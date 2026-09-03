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

"""Frames and their orthogonalization (``gacalc.frame``).

A **frame** is a linearly independent set of vectors -- ``a_1 ∧ … ∧ a_k ≠ 0``
(Hestenes & Sobczyk, Clifford Algebra to Geometric Calculus, p. 27).
``make_orthogonal_frame`` orthogonalizes one by rejection, keeping the first vector
as-is; its result must stay a frame (independent) AND be mutually orthogonal.
Verified symbolically over general vectors (exact ``==``) and numerically over
random vectors (float-tolerant).
"""

import random
from collections.abc import Sequence

import pytest
import sympy
from _helpers import random_vector

from gacalc.base import MultiVectorBase
from gacalc.frame import (
    are_linearly_independent,
    is_frame,
    make_orthogonal_frame,
    make_orthogonal_frame_hestenes,
)
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
from gacalc.measure import content

# A third fully general 3D vector, so the symbolic 3D tests exercise a complete
# 3-vector frame (gn only ships ``sym_vec2_*`` / ``sym_vec3_1`` / ``sym_vec3_2``).
# Same ``symbol * basis`` form as gn's symbolic vectors.
c_1, c_2, c_3 = sympy.symbols("c_1 c_2 c_3")
sym_vec3_3: Gn = c_1 * e_1 + c_2 * e_2 + c_3 * e_3

# --- is_frame / are_linearly_independent -----------------------------------


def test_is_frame_is_are_linearly_independent() -> None:
    """``is_frame`` is a pass-through to ``are_linearly_independent``."""
    assert is_frame([1 * e_1, 1 * e_2]) == are_linearly_independent([1 * e_1, 1 * e_2])
    assert is_frame([1 * e_1, 2 * e_1]) == are_linearly_independent([1 * e_1, 2 * e_1])


def test_independent_sets_are_frames() -> None:
    assert is_frame([1 * e_1])  # a single nonzero vector
    assert is_frame([1 * e_1, 1 * e_2])  # 2D basis
    assert is_frame([1 * e_1, 1 * e_2, 1 * e_3])  # 3D basis
    assert is_frame([1 * e_1 + 1 * e_2, 1 * e_2])  # oblique 2D frame (not orthogonal)


def test_dependent_sets_are_not_frames() -> None:
    assert not is_frame([1 * e_1, 2 * e_1])  # parallel
    assert not is_frame(
        [1 * e_1, 1 * e_2, 1 * e_1 + 1 * e_2]
    )  # third in the span of the first two
    assert not is_frame(
        [1 * e_1, 1 * e_2, 1 * e_3, 1 * e_1]
    )  # a repeat -> 4 vectors in 3D


def test_empty_is_not_a_frame() -> None:
    assert not is_frame([])


def test_symbolic_general_vectors_are_a_frame() -> None:
    assert is_frame([sym_vec2_1, sym_vec2_2])
    assert is_frame([sym_vec3_1, sym_vec3_2])


def test_non_vector_input_raises() -> None:
    """A frame is a set of *vectors*; a bivector member is a category error."""
    with pytest.raises(ValueError):
        is_frame([1 * e_1, e_1 ^ e_2])  # e_1 ∧ e_2 is a bivector


# --- make_orthogonal_frame -------------------------------------------------


def test_orthogonal_frame_keeps_first_vector() -> None:
    a: Gn = 1 * e_1 + 1 * e_2
    frame: list = make_orthogonal_frame([a, 1 * e_2])
    assert frame[0] == a


def test_orthogonal_frame_2d_symbolic() -> None:
    """Orthogonalize a general 2D frame -- ``sym_vec2_1`` / ``sym_vec2_2`` are
    ``a_1 e_1 + a_2 e_2`` / ``b_1 e_1 + b_2 e_2``: the first vector is kept, the
    second becomes orthogonal to it, and the pair still spans the plane."""
    w: list[MultiVectorBase] = make_orthogonal_frame([sym_vec2_1, sym_vec2_2])
    assert w[0] == sym_vec2_1  # first vector unchanged
    assert w[0].is_orthogonal_to(w[1])  # the two are now orthogonal
    assert is_frame(w)  # and still span the plane


def test_orthogonal_frame_3d_concrete() -> None:
    """Orthogonalize a concrete oblique 3D frame, so every value is a readable
    number: keep the first, make each next orthogonal to all the earlier ones."""
    a: Gn = 1 * e_1 + 1 * e_2
    b: Gn = 1 * e_2 + 1 * e_3
    c: Gn = 1 * e_1 + 1 * e_3

    w: list[MultiVectorBase] = make_orthogonal_frame([a, b, c])
    assert w[0] == a
    assert is_frame(w)
    for i in range(3):
        for j in range(i + 1, 3):
            assert w[i].is_orthogonal_to(w[j])


def test_orthogonal_frame_3d_symbolic() -> None:
    """Orthogonalize a *fully general* 3D frame (``sym_vec3_1``, ``sym_vec3_2``,
    ``sym_vec3_3`` -- three arbitrary vectors ``a·e``, ``b·e``, ``c·e``): the
    first is kept, each later one is exactly orthogonal to all earlier ones, and
    the result still spans 3-space. Proves it for *every* 3D frame, not just the
    concrete and numeric samples."""
    frame: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    assert w[0] == sym_vec3_1  # first vector unchanged
    assert is_frame(w)  # still a frame (spans 3-space)
    for i in range(3):
        for j in range(i + 1, 3):
            assert w[i].is_orthogonal_to(w[j])  # exact symbolic orthogonality


def test_orthogonal_frame_orthogonal_numeric_3d() -> None:
    random.seed(20260823)
    for _ in range(100):
        vectors: list[Gn] = [random_vector(3) for _ in range(3)]
        # three random vectors are independent with probability 1
        assert is_frame(vectors, float_close_to_zero=True)
        frame: list = make_orthogonal_frame(vectors)
        assert is_frame(frame, float_close_to_zero=True)
        for i in range(3):
            for j in range(i + 1, 3):
                assert frame[i].is_orthogonal_to(frame[j], float_close_to_zero=True)


def test_make_orthogonal_frame_raises_on_dependent() -> None:
    with pytest.raises(ValueError):
        make_orthogonal_frame([1 * e_1, 2 * e_1])
    with pytest.raises(ValueError):
        make_orthogonal_frame([1 * e_1, 1 * e_2, 1 * e_1 + 1 * e_2])


# --- equivalence with Hestenes' p. 27 orthogonalization (Part 1c) -----------
#
# Hestenes & Sobczyk, Clifford Algebra to Geometric Calculus, p. 27:
#   (3.1)  A_0 := 1,  A_k := v_1 ∧ v_2 ∧ … ∧ v_k        (the prefix k-blades)
#   (3.2)  c_k := reverse(A_{k-1}) A_k                   (the orthogonal frame)
# This equals ``make_orthogonal_frame`` (rejection) up to a positive scalar per
# vector: ``c_k == |A_{k-1}|² · w_k`` (and c_1 == v_1 == w_1), because
# ``A_k = A_{k-1} v_k^⊥`` so ``c_k = (reverse(A_{k-1}) A_{k-1}) v_k^⊥ =
# |A_{k-1}|² v_k^⊥``.  See ``tasks/define-frame.md`` Part 1c.


def _prev_blade_magnitude_squared(vectors: Sequence[MultiVectorBase], k: int):
    """The positive scalar factor ``|A_{k-1}|²`` -- i.e. ``content(v_1..v_{k-1})²``
    (with ``A_0 = 1`` -> ``1``)."""
    if k == 1:
        return 1
    return content(vectors[: k - 1]) ** 2


def test_hestenes_equals_rejection_2d_symbolic() -> None:
    """On a general 2D frame (``sym_vec2_1`` / ``sym_vec2_2``), Hestenes' ``c_k``
    equals the rejection ``w_k`` scaled by ``|A_{k-1}|²``: ``c_1 = w_1`` and
    ``c_2 = |sym_vec2_1|² · w_2``.

    The two are equal but built differently (a blade product vs a scaled
    rejection), so their sympy forms are not structurally identical -- the
    ``(c_2 − |a|² w_2)`` subtraction eager-simplifies to the zero vector."""
    w: list[MultiVectorBase] = make_orthogonal_frame([sym_vec2_1, sym_vec2_2])
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes([sym_vec2_1, sym_vec2_2])
    assert c[0] == sym_vec2_1  # c_1 = w_1 = sym_vec2_1
    factor: object = content([sym_vec2_1]) ** 2  # |A_1|² = |sym_vec2_1|²
    assert c[1] - factor * w[1] == type(c[1]).zero()  # c_2 = |sym_vec2_1|² · w_2


def test_hestenes_equals_rejection_3d_concrete() -> None:
    """On a concrete oblique 3D frame -- so every value is a readable number --
    ``c_k == |A_{k-1}|² · w_k`` for each k."""
    a: Gn = 1 * e_1 + 1 * e_2
    b: Gn = 1 * e_2 + 1 * e_3
    c: Gn = 1 * e_1 + 1 * e_3

    w: list[MultiVectorBase] = make_orthogonal_frame([a, b, c])
    h: list[MultiVectorBase] = make_orthogonal_frame_hestenes([a, b, c])
    assert h[0] == a  # |A_0|² = 1
    assert h[1] == content([a]) ** 2 * w[1]  # |A_1|² = |a|²
    assert h[2] == content([a, b]) ** 2 * w[2]  # |A_2|² = |a ∧ b|²


def test_hestenes_equals_rejection_3d_symbolic() -> None:
    """On a fully general 3D frame (``sym_vec3_1``, ``sym_vec3_2``, ``sym_vec3_3``),
    Hestenes' ``c_k`` equals the rejection ``w_k`` scaled by ``|A_{k-1}|²`` for
    every k -- proven exactly, not just numerically. The ``(c_k − |A_{k-1}|² w_k)``
    subtraction eager-simplifies to the zero vector even though the two
    constructions differ structurally."""
    frame: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes(frame)
    zero: MultiVectorBase = type(c[0]).zero()
    for k in range(1, 4):
        factor = _prev_blade_magnitude_squared(frame, k)
        assert c[k - 1] - factor * w[k - 1] == zero  # c_k = |A_{k-1}|² · w_k


def test_hestenes_equals_rejection_numeric() -> None:
    """``c_k`` (Hestenes) == ``|A_{k-1}|² · w_k`` (rejection) on random 2D/3D frames."""
    random.seed(20260823)
    for dim in (2, 3):
        for _ in range(50):
            vectors: list[Gn] = [random_vector(dim) for _ in range(dim)]
            rejection: list[MultiVectorBase] = make_orthogonal_frame(vectors)
            hestenes: list[MultiVectorBase] = make_orthogonal_frame_hestenes(vectors)
            for k in range(1, dim + 1):
                factor = _prev_blade_magnitude_squared(vectors, k)
                assert hestenes[k - 1].isclose(
                    factor * rejection[k - 1], rel_tol=1e-9, abs_tol=1e-9
                )
