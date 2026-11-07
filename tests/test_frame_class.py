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

"""The ``Frame`` dataclass (``gacalc.frame.Frame``) and its ``InvertibleFunction``.

A ``Frame`` holds a frame ``v_1 … v_k`` together with its orthogonal set
``w_1 … w_k``; ``coefficients()`` gives ``coefficients()[i][j] = (w_j · v_i) / |w_j|²``
with ``v_i = Σ_j coefficients()[i][j] * w_j`` -- the QR decomposition with the
lengths factored out (``tasks/reference/frames-qr-and-reciprocal-frames.md``).

The symbolic tests use fully general frames (every component its own symbol) on
``Gn``, whose eager simplification keeps the 3D expressions small enough for sympy
to decide equality exactly; the 3D symbolic frame takes on the order of a minute
to build, so it is built once per module.  Concrete oblique frames exercise the
graded ``g2``/``g3`` types.
"""

import math
from collections.abc import Sequence

import numpy as np
import pytest
import sympy

from gacalc import g2, g3
from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame, prefix_blades
from gacalc.functions import InvertibleFunction, Linearity, inverse
from gacalc.gn import Gn, e_1, e_2, e_3
from gacalc.transforms import to_matrix


def general_vector(name: str, n: int) -> Gn:
    """A fully symbolic vector ``name_1 * e_1 + … + name_n * e_n`` in ``Gn``."""
    components: tuple[sympy.Symbol, ...] = sympy.symbols(
        " ".join(f"{name}_{i}" for i in range(1, n + 1))
    )
    basis: tuple[Gn, ...] = (e_1, e_2, e_3)[:n]
    return sum((s * e for s, e in zip(components, basis, strict=True)), start=Gn.zero())


def is_zero(value: Real) -> bool:
    """Exact symbolic zero test (``simplify(value) == 0``)."""
    return sympy.simplify(sympy.sympify(value)) == 0


# --- Fixtures: general symbolic frames, built once --------------------------

a_2d: Gn = general_vector("a", 2)
b_2d: Gn = general_vector("b", 2)
x_2d: Gn = general_vector("x", 2)


@pytest.fixture(scope="module")
def frame_2d() -> Frame:
    return Frame([a_2d, b_2d])


a_3d: Gn = general_vector("a", 3)
b_3d: Gn = general_vector("b", 3)
c_3d: Gn = general_vector("c", 3)
x_3d: Gn = general_vector("x", 3)


@pytest.fixture(scope="module")
def frame_3d() -> Frame:
    return Frame([a_3d, b_3d, c_3d])


@pytest.fixture(scope="module")
def function_3d(frame_3d: Frame) -> InvertibleFunction[MultiVectorBase]:
    return frame_3d.to_invertible_function()


# coefficients() is computed on each call (about a minute for the 3D symbolic
# frame), so the tests that read it share one computation per frame.
@pytest.fixture(scope="module")
def frame_2d_coefficients(frame_2d: Frame) -> tuple[tuple[Real, ...], ...]:
    return frame_2d.coefficients()


@pytest.fixture(scope="module")
def frame_3d_coefficients(frame_3d: Frame) -> tuple[tuple[Real, ...], ...]:
    return frame_3d.coefficients()


# --- The representation: orthogonal set + triangular coefficients ---------


@pytest.mark.parametrize("frame_name", ["frame_2d", "frame_3d"])
def test_orthogonal_vectors_are_mutually_orthogonal(
    frame_name: str, request: pytest.FixtureRequest
) -> None:
    frame: Frame = request.getfixturevalue(frame_name)
    w_list: tuple[MultiVectorBase, ...] = frame.orthogonal_vectors
    assert all(
        is_zero(w_list[i].dot(w_list[j]).scalar_part())
        for i in range(len(w_list))
        for j in range(i + 1, len(w_list))
    )


