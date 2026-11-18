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
# # boot_sp2 — the angle $\theta$ that $\vec{\mathbf{a}}$ makes with the x-axis
#
# Part III's Step 2 projects $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$; rotating by
# $-\theta$ lays $\vec{\mathbf{a}}$ on the x-axis. The same picture as `sp2` with the
# names swapped. Built with `epix`; written to `_static/epix/boot-sp2.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import B_ANGLE, SP_LOWER_LEFT, SP_UPPER_RIGHT, A, B
from _scene2d import PendingFigure, Point, epix, unit_circle_scene, vector, wedge

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=SP_LOWER_LEFT, upper_right=SP_UPPER_RIGHT) as fig:
    wedge(start=0.0, finish=B_ANGLE, text=r"$\theta$", radius=0.45)
    vector(
        head=A,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=-6, y=7),
        align=epix.LabelPos.l,
    )
    vector(
        head=B,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=6, y=-6),
        align=epix.LabelPos.r,
    )

# %%
fig
