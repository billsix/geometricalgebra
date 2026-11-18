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

"""How far a ``Frame`` (QR with the lengths factored out) gets toward the SVD.

The three routes of ``tasks/archive/2026/11/18/frame-svd-investigation.md``, each
written with gacalc's own transforms; the finding is in
``tasks/reference/frames-qr-and-reciprocal-frames.md`` ("Does this give the SVD?").

1. ``f = Q ∘ R``: the frame map is a rotation (times an axis reflection when the
   frame is left-handed) after a triangular shear-scale.
2. The QR algorithm: repeated ``Frame`` orthonormalizations of the Gram matrix
   converge to its eigenvectors, giving the SVD numerically in 3D.
3. The closed-form 2D SVD, ``rotation ∘ scale_non_uniform ∘ rotation⁻¹``, built from
   dot products, a wedge and rotations from vectors -- exact on a rational frame.
"""

import math
from collections.abc import Sequence

import pytest
import sympy

from gacalc import g2, g3
from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame
from gacalc.functions import InvertibleFunction, compose, inverse
from gacalc.transforms import projection_rotation, scale_non_uniform, versor_rotation

TOLERANCE: float = 1e-9


def dot(a: MultiVectorBase, b: MultiVectorBase) -> Real:
    """The dot product of two vectors, as a number."""
    return a.dot(b).scalar_part()


def q_factor(
    orthonormal: Sequence[MultiVectorBase],
    basis: Sequence[MultiVectorBase],
) -> list[InvertibleFunction[MultiVectorBase]]:
    """Q as rotations from vectors (plus an axis flip first when Q is left-handed).

    Each rotation turns the image of the next basis vector onto the next ``u_j``;
    it turns in a plane perpendicular to the ``u``'s already placed, so it leaves
    them alone.  The last basis vector then lands on ``±u_n``; ``-`` means Q is a
    reflection, so the list starts (runs first) with the flip of that axis.

    Returns:
        list[InvertibleFunction[MultiVectorBase]]: the parts, for ``compose``.
    """
    rotations: list[InvertibleFunction[MultiVectorBase]] = []
    e: MultiVectorBase
    u: MultiVectorBase
    for e, u in zip(basis[:-1], orthonormal[:-1]):
        placed: MultiVectorBase = compose(rotations)(e) if rotations else e
        if not placed.isclose(u, abs_tol=TOLERANCE):
            # projection_rotation, not versor_rotation: inverting a float 𝒢₃ versor
            # trips on the rounding residue in Ã * A
            # (tasks/inverse-float-versor-rounding.md)
            rotations.insert(
                0,
                InvertibleFunction(
                    projection_rotation(from_vector=placed, to_vector=u),
                    "",
                    projection_rotation(from_vector=u, to_vector=placed),
                    "",
                ),
            )
    last: MultiVectorBase = compose(rotations)(basis[-1]) if rotations else basis[-1]
    flips: list[Real] = [1] * (len(basis) - 1) + [
        1 if last.isclose(orthonormal[-1], abs_tol=TOLERANCE) else -1
    ]
    return [*rotations, scale_non_uniform(*flips)]


FRAMES_2D: list[tuple[g2.Vector, g2.Vector]] = [
    (2.0 * g2.e_1 + 1.0 * g2.e_2, 1.0 * g2.e_1 + 3.0 * g2.e_2),
    (2.0 * g2.e_1 + 1.0 * g2.e_2, 1.0 * g2.e_1 - 3.0 * g2.e_2),  # left-handed
]
FRAMES_3D: list[tuple[g3.Vector, g3.Vector, g3.Vector]] = [
    (
        2.0 * g3.e_1 + 1.0 * g3.e_2 + 0.5 * g3.e_3,
        0.5 * g3.e_1 + 3.0 * g3.e_2 + 1.0 * g3.e_3,
        1.0 * g3.e_1 + 0.25 * g3.e_2 + 2.0 * g3.e_3,
    ),
    (  # left-handed: the third vector swapped to the other side
        2.0 * g3.e_1 + 1.0 * g3.e_2 + 0.5 * g3.e_3,
        0.5 * g3.e_1 + 3.0 * g3.e_2 + 1.0 * g3.e_3,
        -1.0 * g3.e_1 - 0.25 * g3.e_2 - 2.0 * g3.e_3,
    ),
]


