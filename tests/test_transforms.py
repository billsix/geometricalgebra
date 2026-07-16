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

import numpy as np
import pytest
import sympy

from gacalc.g1 import G1
from gacalc.g2 import G2, Vector2
from gacalc.g3 import G3, Vector3
from gacalc.gn import Gn
from gacalc.transforms import (
    InvertibleFunction,
    Linearity,
    NotInvertibleError,
    compose,
    identity,
    inverse,
    labeled,
    projection_rotation,
    rotor_rotation,
    scale_non_uniform,
    to_matrix,
    translate,
    uniform_scale,
)


def vec(cls, *coords):
    """Build a vector of representation ``cls`` from its e_1.. components."""
    return sum(
        (c * cls.basis_vector(i + 1) for i, c in enumerate(coords)),
        start=cls.zero(),
    )


# (rep, a vector of that rep's natural dimension)
DIM_GENERAL = [(Gn, (1, 2, 3)), (G1, (3,)), (G2, (3, 4)), (G3, (1, 2, 3))]


@pytest.mark.parametrize("cls", [Gn, G1, G2, G3])
def test_basis_vector_e1_is_unit(cls):
    assert cls.basis_vector(1) == cls.from_blade_dict({(1,): 1})


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_basis_vector_e2_is_unit(cls):
    assert cls.basis_vector(2) == cls.from_blade_dict({(2,): 1})


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_dimension_general_transforms_preserve_type(cls, coords):
    v = vec(cls, *coords)
    b = vec(cls, *coords)  # translate target must be the same representation
    factors = tuple(range(2, 2 + len(coords)))  # (2,) / (2,3) / (2,3,4)
    fns = [
        translate(b),
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        identity(),
        compose([uniform_scale(2.0), translate(b)]),
    ]
    for fn in fns:
        assert type(fn(v)) is cls


@pytest.mark.parametrize("cls", [Gn, G2, G3])
def test_known_scale_values(cls):
    v = vec(cls, 3, 4)
    # non-uniform scale: stretch e_1 by 2, e_2 by 3
    assert scale_non_uniform(2.0, 3.0)(vec(cls, 1, 1)).is_close(vec(cls, 2, 3))
    # uniform scale
    assert uniform_scale(2.0)(v).is_close(vec(cls, 6, 8))


def test_nd_scale_preserves_type_and_value():
    for cls in (Gn, G3):
        v = vec(cls, 1, 1, 1)
        scaled = scale_non_uniform(2.0, 3.0, 4.0)(v)
        assert type(scaled) is cls
        assert scaled.is_close(vec(cls, 2, 3, 4))


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_invertibility(cls, coords):
    v = vec(cls, *coords)
    factors = tuple(range(2, 2 + len(coords)))
    for fn in [
        uniform_scale(2.0),
        scale_non_uniform(*factors),
        translate(vec(cls, *coords)),
    ]:
        assert inverse(fn)(fn(v)).is_close(v)
    c = compose([uniform_scale(2.0), translate(vec(cls, *coords))])
    assert inverse(c)(c(v)).is_close(v)


def test_non_invertible_scales_raise():
    v = vec(Gn, 1, 1)
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


def test_interpolate_translate_endpoints_and_midpoint():
    b = vec(G3, 10, -20, 4)
    T = translate(b)
    o = G3.zero()
    assert T.at(0.0)(o).is_close(o)  # identity
    assert T.at(0.5)(o).is_close(vec(G3, 5, -10, 2))  # halfway
    assert T.at(1.0)(o).is_close(b)  # full


def test_interpolate_uniform_scale_is_linear_1_to_m():
    # linear law 1 -> m: at(0.5) of scale-by-5 is scale-by-3.
    S = uniform_scale(5.0)
    v = vec(G3, 2, 0, 0)
    assert S.at(0.0)(v).is_close(vec(G3, 2, 0, 0))  # *1
    assert S.at(0.5)(v).is_close(vec(G3, 6, 0, 0))  # *3
    assert S.at(1.0)(v).is_close(vec(G3, 10, 0, 0))  # *5


def test_interpolate_scale_non_uniform_per_factor():
    f = scale_non_uniform(3.0, 5.0, 7.0)
    v = vec(G3, 1, 1, 1)
    assert f.at(0.0)(v).is_close(vec(G3, 1, 1, 1))  # all *1
    assert f.at(0.5)(v).is_close(vec(G3, 2, 3, 4))  # midpoints 2,3,4
    assert f.at(1.0)(v).is_close(vec(G3, 3, 5, 7))  # full


def test_interpolate_identity_is_identity_at_all_t():
    ident = identity()
    v = vec(G3, 1, 2, 3)
    for t in (0.0, 0.5, 1.0):
        assert ident.at(t)(v).is_close(v)


