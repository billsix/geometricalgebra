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
# # sp4 — in standard position the projection is just a coordinate
#
# With $\vec{b}'$ on the x-axis, projecting onto it is trivial: the projection of
# $\vec{a}'$ is its x-coordinate (blue), and the rejection is its y-coordinate (green).
# Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/sp4.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _projection_scene import A_ROT, B_ROT, PROJ_ROT, SP_LOWER_LEFT, SP_UPPER_RIGHT
from _scene2d import (
    BLUE,
    GREEN,
    ORIGIN,
    PendingFigure,
    Point,
    epix,
    right_angle_at,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=SP_LOWER_LEFT, upper_right=SP_UPPER_RIGHT) as fig:
    vector(
        head=A_ROT, text=r"$\vec{a}'$", offset=Point(x=7, y=4), align=epix.LabelPos.r
    )
    vector(
        head=B_ROT, text=r"$\vec{b}'$", offset=Point(x=7, y=-10), align=epix.LabelPos.l
    )
    # projection = x-coordinate of a', blue along the x-axis
    epix.pen(color=BLUE, width=2.0)
    epix.line(tail=ORIGIN, head=PROJ_ROT)
    epix.dot(at=PROJ_ROT)
    epix.label_color(color=BLUE)
    epix.label(
        at=PROJ_ROT, offset=Point(x=-6, y=-12), text=r"$a'_1$", align=epix.LabelPos.r
    )
    # rejection = y-coordinate of a', green and vertical
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=PROJ_ROT, head=A_ROT)
    epix.label_color(color=GREEN)
    mid: Point = Point(
        x=(PROJ_ROT.x1() + A_ROT.x1()) / 2, y=(PROJ_ROT.x2() + A_ROT.x2()) / 2
    )
    epix.label(at=mid, offset=Point(x=9, y=0), text=r"$a'_2$", align=epix.LabelPos.l)
    epix.label_color(color=epix.black())
    right_angle_at(corner=PROJ_ROT, angle=math.pi / 2)

# %%
fig
