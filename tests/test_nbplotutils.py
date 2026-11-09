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

"""The notebook plotting helpers in ``gacalc.nbplotutils``.

Drawn with matplotlib's non-interactive ``Agg`` backend, and checked through the
artists the helper adds to the current axes.
"""

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import sympy  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

import gacalc.g2 as g2  # noqa: E402
import gacalc.g3 as g3  # noqa: E402
import gacalc.gn as gn  # noqa: E402
from gacalc.base import MultiVectorBase  # noqa: E402
from gacalc.nbplotutils import create_graphs, draw_ndc, sine  # noqa: E402


def test_draw_ndc_draws_the_four_corners_of_the_square() -> None:
    # The normalized-device-coordinate square [-1, 1]^2: four corners, in order.
    axes: Axes
    with create_graphs() as axes:
        draw_ndc()
    squares: list[Polygon] = [p for p in axes.patches if isinstance(p, Polygon)]
    assert len(squares) == 1
    # get_xy() repeats the first vertex at the end of a closed polygon.
    corners: np.ndarray = squares[0].get_xy()[:-1]
    expected: np.ndarray = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]])
    assert np.allclose(corners, expected)


@pytest.mark.parametrize(
    ("e_1", "e_2"),
    [
        pytest.param(gn.e_1, gn.e_2, id="gn"),
        pytest.param(g2.Vector.e_1, g2.Vector.e_2, id="g2-vector"),
        pytest.param(g2.G.e_1, g2.G.e_2, id="g2-full"),
    ],
)
def test_sine_is_the_signed_sine_in_the_plane(
    e_1: MultiVectorBase, e_2: MultiVectorBase
) -> None:
    # A quarter turn counterclockwise has sine 1; the other way, -1.
    assert sine(1 * e_1, 1 * e_2) == 1
    assert sine(1 * e_2, 1 * e_1) == -1
    assert sine(3 * e_1, 2 * e_1 + 2 * e_2) == sympy.sqrt(2) / 2


def test_sine_raises_off_the_plane() -> None:
    # A signed sine exists only in 2-D; two 3-D vectors raise instead of giving 0.
    with pytest.raises(ValueError):
        sine(1 * g3.e_1, 1 * g3.e_3)


def test_sine_raises_for_a_non_vector() -> None:
    with pytest.raises(ValueError):
        sine(g2.Bivector.e_12, 1 * g2.e_1)
