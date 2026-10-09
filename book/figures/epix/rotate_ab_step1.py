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
# # rotate_ab_step1 — swing $\vec{a}$ onto the x-axis
#
# Step 1: rotate the whole picture so $\vec{a}$ lands on the x-axis at
# $|\vec{a}| * e_1$, and $\vec{b}$ is carried to $\vec{b}'$. The faint dashed arrows are
# the originals.
# Built with `epix`; `render_epix_figures.py`. CC0.

# %%
from __future__ import annotations

from _rotate_ab_scene import A_ON_E1, B_PRIME, LOWER_LEFT, UPPER_RIGHT, A, B
from _scene2d import (
    ORIGIN,
    PendingFigure,
    Point,
    dashed_vector,
    epix,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig:
    dashed_vector(tail=ORIGIN, head=A)  # a, before
    dashed_vector(tail=ORIGIN, head=B)  # b, before
    vector(
        head=A_ON_E1,
        text=r"$|\vec{a}| * e_1$",
        offset=Point(x=4, y=-11),
        align=epix.LabelPos.c,
    )
    vector(
        head=B_PRIME, text=r"$\vec{b}'$", offset=Point(x=9, y=2), align=epix.LabelPos.l
    )

# %%
fig
