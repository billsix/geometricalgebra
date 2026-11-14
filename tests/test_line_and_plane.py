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

"""``transforms.line_to_plane_projection`` / ``line_from_plane_rejection`` and the
generated 𝒢₃ ``Vector`` methods of the same names.

The doctests show the worked examples; this file runs the round trip over exact,
symbolic and float input, every ``ValueError`` in each direction, and checks the
generated coordinate versions against the factories on the ``Gn`` reference.
"""

import typing

import pytest
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, Real
from gacalc.functions import InvertibleFunction
from gacalc.gn import Gn, e_1, e_2, e_3
from gacalc.transforms import line_from_plane_rejection, line_to_plane_projection

Factory = typing.Callable[..., InvertibleFunction[MultiVectorBase]]

c: sympy.Symbol
d: sympy.Symbol
c, d = sympy.symbols("c d", real=True)
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3", real=True)
b_12: sympy.Symbol
b_13: sympy.Symbol
b_23: sympy.Symbol
b_12, b_13, b_23 = sympy.symbols("b_12 b_13 b_23", real=True)

# (from_vector, plane, c): c * from_vector goes to c * (its image).
CASES: list[tuple[MultiVectorBase, MultiVectorBase, Real]] = [
    (
        1 * g3.e_1 + 2 * g3.e_2 + 3 * g3.e_3,
        1 * g3.Bivector.e_12 + 1 * g3.Bivector.e_23,
        2,
    ),
    (
        2 * g3.e_1 + 1 * g3.e_3,
        2 * g3.Bivector.e_13 - 1 * g3.Bivector.e_12,
        sympy.Rational(-1, 3),
    ),
    (
        1.5 * g3.e_1 - 0.5 * g3.e_2 + 1.0 * g3.e_3,
        1.0 * g3.Bivector.e_12 + 2.0 * g3.Bivector.e_23,
        0.7,
    ),
    (
        Gn.from_real(a_1) * e_1 + Gn.from_real(a_2) * e_2 + Gn.from_real(a_3) * e_3,
        Gn.from_real(b_12) * (e_1 * e_2)
        + Gn.from_real(b_13) * (e_1 * e_3)
        + Gn.from_real(b_23) * (e_2 * e_3),
        c,
    ),
]
IDS: list[str] = ["g3-int", "g3-rational", "g3-float", "gn-symbolic"]
KINDS: list[tuple[Factory, str]] = [
    (line_to_plane_projection, "projected_onto"),
    (line_from_plane_rejection, "rejected_away_from"),
]
KIND_IDS: list[str] = ["projection", "rejection"]
# The generated g3.Vector method of each kind, keyed by the image method.
GENERATED_METHOD: dict[str, str] = {
    "projected_onto": "line_to_plane_projection",
    "rejected_away_from": "line_from_plane_rejection",
}
# Every (kind, case) pair; the symbolic Gn projection takes over 10 s, so it is slow.
ROUND_TRIPS: list[typing.Any] = [
    pytest.param(
        factory,
        image,
        *case,
        id=f"{case_id}-{kind_id}",
        marks=(
            [pytest.mark.slow]
            if (case_id, kind_id) == ("gn-symbolic", "projection")
            else []
        ),
    )
    for (factory, image), kind_id in zip(KINDS, KIND_IDS)
    for case, case_id in zip(CASES, IDS)
]


def tolerant(v: MultiVectorBase) -> bool:
    return any(isinstance(coefficient, float) for coefficient in v)


@pytest.mark.parametrize(("factory", "image", "from_vector", "plane", "c"), ROUND_TRIPS)
def test_round_trip_on_each_line(
    factory: Factory,
    image: str,
    from_vector: MultiVectorBase,
    plane: MultiVectorBase,
    c: Real,
) -> None:
    f: InvertibleFunction[MultiVectorBase] = factory(
        from_vector, plane, float_close_to_zero=tolerant(from_vector)
    )
    shadow: MultiVectorBase = getattr(from_vector, image)(plane)
    x: MultiVectorBase = from_vector * c
    z: MultiVectorBase = shadow * c
    if tolerant(from_vector):
        assert f(x).isclose(z, rel_tol=1e-9, abs_tol=1e-9)
        assert f.inverse(z).isclose(x, rel_tol=1e-9, abs_tol=1e-9)
    else:
        assert f(x) == z
        assert f.inverse(z) == x
        assert f.inverse(f(x)) == x


def test_projection_lands_in_the_plane_and_rejection_off_it() -> None:
    a: MultiVectorBase = 1 * g3.e_1 + 2 * g3.e_2 + 3 * g3.e_3
    B: MultiVectorBase = 1 * g3.Bivector.e_12 + 1 * g3.Bivector.e_23
    zero_trivector: MultiVectorBase = g3.Trivector.zero()
    assert (line_to_plane_projection(a, B)(a) ^ B) == zero_trivector
    rejected: MultiVectorBase = line_from_plane_rejection(a, B)(a)
    assert rejected.left_contraction(B) == g3.Vector.zero()


