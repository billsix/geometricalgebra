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

"""Transform-layer tests: representation-preserving (type round-trip) + values.

The factories in ``gacalc.transforms`` derive any basis vectors they
need from the *type of the value* (``cls.basis_vector(i)``), so a G1/G2/G3/Gn
value in yields the **same concrete type** out.  These tests pin that, plus a few
known values, invertibility, and the non-invertible error paths.

Equality on the specialized classes is simplify-aware, but these use numeric
coefficients, so ``is_close`` (float-tolerant) is the right comparison.
"""

import math
import typing

import numpy as np
import pytest
import sympy

from gacalc.base import MultiVectorBase, MultiVectorFn
from gacalc.g1 import G1
from gacalc.g2 import G2, Vector2
from gacalc.g3 import G3, Vector3
from gacalc.gn import Gn
from gacalc.transforms import (
    ComposableFunction,
    InvertibleFunction,
    Linearity,
    NotInvertibleError,
    compose,
    identity,
    inverse,
    projection_rotation,
    rotor_rotation,
    scale_non_uniform,
    to_matrix,
    translate,
    uniform_scale,
)


def vec(cls: type[MultiVectorBase], *coords: float) -> MultiVectorBase:
    """Build a vector of representation ``cls`` from its e_1.. components."""
    return sum(
        (c * cls.basis_vector(i + 1) for i, c in enumerate(coords)),
        start=cls.zero(),
    )


# (rep, a vector of that rep's natural dimension)
DIM_GENERAL = [(Gn, (1, 2, 3)), (G1, (3,)), (G2, (3, 4)), (G3, (1, 2, 3))]


@pytest.mark.parametrize("cls", [Gn, G1, G2, G3])
def test_basis_vector_e1_is_unit(cls) -> None:
    assert cls.basis_vector(1) == cls.from_blade_dict({(1,): 1})


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_basis_vector_e2_is_unit(cls) -> None:
    assert cls.basis_vector(2) == cls.from_blade_dict({(2,): 1})


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_dimension_general_transforms_preserve_type(cls, coords) -> None:
    v: MultiVectorBase = vec(cls, *coords)
    b: MultiVectorBase = vec(
        cls, *coords
    )  # translate target must be the same representation
    # factors: (2,) / (2,3) / (2,3,4)
    factors: tuple[int, ...] = tuple(range(2, 2 + len(coords)))
    fns: list[InvertibleFunction] = [
        translate(b),
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        identity(),
        compose([uniform_scale(2.0), translate(b)]),
    ]
    fn: InvertibleFunction
    for fn in fns:
        assert type(fn(v)) is cls


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_known_scale_values(cls) -> None:
    v: MultiVectorBase = vec(cls, 3, 4)
    # non-uniform scale: stretch e_1 by 2, e_2 by 3
    assert scale_non_uniform(2.0, 3.0)(vec(cls, 1, 1)).isclose(
        vec(cls, 2, 3), rel_tol=1e-5, abs_tol=1e-5
    )
    # uniform scale
    assert uniform_scale(2.0)(v).isclose(vec(cls, 6, 8), rel_tol=1e-5, abs_tol=1e-5)


def test_nd_scale_preserves_type_and_value() -> None:
    cls: type[MultiVectorBase]
    for cls in (Gn, G3):
        v: MultiVectorBase = vec(cls, 1, 1, 1)
        scaled: MultiVectorBase = scale_non_uniform(2.0, 3.0, 4.0)(v)
        assert type(scaled) is cls
        assert scaled.isclose(vec(cls, 2, 3, 4), rel_tol=1e-5, abs_tol=1e-5)


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_invertibility(cls, coords) -> None:
    v: MultiVectorBase = vec(cls, *coords)
    factors: tuple[int, ...] = tuple(range(2, 2 + len(coords)))
    fn: InvertibleFunction
    for fn in [
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        translate(vec(cls, *coords)),
    ]:
        assert inverse(fn)(fn(v)).isclose(v, rel_tol=1e-5, abs_tol=1e-5)
    c: InvertibleFunction = compose([uniform_scale(2.0), translate(vec(cls, *coords))])
    assert inverse(c)(c(v)).isclose(v, rel_tol=1e-5, abs_tol=1e-5)


