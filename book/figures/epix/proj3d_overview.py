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
# # proj3d_overview — $\vec{\mathbf{a}}$ and the three coordinate planes
#
# The setup for projection in 3D: one vector $\vec{\mathbf{a}}$ and the three coordinate
# planes $\mathbf{e}_{12}$, $\mathbf{e}_{23}$, $\mathbf{e}_{31}$ (faint), each of which
# $\vec{\mathbf{a}}$ can be projected onto. Built with the `epix` package;
# `tools/render_epix_figures.py` writes `_static/epix/proj3d-overview.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from gacalc.epixscene.scene3d import (
    A,
    PendingFigure,
    Point,
    axes3,
    epix,
    frame_scene,
    plane3,
    vector3,
)

# %%
fig: PendingFigure
with frame_scene() as fig:
    plane3(plane="e_12", faint=True)
    plane3(plane="e_23", faint=True)
    plane3(plane="e_31", faint=True)
    axes3()
    vector3(
        head=A,
        text=r"$\vec{\mathbf{a}}$",
        offset=Point(x=6, y=5),
        align=epix.LabelPos.l,
    )

# %%
fig
