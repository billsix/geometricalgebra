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
# # boot_sp4 — in standard position, keep the x-coordinate
#
# With $\vec{\mathbf{a}}$ on the x-axis, the projection of $\vec{\mathbf{b}}'$ is its
# x-coordinate (green) and the rejection its y-coordinate (blue). The same picture as
# `sp4` with the names swapped. Built with `epix`; written to
# `_static/epix/boot-sp4.{pdf,png}`. CC0.

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
        head=A_ROT,
        text=r"$\vec{\mathbf{b}}'$",
        offset=Point(x=7, y=4),
        align=epix.LabelPos.r,
    )
    vector(
        head=B_ROT,
        text=r"$\vec{\mathbf{a}}'$",
        offset=Point(x=7, y=-10),
        align=epix.LabelPos.l,
    )
    # projection = x-coordinate of b', green along the x-axis
    epix.pen(color=GREEN, width=2.0)
    epix.arrow(tail=ORIGIN, head=PROJ_ROT, scale=0.7)
    epix.dot(at=PROJ_ROT)
    epix.label_color(color=GREEN)
    # under the middle of the arrow, clear of the labels at its tip
    epix.label(
        at=0.5 * PROJ_ROT,
        offset=Point(x=0, y=-6),
        text=r"$b'_1$",
        align=epix.LabelPos.b,
    )
    # rejection = y-coordinate of b', blue and vertical
    epix.pen(color=BLUE, width=2.0)
    epix.arrow(tail=PROJ_ROT, head=A_ROT, scale=0.7)
    epix.label_color(color=BLUE)
    mid: Point = Point(
        x=(PROJ_ROT.x1() + A_ROT.x1()) / 2, y=(PROJ_ROT.x2() + A_ROT.x2()) / 2
    )
    epix.label(at=mid, offset=Point(x=6, y=0), text=r"$b'_2$", align=epix.LabelPos.r)
    epix.label_color(color=epix.black())
    right_angle_at(corner=PROJ_ROT, angle=math.pi / 2)

# %%
fig
