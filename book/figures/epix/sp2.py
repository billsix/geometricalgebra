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
# # sp2 — the angle that carries $\vec{b}$ to the x-axis
#
# The rotation we are about to apply: $\vec{b}$ makes an angle $\varphi$ with the
# x-axis, so rotating the whole picture by $-\varphi$ lays $\vec{b}$ flat along it.
# Built with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/sp2.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _projection_scene import B_ANGLE, SP_LOWER_LEFT, SP_UPPER_RIGHT, A, B
from _scene2d import PendingFigure, Point, epix, unit_circle_scene, vector, wedge

# %%
fig: PendingFigure
with unit_circle_scene(lower_left=SP_LOWER_LEFT, upper_right=SP_UPPER_RIGHT) as fig:
    wedge(start=0.0, finish=B_ANGLE, text=r"$\varphi$", radius=0.45)
    vector(head=A, text=r"$\vec{a}$", offset=Point(x=-6, y=7), align=epix.LabelPos.l)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=6, y=-6), align=epix.LabelPos.r)

# %%
fig
