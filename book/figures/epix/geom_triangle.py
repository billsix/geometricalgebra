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
# # geom_triangle — a triangle as a closed chain of sides, and a midsegment
#
# The triangle picture of `geometry-from-vectors.rst`: corners
# $\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}$, the side vectors
# $\vec{\mathbf{b}} - \vec{\mathbf{a}}$, $\vec{\mathbf{c}} - \vec{\mathbf{b}}$,
# $\vec{\mathbf{a}} - \vec{\mathbf{c}}$ chained tip to tail back to the start, and the
# midsegment joining the midpoints of two sides, parallel to the third and half as
# long. Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/geom-triangle.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _geometry_scene import (
    TRI_A,
    TRI_B,
    TRI_C,
    TRI_LOWER_LEFT,
    TRI_UPPER_RIGHT,
    on_segment,
)

from gacalc.epixscene.scene2d import (
    GREEN,
    PURPLE,
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
)

# %%
MID_AB: Point = on_segment(start=TRI_A, finish=TRI_B, t=0.5)
MID_AC: Point = on_segment(start=TRI_A, finish=TRI_C, t=0.5)
fig: PendingFigure
with unit_circle_scene(
    lower_left=TRI_LOWER_LEFT, upper_right=TRI_UPPER_RIGHT, disc=False, basis=False
) as fig:
    # the three sides, chained tip to tail
    epix.pen(color=GREEN, width=1.6)
    epix.arrow(tail=TRI_A, head=TRI_B, scale=0.7)
    epix.arrow(tail=TRI_B, head=TRI_C, scale=0.7)
    epix.arrow(tail=TRI_C, head=TRI_A, scale=0.7)
    epix.label_color(color=GREEN)
    epix.label(
        at=on_segment(start=TRI_A, finish=TRI_B, t=0.75),
        offset=Point(x=0, y=-8),
        text=r"$\vec{\mathbf{b}} - \vec{\mathbf{a}}$",
        align=epix.LabelPos.b,
    )
    epix.label(
        at=on_segment(start=TRI_B, finish=TRI_C, t=0.5),
        offset=Point(x=6, y=4),
        text=r"$\vec{\mathbf{c}} - \vec{\mathbf{b}}$",
        align=epix.LabelPos.tr,
    )
    epix.label(
        at=on_segment(start=TRI_C, finish=TRI_A, t=0.6),
        offset=Point(x=-6, y=2),
        text=r"$\vec{\mathbf{a}} - \vec{\mathbf{c}}$",
        align=epix.LabelPos.l,
    )
    # the midsegment, from the midpoint of ab to the midpoint of ac
    epix.pen(color=PURPLE, width=2.0)
    epix.line(tail=MID_AB, head=MID_AC)
    epix.label_color(color=PURPLE)
    epix.dot(at=MID_AB)
    epix.dot(at=MID_AC)
    epix.label(
        at=on_segment(start=MID_AB, finish=MID_AC, t=0.8),
        offset=Point(x=10, y=4),
        text=r"$\frac{1}{2} * (\vec{\mathbf{c}} - \vec{\mathbf{b}})$",
        align=epix.LabelPos.r,
    )
    epix.label_color(color=epix.black())
    epix.dot(
        at=TRI_A,
        offset=Point(x=-4, y=-4),
        text=r"$\vec{\mathbf{a}}$",
        align=epix.LabelPos.bl,
    )
    epix.dot(
        at=TRI_B,
        offset=Point(x=4, y=-4),
        text=r"$\vec{\mathbf{b}}$",
        align=epix.LabelPos.br,
    )
    epix.dot(
        at=TRI_C,
        offset=Point(x=0, y=6),
        text=r"$\vec{\mathbf{c}}$",
        align=epix.LabelPos.t,
    )

# %%
fig