def test_non_invertible_scales_raise() -> None:
    v: MultiVectorBase = vec(Gn, 1, 1)
    # the forward of a zero scale is fine; the *inverse* is undefined and raises
    with pytest.raises(ValueError):
        inverse(uniform_scale(0.0))(v)
    with pytest.raises(ValueError):
        inverse(scale_non_uniform(2.0, 0.0))(v)


# ---------------------------------------------------------------------------
# Animation layer: at() / steps().  Ported from mvp's mathutils interpolation
# tests, with gacalc-native factories (translate / uniform_scale /
# scale_non_uniform / compose) in place of mvp's rotation factories.
# Property checks: at(0)=identity, at(1)=full, invertibility at every t,
# composites recurse, inverse commutes with at, steps flattens.
# ---------------------------------------------------------------------------


def test_interpolate_translate_endpoints_and_midpoint() -> None:
    b: MultiVectorBase = vec(G3, 10, -20, 4)
    t: InvertibleFunction = translate(b)
    o: G3 = G3.zero()
    assert t.at(0.0)(o).isclose(o, rel_tol=1e-5, abs_tol=1e-5)  # identity
    assert t.at(0.5)(o).isclose(
        vec(G3, 5, -10, 2), rel_tol=1e-5, abs_tol=1e-5
    )  # halfway
    assert t.at(1.0)(o).isclose(b, rel_tol=1e-5, abs_tol=1e-5)  # full


def test_interpolate_uniform_scale_is_linear_1_to_m() -> None:
    # linear law 1 -> m: at(0.5) of scale-by-5 is scale-by-3.
    s: InvertibleFunction = uniform_scale(5.0)
    v: MultiVectorBase = vec(G3, 2, 0, 0)
    assert s.at(0.0)(v).isclose(vec(G3, 2, 0, 0), rel_tol=1e-5, abs_tol=1e-5)  # *1
    assert s.at(0.5)(v).isclose(vec(G3, 6, 0, 0), rel_tol=1e-5, abs_tol=1e-5)  # *3
    assert s.at(1.0)(v).isclose(vec(G3, 10, 0, 0), rel_tol=1e-5, abs_tol=1e-5)  # *5


def test_interpolate_scale_non_uniform_per_factor() -> None:
    f: InvertibleFunction = scale_non_uniform(3.0, 5.0, 7.0)
    v: MultiVectorBase = vec(G3, 1, 1, 1)
    assert f.at(0.0)(v).isclose(vec(G3, 1, 1, 1), rel_tol=1e-5, abs_tol=1e-5)  # all *1
    assert f.at(0.5)(v).isclose(
        vec(G3, 2, 3, 4), rel_tol=1e-5, abs_tol=1e-5
    )  # midpoints 2,3,4
    assert f.at(1.0)(v).isclose(vec(G3, 3, 5, 7), rel_tol=1e-5, abs_tol=1e-5)  # full


def test_interpolate_identity_is_identity_at_all_t() -> None:
    ident: InvertibleFunction = identity()
    v: MultiVectorBase = vec(G3, 1, 2, 3)
    t: float
    for t in (0.0, 0.5, 1.0):
        assert ident.at(t)(v).isclose(v, rel_tol=1e-5, abs_tol=1e-5)


def test_interpolate_composite_recurses_into_components() -> None:
    c: InvertibleFunction = compose([translate(vec(G3, 4, 0, 0)), uniform_scale(3.0)])
    p: MultiVectorBase = vec(G3, 1, 0, 0)
    assert c.at(0.0)(p).isclose(p, rel_tol=1e-5, abs_tol=1e-5)  # identity
    assert c.at(1.0)(p).isclose(
        c(p), rel_tol=1e-5, abs_tol=1e-5
    )  # full == the composite itself


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_interpolate_preserves_representation_at_every_t(cls, coords) -> None:
    # the type round-trip must hold at every interpolation parameter, not just
    # the endpoints.
    f: InvertibleFunction = compose([translate(vec(cls, *coords)), uniform_scale(2.0)])
    v: MultiVectorBase = vec(cls, *coords)
    t: float
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert type(f.at(t)(v)) is cls


