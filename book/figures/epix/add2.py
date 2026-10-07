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
# # add2 — tip-to-tail: $\vec{a}+\vec{b}$
#
# Vector addition drawn tip-to-tail: slide $\vec{b}$ (dashed) so its tail sits on the
# head of $\vec{a}$; the sum $\vec{a}+\vec{b}$ runs from the origin to where the slid
# copy ends. Built with the `epix` package in the style of epix-mirror's `notebooks/`;
# `tools/render_epix_figures.py` writes `_static/epix/add2.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _addition_scene import A_PLUS_B, ADD_LOWER_LEFT, ADD_UPPER_RIGHT, A
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
    lower_left=ADD_LOWER_LEFT, upper_right=ADD_UPPER_RIGHT, disc=False
) as fig:
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=7, y=-3), align=epix.LabelPos.r)
    # b slid to start at a's head (a translated copy, so dashed)
    dashed_vector(
        tail=A,
        head=A_PLUS_B,
        text=r"$\vec{b}$",
        offset=Point(x=8, y=2),
        align=epix.LabelPos.l,
    )
    vector(
        head=A_PLUS_B,
        text=r"$\vec{a}+\vec{b}$",
        offset=Point(x=-6, y=9),
        align=epix.LabelPos.l,
    )

# %%
fig
