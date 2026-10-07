"""Shared scene for the proof-rotate figures (``rotate1`` … ``rotate8``).

One picture, built up step by step across the eight proof figures: the unit disc
with axes, the direction of :math:`\\vec{a}` at angle β, its perpendicular at β + π/2,
the rotation angle θ, the right triangle with legs cos θ and sin θ, and the result
scaled back to length r. The constants here are the single source of the geometry, so
every figure in the sequence agrees with the goal figure (same β, same θ, same r).

Figure files are jupytext percent notebooks in the style of epix-mirror's
``notebooks/``; ``tools/render_epix_figures.py`` runs each in a fresh process (and
skips this ``_``-prefixed helper). CC0, like the hand-drawn SVGs these replace.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from contextlib import contextmanager

import epix
from epix import Point

__all__ = [
    "BETA",
    "THETA",
    "R",
    "ORIGIN",
    "PURPLE",
    "PURPLE_FILL",
    "GREEN",
    "BLUE",
    "Point",
    "epix",
    "polar",
    "unit_circle_scene",
    "vector",
    "wedge",
    "right_angle_marker",
    "leg",
]

BETA: float = math.radians(66)  # the angle of a itself
THETA: float = math.radians(66)  # the angle we rotate BY (same as the goal figure)
R: float = 1.25  # |a|: a is not a unit vector -- the circle is only for scale

ORIGIN: Point = Point(x=0, y=0)
DEFAULT_LOWER_LEFT: Point = Point(x=-1.6, y=-1.3)
DEFAULT_UPPER_RIGHT: Point = Point(x=1.5, y=1.4)
LABEL_RIGHT: Point = Point(x=7, y=0)  # default label offset: just right of a head
UNIT_SCALE_IN: float = 1.2  # inches per unit, kept equal on both axes

PURPLE: epix.Color = epix.rgb(r=0.5, g=0.0, b=0.5)
PURPLE_FILL: epix.Color = epix.rgb(r=0xDD / 255, g=0xCA / 255, b=0xD4 / 255)
GREEN: epix.Color = epix.rgb(r=0.0, g=0.5, b=0.0)
BLUE: epix.Color = epix.rgb(r=0.0, g=0.0, b=0.75)
# The PNGs for the HTML book are flattened onto this, the disc's own fill
# (epix.white(0.95)), so a dark-mode page shows a uniform light panel instead of a
# transparent sheet around the disc.
BACKGROUND: str = "#f2f2f2"


def polar(radius: float, angle: float) -> Point:
    """The point at polar coordinates (radius, angle in radians)."""
    return Point(x=radius * math.cos(angle), y=radius * math.sin(angle))


@contextmanager
def unit_circle_scene(
    lower_left: Point = DEFAULT_LOWER_LEFT,
    upper_right: Point = DEFAULT_UPPER_RIGHT,
) -> Iterator[object]:
    """``epix.figure`` with the unit disc and the labelled axes already drawn.

    The physical size follows the bounding box at ``UNIT_SCALE_IN`` per unit, so
    every figure in the sequence is at the same scale whatever its box.
    """
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * UNIT_SCALE_IN:.2f}x{height * UNIT_SCALE_IN:.2f}in"
    with epix.figure(lower_left=lower_left, upper_right=upper_right, size=size) as fig:
        epix.font_size("large")
        # the unit circle, filled light gray, for scale
        epix.pen(epix.black(0.45), width=0.9)
        epix.fill(epix.white(0.95))
        epix.circle(center=ORIGIN, radius=1)
        epix.nofill()
        # axes with arrowheads
        epix.pen(epix.black(), width=1.1)
        x_end: Point = Point(x=upper_right.x1() - 0.15, y=0)
        y_end: Point = Point(x=0, y=upper_right.x2() - 0.1)
        epix.arrow(tail=Point(x=lower_left.x1() + 0.2, y=0), head=x_end, scale=1)
        epix.arrow(tail=Point(x=0, y=lower_left.x2() + 0.15), head=y_end, scale=1)
        epix.label(x_end, offset=Point(x=5, y=0), text="$x$", align=epix.LabelPos.r)
        epix.label(y_end, offset=Point(x=5, y=-2), text="$y$", align=epix.LabelPos.r)
        yield fig


def vector(
    head: Point,
    text: str = "",
    offset: Point = LABEL_RIGHT,
    align: epix.LabelPos = epix.LabelPos.r,
) -> None:
    """A black segment from the origin to ``head``, with a dot and an optional label."""
    epix.pen(epix.black(), width=1.8)
    epix.line(tail=ORIGIN, head=head)
    epix.dot(at=head)
    if text:
        epix.label(head, offset=offset, text=text, align=align)


def wedge(start: float, finish: float, text: str, radius: float = 0.33) -> None:
    """A purple filled wedge at the origin from ``start`` to ``finish`` (radians)."""
    epix.pen(PURPLE, width=0.8)
    epix.fill(PURPLE_FILL)
    points: list[Point] = [ORIGIN] + [
        polar(radius, start + (finish - start) * i / 24) for i in range(25)
    ]
    epix.Path(data=points, closed=True, filled=True).draw()
    epix.nofill()
    epix.label_color(PURPLE)
    epix.label(polar(0.55 * radius, (start + finish) / 2), text=text)
    epix.label_color(epix.black())


def right_angle_marker(angle: float, size: float = 0.12) -> None:
    """The right-angle square at the origin between ``angle`` and ``angle + π/2``."""
    epix.pen(epix.black(), width=0.9)
    corner_a: Point = polar(size, angle)
    corner_b: Point = polar(size, angle + math.pi / 2)
    corner_ab: Point = Point(
        x=corner_a.x1() + corner_b.x1(), y=corner_a.x2() + corner_b.x2()
    )
    epix.line(tail=corner_a, head=corner_ab)
    epix.line(tail=corner_ab, head=corner_b)


def leg(
    tail: Point, head: Point, color: epix.Color, text: str, angle: float, offset: Point
) -> None:
    """A coloured triangle leg ``tail``→``head``; label rotated by ``angle`` radians."""
    epix.pen(color, width=1.6)
    epix.line(tail=tail, head=head)
    epix.label_color(color)
    epix.label_angle(angle)
    mid: Point = Point(x=(tail.x1() + head.x1()) / 2, y=(tail.x2() + head.x2()) / 2)
    epix.label(mid, offset=offset, text=text, align=epix.LabelPos.c)
    epix.label_angle(0)
    epix.label_color(epix.black())
