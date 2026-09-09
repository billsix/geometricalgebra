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

"""Compile-once matrix templates (``to_matrix_template`` / ``MatrixTemplate``).

The contract under test: a template compiled from a transform built over sympy
symbols, filled with numbers, equals ``to_matrix(backend="numpy")`` of the same
transform built directly over those numbers -- **bit-identical** when every
varying entry is a bare parameter (slots are plain copies), ``allclose`` when
an entry is an expression (a symbolic rotation angle -> ``cos``/``sin``, one
lambdified call per fill).  Covered in all four shapes the maintainer asked for:
𝒢₂ linear and affine (3 x 3), 𝒢₃ linear and affine (4 x 4) -- plus ``Gn`` with
an explicit ``n`` -- and the error paths.
"""

import math
import random
import typing

import numpy as np
import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
import gacalc.gn as gn
from gacalc.base import MultiVectorBase
from gacalc.gn import Gn
from gacalc.transforms import (
    ComposableFunction,
    InvertibleFunction,
    Linearity,
    MatrixTemplate,
    compose,
    plane_rotation,
    scale_non_uniform,
    to_matrix,
    to_matrix_template,
    translate,
    uniform_scale,
)

TX, TY, TZ, W, H, D, S, THETA = sympy.symbols("tx ty tz w h d s theta")

# the random parameter sets every "equals to_matrix" test is run over -- a
# seeded generator for reproducible test inputs, not for anything secret
_rng = random.Random(20260906)  # noqa: S311
SAMPLES: list[tuple[float, ...]] = [
    tuple(_rng.uniform(-100.0, 100.0) for _ in range(4)) for _ in range(25)
]


def numeric(m: "np.ndarray | sympy.Matrix") -> np.ndarray:
    """Narrow ``to_matrix``'s union return for the numpy backend."""
    assert isinstance(m, np.ndarray)
    return m


# ---------------------------------------------------------------------------
# 𝒢₂ (3 x 3)
# ---------------------------------------------------------------------------


def test_g2_linear_scale_is_3x3_with_zero_translation_column() -> None:
    t: MatrixTemplate = to_matrix_template(scale_non_uniform(W, H), g2.Vector, (W, H))
    assert t.shape == (3, 3)
    assert t.constants.dtype == np.float32
    assert t.expressions == ()
    assert set(t.slots) == {(0, 0, 0), (1, 1, 1)}
    m: np.ndarray = t.fill(3.0, 5.0)
    assert m.dtype == np.float32
    assert np.array_equal(m[:, 2], np.array([0.0, 0.0, 1.0], dtype=np.float32))
    assert np.array_equal(m, numeric(to_matrix(scale_non_uniform(3.0, 5.0), g2.Vector)))


def test_g2_linear_quarter_turn_has_no_parameters() -> None:
    t: MatrixTemplate = to_matrix_template(g2.rotate_90_degrees(), g2.Vector, ())
    assert t.params == () and t.slots == () and t.expressions == ()
    m: np.ndarray = t.fill()
    assert np.array_equal(m, numeric(to_matrix(g2.rotate_90_degrees(), g2.Vector)))
    # (x, y) -> (-y, x): column 0 is e_2, column 1 is -e_1
    assert np.array_equal(m[:, 0], np.array([0.0, 1.0, 0.0], dtype=np.float32))
    assert np.array_equal(m[:, 1], np.array([-1.0, 0.0, 0.0], dtype=np.float32))


def test_g2_affine_translate_scale_is_bit_identical_to_to_matrix() -> None:
    fn: InvertibleFunction[g2.Vector] = translate(
        b=TX * g2.Vector.e_1 + TY * g2.Vector.e_2
    ) @ scale_non_uniform(W, H)
    t: MatrixTemplate = to_matrix_template(fn, g2.Vector, (TX, TY, W, H))
    assert t.shape == (3, 3)
    assert t.expressions == ()  # every varying entry is a bare symbol
    assert set(t.slots) == {(0, 2, 0), (1, 2, 1), (0, 0, 2), (1, 1, 3)}
    tx: float
    ty: float
    w: float
    h: float
    for tx, ty, w, h in SAMPLES + [(0.0, 0.0, 0.0, 0.0), (1.5, -2.5, 0.0, 7.0)]:
        direct: InvertibleFunction[g2.Vector] = compose(
            [
                translate(b=tx * g2.Vector.e_1 + ty * g2.Vector.e_2),
                scale_non_uniform(w, h),
            ]
        )
        assert np.array_equal(
            t.fill(tx, ty, w, h), numeric(to_matrix(direct, g2.Vector))
        )


