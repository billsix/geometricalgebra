"""Live ePiX helpers for the Part III notebooks (``bootstrap-*.py``).

Each notebook sets its vectors in one cell, computes every step from them with
gacalc, and draws each step **live** in its own cell, as the frame / QR notebooks do
(see :mod:`_frame_scene`, whose primitives this module re-exports). A reader who
changes the vectors and reruns gets new pictures, so :func:`scene_around` sizes each
figure from the points it has to show (with ``epix.fit_bounds``) rather than from
fixed bounds.

The colours follow the Part III figures: the given vectors black, projections and
the cosine parts green, rejections and the sine parts blue, results purple, and every
label in the colour of what it labels.

``tools/render_epix_figures.py`` skips ``_``-prefixed files, so nothing here is
rendered on its own. CC0, like the other figure helpers.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager

import epix
from _frame_scene import (
    BLUE,
    GREEN,
    ORIGIN2,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    right_angle,
)
from _scene2d import BACKGROUND

__all__: list[str] = [
    "BLACK",
    "BLUE",
    "GREEN",
    "ORIGIN2",
    "PURPLE",
    "LabelPos",
    "PendingFigure",
    "Point",
    "arrow",
    "dashed_arrow",
    "note",
    "point",
    "right_angle",
    "scene_around",
]

BLACK: epix.Color = epix.black()
_MARGIN: float = 0.18  # fraction of the larger extent left around the points
_WIDTH_IN: float = 3.4  # every figure is this wide, whatever the vectors' size


@contextmanager
def scene_around(points: Sequence[Point]) -> Iterator[PendingFigure]:
    """A 2D figure that fits ``points`` and the origin, with light, unlabelled axes.

    The figure is always :data:`_WIDTH_IN` wide with equal scales on both axes, so a
    long vector shrinks the picture instead of overflowing it. ``epix.fit_bounds``
    computes the box and size; the box is needed here too, to draw the axes across
    it."""
    lower_left: Point
    upper_right: Point
    size: str
    lower_left, upper_right, size = epix.fit_bounds(
        points=[ORIGIN2, *points], width=_WIDTH_IN, margin=_MARGIN
    )
    fig: PendingFigure
    with epix.figure(
        lower_left=lower_left,
        upper_right=upper_right,
        size=size,
        background=BACKGROUND,
    ) as fig:
        epix.font_size(size="large")
        epix.pen(color=epix.black(intensity=0.5), width=0.8)
        epix.arrow(
            tail=Point(x=lower_left.x1(), y=0),
            head=Point(x=upper_right.x1(), y=0),
            scale=0.6,
        )
        epix.arrow(
            tail=Point(x=0, y=lower_left.x2()),
            head=Point(x=0, y=upper_right.x2()),
            scale=0.6,
        )
        yield fig
