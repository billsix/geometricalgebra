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


def test_orthogonal_frame_2d_symbolic() -> None:
    """Orthogonalize a general 2D frame -- ``sym_vec2_1`` / ``sym_vec2_2`` are
    ``a_1 * e_1 + a_2 * e_2`` / ``b_1 * e_1 + b_2 * e_2``: the first vector is kept, the
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
    i: int
    j: int
    for i in range(3):
        for j in range(i + 1, 3):
            assert w[i].is_orthogonal_to(w[j])


def test_orthogonal_frame_3d_symbolic() -> None:
    """Orthogonalize a *fully general* 3D frame (``sym_vec3_1``, ``sym_vec3_2``,
    ``sym_vec3_3`` -- three arbitrary vectors ``a * e``, ``b * e``, ``c * e``): the
    first is kept, each later one is exactly orthogonal to all earlier ones, and
    the result still spans 3-space. Proves it for *every* 3D frame, not just the
    concrete and numeric samples."""
    frame: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    assert w[0] == sym_vec3_1  # first vector unchanged
    assert is_frame(w)  # still a frame (spans 3-space)
    i: int
    j: int
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
# |A_{k-1}|² v_k^⊥``, a positive-scalar multiple of w_k.  These tests assert that
# scale-independent parallelism; the exact scale (factor 1) is pinned by the inverse
# variant's exact-equality tests above.  See ``tasks/define-frame.md`` Part 1c.


def test_hestenes_parallel_to_rejection_2d_symbolic() -> None:
    """On a general 2D frame (``sym_vec2_1`` / ``sym_vec2_2``), Hestenes' reverse-based
    ``c_k`` points the same way as the rejection ``w_k`` -- ``c_k ∥ w_k`` -- the
    scale-independent geometric fact. ``c_1 = w_1`` exactly; the inverse variant's test
    pins the exact scale."""
    w: list[MultiVectorBase] = make_orthogonal_frame([sym_vec2_1, sym_vec2_2])
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes([sym_vec2_1, sym_vec2_2])
    assert c[0] == sym_vec2_1  # c_1 = w_1 = sym_vec2_1 (first vector unchanged)
    assert c[1].is_parallel_to(w[1])  # same direction, independent of |A_1|² scaling


def test_hestenes_parallel_to_rejection_3d_concrete() -> None:
    """On a concrete oblique 3D frame -- so every value is a readable number -- each
    reverse-based ``c_k`` is parallel to the rejection ``w_k`` (``c_1`` equal, the rest
    same-direction)."""
    a: Gn = 1 * e_1 + 1 * e_2
    b: Gn = 1 * e_2 + 1 * e_3
    c: Gn = 1 * e_1 + 1 * e_3

    w: list[MultiVectorBase] = make_orthogonal_frame([a, b, c])
    h: list[MultiVectorBase] = make_orthogonal_frame_hestenes([a, b, c])
    assert h[0] == a  # c_1 = w_1 = a (first vector unchanged)
    assert h[1].is_parallel_to(w[1])
    assert h[2].is_parallel_to(w[2])


def test_hestenes_parallel_to_rejection_3d_symbolic() -> None:
    """On a fully general 3D frame (``sym_vec3_1``, ``sym_vec3_2``, ``sym_vec3_3``),
    each reverse-based ``c_k`` is parallel to the rejection ``w_k`` -- proven exactly
    (the symbolic outer product ``c_k ∧ w_k`` is zero), not just numerically."""
    frame: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes(frame)
    assert c[0] == sym_vec3_1  # c_1 = w_1 = sym_vec3_1 (first vector unchanged)
    for k in range(1, 3):
        assert c[k].is_parallel_to(w[k])  # same direction, scale-independent


def test_hestenes_parallel_to_rejection_numeric() -> None:
    """Each ``c_k`` (reverse Hestenes) is parallel to ``w_k`` (rejection) on random
    2D/3D frames -- the float outer product ``c_k ∧ w_k`` is ~zero."""
    random.seed(20260823)
    dim: int
    for dim in (2, 3):
        for _ in range(50):
            vectors: list[Gn] = [random_vector(dim) for _ in range(dim)]
            rejection: list[MultiVectorBase] = make_orthogonal_frame(vectors)
            hestenes: list[MultiVectorBase] = make_orthogonal_frame_hestenes(vectors)
            for k in range(dim):
                assert hestenes[k].is_parallel_to(
                    rejection[k], float_close_to_zero=True
                )


# --- inverse-based Hestenes: equals the rejection frame EXACTLY -------------
#
# make_orthogonal_frame_hestenes_inverse uses inverse(A_{k-1}) in place of
# reverse(A_{k-1}).  Since inverse(A) = reverse(A) / |A|^2 for a blade, the
# |A_{k-1}|^2 factor that scales the reverse variant cancels, so c_k^inv == w_k
# exactly -- same direction AND length, not merely up to a positive scalar.
# Built differently (inverse-blade product vs rejection), so compare via the
# difference eager-simplifying to the zero vector, as the reverse tests do.


def test_hestenes_inverse_equals_rejection_exactly_2d_symbolic() -> None:
    """On a general 2D frame, the inverse-based closed form equals the rejection
    frame exactly: ``c_k^inv == w_k`` for every k (no ``|A_{k-1}|^2`` factor)."""
    w: list[MultiVectorBase] = make_orthogonal_frame([sym_vec2_1, sym_vec2_2])
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes_inverse(
        [sym_vec2_1, sym_vec2_2]
    )
    zero: MultiVectorBase = type(c[0]).zero()
    for k in range(2):
        assert c[k] - w[k] == zero  # exact: the factor is 1, not |A_{k-1}|^2


def test_hestenes_inverse_equals_rejection_exactly_3d_symbolic() -> None:
    """Same exact equality on a fully general 3D frame: ``c_k^inv == w_k`` for all k."""
    frame: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    c: list[MultiVectorBase] = make_orthogonal_frame_hestenes_inverse(frame)
    zero: MultiVectorBase = type(c[0]).zero()
    for k in range(3):
        assert c[k] - w[k] == zero


# --- prefix_blades (the eq-3.1 primitive, lifted to module scope) -----------


def test_prefix_blades_2d_symbolic() -> None:
    """``prefix_blades`` yields ``A_0 = 1``, ``A_1 = v_1``, ``A_2 = v_1 ∧ v_2`` for a
    general 2D frame -- ``k + 1`` blades for ``k`` vectors."""
    vectors: list[Gn] = [sym_vec2_1, sym_vec2_2]
    blades: list[MultiVectorBase] = list(prefix_blades(vectors))
    assert len(blades) == 3  # A_0, A_1, A_2
    assert blades[0] == type(sym_vec2_1).one()  # A_0 = 1
    assert blades[1] == sym_vec2_1  # A_1 = 1 ∧ v_1 = v_1
    assert blades[2] == sym_vec2_1 ^ sym_vec2_2  # A_2 = v_1 ∧ v_2


def test_prefix_blades_3d_symbolic() -> None:
    """On a fully general 3D frame the prefix blades are ``1, v_1, v_1 ∧ v_2,
    v_1 ∧ v_2 ∧ v_3`` -- the running wedge, exact."""
    vectors: list[Gn] = [sym_vec3_1, sym_vec3_2, sym_vec3_3]
    blades: list[MultiVectorBase] = list(prefix_blades(vectors))
    assert blades[0] == type(sym_vec3_1).one()
    assert blades[1] == sym_vec3_1
    assert blades[2] == sym_vec3_1 ^ sym_vec3_2
    assert blades[3] == sym_vec3_1 ^ sym_vec3_2 ^ sym_vec3_3


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

# The general symbolic frames: every component its own symbol.
frames_2d_and_3d: list[list[Gn]] = [
    [sym_vec2_1, sym_vec2_2],
    [sym_vec3_1, sym_vec3_2, sym_vec3_3],
]


def is_zero(value: object) -> bool:
    """Exact symbolic zero test (``simplify(value) == 0``)."""
    return sympy.simplify(sympy.sympify(value)) == 0


def is_zero_vector(value: MultiVectorBase) -> bool:
    """Whether every coefficient of ``value`` simplifies to zero."""
    return all(is_zero(c) for c in value.to_blade_dict().values())


@pytest.mark.parametrize("frame", frames_2d_and_3d, ids=["2d", "3d"])
def test_reciprocal_frame_is_the_kronecker_delta_symbolic(frame: Sequence[Gn]) -> None:
    """H&S p. 28 eq (3.5), the defining property: ``a^k · a_j = δ^k_j`` -- 1 when
    ``j = k`` and 0 when ``j ≠ k`` -- for every pair of a general symbolic frame, i.e.
    the matrix ``[a^k · a_j]`` is the identity."""
    reciprocal: list[MultiVectorBase] = reciprocal_frame(frame)
    k: int
    j: int
    a_upper_k: MultiVectorBase
    a_j: Gn
    for k, a_upper_k in enumerate(reciprocal, start=1):
        for j, a_j in enumerate(frame, start=1):
            assert is_zero(a_upper_k.dot(a_j).scalar_part() - kronecker_delta(k, j))


@pytest.mark.parametrize("frame", frames_2d_and_3d, ids=["2d", "3d"])
def test_reciprocal_vectors_are_pure_vectors_symbolic(frame: Sequence[Gn]) -> None:
    """Eq (3.7)'s product with ``A_n⁻¹`` is a geometric product; it is a pure vector
    (grade 1 only), which is why it can also be read as the dot product."""
    a_upper: MultiVectorBase
    for a_upper in reciprocal_frame(frame):
        assert a_upper.grades() == [1]


@pytest.mark.parametrize(
    ("frame", "y"),
    [(frames_2d_and_3d[0], sym_y2), (frames_2d_and_3d[1], sym_y3)],
    ids=["2d", "3d"],
)
def test_reciprocal_frame_reconstructs_a_vector_symbolic(
    frame: Sequence[Gn], y: Gn
) -> None:
    """The coordinates of ``y`` in the frame are dot products with the reciprocal
    vectors: ``y == Σ_k (a^k · y) * a_k``."""
    rebuilt: MultiVectorBase = sum(
        (
            a_upper_k.dot(y).scalar_part() * a_k
            for a_upper_k, a_k in zip(reciprocal_frame(frame), frame, strict=True)
        ),
        start=Gn.zero(),
    )
    assert is_zero_vector(rebuilt - y)


@pytest.mark.parametrize("frame", frames_2d_and_3d, ids=["2d", "3d"])
def test_last_reciprocal_vector_is_the_last_rejection_symbolic(
    frame: Sequence[Gn],
) -> None:
    """``a^n == w_n / |w_n|²``: ``w_n`` (the last vector of the rejection frame) is
    ``a_n`` with the span of the others rejected out, so it is already perpendicular to
    every other frame vector; dividing by ``|w_n|²`` makes its dot with ``a_n`` one."""
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


def test_prefix_blades_on_a_graded_type() -> None:
    """On the graded ``g2`` types the seed ``A_0`` is the scalar 1, not ``Vector``'s
    ``one()`` (the zero vector, which would make every prefix blade zero)."""
    blades: list[MultiVectorBase] = list(
        prefix_blades([2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2])
    )
    assert blades == [g2.Scalar.one(), 2 * g2.e_1 + 0 * g2.e_2, 6 * (g2.e_1 ^ g2.e_2)]


graded_frames: list[list[MultiVectorBase]] = [
    [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2],
    [
        2 * g3.e_1 + 0 * g3.e_2 + 1 * g3.e_3,
        1 * g3.e_1 + 3 * g3.e_2 + 0 * g3.e_3,
        1 * g3.e_1 + 1 * g3.e_2 + 4 * g3.e_3,
    ],
]


@pytest.mark.parametrize("frame", graded_frames, ids=["g2", "g3"])
def test_hestenes_forms_on_a_graded_type(frame: list[MultiVectorBase]) -> None:
    """On the graded types both Hestenes closed forms are nonzero and agree with the
    rejection frame: the inverse form exactly, the reverse form up to the positive
    scalar ``|A_{k-1}|²``."""
    w: list[MultiVectorBase] = make_orthogonal_frame(frame)
    by_inverse: list[MultiVectorBase] = make_orthogonal_frame_hestenes_inverse(frame)
    by_reverse: list[MultiVectorBase] = make_orthogonal_frame_hestenes(frame)
    assert by_inverse == w
    w_k: MultiVectorBase
    c_k: MultiVectorBase
    for w_k, c_k in zip(w, by_reverse, strict=True):
        assert (c_k ^ w_k) == type(c_k ^ w_k).zero()  # parallel
        assert c_k.dot(w_k).scalar_part() > 0  # same direction, nonzero


def test_reciprocal_frame_on_a_graded_type() -> None:
    """A concrete oblique 3D frame on the graded ``g3`` types satisfies eq (3.5)."""
    frame: list[MultiVectorBase] = [
        2 * g3.e_1 + 0 * g3.e_2 + 1 * g3.e_3,
        1 * g3.e_1 + 3 * g3.e_2 + 0 * g3.e_3,
        1 * g3.e_1 + 1 * g3.e_2 + 4 * g3.e_3,
    ]
    k: int
    j: int
    a_upper_k: MultiVectorBase
    a_j: MultiVectorBase
    for k, a_upper_k in enumerate(reciprocal_frame(frame), start=1):
        for j, a_j in enumerate(frame, start=1):
            assert a_upper_k.dot(a_j).scalar_part() == kronecker_delta(k, j)


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
