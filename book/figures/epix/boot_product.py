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
# # boot_product — $\vec{\mathbf{b}}$ measured along and across $\vec{\mathbf{a}}$
#
# The product $\vec{\mathbf{a}} * \vec{\mathbf{b}}$ keeps two numbers:
# $|\vec{\mathbf{a}}| * x$, with $x$ how far $\vec{\mathbf{b}}$ reaches along
# $\vec{\mathbf{a}}$ (green), and $|\vec{\mathbf{a}}| * y$, with $y$ its height across
# $\vec{\mathbf{a}}$ (blue), which is the area of the parallelogram (purple). Built with
# `epix`; written to `_static/epix/boot-product.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _bootstrap_scene import (
    BLUE,
    GREEN,
    PRODUCT_A,
    PRODUCT_A_ANGLE,
    PRODUCT_B,
    PRODUCT_FOOT,
    colored_segment,
)
from _scene2d import (
    ORIGIN,
    PendingFigure,
    Point,
    epix,
    parallelogram,
    right_angle_at,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-0.45, y=-0.45),
    upper_right=Point(x=1.75, y=1.5),
    disc=False,
) as fig:
    parallelogram(corner_a=PRODUCT_A, corner_b=PRODUCT_B)
    vector(
        head=PRODUCT_A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=7, y=-2),
        align=epix.LabelPos.r,
    )
    vector(
        head=PRODUCT_B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=-5, y=6),
        align=epix.LabelPos.l,
    )
    colored_segment(
        tail=ORIGIN,
        head=PRODUCT_FOOT,
        color=GREEN,
        text=r"$x$",
        offset=Point(x=4, y=-8),
        align=epix.LabelPos.br,
    )
    colored_segment(
        tail=PRODUCT_FOOT,
        head=PRODUCT_B,
        color=BLUE,
        text=r"$y$",
        offset=Point(x=6, y=0),
        align=epix.LabelPos.r,
    )
    right_angle_at(corner=PRODUCT_FOOT, angle=PRODUCT_A_ANGLE + math.pi / 2)

# %%
fig