@pytest.mark.parametrize(
    ("vectors", "basis"),
    [(v, (g2.e_1, g2.e_2)) for v in FRAMES_2D]
    + [(v, (g3.e_1, g3.e_2, g3.e_3)) for v in FRAMES_3D],
)
def test_frame_is_rotation_after_shear_scale(
    vectors: tuple[MultiVectorBase, ...], basis: tuple[MultiVectorBase, ...]
) -> None:
    """Route 1: ``Frame.to_invertible_function() == Q ∘ R`` with Q from versors.

    ``v_i = Σ_j coefficients()[i][j] * w_j = Σ_j (coefficients()[i][j] * |w_j|) * u_j``,
    so R sends ``e_i`` to ``Σ_j coefficients()[i][j] * |w_j| * e_j`` (a triangular
    frame, so ``Frame`` builds it too) and Q sends ``e_j`` to ``u_j``.
    """
    frame: Frame = Frame(vectors)
    lengths: list[Real] = [w.magnitude() for w in frame.orthogonal_vectors()]
    r_columns: tuple[MultiVectorBase, ...] = tuple(
        sum(
            (c * length * e for c, length, e in zip(row, lengths, basis)),
            start=type(basis[0]).zero(),
        )
        for row in frame.coefficients()
    )
    shear_scale: InvertibleFunction[MultiVectorBase] = Frame(
        r_columns
    ).to_invertible_function()
    f: InvertibleFunction[MultiVectorBase] = compose(
        [*q_factor(frame.orthonormal_vectors(), basis), shear_scale]
    )
    e: MultiVectorBase
    v: MultiVectorBase
    for e, v in zip(basis, vectors):
        assert f(e).isclose(v, abs_tol=TOLERANCE)
    x: MultiVectorBase = sum(
        ((0.3 + i) * e for i, e in enumerate(basis)), start=type(basis[0]).zero()
    )
    assert f(x).isclose(frame.to_invertible_function()(x), abs_tol=TOLERANCE)


def test_qr_algorithm_gives_the_svd_in_3d() -> None:
    """Route 2: ``M ← R Q`` on the Gram matrix ``M_ij = v_i · v_j``, with each QR a
    ``Frame``, converges to ``M = diag(σ_i²)``; the accumulated ``Q``'s columns are
    the right singular vectors ``w_i``, so the ``f(w_i)`` are mutually
    perpendicular with lengths ``σ_i`` (``f(w_i) = σ_i * u_i``)."""
    vectors: tuple[g3.Vector, g3.Vector, g3.Vector] = FRAMES_3D[0]
    basis: tuple[g3.Vector, g3.Vector, g3.Vector] = (g3.e_1, g3.e_2, g3.e_3)
    f: InvertibleFunction[MultiVectorBase] = Frame(vectors).to_invertible_function()

    def columns(rows: Sequence[Sequence[Real]]) -> tuple[MultiVectorBase, ...]:
        """The column vectors ``Σ_i rows[i][j] * e_i`` of a 3×3 table."""
        return tuple(
            sum((rows[i][j] * basis[i] for i in range(3)), start=g3.Vector.zero())
            for j in range(3)
        )

    m: tuple[MultiVectorBase, ...] = columns(
        [[dot(a, b) for b in vectors] for a in vectors]
    )
    w: tuple[MultiVectorBase, ...] = basis
    _: int
    for _ in range(200):
        q: tuple[MultiVectorBase, ...] = Frame(m).orthonormal_vectors()
        # R = Qᵀ M is upper triangular; R Q has column j = Σ_k (u_j)_k * R column k
        r: tuple[MultiVectorBase, ...] = columns(
            [[dot(q[i], m[k]) for k in range(3)] for i in range(3)]
        )
        m = tuple(
            sum(
                (q_j.coefficient(e_k) * r_k for e_k, r_k in zip(basis, r)),
                start=g3.Vector.zero(),
            )
            for q_j in q
        )
        w = tuple(
            sum(
                (q_j.coefficient(e_k) * w_k for e_k, w_k in zip(basis, w)),
                start=g3.Vector.zero(),
            )
            for q_j in q
        )
    images: list[MultiVectorBase] = [f(w_i) for w_i in w]
    i: int
    j: int
    for i in range(3):
        assert math.isclose(float(w[i].magnitude()), 1.0, abs_tol=TOLERANCE)
        assert math.isclose(
            float(images[i].magnitude()) ** 2,
            float(m[i].coefficient(basis[i])),
            rel_tol=1e-9,
        )
        for j in range(i + 1, 3):
            assert abs(float(dot(w[i], w[j]))) < TOLERANCE
            assert abs(float(dot(images[i], images[j]))) < 1e-7


