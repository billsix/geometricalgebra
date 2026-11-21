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
# # Points, segments, lines and polygons — calculations
#
# A geometry course starts from points, lines and segments. The chapter builds each one
# from vectors, using only adding vectors and multiplying a vector by a number. Here are
# the same constructions with every coordinate left as a symbol, so each result holds
# for every point at once. Numbers appear only to draw the figures. Each check shows
# both sides, then their difference.

# %%
# twin: GacalcProofs.G2.segmentMidpoint_eq_segment_half
# twin: GacalcProofs.G2.segmentMidpoint_halves
# twin: GacalcProofs.G2.triangle_sides_sum_zero
# twin: GacalcProofs.G2.midsegment_eq_half_side
# twin: GacalcProofs.G2.parallelogram_iff_diagonals_bisect
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
    note,
    point,
    scene_around,
)
from gacalc.epixscene.frame_scene import line
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference

# %% [markdown]
# ## A point is a vector from the origin
#
# The point $A$ is where the arrow $\vec{\mathbf{a}}$ from the origin ends, and its
# coordinates are the arrow's. $\vec{\mathbf{a}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
c_1: sympy.Symbol
c_2: sympy.Symbol
d_1: sympy.Symbol
d_2: sympy.Symbol
a_1, a_2, b_1, b_2, c_1, c_2, d_1, d_2 = sympy.symbols(
    "a_1 a_2 b_1 b_2 c_1 c_2 d_1 d_2", real=True
)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and the point $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 1),
    (a_2, 3),
    (b_1, 4),
    (b_2, 1),
    (c_1, 3),
    (c_2, 4),
    (d_1, 2),
    (d_2, 4),
]

# %% [markdown]
# ## The segment: start at $\vec{\mathbf{a}}$, go part of the way to $\vec{\mathbf{b}}$
#
# $\vec{\mathbf{b}} - \vec{\mathbf{a}}$ is the trip from $\vec{\mathbf{a}}$ to
# $\vec{\mathbf{b}}$. Go the fraction $t$ of that trip and you are at
# $\vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}})$:

# %%
t: sympy.Symbol = sympy.Symbol("t", real=True)
segment_point: Vector = a + Scalar(t) * (b - a)
segment_point

# %% [markdown]
# Before running the next two cells, predict where $t = 0$ and $t = 1$ land. At
# $t = 0$:

# %%
at_values(segment_point, [(t, 0)])

# %% [markdown]
# Its difference from $\vec{\mathbf{a}}$:

# %%
show_difference(at_values(segment_point, [(t, 0)]), a)

# %% [markdown]
# At $t = 1$:

# %%
at_values(segment_point, [(t, 1)])

# %% [markdown]
# Its difference from $\vec{\mathbf{b}}$:

# %%
show_difference(at_values(segment_point, [(t, 1)]), b)

# %% [markdown]
# Every $t$ from $0$ to $1$ gives a point between them: the segment.

# %% [markdown]
# ## The midpoint is the segment at $t = \frac{1}{2}$
#
# Half way along the segment:

# %%
half_way: Vector = at_values(segment_point, [(t, sympy.Rational(1, 2))])
half_way

# %% [markdown]
# The midpoint formula, $\frac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{b}})$, which
# in coordinates is the textbook's
# $\left(\frac{a_1 + b_1}{2}, \frac{a_2 + b_2}{2}\right)$:

# %%
m: Vector = (a + b) / 2
m

# %% [markdown]
# Their difference:

# %%
show_difference(half_way, m)

# %% [markdown]
# The midpoint cuts the segment into two equal halves. From $\vec{\mathbf{a}}$ to the
# midpoint, $\vec{\mathbf{m}} - \vec{\mathbf{a}}$:

# %%
m - a

# %% [markdown]
# and from the midpoint to $\vec{\mathbf{b}}$, $\vec{\mathbf{b}} - \vec{\mathbf{m}}$:

# %%
b - m

# %% [markdown]
# Their difference. The two halves are the same vector, so they have the same length
# and the same direction:

# %%
show_difference(m - a, b - m)

# %% [markdown]
# At the plot values, the midpoint:

# %%
at_values(m, values)

# %% [markdown]
# Drawn at the plot values: the segment, with the points at $t = 0$,
# $t = \frac{1}{2}$ and $t = 1$.

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_M: Point = point(coordinates=list(at_values(m, values)))
fig_segment: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_segment:
    line(tail=P_A, head=P_B, color=PURPLE, width=3.0)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$", align=LabelPos.l)
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    note(
        at=P_M,
        text=r"$\vec{\mathbf{m}}$",
        color=PURPLE,
        offset=Point(x=4, y=6),
        align=LabelPos.tr,
    )
fig_segment

