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
# # geom_line — a ray, its opposite ray, and the whole line
#
# The second picture of `geometry-from-vectors.rst`: the same two points, and the
# points $\vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}})$ for three ranges
# of $t$. $t \ge 0$ is the ray from $\vec{\mathbf{a}}$ through $\vec{\mathbf{b}}$,
# $t \le 0$ its opposite ray, and every $t$ the line. Built with the `epix` package;
# `tools/render_epix_figures.py` writes `_static/epix/geom-line.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _geometry_scene import (
    LINE_LOWER_LEFT,
    LINE_UPPER_RIGHT,
    SEG_A,
    SEG_B,
    on_segment,
)

from gacalc.epixscene.scene2d import (
    BLUE,
    GREEN,
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
)

# %%
FAR_FORWARD: Point = on_segment(start=SEG_A, finish=SEG_B, t=1.6)
FAR_BACK: Point = on_segment(start=SEG_A, finish=SEG_B, t=-0.75)
fig: PendingFigure
with unit_circle_scene(
    lower_left=LINE_LOWER_LEFT, upper_right=LINE_UPPER_RIGHT, disc=False, basis=False
) as fig:
    # the ray t >= 0, from a through b and on
    epix.pen(color=GREEN, width=2.0)
    epix.arrow(tail=SEG_A, head=FAR_FORWARD, scale=0.8)
    epix.label_color(color=GREEN)
    epix.label(
        at=FAR_FORWARD,
        offset=Point(x=0, y=10),
        text=r"$t \ge 0$",
        align=epix.LabelPos.t,
    )
    # the opposite ray t <= 0, from a the other way
    epix.pen(color=BLUE, width=2.0)
    epix.arrow(tail=SEG_A, head=FAR_BACK, scale=0.8)
    epix.label_color(color=BLUE)
    epix.label(
        at=FAR_BACK,
        offset=Point(x=0, y=-10),
        text=r"$t \le 0$",
        align=epix.LabelPos.b,
    )
    epix.label_color(color=epix.black())
    epix.dot(
        at=SEG_A,
        offset=Point(x=4, y=8),
        text=r"$\vec{\mathbf{a}}$, $t = 0$",
        align=epix.LabelPos.tr,
    )
    epix.dot(
        at=SEG_B,
        offset=Point(x=-4, y=-8),
        text=r"$\vec{\mathbf{b}}$, $t = 1$",
        align=epix.LabelPos.bl,
    )

# %%
fig
