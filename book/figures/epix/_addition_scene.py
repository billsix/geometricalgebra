"""Shared vectors for the vector-addition / subtraction figures (``add1`` … ``sub2``).

Two fixed vectors :math:`\\vec{a}` and :math:`\\vec{b}` and the points derived from
them (:math:`\\vec{a}+\\vec{b}`, :math:`-\\vec{b}`, :math:`\\vec{a}-\\vec{b}`), so every
figure in the pair agrees on the same geometry. The generic stage and primitives come
from :mod:`_scene2d`. CC0, like the hand-drawn SVGs these replace.
"""

from __future__ import annotations

from _scene2d import Point

A: Point = Point(x=1.4, y=0.4)  # a: rightish and a little up
B: Point = Point(x=0.5, y=1.1)  # b: upish and a little right
A_PLUS_B: Point = Point(x=A.x1() + B.x1(), y=A.x2() + B.x2())
NEG_B: Point = Point(x=-B.x1(), y=-B.x2())
A_MINUS_B: Point = Point(x=A.x1() - B.x1(), y=A.x2() - B.x2())

# Addition stays in the first quadrant; subtraction reaches down-left for -b. Both use
# UNIT_SCALE_IN per unit (set by unit_circle_scene), so the two framings are at one
# scale.
ADD_LOWER_LEFT: Point = Point(x=-0.5, y=-0.45)
ADD_UPPER_RIGHT: Point = Point(x=2.35, y=1.95)
SUB_LOWER_LEFT: Point = Point(x=-1.15, y=-1.5)
SUB_UPPER_RIGHT: Point = Point(x=2.35, y=1.95)
