# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
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
# # The reciprocal frame — calculations
#
# Companion to the *Proof: The Reciprocal Frame* chapter. On graph paper, the
# coordinates of a point are read off the two axes. The reciprocal frame does the same
# for slanted axes $\vec{\mathbf{a}}_1, \vec{\mathbf{a}}_2$: one dot product per
# coordinate, $x_k = \vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}}$. Each section below
# checks one of the chapter's eight theorems, first in the plane for a fully general
# frame (every coordinate its own symbol), then in space for one slanted frame and a
# fully general vector. Each check shows both sides, then their difference. Numbers
# appear only to draw the figures.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, Real
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
    note,
    point,
    scene_around,
)
from gacalc.epixscene.frame_scene import scene_3d
from gacalc.frame import Frame, InverseMethod, reciprocal_frame
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference

# %% [markdown]
# ## A general frame in the plane
#
# Two vectors $\vec{\mathbf{a}}_1$ and $\vec{\mathbf{a}}_2$, every coordinate a symbol,
# and a general vector $\vec{\mathbf{y}}$ with coordinates $x_1, x_2$ in that frame:
# $\vec{\mathbf{y}} = x_1 * \vec{\mathbf{a}}_1 + x_2 * \vec{\mathbf{a}}_2$. The only
# assumption is that the frame is a frame: its signed area
# $\vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2$ is not $0$.

# %%
p: sympy.Symbol
q: sympy.Symbol
r: sympy.Symbol
t: sympy.Symbol
x_1: sympy.Symbol
x_2: sympy.Symbol
p, q, r, t, x_1, x_2 = sympy.symbols("p q r t x_1 x_2", real=True)
a_1: MultiVectorBase = Scalar(p) * e_1 + Scalar(q) * e_2
a_1

# %% [markdown]
# and $\vec{\mathbf{a}}_2$:

# %%
a_2: MultiVectorBase = Scalar(r) * e_1 + Scalar(t) * e_2
a_2

# %% [markdown]
# A vector $\vec{\mathbf{y}}$ in the frame, with coordinates $x_1$ and $x_2$:

# %%
frame: list[MultiVectorBase] = [a_1, a_2]
y: MultiVectorBase = Scalar(x_1) * a_1 + Scalar(x_2) * a_2
y

# %% [markdown]
# The frame's signed area:

# %%
a_1 ^ a_2

# %% [markdown]
# The values used to draw the plane's figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (p, 2),
    (q, 1),
    (r, 1),
    (t, 2),
    (x_1, 1),
    (x_2, 1),
]

# %% [markdown]
# ## Theorem 1: eq 3.7, the definition
#
# $\vec{\mathbf{a}}^1 = \vec{\mathbf{a}}_2 * (\vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2)^{-1}$
# and
# $\vec{\mathbf{a}}^2 = -1 * \vec{\mathbf{a}}_1 * (\vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2)^{-1}$:
# each frame vector's face (the wedge of the others) divided by the area. By the
# formula, $\vec{\mathbf{a}}^1$ is:

# %%
A_2: MultiVectorBase = a_1 ^ a_2
upper_1: MultiVectorBase = (a_2 * A_2.inverse()).simplified()
upper_1

# %% [markdown]
# gacalc's `reciprocal_frame` builds:

# %%
reciprocal: list[MultiVectorBase] = reciprocal_frame(frame)
reciprocal[0].simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(upper_1, reciprocal[0])

# %% [markdown]
# By the formula, $\vec{\mathbf{a}}^2$ is:

# %%
upper_2: MultiVectorBase = (-1 * (a_1 * A_2.inverse())).simplified()
upper_2

# %% [markdown]
# `reciprocal_frame` builds:

# %%
reciprocal[1].simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(upper_2, reciprocal[1])

# %% [markdown]
# At the plot values, $\vec{\mathbf{a}}^1$:

# %%
at_values(reciprocal[0], values)

# %% [markdown]
# and $\vec{\mathbf{a}}^2$:

# %%
at_values(reciprocal[1], values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_1: Point = point(coordinates=list(at_values(a_1, values)))
P_A_2: Point = point(coordinates=list(at_values(a_2, values)))
P_UPPER_1: Point = point(coordinates=list(at_values(reciprocal[0], values)))
P_UPPER_2: Point = point(coordinates=list(at_values(reciprocal[1], values)))
fig_frame: PendingFigure
with scene_around(points=[P_A_1, P_A_2, P_UPPER_1, P_UPPER_2]) as fig_frame:
    arrow(head=P_A_1, color=BLACK, text=r"$\vec{\mathbf{a}}_1$")
    arrow(head=P_A_2, color=BLACK, text=r"$\vec{\mathbf{a}}_2$", align=LabelPos.l)
    arrow(head=P_UPPER_1, color=GREEN, text=r"$\vec{\mathbf{a}}^1$")
    arrow(head=P_UPPER_2, color=BLUE, text=r"$\vec{\mathbf{a}}^2$", align=LabelPos.l)
fig_frame

# %% [markdown]
# ## Theorem 2: each reciprocal vector is a vector
#
# A vector times a bivector could have a grade-3 part. In the plane it cannot, and in
# general the face lies inside the frame's space, so only grade 1 is left. The grades
# present in $\vec{\mathbf{a}}^1$:

# %%
reciprocal[0].grades()

# %% [markdown]
# and in $\vec{\mathbf{a}}^2$:

# %%
reciprocal[1].grades()

# %% [markdown]
# ## Theorem 3: eq 3.5, the Kronecker delta
#
# $\vec{\mathbf{a}}^k \cdot \vec{\mathbf{a}}_j$ is $1$ when $j = k$ and $0$ otherwise.
# The table of all four dot products, row $k$ and column $j$:

# %%
delta_table: sympy.Matrix = sympy.Matrix(
    [
        [
            sympy.simplify(sympy.sympify(upper.dot(lower).scalar_part()))
            for lower in frame
        ]
        for upper in reciprocal
    ]
)
delta_table

# %% [markdown]
# The identity:

# %%
sympy.eye(2)

# %% [markdown]
# Their difference:

# %%
delta_table - sympy.eye(2)

# %% [markdown]
# ## Theorem 4: eq 3.4, reconstruction
#
# Each coordinate is one dot product. $\vec{\mathbf{a}}^1 \cdot \vec{\mathbf{y}}$ is:

# %%
coordinate_1: Real = sympy.simplify(sympy.sympify(reciprocal[0].dot(y).scalar_part()))
coordinate_1

# %% [markdown]
# Its difference from $x_1$:

# %%
show_difference(coordinate_1, x_1)

# %% [markdown]
# $\vec{\mathbf{a}}^2 \cdot \vec{\mathbf{y}}$ is:

# %%
coordinate_2: Real = sympy.simplify(sympy.sympify(reciprocal[1].dot(y).scalar_part()))
coordinate_2

# %% [markdown]
# Its difference from $x_2$:

# %%
show_difference(coordinate_2, x_2)

# %% [markdown]
# The vector is the sum of its coordinates times the frame,
# $\sum_k (\vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}}) * \vec{\mathbf{a}}_k$:

# %%
rebuilt: MultiVectorBase = sum(
    [
        Scalar(upper.dot(y).scalar_part()) * lower
        for upper, lower in zip(reciprocal, frame)
    ],
    start=0 * e_1,
).simplified()
rebuilt

# %% [markdown]
# $\vec{\mathbf{y}}$ was:

# %%
y.simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(rebuilt, y)

# %% [markdown]
# Drawn at the plot values: $\vec{\mathbf{y}}$ (purple) as $x_1 * \vec{\mathbf{a}}_1$
# (green) plus $x_2 * \vec{\mathbf{a}}_2$ (blue).

# %%
P_Y: Point = point(coordinates=list(at_values(y, values)))
P_X1_A1: Point = point(coordinates=list(at_values(Scalar(x_1) * a_1, values)))
fig_rebuilt: PendingFigure
with scene_around(points=[P_A_1, P_A_2, P_Y]) as fig_rebuilt:
    arrow(head=P_Y, color=PURPLE, text=r"$\vec{\mathbf{y}}$")
    arrow(head=P_X1_A1, color=GREEN, text=r"$x_1 * \vec{\mathbf{a}}_1$")
    arrow(head=P_Y, tail=P_X1_A1, color=BLUE)
    note(
        at=0.5 * (P_X1_A1 + P_Y),
        text=r"$x_2 * \vec{\mathbf{a}}_2$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_A_2, color=BLACK, text=r"$\vec{\mathbf{a}}_2$"
    )
fig_rebuilt

# %% [markdown]
# ## Theorem 5: similar right triangles
#
# Take any vector $\vec{\mathbf{m}}$ perpendicular to $\vec{\mathbf{a}}_2$. Every term
# of $\vec{\mathbf{y}}$ but $x_1 * \vec{\mathbf{a}}_1$ adds no height along
# $\vec{\mathbf{m}}$, so
# $x_1 = (\vec{\mathbf{m}} \cdot \vec{\mathbf{y}}) / (\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_1)$:
# the height of $\vec{\mathbf{y}}$ above $\vec{\mathbf{a}}_2$'s line over the height of
# $\vec{\mathbf{a}}_1$. In the plane the quarter turn of $\vec{\mathbf{a}}_2$,
# $r(\vec{\mathbf{a}}_2; \pi/2)$, is such an $\vec{\mathbf{m}}$:

# %%
m: MultiVectorBase = a_2.rotate_90_degrees()
m

# %% [markdown]
# It is perpendicular to $\vec{\mathbf{a}}_2$,
# $\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_2 = 0$:

# %%
m.dot(a_2).simplified()

# %% [markdown]
# The ratio of the two heights:

# %%
height_of_y: Real = m.dot(y).scalar_part()
height_of_a_1: Real = m.dot(a_1).scalar_part()
height_ratio: Real = sympy.simplify(sympy.sympify(height_of_y / height_of_a_1))
height_ratio

# %% [markdown]
# Its difference from $x_1$:

# %%
show_difference(height_ratio, x_1)

# %% [markdown]
# Folding that division into the vector,
# $\vec{\mathbf{m}} / (\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_1)$:

# %%
folded: MultiVectorBase = (Scalar(1 / height_of_a_1) * m).simplified()
folded

# %% [markdown]
# is the reciprocal vector $\vec{\mathbf{a}}^1$ whatever the length of
# $\vec{\mathbf{m}}$. Its difference from $\vec{\mathbf{a}}^1$:

# %%
show_difference(folded, reciprocal[0])

# %% [markdown]
# ## Theorem 6: the last reciprocal vector is the last rejection over its length squared
#
# $\vec{\mathbf{w}}_2$ is $\vec{\mathbf{a}}_2$ with its part along $\vec{\mathbf{a}}_1$
# rejected:

# %%
w_2: MultiVectorBase = Frame(tuple(frame)).orthogonal_vectors()[-1].simplified()
w_2

# %% [markdown]
# so it is perpendicular to $\vec{\mathbf{a}}_1$,
# $\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{a}}_1 = 0$:

# %%
w_2.dot(a_1).simplified()

# %% [markdown]
# $\vec{\mathbf{w}}_2 / |\vec{\mathbf{w}}_2|^2$:

# %%
w_2_over_length: MultiVectorBase = (
    Scalar(1 / w_2.magnitude_squared()) * w_2
).simplified()
w_2_over_length

# %% [markdown]
# Its difference from $\vec{\mathbf{a}}^2$:

# %%
show_difference(w_2_over_length, reciprocal[1])

# %% [markdown]
# ## Theorems 7 and 8: both inverses undo the frame's map, and they agree
#
# `Frame.to_invertible_function` sends $\vec{\mathbf{e}}_i \mapsto \vec{\mathbf{a}}_i$.
# Its inverse reads the coordinates either with the reciprocal frame or by peeling the
# frame from its last vector. Each round trip is the identity, and the two inverses
# agree on a general vector. The coordinates $\vec{\mathbf{x}}$:

# %%
by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
x: MultiVectorBase = Scalar(x_1) * e_1 + Scalar(x_2) * e_2
x

# %% [markdown]
# The map, then the reciprocal-frame inverse:

# %%
by_reciprocal.inverse(by_reciprocal(x)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{x}}$:

# %%
show_difference(by_reciprocal.inverse(by_reciprocal(x)), x)

# %% [markdown]
# The map, then the peeling inverse:

# %%
by_peel.inverse(by_peel(x)).simplified()

# %% [markdown]
# The round trip gives $\vec{\mathbf{x}}$ back.

# %% [markdown]
# The other order, the reciprocal-frame inverse and then the map, on $\vec{\mathbf{y}}$:

# %%
by_reciprocal(by_reciprocal.inverse(y)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{y}}$:

# %%
show_difference(by_reciprocal(by_reciprocal.inverse(y)), y)

# %% [markdown]
# The peeling inverse and then the map, on $\vec{\mathbf{y}}$:

# %%
by_peel(by_peel.inverse(y)).simplified()

# %% [markdown]
# The round trip gives $\vec{\mathbf{y}}$ back.

# %% [markdown]
# The two inverses agree. The reciprocal-frame inverse of $\vec{\mathbf{y}}$:

# %%
by_reciprocal.inverse(y).simplified()

# %% [markdown]
# the peeling inverse of $\vec{\mathbf{y}}$:

# %%
by_peel.inverse(y).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(by_reciprocal.inverse(y), by_peel.inverse(y))

# %% [markdown]
# ## In space
#
# The same checks for the slanted frame $\vec{\mathbf{b}}_1 = 2 * \vec{\mathbf{e}}_1$,
# $\vec{\mathbf{b}}_2 = 1 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$,
# $\vec{\mathbf{b}}_3 = 1 * \vec{\mathbf{e}}_1 + 1 * \vec{\mathbf{e}}_2 + 2 * \vec{\mathbf{e}}_3$
# and a fully general vector $\vec{\mathbf{z}}$. Here the frame has numbers, not
# symbols: with all nine frame coordinates symbolic, the round trips take minutes each
# (`tasks/reference/frames-qr-and-reciprocal-frames.md`). Now the face of each frame
# vector is a plane, eq 3.7 divides it by the volume
# $\vec{\mathbf{b}}_1 \wedge \vec{\mathbf{b}}_2 \wedge \vec{\mathbf{b}}_3$, and the last
# rejection $\vec{\mathbf{w}}_3$ is $\vec{\mathbf{b}}_3$'s height above the plane of
# $\vec{\mathbf{b}}_1$ and $\vec{\mathbf{b}}_2$.

# %%
z_1: sympy.Symbol
z_2: sympy.Symbol
z_3: sympy.Symbol
z_1, z_2, z_3 = sympy.symbols("z_1 z_2 z_3", real=True)
b_1: MultiVectorBase = 2 * g3.e_1
b_2: MultiVectorBase = 1 * g3.e_1 + 3 * g3.e_2
b_3: MultiVectorBase = 1 * g3.e_1 + 1 * g3.e_2 + 2 * g3.e_3
space_frame: list[MultiVectorBase] = [b_1, b_2, b_3]
z: MultiVectorBase = (
    g3.Scalar(z_1) * g3.e_1 + g3.Scalar(z_2) * g3.e_2 + g3.Scalar(z_3) * g3.e_3
)
z

# %% [markdown]
# Theorem 1, eq 3.7: the reciprocal frame. $\vec{\mathbf{b}}^1$:

# %%
space_reciprocal: list[MultiVectorBase] = reciprocal_frame(space_frame)
space_reciprocal[0]

# %% [markdown]
# $\vec{\mathbf{b}}^2$:

# %%
space_reciprocal[1]

# %% [markdown]
# $\vec{\mathbf{b}}^3$:

# %%
space_reciprocal[2]

# %% [markdown]
# Drawn at the plot values:

# %%
P_B: list[Point] = [point(coordinates=list(lower)) for lower in space_frame]
P_B_UPPER: list[Point] = [point(coordinates=list(upper)) for upper in space_reciprocal]
fig_space: PendingFigure
with scene_3d(
    lower_left=Point(x=-1.0, y=-1.6), upper_right=Point(x=5.4, y=3.6)
) as fig_space:
    # The reciprocal vectors are short, so each label goes where its arrow leaves room.
    upper_labels: list[tuple[Point, LabelPos]] = [
        (Point(x=4, y=-8), LabelPos.br),
        (Point(x=-14, y=0), LabelPos.l),
        (Point(x=0, y=6), LabelPos.t),
    ]
    index: int
    for index in range(3):
        arrow(head=P_B[index], color=BLACK, text=rf"$\vec{{\mathbf{{b}}}}_{index + 1}$")
        arrow(
            head=P_B_UPPER[index],
            color=GREEN,
            text=rf"$\vec{{\mathbf{{b}}}}^{index + 1}$",
            offset=upper_labels[index][0],
            align=upper_labels[index][1],
        )
fig_space

# %% [markdown]
# Theorem 2: each is a vector. The grades present in $\vec{\mathbf{b}}^1$:

# %%
space_reciprocal[0].grades()

# %% [markdown]
# in $\vec{\mathbf{b}}^2$:

# %%
space_reciprocal[1].grades()

# %% [markdown]
# and in $\vec{\mathbf{b}}^3$:

# %%
space_reciprocal[2].grades()

# %% [markdown]
# Theorem 3: the table of dot products $\vec{\mathbf{b}}^k \cdot \vec{\mathbf{b}}_j$:

# %%
space_delta_table: sympy.Matrix = sympy.Matrix(
    [
        [
            sympy.simplify(sympy.sympify(upper.dot(lower).scalar_part()))
            for lower in space_frame
        ]
        for upper in space_reciprocal
    ]
)
space_delta_table

# %% [markdown]
# Its difference from the identity:

# %%
space_delta_table - sympy.eye(3)

# %% [markdown]
# Theorem 4: the coordinates times the frame:

# %%
space_rebuilt: MultiVectorBase = sum(
    [
        g3.Scalar(upper.dot(z).scalar_part()) * lower
        for upper, lower in zip(space_reciprocal, space_frame)
    ],
    start=0 * g3.e_1,
).simplified()
space_rebuilt

# %% [markdown]
# Its difference from $\vec{\mathbf{z}}$:

# %%
show_difference(space_rebuilt, z)

# %% [markdown]
# Theorem 5: with $\vec{\mathbf{n}}$ a normal to $\vec{\mathbf{b}}_1$'s face (the dual
# of $\vec{\mathbf{b}}_2 \wedge \vec{\mathbf{b}}_3$),
# $\vec{\mathbf{n}} / (\vec{\mathbf{n}} \cdot \vec{\mathbf{b}}_1)$ is:

# %%
n: MultiVectorBase = (b_2 ^ b_3).dual()
space_folded: MultiVectorBase = (
    g3.Scalar(sympy.Integer(1) / n.dot(b_1).scalar_part()) * n
).simplified()
space_folded

# %% [markdown]
# Its difference from $\vec{\mathbf{b}}^1$:

# %%
show_difference(space_folded, space_reciprocal[0])

# %% [markdown]
# Theorem 6: $\vec{\mathbf{w}}_3 / |\vec{\mathbf{w}}_3|^2$ is:

# %%
w_3: MultiVectorBase = Frame(tuple(space_frame)).orthogonal_vectors()[-1]
w_3_over_length: MultiVectorBase = (
    g3.Scalar(sympy.Integer(1) / w_3.magnitude_squared()) * w_3
).simplified()
w_3_over_length

# %% [markdown]
# Its difference from $\vec{\mathbf{b}}^3$:

# %%
show_difference(w_3_over_length, space_reciprocal[2])

# %% [markdown]
# Theorems 7 and 8: both inverses undo the map, in both orders, and they agree. The map,
# then the reciprocal-frame inverse, on $\vec{\mathbf{z}}$:

# %%
space_by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
space_by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
space_by_reciprocal.inverse(space_by_reciprocal(z)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{z}}$:

# %%
show_difference(space_by_reciprocal.inverse(space_by_reciprocal(z)), z)

# %% [markdown]
# The map, then the peeling inverse:

# %%
space_by_peel.inverse(space_by_peel(z)).simplified()

# %% [markdown]
# The round trip gives $\vec{\mathbf{z}}$ back.

# %% [markdown]
# The reciprocal-frame inverse, then the map:

# %%
space_by_reciprocal(space_by_reciprocal.inverse(z)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{z}}$:

# %%
show_difference(space_by_reciprocal(space_by_reciprocal.inverse(z)), z)

# %% [markdown]
# The peeling inverse, then the map:

# %%
space_by_peel(space_by_peel.inverse(z)).simplified()

# %% [markdown]
# The round trip gives $\vec{\mathbf{z}}$ back.

# %% [markdown]
# The two inverses agree. The reciprocal-frame inverse of $\vec{\mathbf{z}}$:

# %%
space_by_reciprocal.inverse(z).simplified()

# %% [markdown]
# the peeling inverse of $\vec{\mathbf{z}}$:

# %%
space_by_peel.inverse(z).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(space_by_reciprocal.inverse(z), space_by_peel.inverse(z))