def test_interpolate_preserves_invertibility_at_every_t() -> None:
    f: InvertibleFunction = compose(
        [
            translate(vec(G3, 1, 2, 3)),
            uniform_scale(2.0),
            scale_non_uniform(2.0, 3.0, 4.0),
        ]
    )
    p: MultiVectorBase = vec(G3, 0.7, -0.3, 1.1)
    t: float
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        ft: InvertibleFunction = f.at(t)
        assert inverse(ft)(ft(p)).isclose(p, rel_tol=1e-5, abs_tol=1e-5)


def test_against_arrow_inverse_matches_negated_param() -> None:
    # animating an against-the-arrow edge as inverse(edge.at(t)) must equal the
    # forward edge run with a negated parameter.
    b: MultiVectorBase = vec(G3, 4, -2, 1)
    translate_fn: InvertibleFunction = translate(b)
    p: MultiVectorBase = vec(G3, 1, 1, 1)
    t: float
    for t in (0.0, 0.3, 0.7, 1.0):
        assert inverse(translate_fn.at(t))(p).isclose(
            translate(-b * t)(p), rel_tol=1e-5, abs_tol=1e-5
        )


def test_at_default_is_step_for_handbuilt_function() -> None:
    # neither a law nor components -> identity until t>=1, then itself.
    f: InvertibleFunction = InvertibleFunction(
        lambda v: v + G3.basis_vector(1), "", lambda v: v - G3.basis_vector(1), ""
    )
    o: G3 = G3.zero()
    assert f.at(0.5)(o).isclose(o, rel_tol=1e-5, abs_tol=1e-5)  # step: identity
    assert f.at(1.0)(o).isclose(
        G3.basis_vector(1), rel_tol=1e-5, abs_tol=1e-5
    )  # step: full


def test_inverse_commutes_with_at_for_primitive_and_composite() -> None:
    # the case that matters: inverse(f).at(t) must equal inverse(f.at(t)) at
    # EVERY t, so an against-arrow composite edge animates smoothly, not as a
    # step.
    f: InvertibleFunction = compose(
        [
            translate(vec(G3, 10, 0, 0)),
            uniform_scale(2.0),
            scale_non_uniform(2.0, 3.0, 4.0),
        ]
    )
    p: MultiVectorBase = vec(G3, 1, -0.5, 0.3)
    t: float
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert (
            inverse(f).at(t)(p).isclose(inverse(f.at(t))(p), rel_tol=1e-5, abs_tol=1e-5)
        )
    # and for a bare primitive
    translate_fn: InvertibleFunction = translate(vec(G3, 3, -7, 2))
    for t in (0.0, 0.4, 1.0):
        assert (
            inverse(translate_fn)
            .at(t)(p)
            .isclose(inverse(translate_fn.at(t))(p), rel_tol=1e-5, abs_tol=1e-5)
        )
    # inverting a composite decomposes into the inverted leaves
    assert len(list(inverse(f).steps())) == 3


def test_steps_flattens_nested_composites() -> None:
    inner: InvertibleFunction = compose(
        [translate(vec(G3, 1, 0, 0)), uniform_scale(2.0)]
    )
    outer: InvertibleFunction = compose([scale_non_uniform(2.0, 3.0, 4.0), inner])
    assert len(list(outer.steps())) == 3  # scale + (translate, scale)
    assert len(list(translate(vec(G3, 1, 0, 0)).steps())) == 1


# ---------------------------------------------------------------------------
# Linearity classification: total order LINEAR < AFFINE < NONLINEAR, compose
# joins (max), inverse copies, hand-built defaults to NONLINEAR.
# ---------------------------------------------------------------------------


def test_factory_linearity_tags() -> None:
    assert identity().linearity is Linearity.LINEAR
    assert uniform_scale(2.0).linearity is Linearity.LINEAR
    assert scale_non_uniform(2.0, 3.0).linearity is Linearity.LINEAR
    assert translate(vec(G3, 1, 2, 3)).linearity is Linearity.AFFINE