def test_g2_affine_rotation_and_translation_uses_expression_entries() -> None:
    fn: ComposableFunction[g2.Vector] = compose(
        [
            translate(b=TX * g2.Vector.e_1 + TY * g2.Vector.e_2),
            plane_rotation(g2.e_1, g2.e_2)(THETA),
        ]
    )
    t: MatrixTemplate = to_matrix_template(fn, g2.Vector, (TX, TY, THETA))
    assert t.shape == (3, 3)
    # the translation column is bare symbols; the 2 x 2 rotation block is cos/sin
    assert set(t.slots) == {(0, 2, 0), (1, 2, 1)}
    assert set(t.expression_cells) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    assert t.evaluate_expressions is not None
    tx: float
    ty: float
    theta: float
    for tx, ty, theta, _ in SAMPLES:
        direct: ComposableFunction[g2.Vector] = compose(
            [
                translate(b=tx * g2.Vector.e_1 + ty * g2.Vector.e_2),
                plane_rotation(g2.e_1, g2.e_2)(theta),
            ]
        )
        assert np.allclose(
            t.fill(tx, ty, theta), numeric(to_matrix(direct, g2.Vector)), atol=1e-5
        )
    # and the block really is a rotation: theta = pi/2 is the quarter turn
    m: np.ndarray = t.fill(0.0, 0.0, math.pi / 2)
    assert np.allclose(
        m, numeric(to_matrix(g2.rotate_90_degrees(), g2.Vector)), atol=1e-6
    )


# ---------------------------------------------------------------------------
# 𝒢₃ (4 x 4)
# ---------------------------------------------------------------------------


def test_g3_linear_scale_is_4x4_diagonal() -> None:
    t: MatrixTemplate = to_matrix_template(
        scale_non_uniform(W, H, D), g3.Vector, (W, H, D)
    )
    assert t.shape == (4, 4)
    assert set(t.slots) == {(0, 0, 0), (1, 1, 1), (2, 2, 2)}
    m: np.ndarray = t.fill(2.0, 3.0, 4.0)
    assert np.array_equal(m, np.diag([2.0, 3.0, 4.0, 1.0]).astype(np.float32))
    assert np.array_equal(
        m, numeric(to_matrix(scale_non_uniform(2.0, 3.0, 4.0), g3.Vector))
    )


def test_g3_linear_rotation_about_e2_matches_to_matrix() -> None:
    fn: InvertibleFunction[g3.Vector] = plane_rotation(g3.e_3, g3.e_1)(THETA)
    t: MatrixTemplate = to_matrix_template(fn, g3.Vector, (THETA,))
    assert t.shape == (4, 4)
    assert t.slots == ()
    theta: float
    for _, _, theta, _ in SAMPLES:
        assert np.allclose(
            t.fill(theta),
            numeric(to_matrix(plane_rotation(g3.e_3, g3.e_1)(theta), g3.Vector)),
            atol=1e-5,
        )
    # linear: zero translation column, fixed bottom row
    m: np.ndarray = t.fill(0.7)
    assert np.array_equal(m[:, 3], np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32))
    assert np.array_equal(m[3, :], np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32))


def test_g3_affine_sprite_model_matrix_is_bit_identical_to_to_matrix() -> None:
    # the consumer's case: scale the unit quad to (w, h), translate to (tx, ty)
    fn: InvertibleFunction[g3.Vector] = compose(
        [
            translate(b=TX * g3.Vector.e_1 + TY * g3.Vector.e_2),
            scale_non_uniform(W, H, 1),
        ]
    )
    t: MatrixTemplate = to_matrix_template(fn, g3.Vector, (TX, TY, W, H))
    assert t.shape == (4, 4)
    assert t.expressions == ()
    assert set(t.slots) == {(0, 3, 0), (1, 3, 1), (0, 0, 2), (1, 1, 3)}
    assert float(t.constants[2, 2]) == 1.0 and float(t.constants[3, 3]) == 1.0
    tx: float
    ty: float
    w: float
    h: float
    for tx, ty, w, h in SAMPLES + [(0.0, 0.0, 0.0, 0.0)]:
        direct: InvertibleFunction[g3.Vector] = compose(
            [
                translate(b=tx * g3.Vector.e_1 + ty * g3.Vector.e_2),
                scale_non_uniform(w, h, 1),
            ]
        )
        assert np.array_equal(
            t.fill(tx, ty, w, h), numeric(to_matrix(direct, g3.Vector))
        )


