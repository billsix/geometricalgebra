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
# # boot_rotate_from_projection — one triangle, on $\vec{a}$ and on $\vec{v}$
#
# The first triangle measures $\vec{b}$ against $\vec{a}$: $x$ along $\vec{a}$ (green),
# $y$ across (blue), the angle $\theta$ between them. The second is the same triangle on
# $\vec{v}$: $\cos(\theta) * \vec{v}$ along $\vec{v}$ (green), $\sin(\theta)$ times the
# quarter turn of $\vec{v}$ across (blue), and the rotated $\vec{v}'$ (purple), at the
# same $\theta$ from $\vec{v}$. Built with `epix`; written to
# `_static/epix/boot-rotate-from-projection.{pdf,png}`. CC0.

# %%
from __future__ import annotations

import math

from _bootstrap_scene import (
    BLUE,
    FROM_PROJ_A,
    FROM_PROJ_A_ANGLE,
    FROM_PROJ_B,
    FROM_PROJ_B_ANGLE,
    FROM_PROJ_B_FOOT,
    FROM_PROJ_THETA,
    FROM_PROJ_V,
    FROM_PROJ_V_ANGLE,
    FROM_PROJ_V_COS_PART,
    FROM_PROJ_V_ROTATED,
    GREEN,
    PURPLE,
    colored_segment,
    colored_vector,
)
from _scene2d import (
    ORIGIN,
    PendingFigure,
    Point,
    epix,
    right_angle_at,
    unit_circle_scene,
    vector,
    wedge,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-1.45, y=-0.45), upper_right=Point(x=1.7, y=1.4)
) as fig:
    wedge(
        start=FROM_PROJ_A_ANGLE,
        finish=FROM_PROJ_B_ANGLE,
        text=r"$\theta$",
        radius=0.4,
    )
    wedge(
        start=FROM_PROJ_V_ANGLE,
        finish=FROM_PROJ_V_ANGLE + FROM_PROJ_THETA,
        text=r"$\theta$",
        radius=0.4,
    )
    vector(
        head=FROM_PROJ_A,
        text=r"$\vec{a}$",
        offset=Point(x=7, y=0),
        align=epix.LabelPos.r,
    )
    vector(
        head=FROM_PROJ_B,
        text=r"$\vec{b}$",
        offset=Point(x=4, y=5),
        align=epix.LabelPos.tr,
    )
    vector(
        head=FROM_PROJ_V,
        text=r"$\vec{v}$",
        offset=Point(x=4, y=5),
        align=epix.LabelPos.tr,
    )
    # the first triangle: b measured against a
    colored_segment(
        tail=ORIGIN,
        head=FROM_PROJ_B_FOOT,
        color=GREEN,
        text=r"$x$",
        offset=Point(x=0, y=-8),
        align=epix.LabelPos.b,
    )
    colored_segment(
        tail=FROM_PROJ_B_FOOT,
        head=FROM_PROJ_B,
        color=BLUE,
        text=r"$y$",
        offset=Point(x=7, y=0),
        align=epix.LabelPos.r,
    )
    right_angle_at(corner=FROM_PROJ_B_FOOT, angle=FROM_PROJ_A_ANGLE + math.pi / 2)
    # the same triangle on v
    colored_segment(
        tail=ORIGIN,
        head=FROM_PROJ_V_COS_PART,
        color=GREEN,
        text=r"$\cos(\theta) * \vec{v}$",
        offset=Point(x=-6, y=8),
        align=epix.LabelPos.l,
    )
    colored_segment(
        tail=FROM_PROJ_V_COS_PART,
        head=FROM_PROJ_V_ROTATED,
        color=BLUE,
        text=r"$\sin(\theta) * \vec{r}(\vec{v}; \pi/2)$",
        offset=Point(x=-4, y=12),
        align=epix.LabelPos.tl,
    )
    right_angle_at(corner=FROM_PROJ_V_COS_PART, angle=FROM_PROJ_V_ANGLE + math.pi / 2)
    colored_vector(
        head=FROM_PROJ_V_ROTATED,
        color=PURPLE,
        text=r"$\vec{v}'$",
        offset=Point(x=-6, y=0),
        align=epix.LabelPos.l,
    )

# %%
fig