@pytest.mark.parametrize("frame_name", ["frame_2d", "frame_3d"])
def test_coefficients_are_triangular_with_unit_diagonal(
    frame_name: str, request: pytest.FixtureRequest
) -> None:
    """``v_i`` uses only ``w_1 … w_i`` (zeros above), and exactly one ``w_i``."""
    frame: Frame = request.getfixturevalue(frame_name)
    coefficients: tuple[tuple[Real, ...], ...] = request.getfixturevalue(
        f"{frame_name}_coefficients"
    )
    k: int = len(frame)
    assert all(is_zero(coefficients[i][j]) for i in range(k) for j in range(i + 1, k))
    assert all(is_zero(coefficients[i][i] - 1) for i in range(k))


@pytest.mark.parametrize("frame_name", ["frame_2d", "frame_3d"])
def test_coefficients_rebuild_the_vectors(
    frame_name: str, request: pytest.FixtureRequest
) -> None:
    """``v_i = Σ_j coefficients()[i][j] * w_j`` -- the coefficients are QR's ``R``."""
    frame: Frame = request.getfixturevalue(frame_name)
    coefficients: tuple[tuple[Real, ...], ...] = request.getfixturevalue(
        f"{frame_name}_coefficients"
    )
    rebuilt: list[MultiVectorBase] = [
        sum(
            (c * w for c, w in zip(row, frame.orthogonal_vectors, strict=True)),
            start=Gn.zero(),
        )
        for row in coefficients
    ]
    assert rebuilt == list(frame.vectors)


@pytest.mark.parametrize(
    ("frame_name", "vectors"),
    [("frame_2d", [a_2d, b_2d]), ("frame_3d", [a_3d, b_3d, c_3d])],
)
def test_iter_yields_the_original_vectors(
    frame_name: str, vectors: Sequence[Gn], request: pytest.FixtureRequest
) -> None:
    frame: Frame = request.getfixturevalue(frame_name)
    assert list(frame) == vectors
    assert len(frame) == len(vectors)


@pytest.mark.parametrize(
    ("frame_name", "vectors"),
    [("frame_2d", [a_2d, b_2d]), ("frame_3d", [a_3d, b_3d, c_3d])],
)
def test_squared_lengths_are_ratios_of_span_volumes(
    frame_name: str, vectors: Sequence[Gn], request: pytest.FixtureRequest
) -> None:
    """``|w_i|² = |A_i|² / |A_{i-1}|²`` with ``A_i = v_1 ∧ … ∧ v_i`` (H&S eq 3.1),
    so the product of the ``|w_i|²`` is the squared volume ``|v_1 ∧ … ∧ v_k|²``."""
    frame: Frame = request.getfixturevalue(frame_name)
    A_list: list[MultiVectorBase] = list(prefix_blades(vectors))
    assert all(
        is_zero(
            w.magnitude_squared() * A_list[i].magnitude_squared()
            - A_list[i + 1].magnitude_squared()
        )
        for i, w in enumerate(frame.orthogonal_vectors)
    )
    assert is_zero(
        math.prod(w.magnitude_squared() for w in frame.orthogonal_vectors)
        - A_list[-1].magnitude_squared()
    )


def test_orthonormal_vectors_2d_symbolic(frame_2d: Frame) -> None:
    u_list: tuple[MultiVectorBase, ...] = frame_2d.orthonormal_vectors()
    assert all(is_zero(u.magnitude_squared() - 1) for u in u_list)
    assert is_zero(u_list[0].dot(u_list[1]).scalar_part())


def test_concrete_oblique_frames_on_graded_types() -> None:
    """The graded ``g2.Vector`` / ``g3.Vector`` types, exact integer input."""
    vectors_2d: list[g2.Vector] = [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2]
    frame_2d: Frame = Frame(vectors_2d)
    assert frame_2d.orthogonal_vectors == (
        2 * g2.e_1 + 0 * g2.e_2,
        0 * g2.e_1 + 3 * g2.e_2,
    )
    assert frame_2d.coefficients() == ((1, 0), (sympy.Rational(1, 2), 1))
    assert list(frame_2d) == vectors_2d
    vectors_3d: list[g3.Vector] = [
        2 * g3.e_1 + 0 * g3.e_2 + 1 * g3.e_3,
        1 * g3.e_1 + 3 * g3.e_2 + 0 * g3.e_3,
        1 * g3.e_1 + 1 * g3.e_2 + 4 * g3.e_3,
    ]
    assert list(Frame(vectors_3d)) == vectors_3d