def test_g3_affine_rotation_and_translation_4x4() -> None:
    fn: ComposableFunction[g3.Vector] = compose(
        [
            translate(b=TX * g3.Vector.e_1 + TY * g3.Vector.e_2 + TZ * g3.Vector.e_3),
            plane_rotation(g3.e_1, g3.e_2)(THETA),
        ]
    )
    t: MatrixTemplate = to_matrix_template(fn, g3.Vector, (TX, TY, TZ, THETA))
    assert t.shape == (4, 4)
    assert set(t.slots) == {(0, 3, 0), (1, 3, 1), (2, 3, 2)}
    assert set(t.expression_cells) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    tx: float
    ty: float
    tz: float
    theta: float
    for tx, ty, tz, theta in SAMPLES:
        direct: ComposableFunction[g3.Vector] = compose(
            [
                translate(
                    b=tx * g3.Vector.e_1 + ty * g3.Vector.e_2 + tz * g3.Vector.e_3
                ),
                plane_rotation(g3.e_1, g3.e_2)(theta),
            ]
        )
        assert np.allclose(
            t.fill(tx, ty, tz, theta), numeric(to_matrix(direct, g3.Vector)), atol=1e-5
        )


def test_g3_uniform_scale_then_translate_composes_like_matrices() -> None:
    fn: InvertibleFunction[g3.Vector] = translate(b=TX * g3.Vector.e_1) @ uniform_scale(
        S
    )
    t: MatrixTemplate = to_matrix_template(fn, g3.Vector, (TX, S))
    a: MatrixTemplate = to_matrix_template(
        translate(b=TX * g3.Vector.e_1), g3.Vector, (TX,)
    )
    b: MatrixTemplate = to_matrix_template(uniform_scale(S), g3.Vector, (S,))
    tx: float
    s: float
    for tx, s, _, _ in SAMPLES:
        assert np.allclose(t.fill(tx, s), a.fill(tx) @ b.fill(s), atol=1e-4)


# ---------------------------------------------------------------------------
# Gn, the method forms, and the fill contract
# ---------------------------------------------------------------------------


def test_gn_with_explicit_n() -> None:
    fn: InvertibleFunction[Gn] = translate(
        b=TX * gn.e_1 + TY * gn.e_2
    ) @ scale_non_uniform(W, H)
    t: MatrixTemplate = to_matrix_template(fn, Gn, (TX, TY, W, H), n=2)
    assert t.shape == (3, 3)
    tx: float
    ty: float
    w: float
    h: float
    for tx, ty, w, h in SAMPLES[:5]:
        direct: InvertibleFunction[Gn] = translate(
            b=tx * gn.e_1 + ty * gn.e_2
        ) @ scale_non_uniform(w, h)
        assert np.array_equal(t.fill(tx, ty, w, h), numeric(to_matrix(direct, Gn, n=2)))


def test_gn_requires_explicit_n() -> None:
    with pytest.raises(ValueError, match="pass n explicitly"):
        to_matrix_template(uniform_scale(S), Gn, (S,))


def test_method_form_equals_free_function() -> None:
    fn: InvertibleFunction[g3.Vector] = compose(
        [
            translate(b=TX * g3.Vector.e_1 + TY * g3.Vector.e_2),
            scale_non_uniform(W, H, 1),
        ]
    )
    via_method: MatrixTemplate = fn.to_matrix_template(g3.Vector, (TX, TY, W, H))
    via_function: MatrixTemplate = to_matrix_template(fn, g3.Vector, (TX, TY, W, H))
    assert isinstance(via_method, MatrixTemplate)
    assert via_method.params == via_function.params
    assert via_method.slots == via_function.slots
    assert np.array_equal(via_method.constants, via_function.constants)
    tx: float
    ty: float
    w: float
    h: float
    for tx, ty, w, h in SAMPLES[:5]:
        assert np.array_equal(
            via_method.fill(tx, ty, w, h), via_function.fill(tx, ty, w, h)
        )


def test_to_matrix_method_form() -> None:
    fn: InvertibleFunction[g3.Vector] = translate(
        b=2 * g3.Vector.e_1 + 3 * g3.Vector.e_2 + 4 * g3.Vector.e_3
    )
    assert np.array_equal(
        numeric(fn.to_matrix(g3.Vector)), numeric(to_matrix(fn, g3.Vector))
    )
    sym: sympy.Matrix | np.ndarray = fn.to_matrix(g3.Vector, backend="sympy")
    assert isinstance(sym, sympy.Matrix)
    assert [sym[i, 3] for i in range(4)] == [2, 3, 4, 1]


