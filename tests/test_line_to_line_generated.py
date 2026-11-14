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

"""The generated ``Vector.line_to_line_projection`` / ``line_to_line_rejection``.

Each generated method is the coordinate version of the ``transforms`` factory of
the same name.  This file checks, on fully symbolic vectors of 𝒢₁, 𝒢₂ and 𝒢₃, that
both directions agree with the factory applied to the ``Gn`` reference, and that
the generated versions keep int input exact, reject non-``Vector`` operands, and
(𝒢₁) leave the rejection out.
"""

import types
import typing
from collections.abc import Callable

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.functions import InvertibleFunction
from gacalc.gn import Gn
from gacalc.transforms import line_to_line_projection, line_to_line_rejection

c: sympy.Symbol
d: sympy.Symbol
c, d = sympy.symbols("c d", real=True)


def symbolic_vector(module: types.ModuleType, n: int, prefix: str) -> typing.Any:
    """A vector of ``module`` with one real symbol per coordinate.

    Typed ``Any``: the module, so the concrete ``Vector`` class, is chosen at run
    time, and the methods under test exist only on the generated ``Vector``.
    """
    symbols: list[sympy.Symbol] = list(sympy.symbols(f"{prefix}_1:{n + 1}", real=True))
    return sum(
        [
            module.Scalar(s) * getattr(module, f"e_{i}")
            for i, s in enumerate(symbols, start=1)
        ],
        start=module.Vector.zero(),
    )


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


CASES: list[tuple[types.ModuleType, int, str]] = [
    (g1, 1, "projection"),
    (g2, 2, "projection"),
    (g2, 2, "rejection"),
    (g3, 3, "projection"),
    (g3, 3, "rejection"),
]
IDS: list[str] = [f"g{n}-{kind}" for _, n, kind in CASES]


@pytest.mark.parametrize(("module", "n", "kind"), CASES, ids=IDS)
def test_generated_agrees_with_gn_reference(
    module: types.ModuleType, n: int, kind: str
) -> None:
    a: typing.Any = symbolic_vector(module, n, "a")
    other: typing.Any = symbolic_vector(module, n, "b")
    generated: InvertibleFunction[MultiVectorBase]
    reference: InvertibleFunction[MultiVectorBase]
    match kind:
        case "projection":
            generated = a.line_to_line_projection(to_vector=other)
            reference = line_to_line_projection(
                from_vector=as_gn(a), to_vector=as_gn(other)
            )
            image_of_a: MultiVectorBase = as_gn(a).projected_onto(as_gn(other))
        case "rejection":
            generated = a.line_to_line_rejection(away_from=other)
            reference = line_to_line_rejection(
                from_vector=as_gn(a), away_from=as_gn(other)
            )
            image_of_a = as_gn(a).rejected_away_from(as_gn(other))
        case _:
            raise ValueError(kind)
    x: MultiVectorBase = module.Scalar(c) * a
    z: MultiVectorBase = module.Scalar(d) * module.Vector.from_blade_dict(
        image_of_a.to_blade_dict()
    )
    assert type(generated(x)) is module.Vector
    assert_same(generated(x), reference(as_gn(x)))
    assert_same(generated.inverse(z), reference.inverse(as_gn(z)))


@pytest.mark.parametrize(
    "build",
    [
        lambda: (1 * g2.e_1 + 3 * g2.e_2).line_to_line_projection(to_vector=2 * g2.e_2),
        lambda: (1 * g2.e_1 + 3 * g2.e_2).line_to_line_rejection(away_from=2 * g2.e_1),
    ],
    ids=["projection", "rejection"],
)
def test_int_input_stays_exact(
    build: Callable[[], InvertibleFunction[MultiVectorBase]],
) -> None:
    function: InvertibleFunction[MultiVectorBase] = build()
    x: MultiVectorBase = 1 * g2.e_1 + 3 * g2.e_2
    assert function.inverse(function(x)) == x
    assert all(not isinstance(coefficient, float) for coefficient in function(x))


def test_off_the_line_raises_in_each_direction() -> None:
    P: InvertibleFunction[g3.Vector] = (
        1 * g3.e_1 + 1 * g3.e_2
    ).line_to_line_projection(to_vector=1 * g3.e_1)
    with pytest.raises(ValueError, match="not on the line"):
        P(1 * g3.e_3)
    with pytest.raises(ValueError, match="not on the line"):
        P.inverse(1 * g3.e_2)


def test_degenerate_lines_raise() -> None:
    with pytest.raises(ValueError, match="perpendicular"):
        (1 * g2.e_1).line_to_line_projection(to_vector=1 * g2.e_2)
    with pytest.raises(ValueError, match="parallel"):
        (1 * g2.e_1).line_to_line_rejection(away_from=-2 * g2.e_1)


def test_operand_must_be_this_algebras_vector() -> None:
    with pytest.raises(TypeError, match="takes a Vector"):
        (1 * g2.e_1).line_to_line_projection(to_vector=1 * g2.Bivector.e_12)  # ty: ignore[invalid-argument-type]


def test_g1_has_no_rejection() -> None:
    assert not hasattr(g1.Vector, "line_to_line_rejection")