def test_compose_linearity_is_the_join() -> None:
    b: MultiVectorBase = vec(G3, 1, 2, 3)
    # linear ∘ linear -> linear
    lin: InvertibleFunction = compose(
        [uniform_scale(2.0), scale_non_uniform(2.0, 3.0, 4.0)]
    )
    assert lin.linearity is Linearity.LINEAR
    # linear ∘ affine -> affine (both orders)
    assert compose([uniform_scale(2.0), translate(b)]).linearity is Linearity.AFFINE
    assert compose([translate(b), uniform_scale(2.0)]).linearity is Linearity.AFFINE
    # affine ∘ affine -> affine
    assert compose([translate(b), translate(-b)]).linearity is Linearity.AFFINE
    # anything with a non-linear part -> non-linear
    raw: InvertibleFunction = InvertibleFunction(
        lambda v: v, "", lambda v: v, ""
    )  # defaults NONLINEAR
    assert compose([uniform_scale(2.0), raw]).linearity is Linearity.NONLINEAR


def test_inverse_copies_linearity() -> None:
    assert inverse(translate(vec(G3, 1, 2, 3))).linearity is Linearity.AFFINE
    assert inverse(uniform_scale(2.0)).linearity is Linearity.LINEAR


def test_handbuilt_defaults_to_nonlinear() -> None:
    raw: InvertibleFunction = InvertibleFunction(lambda v: v, "", lambda v: v, "")
    assert raw.linearity is Linearity.NONLINEAR


def test_linearity_is_a_total_order() -> None:
    assert Linearity.LINEAR < Linearity.AFFINE < Linearity.NONLINEAR
    assert max(Linearity.LINEAR, Linearity.AFFINE) is Linearity.AFFINE
    assert max(Linearity.AFFINE, Linearity.NONLINEAR) is Linearity.NONLINEAR


# ---------------------------------------------------------------------------
# to_matrix: always homogeneous (n+1)x(n+1); linear -> zero translation column;
# translation in the LAST column; compose -> product; inverse -> matrix inverse;
# non-linear -> raise; numpy + sympy backends.
# ---------------------------------------------------------------------------


def test_to_matrix_translate_puts_b_in_last_column() -> None:
    cls: type[MultiVectorBase]
    n: int | None
    for cls, n in ((G3, None), (Gn, 3)):
        m: np.ndarray | sympy.Matrix = to_matrix(translate(vec(cls, 2, 3, 4)), cls, n)
        assert m.shape == (4, 4)
        # identity 3x3 linear block
        assert np.allclose(m[:3, :3], np.eye(3))
        # translation in the last column
        assert np.allclose(m[:, 3], [2, 3, 4, 1])
        assert np.allclose(m[3, :], [0, 0, 0, 1])


def test_to_matrix_linear_has_zero_translation_column() -> None:
    # the headline requirement: a linear 3D map is still 4x4, translation zero.
    m: np.ndarray | sympy.Matrix = to_matrix(uniform_scale(2.0), G3)
    assert m.shape == (4, 4)
    assert np.allclose(np.diag(m), [2, 2, 2, 1])
    assert np.allclose(m[:3, 3], [0, 0, 0])  # zero translation column


def test_to_matrix_scale_non_uniform_is_diagonal() -> None:
    m: np.ndarray | sympy.Matrix = to_matrix(scale_non_uniform(2.0, 3.0, 4.0), G3)
    assert np.allclose(m, np.diag([2.0, 3.0, 4.0, 1.0]))


def test_to_matrix_compose_is_matrix_product() -> None:
    f: InvertibleFunction = uniform_scale(2.0)
    g: InvertibleFunction = translate(vec(G3, 1, 2, 3))
    composed: np.ndarray | sympy.Matrix = to_matrix(compose([f, g]), G3)
    product: np.ndarray | sympy.Matrix = to_matrix(f, G3) @ to_matrix(g, G3)
    assert np.allclose(composed, product)


def test_to_matrix_inverse_is_matrix_inverse() -> None:
    fn: InvertibleFunction
    for fn in (translate(vec(G3, 1, 2, 3)), uniform_scale(2.0)):
        m: np.ndarray | sympy.Matrix = to_matrix(fn, G3)
        m_inv: np.ndarray | sympy.Matrix = to_matrix(inverse(fn), G3)
        assert np.allclose(m_inv, np.linalg.inv(m))


