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

"""``transforms.line_to_line_rejection``.

The doctests show the worked example; this file runs the round trip on each line
over exact, symbolic and float input, and every ``ValueError`` in each direction.
"""

import pytest
import sympy

from gacalc import g2, g3
from gacalc.base import MultiVectorBase, Real
from gacalc.functions import InvertibleFunction
from gacalc.gn import Gn, e_1, e_2
from gacalc.transforms import line_to_line_rejection

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
c: sympy.Symbol
a_1, a_2, b_1, b_2, c = sympy.symbols("a_1 a_2 b_1 b_2 c", real=True)

# (from_vector, away_from, a scalar c): c * from_vector goes to c * R(from_vector).
LINE_PAIRS: list[tuple[MultiVectorBase, MultiVectorBase, Real]] = [
    (1 * g2.e_1 + 3 * g2.e_2, 1 * g2.e_2, 2),
    (2 * g3.e_1 + 1 * g3.e_3, 1 * g3.e_1 + 1 * g3.e_2, sympy.Rational(-1, 3)),
    (1.5 * g2.e_1 - 0.5 * g2.e_2, 1.0 * g2.e_1 + 2.0 * g2.e_2, 0.7),
    (
        Gn.from_real(a_1) * e_1 + Gn.from_real(a_2) * e_2,
        Gn.from_real(b_1) * e_1 + Gn.from_real(b_2) * e_2,
        c,
    ),
]
LINE_PAIR_IDS: list[str] = ["g2-int", "g3-rational", "g2-float", "gn-symbolic"]


def tolerant(v: MultiVectorBase) -> bool:
    return any(isinstance(coefficient, float) for coefficient in v)


@pytest.mark.parametrize("from_vector, away_from, c", LINE_PAIRS, ids=LINE_PAIR_IDS)
def test_round_trip_on_each_line(
    from_vector: MultiVectorBase, away_from: MultiVectorBase, c: Real
) -> None:
    R: InvertibleFunction[MultiVectorBase] = line_to_line_rejection(
        from_vector=from_vector,
        away_from=away_from,
        float_close_to_zero=tolerant(from_vector),
    )
    shadow: MultiVectorBase = from_vector.rejected_away_from(away_from)
    x: MultiVectorBase = from_vector * c
    z: MultiVectorBase = shadow * c
    if tolerant(from_vector):
        assert R(x).isclose(z, rel_tol=1e-9, abs_tol=1e-9)
        assert R.inverse(z).isclose(x, rel_tol=1e-9, abs_tol=1e-9)
    else:
        assert R(x) == z
        assert R.inverse(z) == x
        assert R.inverse(R(x)) == x


def test_image_is_perpendicular_to_away_from() -> None:
    away_from: MultiVectorBase = 1 * g3.e_1 + 1 * g3.e_2
    R: InvertibleFunction[MultiVectorBase] = line_to_line_rejection(
        from_vector=2 * g3.e_1 + 1 * g3.e_3, away_from=away_from
    )
    assert R(2 * g3.e_1 + 1 * g3.e_3).dot(away_from).scalar_part() == 0


def test_off_the_line_raises_in_each_direction() -> None:
    R: InvertibleFunction[MultiVectorBase] = line_to_line_rejection(
        from_vector=1 * g2.e_1 + 3 * g2.e_2, away_from=1 * g2.e_2
    )
    with pytest.raises(ValueError, match="not on the line"):
        R(1 * g2.e_2)
    with pytest.raises(ValueError, match="not on the line"):
        R.inverse(1 * g2.e_2)


def test_parallel_lines_raise() -> None:
    with pytest.raises(ValueError, match="parallel"):
        line_to_line_rejection(from_vector=2 * g3.e_1, away_from=-1 * g3.e_1)


@pytest.mark.parametrize(
    "from_vector, away_from",
    [
        (0 * g2.e_1, 1 * g2.e_2),
        (1 * g2.e_1, 0 * g2.e_2),
        (1 * g2.e_1, 1 * g2.Bivector.e_12),
    ],
    ids=["zero-from", "zero-away", "bivector"],
)
def test_bad_lines_raise(
    from_vector: MultiVectorBase, away_from: MultiVectorBase
) -> None:
    with pytest.raises(ValueError):
        line_to_line_rejection(from_vector=from_vector, away_from=away_from)
