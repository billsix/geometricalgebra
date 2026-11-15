"""Shared vectors for the 2D bootstrap figures (``boot_*``), Part III of the book.

One module per figure family, as elsewhere: each ``boot_*`` figure draws one step of the
bootstrap arc (rotation, rotation from projection, the product, projection through the
product, rotation through the product) from the fixed points here. The projection page
reuses the ``sp*`` figures of :mod:`_projection_scene`. Primitives from :mod:`_scene2d`.
CC0.
"""

from __future__ import annotations

import math

from _scene2d import (
    BLUE,
    GREEN,
    ORIGIN,
    PURPLE,
    Point,
    epix,
    polar,
)

__all__: list[str] = [
    "ROTATE_V",
    "ROTATE_V_ANGLE",
    "ROTATE_THETA",
    "ROTATE_V_PERP",
    "ROTATE_COS_PART",
    "ROTATE_RESULT",
    "FROM_PROJ_A",
    "FROM_PROJ_A_ANGLE",
    "FROM_PROJ_B",
    "FROM_PROJ_B_ANGLE",
    "FROM_PROJ_THETA",
    "FROM_PROJ_B_FOOT",
    "FROM_PROJ_V",
    "FROM_PROJ_V_ANGLE",
    "FROM_PROJ_V_COS_PART",
    "FROM_PROJ_V_ROTATED",
    "PRODUCT_A",
    "PRODUCT_B",
    "PRODUCT_A_ANGLE",
    "PRODUCT_FOOT",
    "INVERSE_A",
    "INVERSE_B",
    "INVERSE_A_ANGLE",
    "INVERSE_A_INV",
    "INVERSE_PROJ",
    "ONESIDED_A_ANGLE",
    "ONESIDED_B_ANGLE",
    "ONESIDED_A",
    "ONESIDED_B",
    "ONESIDED_V_ANGLE",
    "ONESIDED_V",
    "ONESIDED_V_ROT",
    "SANDWICH_A",
    "SANDWICH_A_ANGLE",
    "SANDWICH_B",
    "SANDWICH_B_ANGLE",
    "SANDWICH_H",
    "SANDWICH_H_ANGLE",
    "foot_on_line",
    "colored_vector",
    "colored_segment",
    "BLUE",
    "GREEN",
    "PURPLE",
]


def foot_on_line(point: Point, direction: Point) -> Point:
    """The foot of the perpendicular from ``point`` to the line through the origin
    along ``direction``: the projection of ``point`` onto ``direction``."""
    along: float = (point.x1() * direction.x1() + point.x2() * direction.x2()) / (
        direction.x1() ** 2 + direction.x2() ** 2
    )
    return Point(x=along * direction.x1(), y=along * direction.x2())


def colored_vector(
    head: Point,
    color: epix.Color,
    text: str,
    offset: Point,
    align: epix.LabelPos,
    tail: Point = ORIGIN,
) -> None:
    """A coloured arrow ``tail``->``head`` with a label in the same colour."""
    epix.pen(color=color, width=1.8)
    epix.arrow(tail=tail, head=head, scale=0.7)
    epix.label_color(color=color)
    epix.label(at=head, offset=offset, text=text, align=align)
    epix.label_color(color=epix.black())


def colored_segment(
    tail: Point,
    head: Point,
    color: epix.Color,
    text: str,
    offset: Point,
    align: epix.LabelPos,
) -> None:
    """A coloured line ``tail``->``head`` labelled at its midpoint, in its colour."""
    epix.pen(color=color, width=1.6)
    epix.line(tail=tail, head=head)
    middle: Point = Point(x=(tail.x1() + head.x1()) / 2, y=(tail.x2() + head.x2()) / 2)
    epix.label_color(color=color)
    epix.label(at=middle, offset=offset, text=text, align=align)
    epix.label_color(color=epix.black())


# Step 1, the precalculus rotation: v, its quarter turn, and the blend
# cos(theta) * v + sin(theta) * r(v; pi/2).
ROTATE_V_ANGLE: float = math.radians(15)
ROTATE_THETA: float = math.radians(55)
ROTATE_V: Point = polar(radius=1.2, angle=ROTATE_V_ANGLE)
ROTATE_V_PERP: Point = polar(radius=1.2, angle=ROTATE_V_ANGLE + math.pi / 2)
ROTATE_COS_PART: Point = polar(
    radius=1.2 * math.cos(ROTATE_THETA), angle=ROTATE_V_ANGLE
)
ROTATE_RESULT: Point = polar(radius=1.2, angle=ROTATE_V_ANGLE + ROTATE_THETA)

