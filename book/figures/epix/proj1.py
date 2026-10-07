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
# # proj1 — the shadow of $\vec{a}$ on the line through $\vec{b}$
#
# The setup for projection: $\vec{a}$ and $\vec{b}$ from the origin, the line through
# $\vec{b}$ (dashed), and the foot of the perpendicular dropped from $\vec{a}$ onto that
# line. Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/proj1.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import (
    LINE_HIGH,
    LINE_LOW,
    PROJ,
    PROJ_LOWER_LEFT,
    PROJ_UPPER_RIGHT,
    A,
    B,
)
from _scene2d import (
    PendingFigure,
    Point,
    dashed_vector,
    epix,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=PROJ_LOWER_LEFT, upper_right=PROJ_UPPER_RIGHT, disc=False
) as fig:
    # the infinite line through b, drawn dashed and gray
    epix.pen(color=epix.black(intensity=0.5), width=0.8)
    epix.dashed()
    epix.line(tail=LINE_LOW, head=LINE_HIGH)
    epix.line_style(style="-")
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=-6, y=7), align=epix.LabelPos.l)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=6, y=-6), align=epix.LabelPos.r)
    # the perpendicular dropped from a to its foot on the line
    dashed_vector(tail=A, head=PROJ)

# %%
fig
