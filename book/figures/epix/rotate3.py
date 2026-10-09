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
# # rotate3 — rotating the unit direction by 90°
#
# Rotating $(\cos(\beta), \sin(\beta))$ by $\pi/2$ gives $(\cos(\beta+\pi/2),
# \sin(\beta+\pi/2))$ — perpendicular, still on the unit circle. One step of the
# `proof-rotate.rst`
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
unit_point: Point = polar(radius=1, angle=BETA)
perp_point: Point = polar(radius=1, angle=BETA + math.pi / 2)

fig: PendingFigure
with unit_circle_scene() as fig:
    right_angle_marker(angle=BETA)
    vector(head=unit_point, text=r"$(\cos(\beta),\ \sin(\beta))$")
    vector(
        head=perp_point,
        text=r"$\begin{bmatrix} \cos(\beta+\pi/2) \\ \sin(\beta+\pi/2) \end{bmatrix}$",
        offset=Point(x=6, y=16),
        align=epix.LabelPos.c,
    )

# %%
fig
