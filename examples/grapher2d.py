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

"""Plot functions of one variable that gacalc computes, in an OpenGL window.

Run it with ``python examples/grapher2d.py`` (needs the ``gl`` extra and a
display; ``make shell`` provides both).  Each function below is ordinary Python
built on gacalc; add one to ``FUNCTIONS`` to plot it too.  The window, controls
and drawing are :func:`gacalc.gl.grapher2d.run`.
"""

from gacalc.g2 import Vector, e_1, e_2
from gacalc.gl import grapher2d


def e_1_coefficient_of_rotated_e_1(θ: float) -> float:
    """The e_1 coefficient of e_1 rotated by θ: cos(θ)."""
    return float((1.0 * e_1 + 0.0 * e_2).rotate(θ).coefficient(e_1))


def e_2_coefficient_of_rotated_e_1(θ: float) -> float:
    """The e_2 coefficient of e_1 rotated by θ: sin(θ)."""
    return float((1.0 * e_1 + 0.0 * e_2).rotate(θ).coefficient(e_2))


def magnitude_of_x_e_1_plus_e_2(x: float) -> float:
    """|x * e_1 + 1 * e_2|, the distance from the origin to (x, 1)."""
    v: Vector = x * e_1 + 1.0 * e_2
    return float(v.magnitude())


FUNCTIONS: list[grapher2d.PlottedFunction] = [
    grapher2d.PlottedFunction(
        fn=e_1_coefficient_of_rotated_e_1,
        label="e_1 coefficient of rotate(e_1, x)",
        color=(0.95, 0.35, 0.35),
        latex=r"\cos(x)",
    ),
    grapher2d.PlottedFunction(
        fn=e_2_coefficient_of_rotated_e_1,
        label="e_2 coefficient of rotate(e_1, x)",
        color=(0.35, 0.75, 0.95),
        latex=r"\sin(x)",
    ),
    grapher2d.PlottedFunction(
        fn=magnitude_of_x_e_1_plus_e_2,
        label="|x * e_1 + 1 * e_2|",
        color=(0.55, 0.9, 0.5),
        latex=r"|x * e_1 + 1 * e_2|",
    ),
]

if __name__ == "__main__":
    grapher2d.run(FUNCTIONS, title="gacalc: 2D graphing calculator")
