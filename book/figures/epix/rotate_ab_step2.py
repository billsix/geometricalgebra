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
# # rotate_ab_step2 — in standard position, rotate $\vec{\mathbf{e}}_1$ onto $\vec{\mathbf{b}}'$
#
# Step 2: with $\vec{\mathbf{a}}$ on the x-axis, rotate $\vec{\mathbf{e}}_1$ up onto
# $\vec{\mathbf{b}}'$ by the angle $\theta$ — read straight off $\vec{\mathbf{b}}'$'s
# coordinates (its cosine and sine). Built with `epix`; `render_epix_figures.py`. CC0.

# %%
from __future__ import annotations

from _rotate_ab_scene import A_ANGLE, A_ON_E1, B_ANGLE, B_PRIME, LOWER_LEFT, UPPER_RIGHT

from gacalc.epixscene.scene2d import (
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig:
    wedge(start=0.0, finish=B_ANGLE - A_ANGLE, text=r"$\theta$", radius=0.42)
    vector(
        head=A_ON_E1,
        text=r"$|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=4, y=-11),
        align=epix.LabelPos.c,
    )
    vector(
        head=B_PRIME,
        text=r"$\vec{\mathbf{b}}'$",
        offset=Point(x=9, y=2),
        align=epix.LabelPos.l,
    )

# %%
fig
