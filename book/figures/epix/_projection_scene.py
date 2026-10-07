"""Shared vectors for the 2D projection / rejection figures (``proj1`` … ``sp5``).

The result figures show :math:`\\vec{a}` projected onto the line through
:math:`\\vec{b}`; the derivation figures (``sp*``) rotate the whole picture so
:math:`\\vec{b}` lies on the x-axis, read the projection off as the x-coordinate, and
rotate back. All of them share the one :math:`\\vec{a}`, :math:`\\vec{b}` fixed here
(``a`` is the rotation sequence's, length 1.25 at 66°; ``b`` is length 1 at 20°), so
every figure agrees. Primitives come from :mod:`_scene2d`. CC0, like the hand-drawn
SVGs these replace.
"""

from __future__ import annotations

import math

from _scene2d import Point, polar

A_LENGTH: float = 1.25  # |a|: the rotation sequence's a
A_ANGLE: float = math.radians(66)
B_LENGTH: float = 1.0  # b is a unit vector
B_ANGLE: float = math.radians(20)

A: Point = polar(radius=A_LENGTH, angle=A_ANGLE)
B: Point = polar(radius=B_LENGTH, angle=B_ANGLE)


def _project_point(a: Point, b: Point) -> Point:
    """The foot of the perpendicular from ``a`` to the line through ``b``: the point
    ``((a·b)/(b·b)) b``, i.e. the head of the projection vector."""
    scale: float = (a.x1() * b.x1() + a.x2() * b.x2()) / (b.x1() ** 2 + b.x2() ** 2)
    return Point(x=scale * b.x1(), y=scale * b.x2())


PROJ: Point = _project_point(a=A, b=B)  # project(a, b): along b
# reject(a, b) = a - project: the perpendicular remainder, drawn from PROJ to A.

# The infinite line through b, as a segment to draw dashed well past b both ways.
LINE_LOW: Point = Point(x=-0.55 * B.x1(), y=-0.55 * B.x2())
LINE_HIGH: Point = Point(x=1.65 * B.x1(), y=1.65 * B.x2())

# Standard position: rotate everything by -B_ANGLE, so b lands on the x-axis at (|b|, 0)
# and a's angle drops from 66° to 46°. The projection is then just a's x-coordinate.
A_ROT: Point = polar(radius=A_LENGTH, angle=A_ANGLE - B_ANGLE)
B_ROT: Point = polar(radius=B_LENGTH, angle=0.0)
PROJ_ROT: Point = Point(x=A_ROT.x1(), y=0.0)  # keep x, drop y

# One box for the upright (result) figures, one for the standard-position figures (b on
# the x-axis pushes the useful area to the right). Same UNIT_SCALE_IN, so one scale.
PROJ_LOWER_LEFT: Point = Point(x=-0.6, y=-0.45)
PROJ_UPPER_RIGHT: Point = Point(x=1.7, y=1.5)
SP_LOWER_LEFT: Point = Point(x=-0.6, y=-0.5)
SP_UPPER_RIGHT: Point = Point(x=1.7, y=1.5)
