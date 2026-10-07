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
# # rotate6 — rotate x′ by θ and read off the right triangle
#
# In the new frame, rotating $\vec{x'}$ by $\theta$ gives a right triangle on the unit
# circle with legs $\cos\theta$ along $\vec{x'}$ and $\sin\theta$ along $\vec{y'}$.
# One step of the `proof-rotate.rst`
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
    BLUE,
    GREEN,
    ORIGIN,
    THETA,
    Point,
    epix,
    leg,
    polar,
    right_angle_marker,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
x_prime = polar(1, BETA)
y_prime = polar(1, BETA + math.pi / 2)
rotated = polar(1, BETA + THETA)
foot = polar(math.cos(THETA), BETA)  # the projection of the rotated point onto x'

with unit_circle_scene() as fig:
    wedge(BETA, BETA + THETA, r"$\theta$")
    right_angle_marker(BETA)
    vector(x_prime, r"$\vec{x'}$")
    vector(y_prime, r"$\vec{y'}$", offset=Point(x=-7, y=4), align=epix.LabelPos.l)
    vector(rotated)
    leg(ORIGIN, foot, BLUE, r"$\cos\theta$", angle=BETA, offset=Point(x=11, y=-5))
    leg(
        foot,
        rotated,
        GREEN,
        r"$\sin\theta$",
        angle=BETA - math.pi / 2,
        offset=Point(x=5, y=11),
    )

# %%
fig
