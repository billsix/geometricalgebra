"""Shared scene for the "rotation is deformed graph paper" figures (``graphpaper1``–5).

One picture built across the sequence: a 4×4 grid of points ``{0,1,2,3}²`` and the
graph-paper grid lines, rotated by ``ANGLE`` (30°) about the origin — rotating isn't
moving points one by one, it's **turning the sheet of graph paper**, and the points
come along. The last figure plots ``y = x²`` on the rotated frame, to connect to
high-school graphing. Constants live here so every figure agrees; the ``_scene2d``
helpers are re-exported so each figure imports from one place.

Every call passes its arguments by keyword (the ``check_epix_keywords`` gate).
"""

from __future__ import annotations

import math

from _scene2d import (
    BACKGROUND,
    BLUE,
    GREEN,
    ORIGIN,
    PendingFigure,
    Point,
    epix,
    polar,
    unit_circle_scene,
    vector,
)

__all__: list[str] = [
    "ANGLE",
    "COORDS",
    "FAINT",
    "BLUE",
    "GREEN",
    "BACKGROUND",
    "ORIGIN",
    "PendingFigure",
    "Point",
    "epix",
    "polar",
    "vector",
    "unit_circle_scene",
    "rotate",
    "grid_points",
    "draw_grid",
    "parabola_points",
]

ANGLE: float = math.radians(30)  # the demo rotation angle
COORDS: list[int] = [0, 1, 2, 3]  # the 4x4 grid {0,1,2,3}^2
# the original (unrotated) paper, drawn faint under the rotated one
FAINT: epix.Color = epix.black(intensity=0.35)


def rotate(point: Point, angle: float) -> Point:
    """Rotate ``point`` about the origin by ``angle`` radians."""
    cos_a: float = math.cos(angle)
    sin_a: float = math.sin(angle)
    return Point(
        x=point.x1() * cos_a - point.x2() * sin_a,
        y=point.x1() * sin_a + point.x2() * cos_a,
    )


def grid_points(angle: float = 0.0) -> list[Point]:
    """The 16 grid points ``{0,1,2,3}²``, each rotated about the origin by ``angle``."""
    return [
        rotate(point=Point(x=float(i), y=float(j)), angle=angle)
        for j in COORDS
        for i in COORDS
    ]


def draw_grid(
    angle: float = 0.0,
    color: epix.Color = FAINT,
    width: float = 0.7,
    dots: bool = True,
) -> None:
    """Draw the grid lines (and, by default, the points), rotated by ``angle``."""
    low: float = float(COORDS[0])
    high: float = float(COORDS[-1])
    epix.pen(color=color, width=width)
    for i in COORDS:
        line: float = float(i)
        epix.line(
            tail=rotate(point=Point(x=line, y=low), angle=angle),
            head=rotate(point=Point(x=line, y=high), angle=angle),
        )
        epix.line(
            tail=rotate(point=Point(x=low, y=line), angle=angle),
            head=rotate(point=Point(x=high, y=line), angle=angle),
        )
    if dots:
        for grid_point in grid_points(angle=angle):
            epix.dot(at=grid_point)


def parabola_points(
    angle: float, x_min: float, x_max: float, steps: int = 40
) -> list[Point]:
    """``y = x²`` over ``[x_min, x_max]``, placed in the frame rotated by ``angle`` (so
    the curve sits on the rotated graph paper, at frame coordinates ``(x, x²)``)."""
    xs: list[float] = [
        x_min + (x_max - x_min) * step / steps for step in range(steps + 1)
    ]
    return [rotate(point=Point(x=x, y=x * x), angle=angle) for x in xs]