def test_to_matrix_nonlinear_raises() -> None:
    # the guard is tag-driven: this hand-built fn is actually identity, but it
    # is tagged NONLINEAR (the conservative default), so to_matrix refuses.
    raw: InvertibleFunction = InvertibleFunction(lambda v: v, "", lambda v: v, "")
    with pytest.raises(ValueError):
        to_matrix(raw, G3)


def test_to_matrix_gn_requires_explicit_n() -> None:
    t: InvertibleFunction = translate(vec(Gn, 1, 2, 3))
    with pytest.raises(ValueError):
        to_matrix(t, Gn)  # Gn has no DIMENSION to infer
    assert to_matrix(t, Gn, n=3).shape == (4, 4)  # explicit n is fine


def test_to_matrix_sympy_backend_is_exact() -> None:
    m: np.ndarray | sympy.Matrix = to_matrix(
        translate(vec(G3, 2, 3, 4)), G3, backend="sympy"
    )
    assert isinstance(m, sympy.Matrix)
    assert m.shape == (4, 4)
    # exact integer entries, translation in the last column
    assert m[0, 3] == 2 and m[1, 3] == 3 and m[2, 3] == 4 and m[3, 3] == 1
    assert m[:3, :3] == sympy.eye(3)


# ---------------------------------------------------------------------------
# Versor sandwich (base.sandwich) + rotor_rotation (the InvertibleFunction).
# ---------------------------------------------------------------------------


def test_sandwich_rotates_and_preserves_type_3d() -> None:
    # quarter turn in the e_2-e_3 plane: e_2 -> e_3 (use the graded Vector3 so
    # the type round-trip can be checked)
    r: MultiVectorBase = Vector3.rotor_from_vectors(
        from_vector=Vector3.e_2, to_vector=Vector3.e_3
    )
    out: Vector3 = r.sandwich(Vector3.e_2)
    assert type(out) is Vector3
    assert out.isclose(Vector3.e_3, rel_tol=1e-5, abs_tol=1e-5)
    # the axis (e_1) is perpendicular to the plane -> fixed, and still a Vector3
    axis: Vector3 = r.sandwich(Vector3.e_1)
    assert type(axis) is Vector3
    assert axis.isclose(Vector3.e_1, rel_tol=1e-5, abs_tol=1e-5)


def test_sandwich_2d_stays_vector2() -> None:
    r: MultiVectorBase = Vector2.rotor_from_vectors(
        from_vector=Vector2.e_1, to_vector=Vector2.e_2
    )
    out: Vector2 = r.sandwich(Vector2.e_1)
    assert type(out) is Vector2
    assert out.isclose(Vector2.e_2, rel_tol=1e-5, abs_tol=1e-5)


def test_sandwich_of_zero_is_zero() -> None:
    r: MultiVectorBase = Vector3.rotor_from_vectors(
        from_vector=Vector3.e_2, to_vector=Vector3.e_3
    )
    out: Vector3 = r.sandwich(Vector3.zero())
    assert type(out) is Vector3
    assert out.isclose(Vector3.zero(), rel_tol=1e-5, abs_tol=1e-5)


def _to3(angle: float) -> MultiVectorBase:
    return math.cos(angle) * G3.basis_vector(1) + math.sin(angle) * G3.basis_vector(2)


def test_rotor_rotation_is_linear_and_round_trips() -> None:
    r: InvertibleFunction = rotor_rotation(G3.basis_vector(1), _to3(0.7))
    assert r.linearity is Linearity.LINEAR
    v: MultiVectorBase
    for v in (
        G3.basis_vector(1),
        G3.basis_vector(2),
        G3.basis_vector(3),
        vec(G3, 1, 2, 3),
    ):
        assert r.inverse(r(v)).isclose(v, rel_tol=1e-5, abs_tol=1e-5)


def test_rotor_rotation_handles_zero() -> None:
    r: InvertibleFunction = rotor_rotation(G3.basis_vector(1), _to3(0.7))
    assert r(G3.zero()).isclose(G3.zero(), rel_tol=1e-5, abs_tol=1e-5)


