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

"""``transforms.line_to_line_projection`` and ``transforms.coordinate_along``.

The doctests show the worked example; this file runs the round trip on each line
over exact, symbolic and float input, and every ``ValueError`` in each direction.
"""

import pytest
import sympy

from gacalc import g2, g3
from gacalc.base import MultiVectorBase, Real
from gacalc.functions import InvertibleFunction
from gacalc.gn import Gn, e_1, e_2, e_3
from gacalc.transforms import coordinate_along, line_to_line_projection

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
c: sympy.Symbol
a_1, a_2, b_1, b_2, c = sympy.symbols("a_1 a_2 b_1 b_2 c", real=True)

# (from_vector, to_vector, a scalar c): c * from_vector goes to c * P(from_vector).
LINE_PAIRS: list[tuple[MultiVectorBase, MultiVectorBase, Real]] = [
    (1 * g2.e_1 + 3 * g2.e_2, 1 * g2.e_2, 2),
    (2 * g3.e_1 + 1 * g3.e_3, 1 * g3.e_1 + 1 * g3.e_2, sympy.Rational(-1, 3)),
    (1.5 * g2.e_1 - 0.5 * g2.e_2, 1.0 * g2.e_1 + 2.0 * g2.e_2, 0.7),
    (a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2, c),
]
LINE_PAIR_IDS: list[str] = ["g2-int", "g3-rational", "g2-float", "gn-symbolic"]


def tolerant(v: MultiVectorBase) -> bool:
    return any(isinstance(coefficient, float) for coefficient in v)


@pytest.mark.parametrize("from_vector, to_vector, c", LINE_PAIRS, ids=LINE_PAIR_IDS)
def test_round_trip_on_each_line(
    from_vector: MultiVectorBase, to_vector: MultiVectorBase, c: Real
) -> None:
    P: InvertibleFunction[MultiVectorBase] = line_to_line_projection(
        from_vector=from_vector,
        to_vector=to_vector,
        float_close_to_zero=tolerant(from_vector),
    )
    shadow: MultiVectorBase = from_vector.projected_onto(to_vector)
    x: MultiVectorBase = c * from_vector
    z: MultiVectorBase = c * shadow
    if tolerant(from_vector):
        assert P(x).isclose(z, rel_tol=1e-9, abs_tol=1e-9)
        assert P.inverse(z).isclose(x, rel_tol=1e-9, abs_tol=1e-9)
    else:
        assert P(x) == z
        assert P.inverse(z) == x
        assert P.inverse(P(x)) == x


def test_off_the_line_raises_in_each_direction() -> None:
    P: InvertibleFunction[MultiVectorBase] = line_to_line_projection(
        from_vector=1 * g2.e_1 + 3 * g2.e_2, to_vector=1 * g2.e_2
    )
    with pytest.raises(ValueError, match="not on the line"):
        P(1 * g2.e_1)
    with pytest.raises(ValueError, match="not on the line"):
        P.inverse(1 * g2.e_1)


def test_perpendicular_lines_raise() -> None:
    with pytest.raises(ValueError, match="perpendicular"):
        line_to_line_projection(from_vector=1 * g3.e_1, to_vector=1 * g3.e_3)


@pytest.mark.parametrize(
    "from_vector, to_vector",
    [(0 * g2.e_1, 1 * g2.e_2), (1 * g2.e_1, 1 * g2.Bivector.e_12)],
    ids=["zero", "bivector"],
)
def test_bad_lines_raise(
    from_vector: MultiVectorBase, to_vector: MultiVectorBase
) -> None:
    with pytest.raises(ValueError):
        line_to_line_projection(from_vector=from_vector, to_vector=to_vector)


def test_coordinate_along() -> None:
    assert coordinate_along(6 * e_1 + 3 * e_2, along=2 * e_1 + 1 * e_2) == 3
    assert coordinate_along(0 * g3.e_1, along=1 * g3.e_2) == 0
    assert (
        coordinate_along(c * (a_1 * e_1 + a_2 * e_3), along=a_1 * e_1 + a_2 * e_3) == c
    )
    with pytest.raises(ValueError, match="not on the line"):
        coordinate_along(1 * e_1 + 1 * e_2, along=1 * e_1)
    with pytest.raises(ValueError, match="zero vector"):
        coordinate_along(1 * e_1, along=0 * e_1)
    near: Gn = 2.0 * e_1 + 1e-9 * e_2
    with pytest.raises(ValueError, match="not on the line"):
        coordinate_along(near, along=1.0 * e_1)
    assert coordinate_along(near, along=1.0 * e_1, float_close_to_zero=True) == 2.0
