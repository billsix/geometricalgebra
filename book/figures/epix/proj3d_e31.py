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
# # proj3d_e31 — projection of $\vec{a}$ onto the $e_{31}$ (zx) plane
#
# $\vec{a}$ split against the $e_{31}$ plane: the projection (blue) lies in the plane,
# the rejection (green, along y) is the perpendicular remainder. (The book writes this
# plane $e_{31}$, cyclically; gacalc's blade constant is $e_{13}=-e_{31}$.) Built with
# the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/proj3d-e31.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _scene3d import (
    BLUE,
    GREEN,
    ORIGIN3,
    A,
    PendingFigure,
    Point,
    axes3,
    epix,
    frame_scene,
    plane3,
    project_onto,
    right_angle_3d,
    vector3,
)

# %%
fig: PendingFigure
with frame_scene() as fig:
    plane3(plane="e_31")
    axes3()
    proj: Point = project_onto(plane="e_31")
    vector3(head=A, text=r"$\vec{a}$", offset=Point(x=9, y=7), align=epix.LabelPos.l)
    epix.pen(color=BLUE, width=2.0)
    epix.line(tail=ORIGIN3, head=proj)
    epix.dot(at=proj)
    epix.label_color(color=BLUE)
    epix.label(
        at=proj,
        offset=Point(x=-14, y=-11),
        text=r"$\mathrm{proj}_{e_{31}}\,\vec{a}$",
        align=epix.LabelPos.r,
    )
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=proj, head=A)
    epix.label_color(color=GREEN)
    mid_rej: Point = 0.5 * (proj + A)
    epix.label(
        at=mid_rej,
        offset=Point(x=12, y=4),
        text=r"$\mathrm{rej}_{e_{31}}\,\vec{a}$",
        align=epix.LabelPos.l,
    )
    epix.label_color(color=epix.black())
    right_angle_3d(corner=proj, toward_a=A - proj, toward_b=ORIGIN3 - proj)

# %%
fig
