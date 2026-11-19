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
# # boot_project_product — projection is $(\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$
#
# $\vec{\mathbf{a}}^{-1} = \vec{\mathbf{a}} / |\vec{\mathbf{a}}|^2$ points along
# $\vec{\mathbf{a}}$ (purple; shorter, since $|\vec{\mathbf{a}}| > 1$). Scaling it by
# the number $\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}$ lands on the projection of
# $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$ (green), the foot of the perpendicular from
# $\vec{\mathbf{b}}$. Built with `epix`; written to
# `_static/epix/boot-project-product.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _bootstrap_scene import (
    GREEN,
    INVERSE_A,
    INVERSE_A_ANGLE,
    INVERSE_A_INV,
    INVERSE_B,
    INVERSE_PROJ,
    PURPLE,
    colored_vector,
)

from gacalc.epixscene.scene2d import (
    PendingFigure,
    Point,
    epix,
    right_angle_at,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-0.45, y=-0.45), upper_right=Point(x=2.0, y=1.35)
) as fig:
    epix.pen(color=epix.black(intensity=0.5), width=0.8)
    epix.dashed()
    epix.line(tail=INVERSE_B, head=INVERSE_PROJ)
    epix.line_style(style="-")
    right_angle_at(corner=INVERSE_PROJ, angle=INVERSE_A_ANGLE + math.pi / 2)
    vector(
        head=INVERSE_A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=7, y=-2),
        align=epix.LabelPos.r,
    )
    vector(
        head=INVERSE_B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=-5, y=6),
        align=epix.LabelPos.l,
    )
    colored_vector(
        head=INVERSE_PROJ,
        color=GREEN,
        text=r"$(\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$",
        offset=Point(x=4, y=-8),
        align=epix.LabelPos.br,
    )
    colored_vector(
        head=INVERSE_A_INV,
        color=PURPLE,
        text=r"$\vec{\mathbf{a}}^{-1}$",
        offset=Point(x=-6, y=-14),
        align=epix.LabelPos.b,
    )

# %%
fig