def test_interpolate_composite_recurses_into_components():
    c = compose([translate(vec(G3, 4, 0, 0)), uniform_scale(3.0)])
    p = vec(G3, 1, 0, 0)
    assert c.at(0.0)(p).is_close(p)  # identity
    assert c.at(1.0)(p).is_close(c(p))  # full == the composite itself


@pytest.mark.parametrize("cls,coords", DIM_GENERAL)
def test_interpolate_preserves_representation_at_every_t(cls, coords):
    # the type round-trip must hold at every interpolation parameter, not just
    # the endpoints.
    f = compose([translate(vec(cls, *coords)), uniform_scale(2.0)])
    v = vec(cls, *coords)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert type(f.at(t)(v)) is cls


def test_interpolate_preserves_invertibility_at_every_t():
    f = compose(
        [
            translate(vec(G3, 1, 2, 3)),
            uniform_scale(2.0),
            scale_non_uniform(2.0, 3.0, 4.0),
        ]
    )
    p = vec(G3, 0.7, -0.3, 1.1)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        ft = f.at(t)
        assert inverse(ft)(ft(p)).is_close(p)


def test_against_arrow_inverse_matches_negated_param():
    # animating an against-the-arrow edge as inverse(edge.at(t)) must equal the
    # forward edge run with a negated parameter.
    b = vec(G3, 4, -2, 1)
    T = translate(b)
    p = vec(G3, 1, 1, 1)
    for t in (0.0, 0.3, 0.7, 1.0):
        assert inverse(T.at(t))(p).is_close(translate(-b * t)(p))


def test_at_default_is_step_for_handbuilt_function():
    # neither a law nor components -> identity until t>=1, then itself.
    f = InvertibleFunction(
        lambda v: v + G3.basis_vector(1), lambda v: v - G3.basis_vector(1), "", ""
    )
    o = G3.zero()
    assert f.at(0.5)(o).is_close(o)  # step: identity
    assert f.at(1.0)(o).is_close(G3.basis_vector(1))  # step: full


def test_inverse_commutes_with_at_for_primitive_and_composite():
    # the case that matters: inverse(f).at(t) must equal inverse(f.at(t)) at
    # EVERY t, so an against-arrow composite edge animates smoothly, not as a
    # step.
    f = compose(
        [
            translate(vec(G3, 10, 0, 0)),
            uniform_scale(2.0),
            scale_non_uniform(2.0, 3.0, 4.0),
        ]
    )
    p = vec(G3, 1, -0.5, 0.3)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert inverse(f).at(t)(p).is_close(inverse(f.at(t))(p))
    # and for a bare primitive
    T = translate(vec(G3, 3, -7, 2))
    for t in (0.0, 0.4, 1.0):
        assert inverse(T).at(t)(p).is_close(inverse(T.at(t))(p))
    # inverting a composite decomposes into the inverted leaves
    assert len(list(inverse(f).steps())) == 3


def test_steps_flattens_nested_composites():
    inner = compose([translate(vec(G3, 1, 0, 0)), uniform_scale(2.0)])
    outer = compose([scale_non_uniform(2.0, 3.0, 4.0), inner])
    assert len(list(outer.steps())) == 3  # scale + (translate, scale)
    assert len(list(translate(vec(G3, 1, 0, 0)).steps())) == 1


# ---------------------------------------------------------------------------
# Linearity classification: total order LINEAR < AFFINE < NONLINEAR, compose
# joins (max), inverse copies, hand-built defaults to NONLINEAR.
# ---------------------------------------------------------------------------


def test_factory_linearity_tags():
    assert identity().linearity is Linearity.LINEAR
    assert uniform_scale(2.0).linearity is Linearity.LINEAR
    assert scale_non_uniform(2.0, 3.0).linearity is Linearity.LINEAR
    assert translate(vec(G3, 1, 2, 3)).linearity is Linearity.AFFINE


def test_compose_linearity_is_the_join():
    b = vec(G3, 1, 2, 3)
    # linear ∘ linear -> linear
    lin = compose([uniform_scale(2.0), scale_non_uniform(2.0, 3.0, 4.0)])
    assert lin.linearity is Linearity.LINEAR
    # linear ∘ affine -> affine (both orders)
    assert compose([uniform_scale(2.0), translate(b)]).linearity is Linearity.AFFINE
    assert compose([translate(b), uniform_scale(2.0)]).linearity is Linearity.AFFINE
    # affine ∘ affine -> affine
    assert compose([translate(b), translate(-b)]).linearity is Linearity.AFFINE
    # anything with a non-linear part -> non-linear
    raw = InvertibleFunction(lambda v: v, lambda v: v, "", "")  # defaults NONLINEAR
    assert compose([uniform_scale(2.0), raw]).linearity is Linearity.NONLINEAR


