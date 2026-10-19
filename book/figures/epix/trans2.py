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
# # trans2 — `translate(b)` slides the whole graph paper
#
# Applying `translate(b)` adds $\vec{b}$ to *every* point at once: the faint grid is the
# original paper, the solid grid is the same paper slid by $\vec{b}$, and the origin has
# moved to $O' = \vec{b}$. Each sample point follows the same displacement $\vec{b}$
# (dashed arrows), landing on $P+\vec{b}$ and $Q+\vec{b}$. Built with the `epix`
# package; `tools/render_epix_figures.py` writes `_static/epix/trans2.{pdf,png}`. CC0.

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
    dashed_vector,
    epix,
    grid,
    unit_circle_scene,
    vector,
)

# %%
p_image: Point = Point(x=TRANS_P.x1() + B.x1(), y=TRANS_P.x2() + B.x2())
q_image: Point = Point(x=TRANS_Q.x1() + B.x1(), y=TRANS_Q.x2() + B.x2())

fig: PendingFigure
with unit_circle_scene(
    lower_left=TRANS_LOWER_LEFT, upper_right=TRANS_UPPER_RIGHT, disc=False
) as fig:
    # the original paper, faint, and the same paper slid by b, solid
    grid(lower_left=TRANS_LOWER_LEFT, upper_right=TRANS_UPPER_RIGHT, faint=True)
    grid(lower_left=TRANS_LOWER_LEFT, upper_right=TRANS_UPPER_RIGHT, offset=B)

    # the vector doing the sliding, and the moved origin O' = b
    vector(head=B, text=r"$\vec{b}$", offset=Point(x=-6, y=6), align=epix.LabelPos.l)
    epix.dot(at=B)
    epix.label(at=B, offset=Point(x=8, y=-2), text=r"$O'$", align=epix.LabelPos.r)

    # each sample point follows the same displacement b to its image
    epix.dot(at=TRANS_P)
    epix.label(at=TRANS_P, offset=Point(x=-6, y=6), text=r"$P$", align=epix.LabelPos.l)
    dashed_vector(tail=TRANS_P, head=p_image)
    epix.dot(at=p_image)
    epix.label(
        at=p_image, offset=Point(x=6, y=6), text=r"$P+\vec{b}$", align=epix.LabelPos.l
    )

    epix.dot(at=TRANS_Q)
    epix.label(at=TRANS_Q, offset=Point(x=-6, y=6), text=r"$Q$", align=epix.LabelPos.l)
    dashed_vector(tail=TRANS_Q, head=q_image)
    epix.dot(at=q_image)
    epix.label(
        at=q_image, offset=Point(x=6, y=6), text=r"$Q+\vec{b}$", align=epix.LabelPos.l
    )

# %%
fig
