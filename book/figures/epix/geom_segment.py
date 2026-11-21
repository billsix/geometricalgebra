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
# # geom_segment — the segment from $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$
#
# The first picture of `geometry-from-vectors.rst`: two points as position vectors,
# the difference $\vec{\mathbf{b}} - \vec{\mathbf{a}}$ from one to the other, and the
# segment, the points $\vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}})$
# for $0 \le t \le 1$, with $t = 0$, $t = 1/2$ (the midpoint) and $t = 1$ marked. Built
# with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/geom-segment.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _geometry_scene import (
    SEG_A,
    SEG_B,
    SEG_LOWER_LEFT,
    SEG_UPPER_RIGHT,
    on_segment,
)

from gacalc.epixscene.scene2d import (
    GREEN,
    PURPLE,
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
    vector,
)

# %%
MIDPOINT: Point = on_segment(start=SEG_A, finish=SEG_B, t=0.5)
fig: PendingFigure
with unit_circle_scene(
    lower_left=SEG_LOWER_LEFT, upper_right=SEG_UPPER_RIGHT, disc=False
) as fig:
    vector(
        head=SEG_A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=-4, y=6),
        align=epix.LabelPos.l,
    )
    vector(
        head=SEG_B,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=6, y=-4),
        align=epix.LabelPos.r,
    )
    # the segment itself, under the difference arrow
    epix.pen(color=PURPLE, width=3.0)
    epix.line(tail=SEG_A, head=SEG_B)
    # b - a, from the head of a to the head of b
    epix.pen(color=GREEN, width=1.4)
    epix.arrow(tail=SEG_A, head=SEG_B, scale=0.7)
    epix.label_color(color=GREEN)
    epix.label(
        at=on_segment(start=SEG_A, finish=SEG_B, t=0.45),
        offset=Point(x=6, y=6),
        text=r"$\vec{\mathbf{b}} - \vec{\mathbf{a}}$",
        align=epix.LabelPos.tr,
    )
    # the points at t = 0, 1/2, 1: black dots on the purple segment
    epix.pen(color=epix.black(), width=1.0)
    epix.dot_size(diameter=5)
    epix.label_color(color=PURPLE)
    epix.dot(at=SEG_A, offset=Point(x=6, y=6), text=r"$t = 0$", align=epix.LabelPos.tr)
    epix.dot(
        at=MIDPOINT,
        offset=Point(x=-6, y=-6),
        text=r"$t = \frac{1}{2}$",
        align=epix.LabelPos.bl,
    )
    epix.dot(at=SEG_B, offset=Point(x=0, y=10), text=r"$t = 1$", align=epix.LabelPos.t)
    epix.label_color(color=epix.black())

# %%
fig