def test_non_frame_raises() -> None:
    with pytest.raises(ValueError):
        Frame([1 * e_1, 2 * e_1])  # parallel
    with pytest.raises(ValueError):
        Frame([1 * e_1, 1 * e_2, 1 * e_1 + 1 * e_2])  # third in the span
    with pytest.raises(ValueError):
        Frame([])


# --- to_invertible_function --------------------------------------------------


def test_forward_sends_basis_to_frame_2d(frame_2d: Frame) -> None:
    f: InvertibleFunction[MultiVectorBase] = frame_2d.to_invertible_function()
    assert f(1 * e_1) == a_2d
    assert f(1 * e_2) == b_2d
    assert f.linearity == Linearity.LINEAR


def test_forward_sends_basis_to_frame_3d(
    function_3d: InvertibleFunction[MultiVectorBase],
) -> None:
    assert [function_3d(e) for e in (1 * e_1, 1 * e_2, 1 * e_3)] == [a_3d, b_3d, c_3d]


def test_composed_round_trip_is_identity_2d_symbolic(frame_2d: Frame) -> None:
    """``(f⁻¹ ∘ f)(x) == x`` and ``(f ∘ f⁻¹)(x) == x`` for a symbolic ``x``, composed
    with the library's ``@`` (the maintainer's requirement, 2026-11-04)."""
    f: InvertibleFunction[MultiVectorBase] = frame_2d.to_invertible_function()
    assert (inverse(f) @ f)(x_2d) == x_2d
    assert (f @ inverse(f))(x_2d) == x_2d


def test_composed_round_trip_is_identity_3d_symbolic(
    function_3d: InvertibleFunction[MultiVectorBase],
) -> None:
    assert (inverse(function_3d) @ function_3d)(x_3d) == x_3d
    assert (function_3d @ inverse(function_3d))(x_3d) == x_3d


def test_composed_round_trip_concrete_frames_symbolic_input() -> None:
    """A concrete oblique frame with a symbolic input, on the graded types."""
    x_1, x_2, x_3 = sympy.symbols("x_1 x_2 x_3")
    x_2d_graded: g2.Vector = x_1 * g2.e_1 + x_2 * g2.e_2
    f_2d: InvertibleFunction[MultiVectorBase] = Frame(
        [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2]
    ).to_invertible_function()
    assert (inverse(f_2d) @ f_2d)(x_2d_graded) == x_2d_graded
    assert (f_2d @ inverse(f_2d))(x_2d_graded) == x_2d_graded
    x_3d_graded: g3.Vector = x_1 * g3.e_1 + x_2 * g3.e_2 + x_3 * g3.e_3
    f_3d: InvertibleFunction[MultiVectorBase] = Frame(
        [
            2 * g3.e_1 + 0 * g3.e_2 + 1 * g3.e_3,
            1 * g3.e_1 + 3 * g3.e_2 + 0 * g3.e_3,
            1 * g3.e_1 + 1 * g3.e_2 + 4 * g3.e_3,
        ]
    ).to_invertible_function()
    assert (inverse(f_3d) @ f_3d)(x_3d_graded) == x_3d_graded
    assert (f_3d @ inverse(f_3d))(x_3d_graded) == x_3d_graded


