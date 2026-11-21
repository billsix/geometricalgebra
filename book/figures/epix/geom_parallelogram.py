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
# # geom_parallelogram — the diagonals of a parallelogram share a midpoint
#
# The parallelogram picture of `geometry-from-vectors.rst`: corners
# $\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}, \vec{\mathbf{d}}$ in order,
# with $\vec{\mathbf{b}} - \vec{\mathbf{a}} = \vec{\mathbf{c}} - \vec{\mathbf{d}}$, and
# the two diagonals meeting at the midpoint of each, labelled $\vec{\mathbf{m}}$. Built
# with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/geom-parallelogram.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _geometry_scene import (
    PAR_A,
    PAR_B,
    PAR_C,
    PAR_D,
    PAR_LOWER_LEFT,
    PAR_UPPER_RIGHT,
    on_segment,
)

from gacalc.epixscene.scene2d import (
    GREEN,
    PURPLE,
    PURPLE_FILL,
    PendingFigure,
    Point,
    epix,
    unit_circle_scene,
)

# %%
MIDDLE: Point = on_segment(start=PAR_A, finish=PAR_C, t=0.5)
fig: PendingFigure
with unit_circle_scene(
    lower_left=PAR_LOWER_LEFT, upper_right=PAR_UPPER_RIGHT, disc=False, basis=False
) as fig:
    epix.pen(color=epix.black(intensity=0.6), width=0.6)
    epix.fill(color=PURPLE_FILL)
    epix.Path(data=[PAR_A, PAR_B, PAR_C, PAR_D], closed=True, filled=True).draw()
    epix.nofill()
    # the two equal sides, b - a and c - d
    epix.pen(color=GREEN, width=1.6)
    epix.arrow(tail=PAR_A, head=PAR_B, scale=0.7)
    epix.arrow(tail=PAR_D, head=PAR_C, scale=0.7)
    epix.label_color(color=GREEN)
    epix.label(
        at=on_segment(start=PAR_A, finish=PAR_B, t=0.5),
        offset=Point(x=0, y=-8),
        text=r"$\vec{\mathbf{b}} - \vec{\mathbf{a}}$",
        align=epix.LabelPos.b,
    )
    epix.label(
        at=on_segment(start=PAR_D, finish=PAR_C, t=0.5),
        offset=Point(x=0, y=8),
        text=r"$\vec{\mathbf{c}} - \vec{\mathbf{d}}$",
        align=epix.LabelPos.t,
    )
    # the diagonals, meeting at their shared midpoint
    epix.pen(color=PURPLE, width=1.2)
    epix.dashed()
    epix.line(tail=PAR_A, head=PAR_C)
    epix.line(tail=PAR_B, head=PAR_D)
    epix.line_style(style="-")
    epix.label_color(color=PURPLE)
    epix.dot(
        at=MIDDLE,
        offset=Point(x=10, y=0),
        text=r"$\vec{\mathbf{m}}$",
        align=epix.LabelPos.r,
    )
    epix.label_color(color=epix.black())
    epix.dot(
        at=PAR_A,
        offset=Point(x=-4, y=-4),
        text=r"$\vec{\mathbf{a}}$",
        align=epix.LabelPos.bl,
    )
    epix.dot(
        at=PAR_B,
        offset=Point(x=4, y=-4),
        text=r"$\vec{\mathbf{b}}$",
        align=epix.LabelPos.br,
    )
    epix.dot(
        at=PAR_C,
        offset=Point(x=4, y=4),
        text=r"$\vec{\mathbf{c}}$",
        align=epix.LabelPos.tr,
    )
    epix.dot(
        at=PAR_D,
        offset=Point(x=-4, y=4),
        text=r"$\vec{\mathbf{d}}$",
        align=epix.LabelPos.tl,
    )

# %%
fig
