"""Shared ePiX helpers for the frame / QR notebooks (``frame-qr-2d`` / ``frame-qr-3d``).

The notebooks compute a ``gacalc.frame.Frame`` and draw it **live**: each figure cell
builds its scene inside ``epix.figure()`` and displays inline, with no prebuilt image.
That works because ``epix.figure()`` resets ePiX's global drawing state per figure
(github.com/billsix/epix-mirror,
``tasks/archive/2026/11/04/reset-global-state-between-figures.md``).

This module only draws: it takes plain coordinates (``list(v)`` of a gacalc vector is
its coefficient tuple), never gacalc objects, so the arithmetic stays visible in the
notebook. One colour per role, the same in every figure, and every label in its
vector's colour:

- the frame ``v_i``: blue; the orthogonal ``w_i``: green; the unit ``u_i``: purple;
- the target ``y`` and its remainders: red; the recovered coordinates ``x``: black.

``tools/render_epix_figures.py`` skips ``_``-prefixed files, so nothing here is
rendered on its own. CC0, like the other figure helpers.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager

import epix
from _scene2d import BLUE, GREEN, PURPLE, PURPLE_FILL, UNIT_SCALE_IN
from _scene3d import PendingFigure
from epix import LabelPos, Point

from gacalc.base import Real

RED: epix.Color = epix.rgb(r=0.75, g=0.0, b=0.0)
PLANE_FILL: epix.Color = epix.rgb(r=0.80, g=0.86, b=0.95)
# the unit square/cube a map starts from; an explicit RGB, because a tint of black
# fills dark in the eepic output
GRAY_FILL: epix.Color = epix.rgb(r=0.88, g=0.88, b=0.88)
# the edges of the unit cube a 3D map starts from
GRAY_EDGE: epix.Color = epix.black(intensity=0.55)
_BLACK: epix.Color = epix.black()  # hoisted out of a default arg (ruff B008)
_LABEL_OFFSET: Point = Point(x=6, y=4)
_NO_OFFSET: Point = Point(x=0, y=0)
ORIGIN2: Point = Point(x=0, y=0)
ORIGIN3: Point = Point(x=0, y=0, z=0)
# One camera for every 3D figure in the notebook, so a reader can follow the remainder
# from step to step. From here the x and y axes project well apart (about 60 degrees),
# so the plane of v_1, v_2 reads as a plane rather than a sliver.
CAMERA: Point = Point(x=5.0, y=-10.0, z=7.0)
SCALE_3D_IN: float = 0.75  # inches per projected unit in a 3D figure

__all__ = [
    "BLUE",
    "CAMERA",
    "GRAY_FILL",
    "GRAY_EDGE",
    "GREEN",
    "LabelPos",
    "ORIGIN2",
    "ORIGIN3",
    "PLANE_FILL",
    "PURPLE",
    "PURPLE_FILL",
    "RED",
    "PendingFigure",
    "Point",
    "arrow",
    "box_edges",
    "dashed_arrow",
    "note",
    "patch",
    "point",
    "right_angle",
    "scene_2d",
    "scene_3d",
]


def point(coordinates: Sequence[Real]) -> Point:
    """An ePiX point from a gacalc vector's coefficients (2 or 3 of them)."""
    floats: list[float] = [float(c) for c in coordinates]
    match floats:
        case [x, y]:
            return Point(x=x, y=y)
        case [x, y, z]:
            return Point(x=x, y=y, z=z)
        case _:
            raise ValueError(f"expected 2 or 3 coordinates, got {len(floats)}")


@contextmanager
def scene_2d(lower_left: Point, upper_right: Point) -> Iterator[PendingFigure]:
    """A 2D figure with light, unlabelled axes, at the book's 2D scale.

    The axes carry no ``x``/``y`` labels: in these notebooks ``x`` and ``y`` name
    vectors (the coordinates and the target of the frame's map)."""
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * UNIT_SCALE_IN:.2f}x{height * UNIT_SCALE_IN:.2f}in"
    fig: PendingFigure
    with epix.figure(lower_left=lower_left, upper_right=upper_right, size=size) as fig:
        epix.font_size(size="large")
        epix.pen(color=epix.black(intensity=0.5), width=0.8)
        epix.arrow(
            tail=Point(x=lower_left.x1() + 0.2, y=0),
            head=Point(x=upper_right.x1() - 0.15, y=0),
            scale=0.6,
        )
        epix.arrow(
            tail=Point(x=0, y=lower_left.x2() + 0.15),
            head=Point(x=0, y=upper_right.x2() - 0.1),
            scale=0.6,
        )
        yield fig


