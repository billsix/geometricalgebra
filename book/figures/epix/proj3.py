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
# # proj3 — $\vec{\mathbf{a}}=\mathrm{proj}+\mathrm{rej}$
#
# Projection and rejection add up tip-to-tail to $\vec{\mathbf{a}}$: go along
# $\vec{\mathbf{b}}$ to the foot (blue), then perpendicular up to $\vec{\mathbf{a}}$
# (green), and you have arrived at $\vec{\mathbf{a}}$. Built with the `epix` package;
# `tools/render_epix_figures.py` writes `_static/epix/proj3.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import PROJ, PROJ_LOWER_LEFT, PROJ_UPPER_RIGHT, A
from _scene2d import (
    BLUE,
    GREEN,
    ORIGIN,
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=PROJ_LOWER_LEFT, upper_right=PROJ_UPPER_RIGHT, disc=False
) as fig:
    # Label the a vector itself with the identity it satisfies (NOT down on the
    # projection segment, where it reads as the projection's label).
    vector(
        head=A,
        text=(
            r"$\vec{\mathbf{a}}=\mathrm{proj}_{\vec{\mathbf{b}}}\,\vec{\mathbf{a}}"
            r"+\mathrm{rej}_{\vec{\mathbf{b}}}\,\vec{\mathbf{a}}$"
        ),
        offset=Point(x=-4, y=12),
        align=epix.LabelPos.r,
    )
    # projection (blue) then rejection (green), tip-to-tail
    epix.pen(color=BLUE, width=2.0)
    epix.arrow(tail=ORIGIN, head=PROJ, scale=0.7)
    epix.dot(at=PROJ)
    epix.pen(color=GREEN, width=2.0)
    epix.arrow(tail=PROJ, head=A, scale=0.7)
    epix.label_color(color=epix.black())

# %%
fig