def test_inverse_copies_linearity():
    assert inverse(translate(vec(G3, 1, 2, 3))).linearity is Linearity.AFFINE
    assert inverse(uniform_scale(2.0)).linearity is Linearity.LINEAR


def test_handbuilt_defaults_to_nonlinear():
    raw = InvertibleFunction(lambda v: v, lambda v: v, "", "")
    assert raw.linearity is Linearity.NONLINEAR


def test_linearity_is_a_total_order():
    assert Linearity.LINEAR < Linearity.AFFINE < Linearity.NONLINEAR
    assert max(Linearity.LINEAR, Linearity.AFFINE) is Linearity.AFFINE
    assert max(Linearity.AFFINE, Linearity.NONLINEAR) is Linearity.NONLINEAR


# ---------------------------------------------------------------------------
# to_matrix: always homogeneous (n+1)x(n+1); linear -> zero translation column;
# translation in the LAST column; compose -> product; inverse -> matrix inverse;
# non-linear -> raise; numpy + sympy backends.
# ---------------------------------------------------------------------------


def test_to_matrix_translate_puts_b_in_last_column():
    for cls, n in ((G3, None), (Gn, 3)):
        M = to_matrix(translate(vec(cls, 2, 3, 4)), cls, n)
        assert M.shape == (4, 4)
        # identity 3x3 linear block
        assert np.allclose(M[:3, :3], np.eye(3))
        # translation in the last column
        assert np.allclose(M[:, 3], [2, 3, 4, 1])
        assert np.allclose(M[3, :], [0, 0, 0, 1])


def test_to_matrix_linear_has_zero_translation_column():
    # the headline requirement: a linear 3D map is still 4x4, translation zero.
    M = to_matrix(uniform_scale(2.0), G3)
    assert M.shape == (4, 4)
    assert np.allclose(np.diag(M), [2, 2, 2, 1])
    assert np.allclose(M[:3, 3], [0, 0, 0])  # zero translation column


def test_to_matrix_scale_non_uniform_is_diagonal():
    M = to_matrix(scale_non_uniform(2.0, 3.0, 4.0), G3)
    assert np.allclose(M, np.diag([2.0, 3.0, 4.0, 1.0]))


def test_to_matrix_compose_is_matrix_product():
    f = uniform_scale(2.0)
    g = translate(vec(G3, 1, 2, 3))
    composed = to_matrix(compose([f, g]), G3)
    product = to_matrix(f, G3) @ to_matrix(g, G3)
    assert np.allclose(composed, product)


def test_to_matrix_inverse_is_matrix_inverse():
    for fn in (translate(vec(G3, 1, 2, 3)), uniform_scale(2.0)):
        M = to_matrix(fn, G3)
        Minv = to_matrix(inverse(fn), G3)
        assert np.allclose(Minv, np.linalg.inv(M))


def test_to_matrix_nonlinear_raises():
    # the guard is tag-driven: this hand-built fn is actually identity, but it
    # is tagged NONLINEAR (the conservative default), so to_matrix refuses.
    raw = InvertibleFunction(lambda v: v, lambda v: v, "", "")
    with pytest.raises(ValueError):
        to_matrix(raw, G3)


def test_to_matrix_gn_requires_explicit_n():
    T = translate(vec(Gn, 1, 2, 3))
    with pytest.raises(ValueError):
        to_matrix(T, Gn)  # Gn has no DIMENSION to infer
    assert to_matrix(T, Gn, n=3).shape == (4, 4)  # explicit n is fine


def test_to_matrix_sympy_backend_is_exact():
    M = to_matrix(translate(vec(G3, 2, 3, 4)), G3, backend="sympy")
    assert isinstance(M, sympy.Matrix)
    assert M.shape == (4, 4)
    # exact integer entries, translation in the last column
    assert M[0, 3] == 2 and M[1, 3] == 3 and M[2, 3] == 4 and M[3, 3] == 1
    assert M[:3, :3] == sympy.eye(3)


# ---------------------------------------------------------------------------
# Versor sandwich (base.sandwich) + rotor_rotation (the InvertibleFunction).
# ---------------------------------------------------------------------------


def test_sandwich_rotates_and_preserves_type_3d():
    # quarter turn in the e_2-e_3 plane: e_2 -> e_3 (use the graded Vector3 so
    # the type round-trip can be checked)
    R = Vector3.rotor_from_vectors(from_vector=Vector3.e_2, to_vector=Vector3.e_3)
    out = R.sandwich(Vector3.e_2)
    assert type(out) is Vector3
    assert out.is_close(Vector3.e_3)
    # the axis (e_1) is perpendicular to the plane -> fixed, and still a Vector3
    axis = R.sandwich(Vector3.e_1)
    assert type(axis) is Vector3
    assert axis.is_close(Vector3.e_1)


