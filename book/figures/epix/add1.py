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
# # add1 — two vectors $\vec{a}$ and $\vec{b}$
#
# The starting picture of `vector-addition.rst`: two vectors drawn from the origin,
# before we add them. Built with the `epix` Python package
# (github.com/billsix/epix-mirror) in the style of its `notebooks/`;
# `tools/render_epix_figures.py` writes `_static/epix/add1.{pdf,png}` for the book. CC0,
# like the hand-drawn SVGs it replaces.

# %%
from __future__ import annotations

from _addition_scene import ADD_LOWER_LEFT, ADD_UPPER_RIGHT, A, B
from _scene2d import PendingFigure, Point, epix, unit_circle_scene, vector

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=ADD_LOWER_LEFT, upper_right=ADD_UPPER_RIGHT, disc=False
) as fig:
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=7, y=-3), align=epix.LabelPos.r)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-5, y=7), align=epix.LabelPos.l)

# %%
fig
