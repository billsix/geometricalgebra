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
# # rotate4 — name the two directions x′ and y′
#
# The two perpendicular unit directions get names, $\vec{x'}$ and $\vec{y'}$, so their
# details can be set aside for a moment, just as $r$ was. One step of the `proof-
# rotate.rst`
# sequence; the geometry (β, θ, r) is shared with the other steps through
# `_rotation_scene.py`, so the last step lands exactly on the goal figure's
# $\vec{r}(\vec{a};\theta)$. Built with the `epix` Python package
# (github.com/billsix/epix-mirror) in the style of its `notebooks/`.

# %%
from __future__ import annotations

import math

from _rotation_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BETA,
    PendingFigure,
    Point,
    epix,
    polar,
    right_angle_marker,
    unit_circle_scene,
    vector,
)

# %%
x_prime: Point = polar(radius=1, angle=BETA)
y_prime: Point = polar(radius=1, angle=BETA + math.pi / 2)

fig: PendingFigure
with unit_circle_scene() as fig:
    right_angle_marker(angle=BETA)
    vector(head=x_prime, text=r"$\vec{x'}$")
    vector(
        head=y_prime, text=r"$\vec{y'}$", offset=Point(x=-7, y=4), align=epix.LabelPos.l
    )

# %%
fig
