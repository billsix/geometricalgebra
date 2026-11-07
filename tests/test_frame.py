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

import itertools
import random
from collections.abc import Sequence

import pytest
import sympy
from _helpers import random_vector

# pytest.param returns a ParameterSet, which pytest does not export publicly.
from _pytest.mark.structures import ParameterSet

from gacalc import g2, g3
from gacalc.base import MultiVectorBase
from gacalc.frame import (
    all_wedged_except_the_kth,
    are_linearly_independent,
    is_frame,
    kronecker_delta,
    make_orthogonal_frame,
    make_orthogonal_frame_hestenes,
    make_orthogonal_frame_hestenes_inverse,
    prefix_blades,
    reciprocal_frame,
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

# A third fully general 3D vector, so the symbolic 3D tests exercise a complete
# 3-vector frame (gn only ships ``sym_vec2_*`` / ``sym_vec3_1`` / ``sym_vec3_2``).
# Same ``symbol * basis`` form as gn's symbolic vectors.
c_1, c_2, c_3 = sympy.symbols("c_1 c_2 c_3")
sym_vec3_3: Gn = c_1 * e_1 + c_2 * e_2 + c_3 * e_3

# The frames the orthogonalization and reciprocal-frame tests run on, with one id each:
# general symbolic frames (every component its own symbol, so a passing test is a
# proof for every 2D or 3D frame), a concrete oblique 3D frame whose values are
# readable numbers, and concrete oblique frames on the graded g2/g3 types (a graded
# Vector's one() is the zero vector, which folds seeded with 1 must not use).
symbolic_2d_frame: list[MultiVectorBase] = [sym_vec2_1, sym_vec2_2]
symbolic_3d_frame: list[MultiVectorBase] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
FRAMES: list[list[MultiVectorBase]] = [
    symbolic_2d_frame,
    [1 * e_1 + 1 * e_2, 1 * e_2 + 1 * e_3, 1 * e_1 + 1 * e_3],
    symbolic_3d_frame,
    [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2],
    [
        2 * g3.e_1 + 0 * g3.e_2 + 1 * g3.e_3,
        1 * g3.e_1 + 3 * g3.e_2 + 0 * g3.e_3,
        1 * g3.e_1 + 1 * g3.e_2 + 4 * g3.e_3,
    ],
]
FRAME_IDS: list[str] = [
    "gn-2d-symbolic",
    "gn-3d-concrete",
    "gn-3d-symbolic",
    "g2-concrete",
    "g3-concrete",
]

# FRAMES for the tests whose general 3D symbolic case takes over 10 s: that case is
# marked slow, so `make test` skips it and `make test-full` (CI) runs it.
FRAMES_WITH_SLOW_3D_SYMBOLIC: list[ParameterSet] = [
    pytest.param(frame, id=frame_id, marks=pytest.mark.slow)
    if frame_id == "gn-3d-symbolic"
    else pytest.param(frame, id=frame_id)
    for frame, frame_id in zip(FRAMES, FRAME_IDS, strict=True)
]

# --- is_frame / are_linearly_independent -----------------------------------


def test_is_frame_is_are_linearly_independent() -> None:
    """``is_frame`` is a pass-through to ``are_linearly_independent``."""
    assert is_frame([1 * e_1, 1 * e_2]) == are_linearly_independent([1 * e_1, 1 * e_2])
    assert is_frame([1 * e_1, 2 * e_1]) == are_linearly_independent([1 * e_1, 2 * e_1])


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


@pytest.mark.parametrize("frame", FRAMES_WITH_SLOW_3D_SYMBOLIC)
def test_orthogonal_frame_keeps_the_first_and_orthogonalizes_the_rest(
    frame: list[MultiVectorBase],
) -> None:
    """Orthogonalize a frame: the first vector is kept, every pair of the results is
    orthogonal (exactly, so on the symbolic frames this holds for every 2D or 3D
    frame), and the results still span the same space."""
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    assert w[0] == frame[0]  # first vector unchanged
    assert is_frame(w)  # still a frame
    w_i: MultiVectorBase
    w_j: MultiVectorBase
    for w_i, w_j in itertools.combinations(w, 2):
        assert w_i.is_orthogonal_to(w_j)


def test_orthogonal_frame_orthogonal_numeric_3d() -> None:
    random.seed(20260823)
    for _ in range(100):
        vectors: list[Gn] = [random_vector(3) for _ in range(3)]
        # three random vectors are independent with probability 1
        assert is_frame(vectors, float_close_to_zero=True)
        frame: list = make_orthogonal_frame(vectors)
        assert is_frame(frame, float_close_to_zero=True)
        i: int
        j: int
        for i in range(3):
            for j in range(i + 1, 3):
                assert frame[i].is_orthogonal_to(frame[j], float_close_to_zero=True)


def test_make_orthogonal_frame_raises_on_dependent() -> None:
    with pytest.raises(ValueError):
        make_orthogonal_frame([1 * e_1, 2 * e_1])
    with pytest.raises(ValueError):
        make_orthogonal_frame([1 * e_1, 1 * e_2, 1 * e_1 + 1 * e_2])


# --- reverse-based Hestenes orthogonalization: parallel to rejection (Part 1c) ---
#
# Hestenes & Sobczyk, Clifford Algebra to Geometric Calculus, p. 27:
#   (3.1)  A_0 := 1,  A_k := v_1 ∧ v_2 ∧ … ∧ v_k        (the prefix k-blades)
#   (3.2)  c_k := reverse(A_{k-1}) A_k                   (the orthogonal frame)
# Each c_k points the same way as the rejection w_k -- c_k ∥ w_k (and c_1 == w_1) --
# because ``A_k = A_{k-1} v_k^⊥``, so ``c_k = (reverse(A_{k-1}) A_{k-1}) v_k^⊥ =
# |A_{k-1}|² v_k^⊥``, a positive-scalar multiple of w_k.  The symbolic/concrete test
# asserts both the parallelism and that exact factor; the numeric test asserts the
# parallelism.  See ``tasks/define-frame.md`` Part 1c.


@pytest.mark.parametrize("frame", FRAMES_WITH_SLOW_3D_SYMBOLIC)
def test_hestenes_parallel_to_rejection(frame: list[MultiVectorBase]) -> None:
    """Hestenes' reverse-based ``c_k`` points the same way as the rejection ``w_k``
    (``c_k ∥ w_k``, the scale-independent geometric fact), and is exactly
    ``|A_{k-1}|² * w_k``, a positive multiple. ``c_1 = w_1``."""
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes(frame)
    A: list[MultiVectorBase] = list(prefix_blades(frame))
    assert c[0] == frame[0]  # c_1 = w_1 = v_1 (first vector unchanged)
    k: int
    for k in range(1, len(frame)):
        assert c[k].is_parallel_to(w[k])  # same direction, scale-independent
        assert c[k] - A[k].magnitude_squared() * w[k] == type(c[k]).zero()


@pytest.mark.parametrize("dim", [2, 3], ids=["2d", "3d"])
def test_hestenes_parallel_to_rejection_numeric(dim: int) -> None:
    """Each ``c_k`` (reverse Hestenes) is parallel to ``w_k`` (rejection) on random
    frames -- the float outer product ``c_k ∧ w_k`` is ~zero."""
    random.seed(20260823)
    for _ in range(50):
        vectors: list[Gn] = [random_vector(dim) for _ in range(dim)]
        rejection: list[MultiVectorBase] = make_orthogonal_frame(vectors)
        hestenes: list[MultiVectorBase] = make_orthogonal_frame_hestenes(vectors)
        for k in range(dim):
            assert hestenes[k].is_parallel_to(rejection[k], float_close_to_zero=True)


# --- inverse-based Hestenes: equals the rejection frame EXACTLY -------------
#
# make_orthogonal_frame_hestenes_inverse uses inverse(A_{k-1}) in place of
# reverse(A_{k-1}).  Since inverse(A) = reverse(A) / |A|^2 for a blade, the
# |A_{k-1}|^2 factor that scales the reverse variant cancels, so c_k^inv == w_k
# exactly -- same direction AND length, not merely up to a positive scalar.
# Built differently (inverse-blade product vs rejection), so compare via the
# difference eager-simplifying to the zero vector, as the reverse tests do.


@pytest.mark.parametrize("frame", FRAMES_WITH_SLOW_3D_SYMBOLIC)
def test_hestenes_inverse_equals_rejection_exactly(
    frame: list[MultiVectorBase],
) -> None:
    """The inverse-based closed form equals the rejection frame exactly:
    ``c_k^inv == w_k`` for every k (no ``|A_{k-1}|^2`` factor)."""
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes_inverse(frame)
    c_k: MultiVectorBase
    w_k: MultiVectorBase
    for c_k, w_k in zip(c, w, strict=True):
        assert c_k - w_k == type(c_k).zero()  # exact: the factor is 1


# --- prefix_blades (the eq-3.1 primitive, lifted to module scope) -----------


# (vectors, the expected A_0 … A_k), written out so the test does not restate the
# fold it checks.  On g2, A_0 is g2.Scalar.one(): the scalar 1, not Vector.one().
PREFIX_BLADE_CASES: list[tuple[list[MultiVectorBase], list[MultiVectorBase]]] = [
    (symbolic_2d_frame, [Gn.one(), sym_vec2_1, sym_vec2_1 ^ sym_vec2_2]),
    (
        symbolic_3d_frame,
        [
            Gn.one(),
            sym_vec3_1,
            sym_vec3_1 ^ sym_vec3_2,
            sym_vec3_1 ^ sym_vec3_2 ^ sym_vec3_3,
        ],
    ),
    (
        [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2],
        [g2.Scalar.one(), 2 * g2.e_1 + 0 * g2.e_2, 6 * (g2.e_1 ^ g2.e_2)],
    ),
]


@pytest.mark.parametrize(
    ("vectors", "expected"),
    PREFIX_BLADE_CASES,
    ids=["gn-2d-symbolic", "gn-3d-symbolic", "g2-concrete"],
)
def test_prefix_blades(
    vectors: list[MultiVectorBase], expected: list[MultiVectorBase]
) -> None:
    """``prefix_blades`` yields ``A_0 = 1``, ``A_1 = v_1``, ``A_2 = v_1 ∧ v_2``, …:
    ``k + 1`` blades for ``k`` vectors, the running wedge, exact."""
    assert list(prefix_blades(vectors)) == expected


def test_prefix_blades_feeds_hestenes() -> None:
    """The ``A_{k-1}``/``A_k`` pairs ``make_orthogonal_frame_hestenes`` consumes are
    exactly ``prefix_blades``' output -- ``c_k = reverse(A_{k-1}) A_k`` reproduces its
    result from the lifted primitive (the rewire kept the behaviour)."""
    vectors: list[Gn] = [sym_vec2_1, sym_vec2_2]
    blades: list[MultiVectorBase] = list(prefix_blades(vectors))
    rebuilt: list[MultiVectorBase] = [
        (blades[k - 1].reverse() * blades[k]).r_vector_part(1)
        for k in range(1, len(blades))
    ]
    assert rebuilt == make_orthogonal_frame_hestenes(vectors)


def test_prefix_blades_empty_raises() -> None:
    """A public primitive must define the empty case: no operand means no
    representation for ``A_0 = 1``, so it raises (rather than invent one)."""
    with pytest.raises(ValueError, match="nonempty"):
        list(prefix_blades([]))


# --- reciprocal_frame (H&S p. 28, eqs 3.5-3.7) -----------------------------

# A general symbolic vector to take coordinates of, in 2D and 3D.
y_1, y_2, y_3 = sympy.symbols("y_1 y_2 y_3")
sym_y2: Gn = y_1 * e_1 + y_2 * e_2
sym_y3: Gn = y_1 * e_1 + y_2 * e_2 + y_3 * e_3


def is_zero(value: object) -> bool:
    """Exact symbolic zero test (``simplify(value) == 0``)."""
    return sympy.simplify(sympy.sympify(value)) == 0


def is_zero_vector(value: MultiVectorBase) -> bool:
    """Whether every coefficient of ``value`` simplifies to zero."""
    return all(is_zero(c) for c in value.to_blade_dict().values())


@pytest.mark.parametrize("frame", FRAMES, ids=FRAME_IDS)
def test_reciprocal_frame_is_the_kronecker_delta(
    frame: Sequence[MultiVectorBase],
) -> None:
    """H&S p. 28 eq (3.5), the defining property: ``a^k · a_j = δ^k_j`` -- 1 when ``j =
    k`` and 0 when ``j ≠ k`` -- for every pair of a general symbolic frame, i.e. the
    matrix ``[a^k · a_j]`` is the identity. Lean
    (``proofs/GacalcProofs/ReciprocalFrame2D.lean``/``3D.lean``):
    ``dot_recip_kronecker``."""
    reciprocal: list[MultiVectorBase] = reciprocal_frame(frame)
    k: int
    j: int
    a_upper_k: MultiVectorBase
    a_j: MultiVectorBase
    for k, a_upper_k in enumerate(reciprocal, start=1):
        for j, a_j in enumerate(frame, start=1):
            assert is_zero(a_upper_k.dot(a_j).scalar_part() - kronecker_delta(k, j))


@pytest.mark.parametrize("frame", FRAMES, ids=FRAME_IDS)
def test_reciprocal_vectors_are_pure_vectors(frame: Sequence[MultiVectorBase]) -> None:
    """Eq (3.7)'s product with ``A_n⁻¹`` is a geometric product; it is a pure vector
    (grade 1 only), which is why it can also be read as the dot product."""
    a_upper: MultiVectorBase
    for a_upper in reciprocal_frame(frame):
        assert a_upper.grades() == [1]


@pytest.mark.parametrize(
    ("frame", "y"),
    [(symbolic_2d_frame, sym_y2), (symbolic_3d_frame, sym_y3)],
    ids=["2d", "3d"],
)
def test_reciprocal_frame_reconstructs_a_vector_symbolic(
    frame: Sequence[Gn], y: Gn
) -> None:
    """The coordinates of ``y`` in the frame are dot products with the reciprocal
    vectors: ``y == Σ_k (a^k · y) * a_k``. Lean
    (``proofs/GacalcProofs/ReciprocalFrame2D.lean``/``3D.lean``): ``reconstruct``."""
    rebuilt: MultiVectorBase = sum(
        (
            a_upper_k.dot(y).scalar_part() * a_k
            for a_upper_k, a_k in zip(reciprocal_frame(frame), frame, strict=True)
        ),
        start=Gn.zero(),
    )
    assert is_zero_vector(rebuilt - y)


@pytest.mark.parametrize("frame", FRAMES_WITH_SLOW_3D_SYMBOLIC)
def test_last_reciprocal_vector_is_the_last_rejection(
    frame: Sequence[MultiVectorBase],
) -> None:
    """``a^n == w_n / |w_n|²``: ``w_n`` (the last vector of the rejection frame) is
    ``a_n`` with the span of the others rejected out, so it is already perpendicular to
    every other frame vector; dividing by ``|w_n|²`` makes its dot with ``a_n`` one.
    Lean (``proofs/GacalcProofs/ReciprocalFrame2D.lean``/``3D.lean``):
    ``recip2_eq_reject_div`` / ``recip3_eq_reject_div``."""
    w_n: MultiVectorBase = make_orthogonal_frame(frame)[-1]
    assert is_zero_vector(reciprocal_frame(frame)[-1] - w_n / w_n.magnitude_squared())


def test_reciprocal_frame_of_the_standard_basis_is_itself() -> None:
    """An orthonormal frame is its own reciprocal."""
    basis: list[Gn] = [1 * e_1, 1 * e_2, 1 * e_3]
    assert reciprocal_frame(basis) == basis


def test_reciprocal_frame_raises_on_a_non_frame() -> None:
    """A dependent set has ``A_n = 0``, which has no inverse."""
    with pytest.raises(ValueError):
        reciprocal_frame([1 * e_1, 2 * e_1])
    with pytest.raises(ValueError):
        reciprocal_frame([])


def test_all_wedged_except_the_kth_leaves_out_one_vector() -> None:
    """``a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n``, k counted from 1: one vector leaves the empty
    wedge (the scalar 1), and a ``k`` outside ``1 … n`` raises."""
    frame: list[Gn] = [sym_vec2_1, sym_vec2_2]
    assert all_wedged_except_the_kth(frame, 1) == sym_vec2_2
    assert all_wedged_except_the_kth(frame, 2) == sym_vec2_1
    assert all_wedged_except_the_kth([sym_vec2_1], 1) == Gn.one()
    bad_k: int
    for bad_k in (0, 3):
        with pytest.raises(ValueError):
            all_wedged_except_the_kth(frame, bad_k)


def test_kronecker_delta() -> None:
    """``δ^k_j`` is 1 on the diagonal (``j = k``), 0 off it, and symmetric; over
    ``1 … n`` it is the identity matrix."""
    assert [kronecker_delta(k, k) for k in range(1, 5)] == [1, 1, 1, 1]
    assert [kronecker_delta(1, j) for j in (2, 3, 4)] == [0, 0, 0]
    assert kronecker_delta(3, 1) == kronecker_delta(1, 3) == 0
    identity: sympy.Matrix = sympy.Matrix(
        4, 4, lambda row, column: kronecker_delta(row + 1, column + 1)
    )
    assert identity == sympy.eye(4)
