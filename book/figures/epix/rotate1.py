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
# # rotate1 — a point by its length and its angle
#
# A Cartesian point $\vec{a}$ described by its length $r$ and the cosine and sine of
# its angle $\beta$: the right triangle on the unit circle, scaled by $r$. One step of
# the `proof-rotate.rst`
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
    PendingFigure,
    Point,
    R,
    leg,
    polar,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
unit_point: Point = polar(radius=1, angle=BETA)
a: Point = polar(radius=R, angle=BETA)
foot: Point = Point(x=unit_point.x1(), y=0)

fig: PendingFigure
with unit_circle_scene() as fig:
    wedge(start=0, finish=BETA, text=r"$\beta$")
    leg(
        tail=foot,
        head=unit_point,
        color=GREEN,
        text=r"$\sin\beta$",
        angle=0,
        offset=Point(x=24, y=0),
    )
    leg(
        tail=ORIGIN,
        head=foot,
        color=BLUE,
        text=r"$\cos\beta$",
        angle=0,
        offset=Point(x=0, y=-13),
    )
    vector(head=a, text=r"$r\,(\cos\beta,\ \sin\beta)$")

# %%
fig
