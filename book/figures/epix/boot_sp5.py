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
# # boot_sp5 — rotated back: the projection of $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$
#
# The projection along $\vec{\mathbf{a}}$ (green) and the rejection across it (blue).
# The same picture as `sp5` with the names swapped. Built with `epix`; written to
# `_static/epix/boot-sp5.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _projection_scene import B_ANGLE, PROJ, SP_LOWER_LEFT, SP_UPPER_RIGHT, A, B

from gacalc.epixscene.scene2d import (
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
        head=A,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=-6, y=7),
        align=epix.LabelPos.l,
    )
    vector(
        head=B,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=9, y=2),
        align=epix.LabelPos.l,
    )
    # projection along a (green)
    epix.pen(color=GREEN, width=2.0)
    epix.arrow(tail=ORIGIN, head=PROJ, scale=0.7)
    epix.dot(at=PROJ)
    epix.label_color(color=GREEN)
    epix.label(
        at=PROJ,
        offset=Point(x=-11, y=-12),
        text=r"$\mathrm{proj}_{\vec{\mathbf{a}}}\,\vec{\mathbf{b}}$",
        align=epix.LabelPos.r,
    )
    # rejection perpendicular (blue)
    epix.pen(color=BLUE, width=2.0)
    epix.arrow(tail=PROJ, head=A, scale=0.7)
    epix.label_color(color=epix.black())
    right_angle_at(corner=PROJ, angle=B_ANGLE + math.pi / 2)

# %%
fig
