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
# # sub1 — subtraction as the connecting vector: $\vec{a}-\vec{b}$
#
# $\vec{a}-\vec{b}$ is the vector that runs from the head of $\vec{b}$ to the head of
# $\vec{a}$ — the thing you add to $\vec{b}$ to get $\vec{a}$. Built with the `epix`
# package; `tools/render_epix_figures.py` writes `_static/epix/sub1.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _addition_scene import SUB_LOWER_LEFT, SUB_UPPER_RIGHT, A, B
from _scene2d import GREEN, PendingFigure, Point, epix, unit_circle_scene, vector

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=SUB_LOWER_LEFT, upper_right=SUB_UPPER_RIGHT, disc=False
) as fig:
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=7, y=-3), align=epix.LabelPos.r)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-5, y=7), align=epix.LabelPos.l)
    # a - b: the connector from b's head to a's head
    epix.pen(color=GREEN, width=1.8)
    epix.line(tail=B, head=A)
    epix.dot(at=A)
    epix.label_color(color=GREEN)
    mid: Point = Point(x=(A.x1() + B.x1()) / 2, y=(A.x2() + B.x2()) / 2)
    epix.label(
        at=mid,
        offset=Point(x=4, y=10),
        text=r"$\vec{a}-\vec{b}$",
        align=epix.LabelPos.l,
    )
    epix.label_color(color=epix.black())

# %%
fig
