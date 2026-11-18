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
# # boot_sp3 — $\vec{\mathbf{a}}$ rotated onto the x-axis, $\vec{\mathbf{b}}$ carried along
#
# The originals faint and dashed, the rotated $\vec{\mathbf{a}}'$, $\vec{\mathbf{b}}'$
# solid. The same picture as `sp3` with the names swapped. Built with `epix`; written to
# `_static/epix/boot-sp3.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import A_ROT, B_ROT, SP_LOWER_LEFT, SP_UPPER_RIGHT, A, B
from _scene2d import ORIGIN, PendingFigure, Point, epix, unit_circle_scene, vector

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=SP_LOWER_LEFT, upper_right=SP_UPPER_RIGHT) as fig:
    # the originals, faint and dashed
    epix.pen(color=epix.black(intensity=0.55), width=1.0)
    epix.dashed()
    epix.arrow(tail=ORIGIN, head=A, scale=0.7)
    epix.arrow(tail=ORIGIN, head=B, scale=0.7)
    epix.line_style(style="-")
    epix.label_color(color=epix.black(intensity=0.55))
    epix.label(
        at=A, offset=Point(x=-6, y=7), text=r"$\vec{\mathbf{b}}$", align=epix.LabelPos.l
    )
    epix.label(
        at=B, offset=Point(x=4, y=8), text=r"$\vec{\mathbf{a}}$", align=epix.LabelPos.l
    )
    epix.label_color(color=epix.black())
    # the rotated vectors, solid
    vector(
        head=A_ROT,
        text=r"$\vec{\mathbf{b}}'$",
        offset=Point(x=7, y=4),
        align=epix.LabelPos.r,
    )
    vector(
        head=B_ROT,
        text=r"$\vec{\mathbf{a}}'$",
        offset=Point(x=2, y=-11),
        align=epix.LabelPos.c,
    )

# %%
fig
