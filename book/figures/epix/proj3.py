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
# # proj3 — $\vec{a}=\mathrm{proj}+\mathrm{rej}$
#
# Projection and rejection add up tip-to-tail to $\vec{a}$: go along $\vec{b}$ to the
# foot (blue), then perpendicular up to $\vec{a}$ (green), and you have arrived at
# $\vec{a}$.
# Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/proj3.{pdf,png}`. CC0.

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
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=-7, y=6), align=epix.LabelPos.l)
    # projection (blue) then rejection (green), tip-to-tail
    epix.pen(color=BLUE, width=2.0)
    epix.line(tail=ORIGIN, head=PROJ)
    epix.dot(at=PROJ)
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=PROJ, head=A)
    epix.label_color(color=epix.black())
    epix.label(
        at=PROJ,
        offset=Point(x=0, y=-12),
        text=(
            r"$\vec{a}=\mathrm{proj}_{\vec{b}}\,\vec{a}"
            r"+\mathrm{rej}_{\vec{b}}\,\vec{a}$"
        ),
        align=epix.LabelPos.c,
    )

# %%
fig