# %% [markdown]
# ## Its length is the distance formula
#
# The length of the segment is the length of the trip
# $\vec{\mathbf{b}} - \vec{\mathbf{a}}$, by the Pythagorean theorem on its two
# coordinates. gacalc's length, $|\vec{\mathbf{b}} - \vec{\mathbf{a}}|$:

# %%
length: Real = (b - a).magnitude()
length

# %% [markdown]
# The textbook's distance formula:

# %%
distance: Real = sympy.sqrt((b_1 - a_1) ** 2 + (b_2 - a_2) ** 2)
distance

# %% [markdown]
# Their difference:

# %%
show_difference(length, distance)

# %% [markdown]
# ## Rays and lines: let $t$ run further
#
# The same formula with $t \ge 0$ is the ray from $\vec{\mathbf{a}}$ through
# $\vec{\mathbf{b}}$; with $t \le 0$ it is the opposite ray, and with every $t$ the
# whole line. At $t = 2$ the point is past $\vec{\mathbf{b}}$, on the ray:

# %%
at_values(segment_point, [(t, 2)])

# %% [markdown]
# and at $t = -1$ it is behind $\vec{\mathbf{a}}$, on the opposite ray:

# %%
at_values(segment_point, [(t, -1)])

# %% [markdown]
# Drawn at the plot values, $t$ from $-1$ to $2$: the ray $t \ge 0$ green, the
# opposite ray $t \le 0$ blue.

# %%
P_FORWARD: Point = point(
    coordinates=list(at_values(at_values(segment_point, [(t, 2)]), values))
)
P_BACK: Point = point(
    coordinates=list(at_values(at_values(segment_point, [(t, -1)]), values))
)
fig_line: PendingFigure
with scene_around(points=[P_A, P_B, P_FORWARD, P_BACK], basis=False) as fig_line:
    arrow(tail=P_A, head=P_FORWARD, color=GREEN, text=r"$t \ge 0$")
    arrow(tail=P_A, head=P_BACK, color=BLUE, text=r"$t \le 0$", align=LabelPos.l)
    note(at=P_A, text=r"$\vec{\mathbf{a}}$", align=LabelPos.tr)
    note(at=P_B, text=r"$\vec{\mathbf{b}}$", align=LabelPos.tr)
fig_line

# %% [markdown]
# ## A triangle is a closed trip
#
# Add a third corner $\vec{\mathbf{c}}$:

# %%
c: Vector = Scalar(c_1) * e_1 + Scalar(c_2) * e_2
c

# %% [markdown]
# Walk the sides in order, $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$ to
# $\vec{\mathbf{c}}$ and back to $\vec{\mathbf{a}}$. Before running the cell, predict
# the total trip.
# $(\vec{\mathbf{b}} - \vec{\mathbf{a}}) + (\vec{\mathbf{c}} - \vec{\mathbf{b}}) + (\vec{\mathbf{a}} - \vec{\mathbf{c}})$:

# %%
round_trip: Vector = (b - a) + (c - b) + (a - c)
round_trip

# %% [markdown]
# Why zero? The first two sides together,
# $(\vec{\mathbf{b}} - \vec{\mathbf{a}}) + (\vec{\mathbf{c}} - \vec{\mathbf{b}})$:

# %%
(b - a) + (c - b)

# %% [markdown]
# are the direct trip from $\vec{\mathbf{a}}$ to $\vec{\mathbf{c}}$,
# $\vec{\mathbf{c}} - \vec{\mathbf{a}}$:

# %%
c - a

# %% [markdown]
# Their difference:

# %%
show_difference((b - a) + (c - b), c - a)

# %% [markdown]
# The third side, $\vec{\mathbf{a}} - \vec{\mathbf{c}}$, is that trip backwards, so
# the whole walk adds up to zero.

# %% [markdown]
# ## The midsegment is parallel to the third side and half as long
#
# The midpoint of side $\vec{\mathbf{a}}\vec{\mathbf{b}}$ and of side
# $\vec{\mathbf{a}}\vec{\mathbf{c}}$:

# %%
m_ab: Vector = (a + b) / 2
m_ab

# %% [markdown]
# and

# %%
m_ac: Vector = (a + c) / 2
m_ac

# %% [markdown]
# The midsegment, the trip from one midpoint to the other:

# %%
m_ac - m_ab

# %% [markdown]
# Half the third side, $\frac{1}{2} * (\vec{\mathbf{c}} - \vec{\mathbf{b}})$:

# %%
(c - b) / 2

# %% [markdown]
# Their difference. The midsegment is a number, $\frac{1}{2}$, times the third side:
# it points the same way and is half as long.

# %%
show_difference(m_ac - m_ab, (c - b) / 2)

# %% [markdown]
# At the plot values, the two midpoints:

# %%
at_values(m_ab, values)

# %% [markdown]
# and

# %%
at_values(m_ac, values)

