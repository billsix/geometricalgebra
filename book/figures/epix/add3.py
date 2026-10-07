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
# # add3 — the parallelogram: $\vec{a}+\vec{b}=\vec{b}+\vec{a}$
#
# Both orders of the sum land on the same corner: slide $\vec{b}$ onto $\vec{a}$'s head,
# or slide $\vec{a}$ onto $\vec{b}$'s head, and either way you reach $\vec{a}+\vec{b}$ —
# the far corner of the parallelogram the two vectors span. This is why addition
# commutes. Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/add3.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _addition_scene import A_PLUS_B, ADD_LOWER_LEFT, ADD_UPPER_RIGHT, A, B
from _scene2d import (
    PendingFigure,
    Point,
    dashed_vector,
    epix,
    parallelogram,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=ADD_LOWER_LEFT, upper_right=ADD_UPPER_RIGHT, disc=False
) as fig:
    parallelogram(corner_a=A, corner_b=B)
    # the two originals from the origin
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=7, y=-3), align=epix.LabelPos.r)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-5, y=7), align=epix.LabelPos.l)
    # the two slid copies that close the parallelogram (dashed translated copies)
    dashed_vector(tail=A, head=A_PLUS_B)  # b slid onto a's head
    dashed_vector(tail=B, head=A_PLUS_B)  # a slid onto b's head
    epix.dot(at=A_PLUS_B)
    epix.label(
        at=A_PLUS_B,
        offset=Point(x=6, y=6),
        text=r"$\vec{a}+\vec{b}$",
        align=epix.LabelPos.l,
    )

# %%
fig