# Step 3, the rotation from a to b, from projection: two copies of one triangle. The
# first is b measured against a: x along a, y across, hypotenuse |b|, angle theta at the
# origin. The second is the same triangle on v, outside the angle from a to b: legs
# cos(theta) * v along v and sin(theta) * r(v; pi/2) across, hypotenuse the rotated v.
FROM_PROJ_A_ANGLE: float = math.radians(12)
FROM_PROJ_B_ANGLE: float = math.radians(57)
FROM_PROJ_THETA: float = FROM_PROJ_B_ANGLE - FROM_PROJ_A_ANGLE
FROM_PROJ_A: Point = polar(radius=1.45, angle=FROM_PROJ_A_ANGLE)
FROM_PROJ_B: Point = polar(radius=1.0, angle=FROM_PROJ_B_ANGLE)
FROM_PROJ_B_FOOT: Point = foot_on_line(point=FROM_PROJ_B, direction=FROM_PROJ_A)
FROM_PROJ_V_ANGLE: float = math.radians(112)
FROM_PROJ_V_LENGTH: float = 1.15
FROM_PROJ_V: Point = polar(radius=FROM_PROJ_V_LENGTH, angle=FROM_PROJ_V_ANGLE)
FROM_PROJ_V_COS_PART: Point = polar(
    radius=FROM_PROJ_V_LENGTH * math.cos(FROM_PROJ_THETA), angle=FROM_PROJ_V_ANGLE
)
FROM_PROJ_V_ROTATED: Point = polar(
    radius=FROM_PROJ_V_LENGTH, angle=FROM_PROJ_V_ANGLE + FROM_PROJ_THETA
)

# Step 4, the product a * b: b measured along and across a, by Step 2.
PRODUCT_A_ANGLE: float = math.radians(15)
PRODUCT_A: Point = polar(radius=1.2, angle=PRODUCT_A_ANGLE)
PRODUCT_B: Point = polar(radius=1.05, angle=math.radians(70))
PRODUCT_FOOT: Point = foot_on_line(point=PRODUCT_B, direction=PRODUCT_A)

# Step 5, projection through the product: a is longer than 1, so a^-1 = a / |a|^2 is
# visibly shorter than a, along the same line; b is projected onto a.
INVERSE_A_ANGLE: float = math.radians(15)
INVERSE_A: Point = polar(radius=1.5, angle=INVERSE_A_ANGLE)
INVERSE_A_INV: Point = polar(radius=1 / 1.5, angle=INVERSE_A_ANGLE)
INVERSE_B: Point = polar(radius=1.5, angle=math.radians(45))
INVERSE_PROJ: Point = foot_on_line(point=INVERSE_B, direction=INVERSE_A)

# Step 6, rotation through the product: the angle theta from a to b, applied to v.
ONESIDED_A_ANGLE: float = math.radians(10)
ONESIDED_B_ANGLE: float = math.radians(60)
ONESIDED_A: Point = polar(radius=1.0, angle=ONESIDED_A_ANGLE)
ONESIDED_B: Point = polar(radius=1.25, angle=ONESIDED_B_ANGLE)
ONESIDED_V_ANGLE: float = math.radians(115)
ONESIDED_V: Point = polar(radius=1.1, angle=ONESIDED_V_ANGLE)
ONESIDED_V_ROT: Point = polar(
    radius=1.1, angle=ONESIDED_V_ANGLE + ONESIDED_B_ANGLE - ONESIDED_A_ANGLE
)
# The sandwich figure: a wider angle from a to b, so each half-angle wedge has room for
# its label, and the half-angle vector h halfway between.
SANDWICH_A_ANGLE: float = math.radians(10)
SANDWICH_B_ANGLE: float = math.radians(78)
SANDWICH_A: Point = polar(radius=1.0, angle=SANDWICH_A_ANGLE)
SANDWICH_B: Point = polar(radius=1.25, angle=SANDWICH_B_ANGLE)
SANDWICH_H_ANGLE: float = (SANDWICH_A_ANGLE + SANDWICH_B_ANGLE) / 2
SANDWICH_H: Point = polar(radius=1.3, angle=SANDWICH_H_ANGLE)
