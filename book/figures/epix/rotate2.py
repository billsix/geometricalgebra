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
# # rotate2 — the unit direction of a, remembering r
#
# Similar triangles: work on the unit circle and keep the length $r$ aside. The unit
# point in the direction of $\vec{a}$ is $(\cos\beta, \sin\beta)$. One step of the
# `proof-rotate.rst`
# sequence; the geometry (β, θ, r) is shared with the other steps through
# `_rotation_scene.py`, so the last step lands exactly on the goal figure's
# $\vec{r}(\vec{a};\theta)$. Built with the `epix` Python package
# (github.com/billsix/epix-mirror) in the style of its `notebooks/`.

# %%
from __future__ import annotations

from _rotation_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BETA,
    BLUE,
    GREEN,
    ORIGIN,
    Point,
    leg,
    polar,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
unit_point = polar(1, BETA)
foot = Point(x=unit_point.x1(), y=0)

with unit_circle_scene() as fig:
    wedge(0, BETA, r"$\beta$")
    leg(foot, unit_point, GREEN, r"$\sin\beta$", angle=0, offset=Point(x=24, y=0))
    leg(ORIGIN, foot, BLUE, r"$\cos\beta$", angle=0, offset=Point(x=0, y=-13))
    vector(unit_point, r"$(\cos\beta,\ \sin\beta)$")

# %%
fig
