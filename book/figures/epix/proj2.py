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
# # proj2 — projection (along $\vec{b}$) and rejection (perpendicular)
#
# The projection of $\vec{a}$ onto $\vec{b}$ (blue, along $\vec{b}$) and the rejection
# (green, perpendicular), meeting at a right angle. Built with the `epix` package;
# `tools/render_epix_figures.py` writes `_static/epix/proj2.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _projection_scene import B_ANGLE, PROJ, PROJ_LOWER_LEFT, PROJ_UPPER_RIGHT, A, B
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
with unit_circle_scene(
    lower_left=PROJ_LOWER_LEFT, upper_right=PROJ_UPPER_RIGHT, disc=False
) as fig:
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=-6, y=7), align=epix.LabelPos.l)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=6, y=-6), align=epix.LabelPos.r)
    # projection: blue, from the origin along b to the foot
    epix.pen(color=BLUE, width=2.0)
    epix.line(tail=ORIGIN, head=PROJ)
    epix.dot(at=PROJ)
    epix.label_color(color=BLUE)
    epix.label(
        at=PROJ,
        offset=Point(x=2, y=-11),
        text=r"$\mathrm{proj}_{\vec{b}}\,\vec{a}$",
        align=epix.LabelPos.c,
    )
    # rejection: green, from the foot up to a (perpendicular to b)
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=PROJ, head=A)
    epix.label_color(color=GREEN)
    mid: Point = Point(x=(PROJ.x1() + A.x1()) / 2, y=(PROJ.x2() + A.x2()) / 2)
    epix.label(
        at=mid,
        offset=Point(x=9, y=2),
        text=r"$\mathrm{rej}_{\vec{b}}\,\vec{a}$",
        align=epix.LabelPos.l,
    )
    epix.label_color(color=epix.black())
    # the right angle at the foot, between the line (toward O) and the rejection
    right_angle_at(corner=PROJ, angle=B_ANGLE + math.pi / 2)

# %%
fig
