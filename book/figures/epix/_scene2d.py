"""Shared 2D scene helpers for the book's ePiX figures.

The disc-and-axes stage, colours, and the small drawing primitives (vectors, a filled
angle wedge, a right-angle marker, a triangle leg, a translated dashed copy, a
parallelogram) that every 2D figure in the book is built from. ``_rotation_scene`` adds
the rotation-sequence constants on top and re-exports these; the vector-addition and
projection figures import them directly.

Figure files are jupytext percent notebooks in the style of epix-mirror's
``notebooks/``; ``tools/render_epix_figures.py`` runs each in a fresh process (and skips
these ``_``-prefixed helpers). CC0, like the hand-drawn SVGs these replace.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from contextlib import contextmanager

import epix
from epix import Point

# What `epix.figure(...)` yields: a proxy that becomes the rendered `Figure` after the
# `with` block (its `.eepic`/`.png`/`.save` forward to it). epix keeps the class
# private, so the figure files type their `fig` through this alias.
from epix.figure import _Pending as PendingFigure

__all__: list[str] = [
    "ORIGIN",
    "DEFAULT_LOWER_LEFT",
    "DEFAULT_UPPER_RIGHT",
    "LABEL_RIGHT",
    "UNIT_SCALE_IN",
    "PURPLE",
    "PURPLE_FILL",
    "GREEN",
    "BLUE",
    "BACKGROUND",
    "PendingFigure",
    "Point",
    "epix",
    "polar",
    "unit_circle_scene",
    "vector",
    "dashed_vector",
    "parallelogram",
    "wedge",
    "right_angle_marker",
    "right_angle_at",
    "leg",
]

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
    disc: bool = True,
) -> Iterator[PendingFigure]:
    """``epix.figure`` with the labelled axes (and, by default, the unit disc) drawn.

    The physical size follows the bounding box at ``UNIT_SCALE_IN`` per unit, so every
    figure is at the same scale whatever its box. Pass ``disc=False`` for a figure that
    does not need the unit circle (e.g. vector addition) -- the axes are still drawn.
    """
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * UNIT_SCALE_IN:.2f}x{height * UNIT_SCALE_IN:.2f}in"
    fig: PendingFigure
    with epix.figure(lower_left=lower_left, upper_right=upper_right, size=size) as fig:
        epix.font_size(size="large")
        if disc:
            # the unit circle, filled light gray, for scale
            epix.pen(color=epix.black(intensity=0.45), width=0.9)
            epix.fill(color=epix.white(intensity=0.95))
            epix.circle(center=ORIGIN, radius=1)
            epix.nofill()
        # axes with arrowheads
        epix.pen(color=epix.black(), width=1.1)
        x_end: Point = Point(x=upper_right.x1() - 0.15, y=0)
        y_end: Point = Point(x=0, y=upper_right.x2() - 0.1)
        epix.arrow(tail=Point(x=lower_left.x1() + 0.2, y=0), head=x_end, scale=1)
        epix.arrow(tail=Point(x=0, y=lower_left.x2() + 0.15), head=y_end, scale=1)
        epix.label(at=x_end, offset=Point(x=5, y=0), text="$x$", align=epix.LabelPos.r)
        epix.label(at=y_end, offset=Point(x=5, y=-2), text="$y$", align=epix.LabelPos.r)
        yield fig


def vector(
    head: Point,
    text: str = "",
    offset: Point = LABEL_RIGHT,
    align: epix.LabelPos = epix.LabelPos.r,
) -> None:
    """A black segment from the origin to ``head``, with a dot and an optional label."""
    epix.pen(color=epix.black(), width=1.8)
    epix.line(tail=ORIGIN, head=head)
    epix.dot(at=head)
    if text:
        epix.label(at=head, offset=offset, text=text, align=align)


def dashed_vector(
    tail: Point,
    head: Point,
    text: str = "",
    offset: Point = LABEL_RIGHT,
    align: epix.LabelPos = epix.LabelPos.r,
) -> None:
    """A dashed black segment ``tail``->``head`` -- a translated copy of a vector."""
    epix.pen(color=epix.black(), width=1.4)
    epix.dashed()
    epix.line(tail=tail, head=head)
    epix.line_style(style="-")  # back to solid for whatever draws next
    epix.dot(at=head)
    if text:
        epix.label(at=head, offset=offset, text=text, align=align)


def parallelogram(
    corner_a: Point, corner_b: Point, color: epix.Color = PURPLE_FILL
) -> None:
    """A light-filled parallelogram with corners O, ``corner_a``, ``corner_a+corner_b``,
    ``corner_b`` -- the span of two vectors from the origin."""
    far: Point = Point(x=corner_a.x1() + corner_b.x1(), y=corner_a.x2() + corner_b.x2())
    epix.pen(color=epix.black(intensity=0.6), width=0.6)
    epix.fill(color=color)
    epix.Path(data=[ORIGIN, corner_a, far, corner_b], closed=True, filled=True).draw()
    epix.nofill()


def wedge(start: float, finish: float, text: str, radius: float = 0.33) -> None:
    """A purple filled wedge at the origin from ``start`` to ``finish`` (radians)."""
    epix.pen(color=PURPLE, width=0.8)
    epix.fill(color=PURPLE_FILL)
    points: list[Point] = [ORIGIN] + [
        polar(radius=radius, angle=start + (finish - start) * i / 24) for i in range(25)
    ]
    epix.Path(data=points, closed=True, filled=True).draw()
    epix.nofill()
    epix.label_color(color=PURPLE)
    epix.label(at=polar(radius=0.55 * radius, angle=(start + finish) / 2), text=text)
    epix.label_color(color=epix.black())


def right_angle_marker(angle: float, size: float = 0.12) -> None:
    """The right-angle square at the origin between ``angle`` and ``angle + π/2``."""
    epix.pen(color=epix.black(), width=0.9)
    corner_a: Point = polar(radius=size, angle=angle)
    corner_b: Point = polar(radius=size, angle=angle + math.pi / 2)
    corner_ab: Point = Point(
        x=corner_a.x1() + corner_b.x1(), y=corner_a.x2() + corner_b.x2()
    )
    epix.line(tail=corner_a, head=corner_ab)
    epix.line(tail=corner_ab, head=corner_b)


def right_angle_at(corner: Point, angle: float, size: float = 0.1) -> None:
    """A right-angle square with its corner at ``corner``, spanning ``angle`` to
    ``angle + π/2`` (radians) -- the arbitrary-corner ``right_angle_marker``."""
    epix.pen(color=epix.black(), width=0.9)
    leg_a: Point = polar(radius=size, angle=angle)
    leg_b: Point = polar(radius=size, angle=angle + math.pi / 2)
    p_a: Point = Point(x=corner.x1() + leg_a.x1(), y=corner.x2() + leg_a.x2())
    p_b: Point = Point(x=corner.x1() + leg_b.x1(), y=corner.x2() + leg_b.x2())
    p_ab: Point = Point(
        x=corner.x1() + leg_a.x1() + leg_b.x1(),
        y=corner.x2() + leg_a.x2() + leg_b.x2(),
    )
    epix.line(tail=p_a, head=p_ab)
    epix.line(tail=p_ab, head=p_b)


def leg(
    tail: Point, head: Point, color: epix.Color, text: str, angle: float, offset: Point
) -> None:
    """A coloured triangle leg ``tail``→``head``; label rotated by ``angle`` radians."""
    epix.pen(color=color, width=1.6)
    epix.line(tail=tail, head=head)
    epix.label_color(color=color)
    epix.label_angle(t=angle)
    mid: Point = Point(x=(tail.x1() + head.x1()) / 2, y=(tail.x2() + head.x2()) / 2)
    epix.label(at=mid, offset=offset, text=text, align=epix.LabelPos.c)
    epix.label_angle(t=0)
    epix.label_color(color=epix.black())