def test_rotor_rotation_matches_projection_rotate() -> None:
    # the two formulations of a rotation agree (rotor sandwich vs projection),
    # including the perpendicular axis being fixed
    to: MultiVectorBase = _to3(0.7)
    rotor_fn: InvertibleFunction = rotor_rotation(G3.basis_vector(1), to)
    proj_fn: MultiVectorFn = projection_rotation(
        from_vector=G3.basis_vector(1), to_vector=to
    )
    v: MultiVectorBase
    for v in (
        G3.basis_vector(1),
        G3.basis_vector(2),
        G3.basis_vector(3),
        vec(G3, 2, -1, 3),
    ):
        assert rotor_fn(v).isclose(proj_fn(v), rel_tol=1e-5, abs_tol=1e-5)


# --- constructing ComposableFunction / InvertibleFunction directly to label a
# --- bare callable so it joins a compose pipeline (the type is chosen by which
# --- constructor you call: no inverse -> ComposableFunction; inverse -> Invertible)


def _plane_e12() -> MultiVectorBase:
    return Vector3.e_1 ^ Vector3.e_2


def test_composable_function_carries_label_and_applies() -> None:
    p: ComposableFunction = ComposableFunction(
        Vector3.project(_plane_e12()), "P_{B}", linearity=Linearity.LINEAR
    )
    assert p.latex_repr == "P_{B}"
    assert p._repr_latex_() == "$P_{B}$"
    assert p.linearity is Linearity.LINEAR
    # projects onto the e1-e2 plane: the e3 component is dropped
    assert p(Vector3.e_1 + Vector3.e_3).isclose(Vector3.e_1, rel_tol=1e-5, abs_tol=1e-5)


def test_composable_functions_compose_into_pipeline_latex() -> None:
    # project()/reflect() are typed at MultiVectorBase, so wrapping them gives
    # ComposableFunction[MultiVectorBase]s that compose with one another cleanly.
    # (Mixing one with a concretely-typed factory like translate works at runtime
    # but not under the invariant generic -- see the composable-function task.)
    p: ComposableFunction = ComposableFunction(Vector3.project(_plane_e12()), "P_{B}")
    m: ComposableFunction = ComposableFunction(Vector3.reflect(_plane_e12()), "M_{B}")
    pipe: ComposableFunction = p @ m
    # the whole pipeline renders as one combined LaTeX expression
    assert pipe.latex_repr == "P_{B} \\circ M_{B}"
    # applies M (reflect across the plane) first, then P (project onto it):
    # e_1 + e_3  --reflect-->  e_1 - e_3  --project-->  e_1
    assert pipe(Vector3.e_1 + Vector3.e_3).isclose(
        Vector3.e_1, rel_tol=1e-5, abs_tol=1e-5
    )


def test_composable_function_is_not_invertible() -> None:
    p: ComposableFunction = ComposableFunction(Vector3.project(_plane_e12()), "P_{B}")
    m: ComposableFunction = ComposableFunction(Vector3.reflect(_plane_e12()), "M_{B}")
    # a ComposableFunction has no inverse capability
    assert isinstance(p, ComposableFunction) and not isinstance(p, InvertibleFunction)
    # inverting a projection is meaningless -> a clear error. (cast: we are
    # deliberately feeding a non-invertible in to prove the runtime guard fires.)
    with pytest.raises(NotInvertibleError):
        inverse(typing.cast(InvertibleFunction, p))
    # inverting a whole pipeline that contains it errors too
    with pytest.raises(NotInvertibleError):
        inverse(typing.cast(InvertibleFunction, p @ m))


def test_invertible_function_with_real_inverse_roundtrips() -> None:
    # a reflection is an involution -- construct an InvertibleFunction with it as
    # its own inverse, and it inverts.
    reflect_fn: InvertibleFunction = Vector3.reflect(_plane_e12())
    m: InvertibleFunction = InvertibleFunction(
        func=reflect_fn,
        latex_repr="M_{B}",
        inverse=reflect_fn,
        latex_repr_inv="M_{B}^{-1}",
        linearity=Linearity.LINEAR,
    )
    assert m.latex_repr_inv == "M_{B}^{-1}"
    v: Vector3 = Vector3.e_1 + Vector3.e_3
    assert inverse(m)(m(v)).isclose(v, rel_tol=1e-5, abs_tol=1e-5)
