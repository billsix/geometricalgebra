"""Shared 3D scene helpers for the book's projection-in-3D figures (``proj3d_*``).

ePiX projects 3D through a camera, so a figure sets the camera once and draws 3D points
(``Point(x=, y=, z=)``); these helpers give the whole section one camera, one vector
:math:`\\vec{a}`, a light-filled coordinate-plane patch per plane, 3D axes, a 3D vector,
and a right-angle marker in space. The coordinate planes are named the book's way ---
``e_12`` (the xy-plane), ``e_23`` (yz) and ``e_31`` (zx). CC0, like the hand-drawn SVGs
these replace.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import epix
from _scene2d import BLUE, GREEN
from epix import Point
from epix.figure import _Pending as PendingFigure

__all__: list[str] = [
    "CAMERA",
    "FRAME_LOWER_LEFT",
    "FRAME_UPPER_RIGHT",
    "AX",
    "AY",
    "AZ",
    "A",
    "ORIGIN3",
    "BLUE",
    "GREEN",
    "PendingFigure",
    "Point",
    "epix",
    "frame_scene",
    "axes3",
    "plane3",
    "vector3",
    "project_onto",
    "right_angle_3d",
]

CAMERA: Point = Point(x=9.0, y=-6.0, z=5.0)  # a +x, -y, +z view: x forward-right, z up
FRAME_LOWER_LEFT: Point = Point(x=-1.3, y=-1.1)
FRAME_UPPER_RIGHT: Point = Point(x=2.1, y=2.3)
UNIT_SCALE_IN: float = 1.25  # inches per projected unit, kept equal on both axes

AX: float = 1.0  # the one vector a the whole section uses
AY: float = 0.7
AZ: float = 0.9
A: Point = Point(x=AX, y=AY, z=AZ)

ORIGIN3: Point = Point(x=0.0, y=0.0, z=0.0)
_AXIS_X: Point = Point(x=1.8, y=0.0, z=0.0)
_AXIS_Y: Point = Point(x=0.0, y=1.8, z=0.0)
_AXIS_Z: Point = Point(x=0.0, y=0.0, z=1.5)
# the square patch each plane is drawn as, in its own two coordinates
_PATCH_LOW: float = -0.3
_PATCH_HIGH: float = 1.6
_PLANE_FILL: epix.Color = epix.rgb(r=0.80, g=0.86, b=0.95)
_BLACK: epix.Color = epix.black()  # hoisted out of a default arg (ruff B008)
_VEC3_LABEL_OFFSET: Point = Point(x=5, y=4)


@contextmanager
def frame_scene(
    camera: Point = CAMERA,
    lower_left: Point = FRAME_LOWER_LEFT,
    upper_right: Point = FRAME_UPPER_RIGHT,
) -> Iterator[PendingFigure]:
    """``epix.figure`` with the 3D camera set. The body draws the plane patch first (so
    it sits behind), then calls ``axes3()``, then the vectors."""
    width: float = upper_right.x1() - lower_left.x1()
    height: float = upper_right.x2() - lower_left.x2()
    size: str = f"{width * UNIT_SCALE_IN:.2f}x{height * UNIT_SCALE_IN:.2f}in"
    fig: PendingFigure
    with epix.figure(lower_left=lower_left, upper_right=upper_right, size=size) as fig:
        epix.font_size(size="large")
        epix.camera.at(camera)
        yield fig


def axes3() -> None:
    """The three axes as arrows from the origin, with labels x, y, z."""
    epix.pen(color=epix.black(), width=1.1)
    epix.arrow(tail=ORIGIN3, head=_AXIS_X, scale=1)
    epix.arrow(tail=ORIGIN3, head=_AXIS_Y, scale=1)
    epix.arrow(tail=ORIGIN3, head=_AXIS_Z, scale=1)
    epix.label(at=_AXIS_X, offset=Point(x=4, y=-5), text="$x$", align=epix.LabelPos.r)
    epix.label(at=_AXIS_Y, offset=Point(x=6, y=-2), text="$y$", align=epix.LabelPos.r)
    epix.label(at=_AXIS_Z, offset=Point(x=-2, y=7), text="$z$", align=epix.LabelPos.t)


def plane3(plane: str, faint: bool = False) -> None:
    """A light-filled square patch of the named plane (``e_12``/``e_23``/``e_31``).

    ``faint=True`` draws it lighter, for the overview showing all three at once."""
    lo: float = _PATCH_LOW
    hi: float = _PATCH_HIGH
    if plane == "e_12":  # the xy-plane, z = 0
        corners: list[Point] = [
            Point(x=lo, y=lo, z=0.0),
            Point(x=hi, y=lo, z=0.0),
            Point(x=hi, y=hi, z=0.0),
            Point(x=lo, y=hi, z=0.0),
        ]
    elif plane == "e_23":  # the yz-plane, x = 0
        corners = [
            Point(x=0.0, y=lo, z=lo),
            Point(x=0.0, y=hi, z=lo),
            Point(x=0.0, y=hi, z=hi),
            Point(x=0.0, y=lo, z=hi),
        ]
    elif plane == "e_31":  # the zx-plane, y = 0
        corners = [
            Point(x=lo, y=0.0, z=lo),
            Point(x=hi, y=0.0, z=lo),
            Point(x=hi, y=0.0, z=hi),
            Point(x=lo, y=0.0, z=hi),
        ]
    else:
        raise ValueError(f"unknown plane {plane!r}: expected e_12, e_23 or e_31")
    intensity: float = 0.25 if faint else 0.5
    epix.pen(color=epix.black(intensity=intensity), width=0.5)
    fill: epix.Color = epix.rgb(r=0.90, g=0.93, b=0.97) if faint else _PLANE_FILL
    epix.fill(color=fill)
    epix.Path(data=corners, closed=True, filled=True).draw()
    epix.nofill()


def project_onto(plane: str) -> Point:
    """The projection of :data:`A` onto the named plane (drop the third axis)."""
    if plane == "e_12":
        return Point(x=AX, y=AY, z=0.0)
    if plane == "e_23":
        return Point(x=0.0, y=AY, z=AZ)
    if plane == "e_31":
        return Point(x=AX, y=0.0, z=AZ)
    raise ValueError(f"unknown plane {plane!r}: expected e_12, e_23 or e_31")


def vector3(
    head: Point,
    color: epix.Color = _BLACK,
    width: float = 1.8,
    text: str = "",
    offset: Point = _VEC3_LABEL_OFFSET,
    align: epix.LabelPos = epix.LabelPos.l,
) -> None:
    """A 3D segment from the origin to ``head``, with a dot and an optional label."""
    epix.pen(color=color, width=width)
    epix.line(tail=ORIGIN3, head=head)
    epix.dot(at=head)
    if text:
        epix.label_color(color=color)
        epix.label(at=head, offset=offset, text=text, align=align)
        epix.label_color(color=epix.black())


def right_angle_3d(
    corner: Point, toward_a: Point, toward_b: Point, size: float = 0.14
) -> None:
    """A right-angle square at ``corner``, its two (perpendicular) legs along the
    directions ``toward_a`` and ``toward_b``, scaled to ``size``."""
    unit_a: Point = (size / toward_a.norm()) * toward_a
    unit_b: Point = (size / toward_b.norm()) * toward_b
    corner_a: Point = corner + unit_a
    corner_b: Point = corner + unit_b
    corner_ab: Point = corner + unit_a + unit_b
    epix.pen(color=epix.black(), width=0.9)
    epix.line(tail=corner_a, head=corner_ab)
    epix.line(tail=corner_ab, head=corner_b)
