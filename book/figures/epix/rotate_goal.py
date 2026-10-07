# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # rotate-goal — "rotate any point $\vec{a}$ about the origin by $\theta$"
#
# The goal picture of `rotate.rst` / `proof-rotate.rst`: a point $\vec{a}$ in the plane
# (drawn as a vector from the origin), its rotation $\vec{r}(\vec{a};\theta)$ by the
# angle $\theta$, the angle marked as a wedge, and the unit circle for scale. Built with
# the `epix` Python package (github.com/billsix/epix-mirror) in the style of its
# `notebooks/`; `tools/render_epix_figures.py` runs this file and writes
# `_static/epix/rotate-goal.{pdf,png}` for the book. CC0, like the hand-drawn SVG it
# replaced.

# %%
from __future__ import annotations

import math

import epix
from epix import Point
from epix.figure import _Pending as PendingFigure  # what epix.figure() yields

ORIGIN: Point = Point(x=0, y=0)
A_LENGTH: float = 1.25  # |a|: a is NOT a unit vector -- the circle is only for scale
A_ANGLE: float = math.radians(66)  # direction of a
THETA: float = math.radians(66)  # the rotation angle
WEDGE_RADIUS: float = 0.33

PURPLE: epix.Color = epix.rgb(r=0.5, g=0.0, b=0.5)
BACKGROUND: str = "#f2f2f2"  # HTML PNGs are flattened onto the disc fill
PURPLE_FILL: epix.Color = epix.rgb(r=0xDD / 255, g=0xCA / 255, b=0xD4 / 255)


def polar(radius: float, angle: float) -> Point:
    """The point at polar coordinates (radius, angle in radians)."""
    return Point(x=radius * math.cos(angle), y=radius * math.sin(angle))


a: Point = polar(radius=A_LENGTH, angle=A_ANGLE)
rotated_a: Point = polar(radius=A_LENGTH, angle=A_ANGLE + THETA)

# %%
fig: PendingFigure
with epix.figure(
    lower_left=Point(x=-1.6, y=-1.3),  # room for the r(a;theta) label at left
    upper_right=Point(x=1.5, y=1.4),
    size="3.72x3.24in",  # 1.2 in per unit on both axes
) as fig:
    epix.font_size(size="large")

    # the unit circle, filled light gray, for scale
    epix.pen(color=epix.black(intensity=0.45), width=0.9)
    epix.fill(color=epix.white(intensity=0.95))
    epix.circle(center=ORIGIN, radius=1)
    epix.nofill()

    # axes with arrowheads
    epix.pen(color=epix.black(), width=1.1)
    epix.arrow(tail=Point(x=-1.15, y=0), head=Point(x=1.3, y=0), scale=1)
    epix.arrow(tail=Point(x=0, y=-1.15), head=Point(x=0, y=1.3), scale=1)
    epix.label(
        at=Point(x=1.3, y=0), offset=Point(x=5, y=0), text="$x$", align=epix.LabelPos.r
    )
    epix.label(
        at=Point(x=0, y=1.3), offset=Point(x=5, y=-2), text="$y$", align=epix.LabelPos.r
    )

    # the angle theta as a filled wedge from a's direction to the rotated direction
    epix.pen(color=PURPLE, width=0.8)
    epix.fill(color=PURPLE_FILL)
    wedge_points: list[Point] = [ORIGIN] + [
        polar(radius=WEDGE_RADIUS, angle=A_ANGLE + THETA * i / 24) for i in range(25)
    ]
    epix.Path(data=wedge_points, closed=True, filled=True).draw()
    epix.nofill()
    epix.label_color(color=PURPLE)
    epix.label(
        at=polar(radius=0.55 * WEDGE_RADIUS, angle=A_ANGLE + THETA / 2),
        text=r"$\theta$",
    )
    epix.label_color(color=epix.black())

    # a and its rotation, as vectors from the origin with a dot at the head
    epix.pen(color=epix.black(), width=1.8)
    epix.line(tail=ORIGIN, head=a)
    epix.line(tail=ORIGIN, head=rotated_a)
    epix.dot(at=a)
    epix.dot(at=rotated_a)
    epix.label(at=a, offset=Point(x=7, y=0), text=r"$\vec{a}$", align=epix.LabelPos.r)
    epix.label(
        at=rotated_a,
        offset=Point(x=-7, y=2),
        text=r"$\vec{r}(\vec{a};\theta)$",
        align=epix.LabelPos.l,
    )

# %%
fig
