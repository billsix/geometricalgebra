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
# # sp1 — the goal: project $\vec{\mathbf{a}}$ onto the line through $\vec{\mathbf{b}}$
#
# The starting picture of the standard-position derivation: $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$, the line through $\vec{\mathbf{b}}$ (dashed), and the shadow of
# $\vec{\mathbf{a}}$ on it. Built with the `epix` package;
# `tools/render_epix_figures.py` writes `_static/epix/sp1.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import (
    LINE_HIGH,
    LINE_LOW,
    PROJ,
    SP_LOWER_LEFT,
    SP_UPPER_RIGHT,
    A,
    B,
)

from gacalc.epixscene.scene2d import (
    PendingFigure,
    Point,
    dashed_vector,
    epix,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=SP_LOWER_LEFT, upper_right=SP_UPPER_RIGHT) as fig:
    epix.pen(color=epix.black(intensity=0.5), width=0.8)
    epix.dashed()
    epix.line(tail=LINE_LOW, head=LINE_HIGH)
    epix.line_style(style="-")
    vector(
        head=A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=-6, y=7),
        align=epix.LabelPos.l,
    )
    vector(
        head=B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=6, y=-6),
        align=epix.LabelPos.r,
    )
    dashed_vector(tail=A, head=PROJ)

# %%
fig
