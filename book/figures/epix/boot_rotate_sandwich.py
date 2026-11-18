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
# # boot_rotate_sandwich — the half-angle vector $\vec{\mathbf{h}}$ of the sandwich
#
# $\vec{\mathbf{h}}$ (dashed) bisects the angle $\theta$ from $\vec{\mathbf{a}}$ to
# $\vec{\mathbf{b}}$, so the versor $R$ built from $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{h}}$ turns by $\theta / 2$. The sandwich $R * \vec{\mathbf{v}} * R^{-1}$
# applies that half turn twice, once from each side, and the two halves add up to
# $\theta$. Built with `epix`; written to `_static/epix/boot-rotate-sandwich.{pdf,png}`.
# CC0.

# %%
from __future__ import annotations

from _bootstrap_scene import (
    SANDWICH_A,
    SANDWICH_A_ANGLE,
    SANDWICH_B,
    SANDWICH_B_ANGLE,
    SANDWICH_H,
    SANDWICH_H_ANGLE,
)
from _scene2d import (
    ORIGIN,
    PendingFigure,
    Point,
    dashed_vector,
    epix,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-0.45, y=-0.45), upper_right=Point(x=1.55, y=1.5)
) as fig:
    wedge(
        start=SANDWICH_A_ANGLE,
        finish=SANDWICH_H_ANGLE,
        text=r"$\frac{\theta}{2}$",
        radius=0.85,
    )
    wedge(
        start=SANDWICH_H_ANGLE,
        finish=SANDWICH_B_ANGLE,
        text=r"$\frac{\theta}{2}$",
        radius=0.85,
    )
    dashed_vector(
        tail=ORIGIN,
        head=SANDWICH_H,
        text=r"$\vec{\mathbf{h}}$",
        offset=Point(x=7, y=0),
        align=epix.LabelPos.r,
    )
    vector(
        head=SANDWICH_A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=7, y=0),
        align=epix.LabelPos.r,
    )
    vector(
        head=SANDWICH_B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=5, y=5),
        align=epix.LabelPos.tr,
    )

# %%
fig