# %% [markdown]
# Drawn at the plot values: the sides chained tip to tail, and the midsegment.

# %%
P_C: Point = point(coordinates=list(at_values(c, values)))
P_M_AB: Point = point(coordinates=list(at_values(m_ab, values)))
P_M_AC: Point = point(coordinates=list(at_values(m_ac, values)))
fig_triangle: PendingFigure
with scene_around(points=[P_A, P_B, P_C], basis=False) as fig_triangle:
    arrow(tail=P_A, head=P_B, color=GREEN)
    arrow(tail=P_B, head=P_C, color=GREEN)
    arrow(tail=P_C, head=P_A, color=GREEN)
    line(tail=P_M_AB, head=P_M_AC, color=PURPLE, width=2.0)
    note(at=P_A, text=r"$\vec{\mathbf{a}}$", align=LabelPos.bl)
    note(at=P_B, text=r"$\vec{\mathbf{b}}$", align=LabelPos.br)
    note(at=P_C, text=r"$\vec{\mathbf{c}}$", align=LabelPos.t)
fig_triangle

# %% [markdown]
# ## The diagonals of a parallelogram cut each other in half
#
# Take four corners in order,
# $\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}, \vec{\mathbf{d}}$. The
# quadrilateral is a parallelogram when side $\vec{\mathbf{a}}\vec{\mathbf{b}}$ and
# side $\vec{\mathbf{d}}\vec{\mathbf{c}}$ are the same trip,
# $\vec{\mathbf{b}} - \vec{\mathbf{a}} = \vec{\mathbf{c}} - \vec{\mathbf{d}}$.
# The fourth corner $\vec{\mathbf{d}}$:

# %%
d: Vector = Scalar(d_1) * e_1 + Scalar(d_2) * e_2
d

# %% [markdown]
# The midpoint of the diagonal from $\vec{\mathbf{a}}$ to $\vec{\mathbf{c}}$, minus
# the midpoint of the diagonal from $\vec{\mathbf{b}}$ to $\vec{\mathbf{d}}$:

# %%
midpoint_gap: Vector = (a + c) / 2 - (b + d) / 2
midpoint_gap

# %% [markdown]
# Minus one half of the mismatch between the two sides,
# $-\frac{1}{2} * ((\vec{\mathbf{b}} - \vec{\mathbf{a}}) - (\vec{\mathbf{c}} - \vec{\mathbf{d}}))$:

# %%
side_gap: Vector = Scalar(sympy.Rational(-1, 2)) * ((b - a) - (c - d))
side_gap

# %% [markdown]
# Their difference. The gap between the midpoints is always minus half the gap
# between the sides, so one is zero exactly when the other is: the sides match (a
# parallelogram) exactly when the diagonals share their midpoint.

# %%
show_difference(midpoint_gap, side_gap)

# %% [markdown]
# Drawn at the plot values with $\vec{\mathbf{c}}$ moved to
# $\vec{\mathbf{b}} + \vec{\mathbf{d}} - \vec{\mathbf{a}}$, which makes the sides
# match. The two diagonals meet at one point:

# %%
c_parallelogram: Vector = b + d - a
at_values(c_parallelogram, values)

# %% [markdown]
# The diagonals' midpoints there, first of $\vec{\mathbf{a}}\vec{\mathbf{c}}$:

# %%
at_values((a + c_parallelogram) / 2, values)

# %% [markdown]
# then of $\vec{\mathbf{b}}\vec{\mathbf{d}}$:

# %%
at_values((b + d) / 2, values)

# %% [markdown]
# Drawn:

# %%
P_D: Point = point(coordinates=list(at_values(d, values)))
P_C_PARALLELOGRAM: Point = point(coordinates=list(at_values(c_parallelogram, values)))
fig_parallelogram: PendingFigure
with scene_around(
    points=[P_A, P_B, P_C_PARALLELOGRAM, P_D], basis=False
) as fig_parallelogram:
    arrow(tail=P_A, head=P_B, color=GREEN)
    arrow(tail=P_D, head=P_C_PARALLELOGRAM, color=GREEN)
    line(tail=P_B, head=P_C_PARALLELOGRAM)
    line(tail=P_A, head=P_D)
    line(tail=P_A, head=P_C_PARALLELOGRAM, color=PURPLE)
    line(tail=P_B, head=P_D, color=PURPLE)
    note(at=P_A, text=r"$\vec{\mathbf{a}}$", align=LabelPos.bl)
    note(at=P_B, text=r"$\vec{\mathbf{b}}$", align=LabelPos.br)
    note(at=P_C_PARALLELOGRAM, text=r"$\vec{\mathbf{c}}$", align=LabelPos.tr)
    note(at=P_D, text=r"$\vec{\mathbf{d}}$", align=LabelPos.tl)
fig_parallelogram
