"""Shared vectors for the rotate-from-a-to-b figures (``rotate_ab_goal`` … ``_step3``).

The chapter rotates ``a``'s direction onto ``b``'s by reduction to standard position:
swing ``a`` onto the x-axis, rotate to ``b'`` (where ``b`` has been carried), then undo
the first rotation. ``a`` and ``b`` are deliberately **not** unit length (``a`` longer
than the unit circle, ``b`` shorter) — magnitudes don't set the rotation, directions do.
All figures share the one ``a``, ``b`` fixed here. Primitives from :mod:`_scene2d`. CC0.
"""

from __future__ import annotations

import math

from _scene2d import Point, polar

A_LENGTH: float = 1.1  # |a|: longer than unit (outside the circle) — not unit length
A_ANGLE: float = math.radians(25)
B_LENGTH: float = 0.8  # |b|: shorter than unit (inside the circle) — not unit length
B_ANGLE: float = math.radians(70)

A: Point = polar(radius=A_LENGTH, angle=A_ANGLE)
B: Point = polar(radius=B_LENGTH, angle=B_ANGLE)

# After step 1 (rotate the whole picture by -A_ANGLE, swinging a onto the x-axis):
# a lands on |a|*e_1, and b is carried to b' at angle (B_ANGLE - A_ANGLE), same length.
A_ON_E1: Point = polar(radius=A_LENGTH, angle=0.0)
B_PRIME: Point = polar(radius=B_LENGTH, angle=B_ANGLE - A_ANGLE)

# The result: a rotated onto b's direction = (|a|/|b|) b — length |a| at b's angle.
RESULT: Point = polar(radius=A_LENGTH, angle=B_ANGLE)

LOWER_LEFT: Point = Point(x=-0.55, y=-0.5)
UPPER_RIGHT: Point = Point(x=1.5, y=1.35)
