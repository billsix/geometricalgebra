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
# # boot_rotate_onesided — $\vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})$ turns $\vec{\mathbf{v}}$ by $\theta$
#
# The product of the two unit vectors carries the angle $\theta$ from $\vec{\mathbf{a}}$
# to $\vec{\mathbf{b}}$; multiplying any $\vec{\mathbf{v}}$ by it on the right turns
# $\vec{\mathbf{v}}$ by the same $\theta$ (purple). Built with `epix`; written to
# `_static/epix/boot-rotate-onesided.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _bootstrap_scene import (
    ONESIDED_A,
    ONESIDED_A_ANGLE,
    ONESIDED_B,
    ONESIDED_B_ANGLE,
    ONESIDED_V,
    ONESIDED_V_ANGLE,
    ONESIDED_V_ROT,
    PURPLE,
    colored_vector,
)
from _scene2d import PendingFigure, Point, epix, unit_circle_scene, vector, wedge

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-1.45, y=-0.45), upper_right=Point(x=1.5, y=1.45)
) as fig:
    wedge(
        start=ONESIDED_A_ANGLE,
        finish=ONESIDED_B_ANGLE,
        text=r"$\theta$",
        radius=0.4,
    )
    wedge(
        start=ONESIDED_V_ANGLE,
        finish=ONESIDED_V_ANGLE + ONESIDED_B_ANGLE - ONESIDED_A_ANGLE,
        text=r"$\theta$",
        radius=0.4,
    )
    vector(
        head=ONESIDED_A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=7, y=0),
        align=epix.LabelPos.r,
    )
    vector(
        head=ONESIDED_B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=5, y=5),
        align=epix.LabelPos.tr,
    )
    vector(
        head=ONESIDED_V,
        text=r"$\vec{\mathbf{v}}$",
        offset=Point(x=4, y=6),
        align=epix.LabelPos.tr,
    )
    colored_vector(
        head=ONESIDED_V_ROT,
        color=PURPLE,
        text=r"$\vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})$",
        offset=Point(x=0, y=8),
        align=epix.LabelPos.t,
    )

# %%
fig
