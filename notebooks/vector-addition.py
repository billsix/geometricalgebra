# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% tags=["remove-cell"]
# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

# %% [markdown]
# # Vector Addition — calculations
#
# You already know that $3 + 5 = 5 + 3$. The chapter's pictures say that
# $\vec{\mathbf{a}} + \vec{\mathbf{b}}$ and $\vec{\mathbf{b}} + \vec{\mathbf{a}}$ land
# on the same corner of the parallelogram. Here is the same fact in coordinates: adding
# two vectors adds their coordinates, and each coordinate is a sum of two ordinary
# numbers, which gives the same answer in either order. The coordinates are left as
# symbols, so every result holds for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$.
# Numbers appear only to draw the figures. Each check shows both sides, then their
# difference.

# %%
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    BLUE,
    GREEN,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    point,
    scene_around,
)
from gacalc.epixscene.frame_scene import GRAY_EDGE, line
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference
from gacalc.transforms import translate

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# ## $\vec{\mathbf{a}} + \vec{\mathbf{b}} = \vec{\mathbf{b}} + \vec{\mathbf{a}}$
#
# Before running the next two cells, predict each coordinate of
# $\vec{\mathbf{a}} + \vec{\mathbf{b}}$ and of $\vec{\mathbf{b}} + \vec{\mathbf{a}}$.
# $\vec{\mathbf{a}} + \vec{\mathbf{b}}$:

# %%
a + b

# %% [markdown]
# $\vec{\mathbf{b}} + \vec{\mathbf{a}}$:

# %%
b + a

# %% [markdown]
# Each coordinate is the same two numbers added in the other order. Their difference:

# %%
show_difference(a + b, b + a)

# %% [markdown]
# At the plot values, $\vec{\mathbf{a}} + \vec{\mathbf{b}}$:

# %%
at_values(a + b, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_SUM: Point = point(coordinates=list(at_values(a + b, values)))
fig_sum: PendingFigure
with scene_around(points=[P_A, P_B, P_SUM]) as fig_sum:
    arrow(head=P_SUM, color=PURPLE, text=r"$\vec{\mathbf{a}} + \vec{\mathbf{b}}$")
    arrow(head=P_A, color=GREEN, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_SUM, tail=P_A, color=BLUE)
    arrow(head=P_B, color=BLUE, text=r"$\vec{\mathbf{b}}$", align=LabelPos.l)
    arrow(head=P_SUM, tail=P_B, color=GREEN)
fig_sum

# %% [markdown]
# ## Subtraction
#
# The chapter's second pair of pictures: $\vec{\mathbf{a}} - \vec{\mathbf{b}}$ is what
# you add to $\vec{\mathbf{b}}$ to get back $\vec{\mathbf{a}}$.
# $\vec{\mathbf{a}} - \vec{\mathbf{b}}$:

# %%
a - b

# %% [markdown]
# $(\vec{\mathbf{a}} - \vec{\mathbf{b}}) + \vec{\mathbf{b}}$:

# %%
(a - b) + b

# %% [markdown]
# Its difference from $\vec{\mathbf{a}}$:

# %%
show_difference((a - b) + b, a)

# %% [markdown]
# It is the same as adding the opposite. $\vec{\mathbf{a}} + (-\vec{\mathbf{b}})$:

# %%
a + (-b)

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} - \vec{\mathbf{b}}$:

# %%
show_difference(a - b, a + (-b))

# %% [markdown]
# At the plot values, $\vec{\mathbf{a}} - \vec{\mathbf{b}}$:

# %%
at_values(a - b, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_DIFFERENCE: Point = point(coordinates=list(at_values(a - b, values)))
fig_difference: PendingFigure
with scene_around(points=[P_A, P_B, P_DIFFERENCE]) as fig_difference:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLUE, text=r"$\vec{\mathbf{b}}$", align=LabelPos.l)
    arrow(
        head=P_DIFFERENCE, color=PURPLE, text=r"$\vec{\mathbf{a}} - \vec{\mathbf{b}}$"
    )
    dashed_arrow(tail=P_B, head=P_A, color=PURPLE)
fig_difference

# %% [markdown]
# ## Translate: adding the same vector to everything
#
# Fix $\vec{\mathbf{b}}$ and let the other input vary, and $+$ becomes a one-input
# machine, `translate(b=b)`: feed it any point $\vec{\mathbf{v}}$, get
# $\vec{\mathbf{v}} + \vec{\mathbf{b}}$. This is **partial binding**: one of the two
# blanks of $+$ filled in. It moves every point the same way, so applying it to the
# whole plane slides the graph paper by $\vec{\mathbf{b}}$.

# %%
t: InvertibleFunction[Vector] = translate(b=b)
t

# %% [markdown]
# Applied to $\vec{\mathbf{a}}$, it gives the one-off sum:

# %%
t(a)

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} + \vec{\mathbf{b}}$:

# %%
show_difference(t(a), a + b)

# %% [markdown]
# It moves every point by the same $\vec{\mathbf{b}}$. $\vec{\mathbf{e}}_1$ goes to:

# %%
t(1 * e_1)

# %% [markdown]
# and $\vec{\mathbf{e}}_2$ to:

# %%
t(1 * e_2)

# %% [markdown]
# A whole sheet of graph paper, a 3 by 3 lattice of points, each slid by
# $\vec{\mathbf{b}}$ at the plot values. (No separate check is needed:
# $\vec{\mathbf{a}}$ above is symbolic, so
# $t(\vec{\mathbf{a}}) = \vec{\mathbf{a}} + \vec{\mathbf{b}}$ already covers every
# point.)

# %%
P_SHIFT: Point = point(coordinates=list(at_values(b, values)))

fig_lattice: PendingFigure
with scene_around(
    points=[Point(x=2, y=2), Point(x=2, y=2) + P_SHIFT, P_SHIFT]
) as fig_lattice:
    k: int
    for k in range(3):
        line(tail=Point(x=k, y=0), head=Point(x=k, y=2), color=GRAY_EDGE)
        line(tail=Point(x=0, y=k), head=Point(x=2, y=k), color=GRAY_EDGE)
        line(tail=Point(x=k, y=0) + P_SHIFT, head=Point(x=k, y=2) + P_SHIFT, color=BLUE)
        line(tail=Point(x=0, y=k) + P_SHIFT, head=Point(x=2, y=k) + P_SHIFT, color=BLUE)
    arrow(head=P_SHIFT, color=PURPLE, text=r"$\vec{\mathbf{b}}$", align=LabelPos.l)
fig_lattice

# %% [markdown]
# Its **inverse** is `translate(b=-b)`: sliding the paper back undoes the slide.
# $t^{-1}(t(\vec{\mathbf{a}}))$:

# %%
t.inverse(t(a))

# %% [markdown]
# Its difference from $\vec{\mathbf{a}}$:

# %%
show_difference(t.inverse(t(a)), a)

# %% [markdown]
# `t.at(0.5)` is the paper slid half way. $t_{0.5}(\vec{\mathbf{a}})$:

# %%
t.at(0.5)(a)

# %% [markdown]
# $\vec{\mathbf{a}} + 0.5 * \vec{\mathbf{b}}$:

# %%
a + b * 0.5

# %% [markdown]
# Their difference:

# %%
show_difference(t.at(0.5)(a), a + b * 0.5)
