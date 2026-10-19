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
# # trans1 — the graph paper, before translating
#
# The grid, the axes, the fixed vector $\vec{b}$, and two sample points $P$ and $Q$ on
# the lattice. The next figure (`trans2`) slides this whole paper by $\vec{b}$. Built
# with the `epix` package; `tools/render_epix_figures.py` writes
# `_static/epix/trans1.{pdf,png}`. CC0.

# %%
from __future__ import annotations

from _addition_scene import (
    TRANS_LOWER_LEFT,
    TRANS_P,
    TRANS_Q,
    TRANS_UPPER_RIGHT,
    B,
)
from _scene2d import (
    PendingFigure,
    Point,
    epix,
    grid,
    unit_circle_scene,
    vector,
)

# %%
fig: PendingFigure
with unit_circle_scene(
    lower_left=TRANS_LOWER_LEFT, upper_right=TRANS_UPPER_RIGHT, disc=False
) as fig:
    grid(lower_left=TRANS_LOWER_LEFT, upper_right=TRANS_UPPER_RIGHT)
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-6, y=6), align=epix.LabelPos.l)
    epix.dot(at=TRANS_P)
    epix.label(at=TRANS_P, offset=Point(x=6, y=6), text=r"$P$", align=epix.LabelPos.l)
    epix.dot(at=TRANS_Q)
    epix.label(at=TRANS_Q, offset=Point(x=6, y=6), text=r"$Q$", align=epix.LabelPos.l)

# %%
fig
