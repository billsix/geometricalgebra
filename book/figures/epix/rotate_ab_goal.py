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
# # rotate_ab_goal — rotate $\vec{\mathbf{a}}$'s direction onto $\vec{\mathbf{b}}$'s
#
# The goal: swing $\vec{\mathbf{a}}$'s direction onto $\vec{\mathbf{b}}$'s, through the
# angle $\theta$ between them. $\vec{\mathbf{a}}$, $\vec{\mathbf{b}}$ are not unit
# length (a outside, b inside). Built with `epix`; `render_epix_figures.py`. CC0.

# %%
from __future__ import annotations

from _rotate_ab_scene import A_ANGLE, B_ANGLE, LOWER_LEFT, UPPER_RIGHT, A, B

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
    wedge(start=0.0, finish=A_ANGLE, text=r"$\beta$", radius=0.3)
    wedge(start=A_ANGLE, finish=B_ANGLE, text=r"$\theta$", radius=0.55)
    vector(
        head=A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=8, y=-2),
        align=epix.LabelPos.l,
    )
    vector(
        head=B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=2, y=9),
        align=epix.LabelPos.c,
    )

# %%
fig