@contextmanager
def scene_3d(
    lower_left: Point, upper_right: Point, scale_in: float = SCALE_3D_IN
) -> Iterator[PendingFigure]:
    """A 3D figure seen from :data:`CAMERA`, with light, unlabelled axes (as in
    :func:`scene_2d`, ``x`` and ``y`` name vectors here).

    ``scale_in`` is inches per projected unit; the 3D frames are larger than the
    book's other 3D figures, so the default is smaller than ``_scene3d``'s."""
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * scale_in:.2f}x{height * scale_in:.2f}in"
    fig: PendingFigure
    with epix.figure(lower_left=lower_left, upper_right=upper_right, size=size) as fig:
        epix.font_size(size="large")
        epix.camera.at(CAMERA)
        epix.pen(color=epix.black(intensity=0.5), width=0.8)
        axis: Point
        for axis in (
            Point(x=4.8, y=0, z=0),
            Point(x=0, y=3.8, z=0),
            Point(x=0, y=0, z=3.0),
        ):
            epix.arrow(tail=ORIGIN3, head=axis, scale=0.6)
        yield fig


def arrow(
    head: Point,
    tail: Point = ORIGIN2,
    color: epix.Color = _BLACK,
    text: str = "",
    offset: Point = _LABEL_OFFSET,
    align: epix.LabelPos = epix.LabelPos.r,
    width: float = 1.6,
) -> None:
    """A solid arrow ``tail`` -> ``head`` (from the origin by default), labelled in its
    own colour. Works in 2D and 3D: an ePiX point always has a third coordinate, so
    the 2D origin is the 3D one."""
    epix.pen(color=color, width=width)
    epix.arrow(tail=tail, head=head, scale=0.7)
    if text:
        epix.label_color(color=color)
        epix.label(at=head, offset=offset, text=text, align=align)
        epix.label_color(color=epix.black())


def dashed_arrow(
    tail: Point,
    head: Point,
    color: epix.Color = _BLACK,
    text: str = "",
    offset: Point = _LABEL_OFFSET,
    align: epix.LabelPos = epix.LabelPos.r,
) -> None:
    """A dashed arrow ``tail`` -> ``head``: a translated copy, or a drop to a line."""
    epix.dashed()
    arrow(
        head=head,
        tail=tail,
        color=color,
        text=text,
        offset=offset,
        align=align,
        width=1.1,
    )
    epix.line_style(style="-")  # back to solid for whatever draws next


def note(
    at: Point,
    text: str,
    color: epix.Color = _BLACK,
    offset: Point = _NO_OFFSET,
    align: epix.LabelPos = epix.LabelPos.c,
) -> None:
    """A label at any point (a length beside a dashed line, an equation over the
    scene), in the colour of what it describes."""
    epix.label_color(color=color)
    epix.label(at=at, offset=offset, text=text, align=align)
    epix.label_color(color=epix.black())


def patch(corners: Sequence[Point], color: epix.Color = PLANE_FILL) -> None:
    """A light-filled polygon (a parallelogram, a box face, a plane patch)."""
    epix.pen(color=epix.black(intensity=0.6), width=0.5)
    epix.fill(color=color)
    epix.Path(data=list(corners), closed=True, filled=True).draw()
    epix.nofill()


def right_angle(
    corner: Point, toward_a: Point, toward_b: Point, size: float = 0.18
) -> None:
    """A right-angle square at ``corner`` with legs along the directions ``toward_a``
    and ``toward_b`` (which must be perpendicular). 2D or 3D."""
    unit_a: Point = (size / toward_a.norm()) * toward_a
    unit_b: Point = (size / toward_b.norm()) * toward_b
    epix.pen(color=epix.black(), width=0.8)
    epix.line(tail=corner + unit_a, head=corner + unit_a + unit_b)
    epix.line(tail=corner + unit_a + unit_b, head=corner + unit_b)


def box_edges(
    a: Point, b: Point, c: Point, color: epix.Color = _BLACK, width: float = 0.9
) -> None:
    """The 12 edges of the parallelepiped spanned by ``a``, ``b`` and ``c`` (a unit
    cube when they are the basis vectors)."""
    epix.pen(color=color, width=width)
    edge: Point
    first: Point
    second: Point
    corner: Point
    # each edge direction starts from the four corners the other two directions span
    for edge, first, second in ((a, b, c), (b, a, c), (c, a, b)):
        for corner in (ORIGIN3, first, second, first + second):
            epix.line(tail=corner, head=corner + edge)