def test_to_matrix_accepts_a_plain_composable_function() -> None:
    # a hand-built linear ComposableFunction (no inverse) is still matrix-able
    double: ComposableFunction[MultiVectorBase] = ComposableFunction(
        lambda x: 2 * x, "D", linearity=Linearity.LINEAR
    )
    m = numeric(to_matrix(double, g2.Vector))
    assert np.array_equal(m, np.diag([2.0, 2.0, 1.0]).astype(np.float32))
    t: MatrixTemplate = to_matrix_template(double, g2.Vector, ())
    assert np.array_equal(t.fill(), m)


def test_fill_returns_a_fresh_array_each_call() -> None:
    t: MatrixTemplate = to_matrix_template(uniform_scale(S), g2.Vector, (S,))
    a: np.ndarray = t.fill(2.0)
    a[0, 0] = 99.0
    assert float(t.fill(2.0)[0, 0]) == 2.0
    assert float(t.constants[0, 0]) == 0.0  # the template itself is untouched


def test_call_is_fill() -> None:
    t: MatrixTemplate = to_matrix_template(uniform_scale(S), g2.Vector, (S,))
    assert np.array_equal(t(2.5), t.fill(2.5))


def test_params_order_fixes_fill_argument_order() -> None:
    fn: InvertibleFunction[g2.Vector] = scale_non_uniform(W, H)
    wh: MatrixTemplate = to_matrix_template(fn, g2.Vector, (W, H))
    hw: MatrixTemplate = to_matrix_template(fn, g2.Vector, (H, W))
    assert np.array_equal(wh.fill(3.0, 5.0), hw.fill(5.0, 3.0))
    assert not np.array_equal(wh.fill(3.0, 5.0), hw.fill(3.0, 5.0))


def test_unused_parameter_is_ignored() -> None:
    t: MatrixTemplate = to_matrix_template(uniform_scale(S), g2.Vector, (S, THETA))
    assert t.params == (S, THETA)
    assert np.array_equal(
        t.fill(2.0, 123.0), numeric(to_matrix(uniform_scale(2.0), g2.Vector))
    )


def test_integer_and_symbolic_free_values_fill_as_floats() -> None:
    t: MatrixTemplate = to_matrix_template(uniform_scale(S), g2.Vector, (S,))
    m: np.ndarray = t.fill(2)
    assert m.dtype == np.float32 and float(m[0, 0]) == 2.0


def test_frozen() -> None:
    t: MatrixTemplate = to_matrix_template(uniform_scale(S), g2.Vector, (S,))
    with pytest.raises(dataclasses_frozen_error()):
        t.slots = ()  # ty: ignore[invalid-assignment]


def dataclasses_frozen_error() -> type[Exception]:
    import dataclasses

    return dataclasses.FrozenInstanceError


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------


def test_missing_parameter_is_a_value_error_naming_the_symbol() -> None:
    fn: InvertibleFunction[g2.Vector] = translate(
        b=TX * g2.Vector.e_1 + TY * g2.Vector.e_2
    )
    with pytest.raises(ValueError, match=r"depends on \['ty'\]"):
        to_matrix_template(fn, g2.Vector, (TX,))


def test_repeated_parameter_is_a_value_error() -> None:
    with pytest.raises(ValueError, match="repeated symbol"):
        to_matrix_template(uniform_scale(S), g2.Vector, (S, S))


def test_nonlinear_is_a_value_error() -> None:
    perspective: InvertibleFunction[typing.Any] = InvertibleFunction(
        func=lambda v: v, latex_repr="P", inverse=lambda v: v, latex_repr_inv="P^-1"
    )  # linearity defaults to NONLINEAR
    with pytest.raises(ValueError, match="linear/affine functions only"):
        to_matrix_template(perspective, g3.Vector, ())


def test_wrong_fill_arity_is_a_type_error() -> None:
    t: MatrixTemplate = to_matrix_template(scale_non_uniform(W, H), g2.Vector, (W, H))
    with pytest.raises(TypeError, match=r"takes 2 values \(w, h\); got 1"):
        t.fill(3.0)
    with pytest.raises(TypeError, match="got 3"):
        t.fill(1.0, 2.0, 3.0)
