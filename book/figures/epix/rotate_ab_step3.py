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
# # rotate_ab_step3 — undo step 1, landing on $\vec{b}$'s direction
#
# Step 3: rotate back (the inverse of step 1). The image of $\vec{a}$ lands on
# $\vec{b}$'s direction, with $\vec{a}$'s own length: $(|\vec{a}|/|\vec{b}|) * \vec{b}$.
# The faint dashed arrow is $\vec{b}'$ (before undoing). Built with `epix`;
# `render_epix_figures.py`. CC0.

# %%
from __future__ import annotations

from _rotate_ab_scene import B_PRIME, LOWER_LEFT, RESULT, UPPER_RIGHT, B
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
    dashed_vector(tail=ORIGIN, head=B_PRIME)  # b', before undoing
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-11, y=2), align=epix.LabelPos.r)
    vector(
        head=RESULT,
        text=r"$\tfrac{|\vec{a}|}{|\vec{b}|}\,\vec{b}$",
        offset=Point(x=6, y=6),
        align=epix.LabelPos.l,
    )

# %%
fig
