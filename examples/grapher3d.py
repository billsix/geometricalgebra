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

"""Plot functions of two variables that gacalc computes, as surfaces.

Run it with ``python examples/grapher3d.py`` (needs the ``gl`` extra and a
display; ``make shell`` provides both).  Each surface below is ordinary Python
built on gacalc; the Surface menu switches between them.  The window, controls
and drawing are :func:`gacalc.gl.grapher3d.run`.
"""

from gacalc.g2 import Bivector, Vector, e_1, e_2, e_12
from gacalc.gl import grapher3d


def magnitude(x: float, y: float) -> float:
    """|x * e_1 + y * e_2|: a cone with its tip at the origin."""
    v: Vector = x * e_1 + y * e_2
    return float(v.magnitude())


def dot_with_diagonal(x: float, y: float) -> float:
    """(x * e_1 + y * e_2) · (1 * e_1 + 1 * e_2): a tilted plane, x + y."""
    v: Vector = x * e_1 + y * e_2
    diagonal: Vector = 1.0 * e_1 + 1.0 * e_2
    return float(v.dot(diagonal).scalar_part()) / 2.0


def wedge_with_reflection(x: float, y: float) -> float:
    """The e_12 coefficient of a ∧ b for a = x * e_1 + y * e_2 and its mirror
    image b = y * e_1 + x * e_2: x² - y², a saddle (scaled by 1/8)."""
    a: Vector = x * e_1 + y * e_2
    b: Vector = y * e_1 + x * e_2
    A: Bivector = a ^ b
    return float(A.coefficient(e_12)) / 8.0


SURFACES: list[grapher3d.Surface] = [
    grapher3d.Surface(
        fn=magnitude,
        label="cone: |x * e_1 + y * e_2|",
        color=(0.45, 0.8, 0.95),
        latex=r"z=|x * e_1 + y * e_2|",
    ),
    grapher3d.Surface(
        fn=dot_with_diagonal,
        label="plane: a . (1 * e_1 + 1 * e_2) / 2",
        color=(0.95, 0.55, 0.35),
        latex=r"z=\tfrac{1}{2} * (x * e_1 + y * e_2) \cdot (1 * e_1 + 1 * e_2)",
    ),
    grapher3d.Surface(
        fn=wedge_with_reflection,
        label="saddle: (a ^ b) e_12 coefficient / 8",
        color=(0.6, 0.9, 0.5),
        latex=r"z=\tfrac{1}{8} * \langle a \wedge b \rangle_{e_{12}}",
    ),
]

if __name__ == "__main__":
    grapher3d.run(SURFACES, title="gacalc: 3D graphing calculator")
