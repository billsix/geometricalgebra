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
# # rotate9 — a's triangle is the unit triangle, scaled
#
# The two right triangles — the one on the unit circle (legs $\cos(\theta)$,
# $\sin(\theta)$) and $\vec{a}$'s own (legs $r * \cos(\theta)$, $r * \sin(\theta)$) —
# have the same angles, so they are **similar**: $\vec{a}$'s legs are just the unit
# legs scaled by $r$. That is why scaling the unit result by $r$ lands exactly on the
# rotated $\vec{a}$. The small triangle is drawn on top (a lighter shade of its big
# counterpart's colour) so the shared shape stays visible. Last step of the
# `proof-rotate.rst` sequence; geometry shared through `_rotation_scene.py`. Built with
# the `epix` Python package (github.com/billsix/epix-mirror).

# %%
from __future__ import annotations

import math

from _rotation_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    BETA,
    BLUE,
    GREEN,
    ORIGIN,
    THETA,
    PendingFigure,
    Point,
    R,
    epix,
    leg,
    polar,
    unit_circle_scene,
    vector,
    wedge,
)
from _scene2d import dashed_vector

# %%
# Lighter shades of BLUE/GREEN for the small (unit) triangle -- same hue as its big
# counterpart (so corresponding sides read as "the same side, scaled"), lighter so the
# small triangle stays visible where its legs lie on top of the big ones.
LIGHT_BLUE: epix.Color = epix.rgb(r=0.3, g=0.55, b=1.0)
LIGHT_GREEN: epix.Color = epix.rgb(r=0.2, g=0.72, b=0.35)

# unit (reference) triangle, radius 1
x_prime: Point = polar(radius=1, angle=BETA)
y_prime: Point = polar(radius=1, angle=BETA + math.pi / 2)
rotated: Point = polar(radius=1, angle=BETA + THETA)
foot: Point = polar(radius=math.cos(THETA), angle=BETA)

# a's similar triangle, radius R (= |a|)
result: Point = polar(radius=R, angle=BETA + THETA)
big_foot: Point = polar(radius=R * math.cos(THETA), angle=BETA)

fig: PendingFigure
with unit_circle_scene(
    lower_left=Point(x=-2.7, y=-1.3), upper_right=Point(x=2.0, y=2.7)
) as fig:
    wedge(start=BETA, finish=BETA + THETA, text=r"$\theta$")
    vector(head=x_prime, text=r"$\vec{x'}$")
    vector(
        head=y_prime, text=r"$\vec{y'}$", offset=Point(x=-7, y=4), align=epix.LabelPos.l
    )

    # a's (big) similar triangle first: bold hypotenuse = a, sin leg labelled. The two
    # cos legs are collinear (both along x'), so they are drawn unlabelled and their
    # labels placed explicitly below, at well-separated radii.
    leg(
        tail=ORIGIN,
        head=big_foot,
        color=BLUE,
        text="",
        angle=BETA,
        offset=ORIGIN,
    )
    leg(
        tail=big_foot,
        head=result,
        color=GREEN,
        text=r"$r * \sin(\theta)$",
        angle=BETA - math.pi / 2,
        offset=Point(x=16, y=11),
    )
    vector(head=result, text=r"$\vec{r}(\vec{a};\theta)$", offset=Point(x=6, y=10))

    # the unit (small) triangle on top: dashed hypotenuse, lighter legs so it stays seen
    dashed_vector(tail=ORIGIN, head=rotated)
    leg(
        tail=ORIGIN,
        head=foot,
        color=LIGHT_BLUE,
        text="",
        angle=BETA,
        offset=ORIGIN,
    )
    leg(
        tail=foot,
        head=rotated,
        color=LIGHT_GREEN,
        text=r"$\sin(\theta)$",
        angle=BETA - math.pi / 2,
        offset=Point(x=5, y=10),
    )

    # the two collinear cos labels, placed apart along x', each matched to its leg:
    # r*cos near the big leg's far end, cos near the origin, both below the x' line.
    epix.label_angle(t=BETA)
    epix.label_color(color=BLUE)
    epix.label(
        at=polar(radius=0.66, angle=BETA),
        offset=Point(x=22, y=-10),
        text=r"$r * \cos(\theta)$",
        align=epix.LabelPos.c,
    )
    epix.label_color(color=LIGHT_BLUE)
    epix.label(
        at=polar(radius=0.10, angle=BETA),
        offset=Point(x=13, y=-9),
        text=r"$\cos(\theta)$",
        align=epix.LabelPos.c,
    )
    epix.label_angle(t=0)
    epix.label_color(color=epix.black())

# %%
fig
