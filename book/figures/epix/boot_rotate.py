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
# # boot_rotate — a rotation is a blend of $\vec{\mathbf{v}}$ and its quarter turn
#
# To rotate $\vec{\mathbf{v}}$ by $\theta$, walk $\cos(\theta)$ of the way along
# $\vec{\mathbf{v}}$ (blue), then $\sin(\theta)$ of the way along its quarter turn
# $\vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$ (green), and land on the rotated vector
# (purple). Built with `epix`; `tools/render_epix_figures.py` writes
# `_static/epix/boot-rotate.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _bootstrap_scene import (
    BLUE,
    GREEN,
    PURPLE,
    ROTATE_COS_PART,
    ROTATE_RESULT,
    ROTATE_THETA,
    ROTATE_V,
    ROTATE_V_ANGLE,
    ROTATE_V_PERP,
    colored_segment,
    colored_vector,
)

from gacalc.epixscene.scene2d import (
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
# basis=False: the figure's own cos(theta) * v leg lies near e_1 at about unit length,
# so the basis label would collide with its label
with unit_circle_scene(
    lower_left=Point(x=-0.9, y=-0.45), upper_right=Point(x=1.55, y=1.5), basis=False
) as fig:
    wedge(
        start=ROTATE_V_ANGLE,
        finish=ROTATE_V_ANGLE + ROTATE_THETA,
        text=r"$\theta$",
        radius=0.4,
    )
    dashed_vector(
        tail=ORIGIN,
        head=ROTATE_V_PERP,
        text=r"$\vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$",
        offset=Point(x=-4, y=6),
        align=epix.LabelPos.l,
    )
    vector(
        head=ROTATE_V,
        text=r"$\vec{\mathbf{v}}$",
        offset=Point(x=7, y=-3),
        align=epix.LabelPos.r,
    )
    colored_segment(
        tail=ORIGIN,
        head=ROTATE_COS_PART,
        color=BLUE,
        text=r"$\cos(\theta) * \vec{\mathbf{v}}$",
        offset=Point(x=4, y=-9),
        align=epix.LabelPos.br,
    )
    colored_segment(
        tail=ROTATE_COS_PART,
        head=ROTATE_RESULT,
        color=GREEN,
        text=r"$\sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$",
        offset=Point(x=8, y=0),
        align=epix.LabelPos.r,
    )
    colored_vector(
        head=ROTATE_RESULT,
        color=PURPLE,
        text=r"$\vec{\mathbf{r}}(\vec{\mathbf{v}}; \theta)$",
        offset=Point(x=4, y=7),
        align=epix.LabelPos.tr,
    )

# %%
fig