def test_off_the_line_raises_in_each_direction() -> None:
    f: InvertibleFunction[MultiVectorBase] = line_to_plane_projection(
        1 * g3.e_1 + 1 * g3.e_3, 1 * g3.Bivector.e_12
    )
    with pytest.raises(ValueError, match="not on the line"):
        f(1 * g3.e_2)
    with pytest.raises(ValueError, match="not on the line"):
        f.inverse(1 * g3.e_2)


def test_degenerate_configurations_raise() -> None:
    with pytest.raises(ValueError, match="perpendicular to the plane"):
        line_to_plane_projection(2 * g3.e_3, 1 * g3.Bivector.e_12)
    with pytest.raises(ValueError, match="lies in the plane"):
        line_from_plane_rejection(1 * g3.e_1 + 1 * g3.e_2, 1 * g3.Bivector.e_12)


@pytest.mark.parametrize(("factory", "image"), KINDS, ids=KIND_IDS)
@pytest.mark.parametrize(
    ("from_vector", "plane"),
    [
        (0 * g3.e_1, 1 * g3.Bivector.e_12),
        (1 * g3.e_1, g3.Bivector.zero()),
        (1 * g3.e_1, 1 * g3.e_2),
        (1 * g3.Bivector.e_12, 1 * g3.Bivector.e_12),
    ],
    ids=["zero-vector", "zero-plane", "vector-plane", "bivector-line"],
)
def test_bad_arguments_raise(
    factory: Factory, image: str, from_vector: MultiVectorBase, plane: MultiVectorBase
) -> None:
    with pytest.raises(ValueError):
        factory(from_vector, plane)


def as_gn(value: MultiVectorBase) -> Gn:
    """``value`` in the ``Gn`` reference representation."""
    return Gn.from_blade_dict(value.to_blade_dict())


def assert_same(value: MultiVectorBase, reference: MultiVectorBase) -> None:
    """``value`` and ``reference`` have equal blade dicts after simplification."""
    difference: Gn = as_gn(value) - as_gn(reference)
    assert all(
        sympy.simplify(sympy.sympify(coefficient)) == 0
        for coefficient in difference.to_blade_dict().values()
    )


@pytest.mark.parametrize(("factory", "image"), KINDS, ids=KIND_IDS)
def test_generated_agrees_with_gn_reference(factory: Factory, image: str) -> None:
    a: g3.Vector = (
        g3.Scalar(a_1) * g3.e_1 + g3.Scalar(a_2) * g3.e_2 + g3.Scalar(a_3) * g3.e_3
    )
    B: g3.Bivector = (
        g3.Scalar(b_12) * g3.Bivector.e_12
        + g3.Scalar(b_13) * g3.Bivector.e_13
        + g3.Scalar(b_23) * g3.Bivector.e_23
    )
    generated: InvertibleFunction[g3.Vector] = getattr(a, GENERATED_METHOD[image])(B)
    reference: InvertibleFunction[MultiVectorBase] = factory(as_gn(a), as_gn(B))
    x: g3.Vector = g3.Scalar(c) * a
    image_of_a: MultiVectorBase = getattr(as_gn(a), image)(as_gn(B))
    z: g3.Vector = g3.Scalar(d) * g3.Vector.from_blade_dict(image_of_a.to_blade_dict())
    assert type(generated(x)) is g3.Vector
    assert_same(generated(x), reference(as_gn(x)))
    assert_same(generated.inverse(z), reference.inverse(as_gn(z)))


def test_generated_int_input_stays_exact() -> None:
    a: g3.Vector = 1 * g3.e_1 + 2 * g3.e_2 + 3 * g3.e_3
    f: InvertibleFunction[g3.Vector] = a.line_to_plane_projection(
        to_plane=2 * g3.Bivector.e_12 + 1 * g3.Bivector.e_23
    )
    assert f.inverse(f(a)) == a
    assert all(not isinstance(coefficient, float) for coefficient in f(a))


def test_generated_operand_must_be_a_bivector() -> None:
    with pytest.raises(TypeError, match="takes a Bivector"):
        (1 * g3.e_1).line_to_plane_projection(to_plane=1 * g3.e_2)  # ty: ignore[invalid-argument-type]


def test_generated_degenerate_configurations_raise() -> None:
    with pytest.raises(ValueError, match="perpendicular to the plane"):
        (2 * g3.e_3).line_to_plane_projection(to_plane=1 * g3.Bivector.e_12)
    with pytest.raises(ValueError, match="lies in the plane"):
        (1 * g3.e_1).line_from_plane_rejection(away_from_plane=1 * g3.Bivector.e_12)
    with pytest.raises(ValueError, match="spans no plane"):
        (1 * g3.e_1).line_to_plane_projection(to_plane=g3.Bivector.zero())
