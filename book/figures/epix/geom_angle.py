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
# # geom_angle — an angle, its measure, and the triangle's area
#
# The angle picture of `product-from-projection.rst`: the angle at the vertex
# $\vec{\mathbf{b}}$ between the rays toward $\vec{\mathbf{a}}$ and toward
# $\vec{\mathbf{c}}$, along $\vec{\mathbf{u}} = \vec{\mathbf{a}} - \vec{\mathbf{b}}$
# and $\vec{\mathbf{v}} = \vec{\mathbf{c}} - \vec{\mathbf{b}}$, its measure $\theta$,
# and the triangle the two sides close, whose area is half the parallelogram's. Built
# with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/geom-angle.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _geometry_scene import (
    ANG_A,
    ANG_B,
    ANG_C,
    ANG_LOWER_LEFT,
    ANG_UPPER_RIGHT,
)

from gacalc.epixscene.scene2d import (
    BLUE,
    GREEN,
    PURPLE,
    PURPLE_FILL,
    PendingFigure,
    Point,
    epix,
    polar,
    unit_circle_scene,
)

# %%
U: Point = ANG_A - ANG_B
V: Point = ANG_C - ANG_B
START: float = math.atan2(U.x2(), U.x1())
FINISH: float = math.atan2(V.x2(), V.x1())
fig: PendingFigure
with unit_circle_scene(
    lower_left=ANG_LOWER_LEFT, upper_right=ANG_UPPER_RIGHT, disc=False, basis=False
) as fig:
    # the triangle the two sides close
    epix.pen(color=epix.black(intensity=0.6), width=0.6)
    epix.fill(color=PURPLE_FILL)
    epix.Path(data=[ANG_B, ANG_A, ANG_C], closed=True, filled=True).draw()
    epix.nofill()
    epix.label_color(color=PURPLE)
    epix.label(
        at=(1 / 3) * (ANG_A + ANG_B + ANG_C) + Point(x=0.15, y=0.0),
        text=r"$\frac{1}{2} * |\vec{\mathbf{u}} \wedge \vec{\mathbf{v}}|$",
    )
    # the angle's measure, an arc at the vertex
    epix.pen(color=PURPLE, width=1.0)
    arc: list[Point] = [
        ANG_B + polar(radius=0.3, angle=START + (FINISH - START) * i / 24)
        for i in range(25)
    ]
    epix.Path(data=arc, closed=False, filled=False).draw()
    epix.label(
        at=ANG_B + polar(radius=0.42, angle=(START + FINISH) / 2),
        text=r"$\theta$",
    )
    # the two sides of the angle, from the vertex
    epix.pen(color=GREEN, width=1.8)
    epix.arrow(tail=ANG_B, head=ANG_A, scale=0.7)
    epix.label_color(color=GREEN)
    epix.label(
        at=ANG_B + 0.6 * U,
        offset=Point(x=0, y=-8),
        text=r"$\vec{\mathbf{u}} = \vec{\mathbf{a}} - \vec{\mathbf{b}}$",
        align=epix.LabelPos.b,
    )
    epix.pen(color=BLUE, width=1.8)
    epix.arrow(tail=ANG_B, head=ANG_C, scale=0.7)
    epix.label_color(color=BLUE)
    epix.label(
        at=ANG_C,
        offset=Point(x=0, y=6),
        text=r"$\vec{\mathbf{v}} = \vec{\mathbf{c}} - \vec{\mathbf{b}}$",
        align=epix.LabelPos.t,
    )
    epix.label_color(color=epix.black())
    epix.dot(
        at=ANG_B,
        offset=Point(x=-4, y=-4),
        text=r"$\vec{\mathbf{b}}$",
        align=epix.LabelPos.bl,
    )

# %%
fig
