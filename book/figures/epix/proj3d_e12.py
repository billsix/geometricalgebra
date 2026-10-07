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
# # proj3d_e12 — projection of $\vec{a}$ onto the $e_{12}$ (xy) plane
#
# $\vec{a}$ split against the $e_{12}$ plane: the projection (blue) lies in the plane,
# the rejection (green) is the perpendicular remainder, meeting at a right angle. Built
# with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/proj3d-e12.{pdf,png}`. CC0.

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
    plane3(plane="e_12")
    axes3()
    proj: Point = project_onto(plane="e_12")
    vector3(head=A, text=r"$\vec{a}$", offset=Point(x=5, y=5), align=epix.LabelPos.l)
    # projection: in the plane, blue
    epix.pen(color=BLUE, width=2.0)
    epix.line(tail=ORIGIN3, head=proj)
    epix.dot(at=proj)
    epix.label_color(color=BLUE)
    epix.label(
        at=proj,
        offset=Point(x=-6, y=-10),
        text=r"$\mathrm{proj}$",
        align=epix.LabelPos.c,
    )
    # rejection: perpendicular to the plane, green
    epix.pen(color=GREEN, width=2.0)
    epix.line(tail=proj, head=A)
    epix.label_color(color=GREEN)
    epix.label(
        at=A, offset=Point(x=13, y=-12), text=r"$\mathrm{rej}$", align=epix.LabelPos.l
    )
    epix.label_color(color=epix.black())
    right_angle_3d(corner=proj, toward_a=A - proj, toward_b=ORIGIN3 - proj)

# %%
fig
