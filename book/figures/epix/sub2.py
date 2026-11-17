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
# # sub2 — subtraction as adding the opposite: $\vec{\mathbf{a}}+(-\vec{\mathbf{b}})$
#
# The same difference the other way: flip $\vec{\mathbf{b}}$ to get $-\vec{\mathbf{b}}$,
# then add it tip-to-tail to $\vec{\mathbf{a}}$. The result lands on the same point as
# the connector in `sub1`, so
# $\vec{\mathbf{a}}-\vec{\mathbf{b}}=\vec{\mathbf{a}}+(-\vec{\mathbf{b}})$. Built with
# the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/sub2.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _addition_scene import A_MINUS_B, NEG_B, SUB_LOWER_LEFT, SUB_UPPER_RIGHT, A
from _scene2d import (
    GREEN,
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
with unit_circle_scene(
    lower_left=SUB_LOWER_LEFT, upper_right=SUB_UPPER_RIGHT, disc=False
) as fig:
    vector(
        head=A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=7, y=-3),
        align=epix.LabelPos.r,
    )
    # -b from the origin (the flipped b)
    vector(
        head=NEG_B,
        text=r"$-\vec{\mathbf{b}}$",
        offset=Point(x=-6, y=-6),
        align=epix.LabelPos.l,
    )
    # -b slid onto a's head (a translated copy, so dashed)
    dashed_vector(tail=A, head=A_MINUS_B)
    # the sum a + (-b) = a - b, from the origin
    epix.pen(color=GREEN, width=1.8)
    epix.arrow(tail=ORIGIN, head=A_MINUS_B, scale=0.7)
    epix.dot(at=A_MINUS_B)
    epix.label_color(color=GREEN)
    epix.label(
        at=A_MINUS_B,
        offset=Point(x=-4, y=-6),
        text=r"$\vec{\mathbf{a}}-\vec{\mathbf{b}}$",
        align=epix.LabelPos.bl,
    )
    epix.label_color(color=epix.black())

# %%
fig
