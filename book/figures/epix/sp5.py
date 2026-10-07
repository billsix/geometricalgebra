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
# # sp5 — rotate back: the projection and rejection of the original $\vec{a}$
#
# Undo the rotation by $+\varphi$ and the coordinate split from `sp4` lands exactly
# on the projection (blue) and rejection (green) of the original $\vec{a}$ onto
# $\vec{b}$ — the same answer the geometric-algebra formula gives. Built with the
# `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/sp5.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _projection_scene import B_ANGLE, PROJ, SP_LOWER_LEFT, SP_UPPER_RIGHT, A, B
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
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=-6, y=7), align=epix.LabelPos.l)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=6, y=-6), align=epix.LabelPos.r)
    # projection along b (blue)
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
    # rejection perpendicular (green)
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=PROJ, head=A)
    epix.label_color(color=epix.black())
    right_angle_at(corner=PROJ, angle=B_ANGLE + math.pi / 2)

# %%
fig