def test_sandwich_2d_stays_vector2():
    R = Vector2.rotor_from_vectors(from_vector=Vector2.e_1, to_vector=Vector2.e_2)
    out = R.sandwich(Vector2.e_1)
    assert type(out) is Vector2
    assert out.is_close(Vector2.e_2)


def test_sandwich_of_zero_is_zero():
    R = Vector3.rotor_from_vectors(from_vector=Vector3.e_2, to_vector=Vector3.e_3)
    out = R.sandwich(Vector3.zero())
    assert type(out) is Vector3
    assert out.is_close(Vector3.zero())


def _to3(angle):
    return math.cos(angle) * G3.basis_vector(1) + math.sin(angle) * G3.basis_vector(2)


def test_rotor_rotation_is_linear_and_round_trips():
    R = rotor_rotation(G3.basis_vector(1), _to3(0.7))
    assert R.linearity is Linearity.LINEAR
    for v in (
        G3.basis_vector(1),
        G3.basis_vector(2),
        G3.basis_vector(3),
        vec(G3, 1, 2, 3),
    ):
        assert R.inverse(R(v)).is_close(v)


def test_rotor_rotation_handles_zero():
    R = rotor_rotation(G3.basis_vector(1), _to3(0.7))
    assert R(G3.zero()).is_close(G3.zero())


def test_rotor_rotation_matches_projection_rotate():
    # the two formulations of a rotation agree (rotor sandwich vs projection),
    # including the perpendicular axis being fixed
    to = _to3(0.7)
    rotor_fn = rotor_rotation(G3.basis_vector(1), to)
    proj_fn = projection_rotation(from_vector=G3.basis_vector(1), to_vector=to)
    for v in (
        G3.basis_vector(1),
        G3.basis_vector(2),
        G3.basis_vector(3),
        vec(G3, 2, -1, 3),
    ):
        assert rotor_fn(v).is_close(proj_fn(v))


# --- labeled: opt-in LaTeX label so bare functions join the compose pipeline ---


def _plane_e12():
    return Vector3.e_1 ^ Vector3.e_2


def test_labeled_carries_label_and_applies():
    P = labeled(Vector3.project(_plane_e12()), "P_{B}", linearity=Linearity.LINEAR)
    assert P.latex_repr == "P_{B}"
    assert P._repr_latex_() == "$P_{B}$"
    assert P.linearity is Linearity.LINEAR
    # projects onto the e1-e2 plane: the e3 component is dropped
    assert P(Vector3.e_1 + Vector3.e_3).is_close(Vector3.e_1)


def test_labeled_composes_into_pipeline_latex():
    # project()/reflect() return the type-erased MultiVectorFn, so labelled
    # algebra functions are InvertibleFunction[MultiVectorBase] and compose with
    # one another cleanly. (Mixing one with a concretely-typed factory like
    # translate works at runtime but not under the invariant generic -- see the
    # reassess-composable-function-interface task.)
    P = labeled(Vector3.project(_plane_e12()), "P_{B}")
    M = labeled(Vector3.reflect(_plane_e12()), "M_{B}")
    pipe = P @ M
    # the whole pipeline renders as one combined LaTeX expression
    assert pipe.latex_repr == "P_{B} \\circ M_{B}"
    # applies M (reflect across the plane) first, then P (project onto it):
    # e_1 + e_3  --reflect-->  e_1 - e_3  --project-->  e_1
    assert pipe(Vector3.e_1 + Vector3.e_3).is_close(Vector3.e_1)


def test_labeled_defaults_to_not_invertible():
    P = labeled(Vector3.project(_plane_e12()), "P_{B}")
    M = labeled(Vector3.reflect(_plane_e12()), "M_{B}")
    assert P.latex_repr_inv == "P_{B}^{-1}"  # default label
    # inverting a projection is meaningless -> a clear error when applied
    with pytest.raises(NotInvertibleError):
        inverse(P)(Vector3.e_1)
    # inverting a whole pipeline that contains it errors too
    with pytest.raises(NotInvertibleError):
        inverse(P @ M)(Vector3.e_1)


def test_labeled_with_real_inverse_roundtrips():
    # a reflection is an involution -- pass it as its own inverse, and it inverts
    reflect_fn = Vector3.reflect(_plane_e12())
    M = labeled(reflect_fn, "M_{B}", inverse=reflect_fn, linearity=Linearity.LINEAR)
    assert M.latex_repr_inv == "M_{B}^{-1}"
    v = Vector3.e_1 + Vector3.e_3
    assert inverse(M)(M(v)).is_close(v)