def test_round_trip_numeric_float() -> None:
    """Float input: equal up to rounding (inexactness accepted, 2026-11-04)."""
    f: InvertibleFunction[MultiVectorBase] = Frame(
        [
            2.0 * g3.e_1 + 0.5 * g3.e_2 + 1.0 * g3.e_3,
            1.0 * g3.e_1 + 3.0 * g3.e_2 + 0.0 * g3.e_3,
            1.0 * g3.e_1 + 1.0 * g3.e_2 + 4.0 * g3.e_3,
        ]
    ).to_invertible_function()
    x: g3.Vector = 0.3 * g3.e_1 - 1.7 * g3.e_2 + 2.2 * g3.e_3
    assert inverse(f)(f(x)).isclose(x, abs_tol=1e-12)


def test_matrix_columns_are_the_frame_vectors_2d(frame_2d: Frame) -> None:
    f: InvertibleFunction[MultiVectorBase] = frame_2d.to_invertible_function()
    matrix: sympy.Matrix | np.ndarray = to_matrix(f, Gn, n=2, backend="sympy")
    assert all(
        is_zero(matrix[row, column] - v.coefficient(basis))
        for column, v in enumerate([a_2d, b_2d])
        for row, basis in enumerate([e_1, e_2])
    )


def test_reciprocal_vectors_are_the_inverse_coordinates_2d_symbolic(
    frame_2d: Frame,
) -> None:
    """The reciprocal frame and the peel inverse give the same coordinates: the
    inverse's ``x_i`` is ``vⁱ · y``
    (``tasks/reference/frames-qr-and-reciprocal-frames.md``)."""
    y: MultiVectorBase = frame_2d.to_invertible_function()(x_2d)
    coordinates: MultiVectorBase = sum(
        (
            v_upper.dot(y).scalar_part() * e
            for v_upper, e in zip(
                frame_2d.reciprocal_vectors(), (e_1, e_2), strict=True
            )
        ),
        start=Gn.zero(),
    )
    peeled: MultiVectorBase = frame_2d.to_invertible_function().inverse(y)
    assert all(is_zero(c) for c in (coordinates - peeled).to_blade_dict().values())
    assert all(is_zero(c) for c in (coordinates - x_2d).to_blade_dict().values())


def test_reciprocal_vectors_are_the_inverse_coordinates_3d_symbolic(
    frame_3d: Frame, function_3d: InvertibleFunction[MultiVectorBase]
) -> None:
    """3D: the peel inverse's coordinates equal the dot products with the reciprocal
    frame, for a general symbolic frame and a general symbolic vector."""
    y: MultiVectorBase = function_3d(x_3d)
    coordinates: MultiVectorBase = sum(
        (
            v_upper.dot(y).scalar_part() * e
            for v_upper, e in zip(
                frame_3d.reciprocal_vectors(), (e_1, e_2, e_3), strict=True
            )
        ),
        start=Gn.zero(),
    )
    peeled: MultiVectorBase = function_3d.inverse(y)
    assert all(is_zero(c) for c in (coordinates - peeled).to_blade_dict().values())


def test_frame_smaller_than_space_raises() -> None:
    """``k < n``: the forward map would drop components, so no inverse."""
    with pytest.raises(ValueError):
        Frame([1 * g3.e_1 + 0 * g3.e_2 + 0 * g3.e_3]).to_invertible_function()
    with pytest.raises(ValueError):
        Frame([1 * e_1, 1 * e_3]).to_invertible_function()  # Gn: highest index is 3


def test_map_rejects_a_non_vector() -> None:
    """The frame's map and its inverse are defined on vectors only: a bivector or a
    scalar raises ``ValueError`` in either direction."""
    f: InvertibleFunction[MultiVectorBase] = Frame(
        [2 * g2.e_1 + 0 * g2.e_2, 1 * g2.e_1 + 3 * g2.e_2]
    ).to_invertible_function()
    non_vector: MultiVectorBase
    for non_vector in (g2.e_1 ^ g2.e_2, g2.G.from_real(3)):
        with pytest.raises(ValueError):
            f(non_vector)
        with pytest.raises(ValueError):
            f.inverse(non_vector)
