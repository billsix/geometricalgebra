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
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

from gacalc.nbplotutils import create_graphs, draw_ndc  # noqa: E402


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