def svd_2d(
    v_1: g2.Vector, v_2: g2.Vector
) -> tuple[list[InvertibleFunction[MultiVectorBase]], Real, Real, g2.Vector]:
    """The closed-form 2D SVD of the frame map ``e_i ↦ v_i``.

    The squared singular values are the eigenvalues of the Gram matrix
    ``[[v_1·v_1, v_1·v_2], [v_1·v_2, v_2·v_2]]``: their sum is
    ``|v_1|² + |v_2|²`` and their product is ``|v_1 ∧ v_2|²``.  An eigenvector for
    the larger one is ``w_1 ∝ (g_12, λ_1 − g_11)``.

    Returns:
        tuple: ``U``'s parts (rotations from vectors, with an axis flip when the
        frame is left-handed), ``σ_1``, ``σ_2``, and the unit ``w_1``.
    """
    g_11: Real = dot(v_1, v_1)
    g_12: Real = dot(v_1, v_2)
    g_22: Real = dot(v_2, v_2)
    area_squared: Real = (v_1 ^ v_2).magnitude_squared()
    half_trace: Real = (g_11 + g_22) / 2
    root: Real = sympy.sqrt(half_trace**2 - area_squared)
    λ_1: Real = half_trace + root
    λ_2: Real = half_trace - root
    w_1: g2.Vector = (
        g2.Scalar(g_12) * g2.e_1 + g2.Scalar(λ_1 - g_11) * g2.e_2
    ).normalize()
    w_2: g2.Vector = w_1.rotate_90_degrees()
    σ_1: Real = sympy.sqrt(λ_1)
    σ_2: Real = sympy.sqrt(λ_2)
    f: InvertibleFunction[MultiVectorBase] = Frame((v_1, v_2)).to_invertible_function()
    u: list[MultiVectorBase] = [f(w_1) / σ_1, f(w_2) / σ_2]
    return q_factor(u, (g2.e_1, g2.e_2)), σ_1, σ_2, w_1


def test_closed_form_2d_svd_is_exact() -> None:
    """Route 3, exact: a frame built as ``U Σ Wᵀ`` from Pythagorean rotations
    (``σ = 5, 2``) is taken apart again, and ``U ∘ Σ ∘ W⁻¹`` equals the frame map
    exactly (sympy rationals, no floats)."""
    c: sympy.Rational = sympy.Rational(3, 5)
    s: sympy.Rational = sympy.Rational(4, 5)
    # U turns by (3/5, 4/5), W by (5/13, 12/13); v_i = U Σ Wᵀ e_i
    w_cos: sympy.Rational = sympy.Rational(5, 13)
    w_sin: sympy.Rational = sympy.Rational(12, 13)
    u_1: g2.Vector = g2.Scalar(c) * g2.e_1 + g2.Scalar(s) * g2.e_2
    u_2: g2.Vector = u_1.rotate_90_degrees()
    v_1: g2.Vector = g2.Scalar(5 * w_cos) * u_1 - g2.Scalar(2 * w_sin) * u_2
    v_2: g2.Vector = g2.Scalar(5 * w_sin) * u_1 + g2.Scalar(2 * w_cos) * u_2
    u_parts: list[InvertibleFunction[MultiVectorBase]]
    σ_1: Real
    σ_2: Real
    w_1: g2.Vector
    u_parts, σ_1, σ_2, w_1 = svd_2d(v_1, v_2)
    assert (σ_1, σ_2) == (5, 2)
    w: InvertibleFunction[MultiVectorBase] = versor_rotation(
        from_vector=g2.e_1, to_vector=w_1
    )
    svd: InvertibleFunction[MultiVectorBase] = compose(
        [*u_parts, scale_non_uniform(σ_1, σ_2), inverse(w)]
    )
    f: InvertibleFunction[MultiVectorBase] = Frame((v_1, v_2)).to_invertible_function()
    e: g2.Vector
    for e in (g2.e_1, g2.e_2):
        difference: MultiVectorBase = svd(e) - f(e)
        assert all(sympy.simplify(coefficient) == 0 for coefficient in difference)
