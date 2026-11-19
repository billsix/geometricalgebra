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
# # Frames and QR in two dimensions — calculations
#
# Companion to the *Frames and QR* chapter. On graph paper the two axes are
# perpendicular, and a point's coordinates are read straight off them. A frame is a pair
# of slanted axes $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$; this notebook builds
# perpendicular axes $\vec{\mathbf{w}}_1, \vec{\mathbf{w}}_2$ from them, then uses those
# to read a point's coordinates in the slanted frame.
#
# Each section computes with gacalc's `Frame` (`gacalc.frame`) on symbolic coordinates,
# so every result is a formula for every frame, then draws it with ePiX, live, at the
# plot values. The colours are the same throughout: the frame $\vec{\mathbf{v}}_i$ is
# blue, the orthogonal $\vec{\mathbf{w}}_i$ green, the unit $\vec{\mathbf{u}}_i$ purple,
# and the target $\vec{\mathbf{y}}$ and its remainders red. The axes are drawn light and
# unlabelled: here $\vec{\mathbf{x}}$ and $\vec{\mathbf{y}}$ are vectors, the
# coordinates and the target of the frame's map. Each check shows both sides, then their
# difference.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.epixscene.frame_scene import (
    BLUE,
    GRAY_FILL,
    GREEN,
    ORIGIN2,
    PURPLE,
    PURPLE_FILL,
    RED,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    patch,
    point,
    right_angle,
    scene_2d,
)
from gacalc.frame import Frame
from gacalc.functions import InvertibleFunction, MatrixBackend, inverse
from gacalc.g2 import G, Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## A frame and its orthogonal set
#
# Two vectors, every coordinate a symbol. `Frame` keeps them as they are:

# %%
p: sympy.Symbol
q: sympy.Symbol
r: sympy.Symbol
t: sympy.Symbol
p, q, r, t = sympy.symbols("p q r t", real=True)
v_1: Vector = Scalar(p) * e_1 + Scalar(q) * e_2
v_1

# %% [markdown]
# and $\vec{\mathbf{v}}_2$:

# %%
v_2: Vector = Scalar(r) * e_1 + Scalar(t) * e_2
v_2

# %% [markdown]
# The values used to draw the figures in the first part of the notebook; the figures'
# frames are sized for these values. They are neither perpendicular nor of unit length.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(p, 2), (q, 1), (r, 1), (t, 2)]


def tex(value: Real) -> str:
    """``value`` at the plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, values))


# %% [markdown]
# `orthogonal_vectors()` computes the orthogonal set:
# $\vec{\mathbf{w}}_1 = \vec{\mathbf{v}}_1$, and $\vec{\mathbf{w}}_2$ is
# $\vec{\mathbf{v}}_2$ with its part along $\vec{\mathbf{v}}_1$ rejected.
# $\vec{\mathbf{w}}_1$:

# %%
frame: Frame = Frame((v_1, v_2))
w_1: MultiVectorBase
w_2: MultiVectorBase
w_1, w_2 = frame.orthogonal_vectors()
w_1

# %% [markdown]
# $\vec{\mathbf{w}}_2$:

# %%
w_2 = w_2.simplified()
w_2

# %% [markdown]
# They are perpendicular, $\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{w}}_2 = 0$:

# %%
sympy.simplify(sympy.sympify(w_1.dot(w_2).scalar_part()))

# %% [markdown]
# The unit vectors $\vec{\mathbf{u}}_i = \vec{\mathbf{w}}_i / |\vec{\mathbf{w}}_i|$
# (purple, short) are the orthonormal set. $\vec{\mathbf{u}}_1$:

# %%
u_1: MultiVectorBase
u_2: MultiVectorBase
u_1, u_2 = frame.orthonormal_vectors()
u_1 = u_1.simplified()
u_1

# %% [markdown]
# $\vec{\mathbf{u}}_2$:

# %%
u_2 = u_2.simplified()
u_2

# %% [markdown]
# Drawn at the plot values:

# %%
P_V1: Point = point(coordinates=list(at_values(v_1, values)))
P_V2: Point = point(coordinates=list(at_values(v_2, values)))
P_W2: Point = point(coordinates=list(at_values(w_2, values)))
P_U1: Point = point(coordinates=list(at_values(u_1, values)))
P_U2: Point = point(coordinates=list(at_values(u_2, values)))
fig: PendingFigure
with scene_2d(lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.0, y=2.6)) as fig:
    arrow(head=P_V1, color=BLUE, text=r"$\vec{\mathbf{v}}_1 = \vec{\mathbf{w}}_1$")
    arrow(head=P_V2, color=BLUE, text=r"$\vec{\mathbf{v}}_2$", offset=Point(x=6, y=2))
    arrow(
        head=P_W2,
        color=GREEN,
        text=r"$\vec{\mathbf{w}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN2, toward_a=P_V1, toward_b=P_W2)
    # w_2 is v_2 minus its shadow on v_1: the dashed drop from v_2 to the v_1 line
    dashed_arrow(tail=P_V2, head=P_V2 - P_W2, color=GREEN)
    # the unit vectors last, so they sit on top of the longer w's they point along
    arrow(
        head=P_U1,
        color=PURPLE,
        width=3.0,
        text=r"$\vec{\mathbf{u}}_1$",
        offset=Point(x=4, y=-10),
    )
    arrow(
        head=P_U2,
        color=PURPLE,
        width=3.0,
        text=r"$\vec{\mathbf{u}}_2$",
        offset=Point(x=8, y=0),
    )
fig

# %% [markdown]
# ## The coefficients are shadows
#
# `coefficients()` is the table
# $(\vec{\mathbf{w}}_j \cdot \vec{\mathbf{v}}_i) / |\vec{\mathbf{w}}_j|^2$: row $i$ says
# how much of each $\vec{\mathbf{w}}_j$ it takes to rebuild $\vec{\mathbf{v}}_i$. It is
# triangular, because $\vec{\mathbf{v}}_1 = \vec{\mathbf{w}}_1$ uses no
# $\vec{\mathbf{w}}_2$, and its diagonal is all ones, because each $\vec{\mathbf{v}}_i$
# is $\vec{\mathbf{w}}_i$ plus a part in the earlier directions.

# %%
table: sympy.Matrix = sympy.Matrix(frame.coefficients()).applyfunc(sympy.simplify)
table

# %% [markdown]
# The entry below the diagonal is the length of $\vec{\mathbf{v}}_2$'s shadow on
# $\vec{\mathbf{w}}_1$, in units of $|\vec{\mathbf{w}}_1|$:

# %%
c_21: Real = table.row(1)[0]
c_21

# %% [markdown]
# Rebuilding $\vec{\mathbf{v}}_2$ from the table,
# $c_{21} * \vec{\mathbf{w}}_1 + 1 * \vec{\mathbf{w}}_2$:

# %%
rebuilt_v_2: MultiVectorBase = (Scalar(c_21) * w_1 + 1 * w_2).simplified()
rebuilt_v_2

# %% [markdown]
# Its difference from $\vec{\mathbf{v}}_2$:

# %%
(v_2 - rebuilt_v_2).simplified()

# %% [markdown]
# At the plot values, $c_{21}$:

# %%
at_values(c_21, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_SHADOW: Point = point(coordinates=list(at_values(Scalar(c_21) * w_1, values)))
fig_shadow: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.0, y=2.6)
) as fig_shadow:
    arrow(head=P_V1, color=BLUE, text=r"$\vec{\mathbf{w}}_1$", offset=Point(x=6, y=-4))
    arrow(head=P_V2, color=BLUE, text=r"$\vec{\mathbf{v}}_2$", offset=Point(x=0, y=6))
    arrow(
        head=P_SHADOW,
        color=GREEN,
        text=rf"${tex(c_21)} * \vec{{\mathbf{{w}}}}_1$",
        offset=Point(x=4, y=-10),
    )
    dashed_arrow(tail=P_SHADOW, head=P_V2, color=GREEN)
    note(
        at=0.5 * (P_SHADOW + P_V2),
        text=r"$\vec{\mathbf{w}}_2$",
        color=GREEN,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_SHADOW, toward_a=P_V1, toward_b=P_W2)
fig_shadow

# %% [markdown]
# ## Area is base times height
#
# The parallelogram of $\vec{\mathbf{v}}_1$ and $\vec{\mathbf{v}}_2$ has base
# $|\vec{\mathbf{w}}_1|$ along $\vec{\mathbf{v}}_1$ and height $|\vec{\mathbf{w}}_2|$,
# the part of $\vec{\mathbf{v}}_2$ that sticks out of $\vec{\mathbf{v}}_1$'s line. Their
# product is the area, the magnitude of $\vec{\mathbf{v}}_1 \wedge \vec{\mathbf{v}}_2$.
# The base:

# %%
base: Real = w_1.magnitude()
base

# %% [markdown]
# the height:

# %%
height: Real = sympy.simplify(sympy.sympify(w_2.magnitude()))
height

# %% [markdown]
# base times height:

# %%
base_times_height: Real = sympy.simplify(sympy.sympify(base * height))
base_times_height

# %% [markdown]
# The area $|\vec{\mathbf{v}}_1 \wedge \vec{\mathbf{v}}_2|$:

# %%
area: Real = (v_1 ^ v_2).magnitude()
area

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(base_times_height - area))

# %% [markdown]
# Drawn at the plot values:

# %%
fig_area: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.4, y=3.4)
) as fig_area:
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    arrow(
        head=P_V1,
        color=BLUE,
        text=rf"$|\vec{{\mathbf{{w}}}}_1| = {tex(base)}$",
        offset=Point(x=6, y=-6),
    )
    arrow(
        head=P_V2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-6, y=4),
        align=LabelPos.l,
    )
    dashed_arrow(tail=P_SHADOW, head=P_V2, color=GREEN)
    note(
        at=0.5 * (P_SHADOW + P_V2),
        text=rf"$|\vec{{\mathbf{{w}}}}_2| = {tex(height)}$",
        color=GREEN,
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    right_angle(corner=P_SHADOW, toward_a=P_V1, toward_b=P_W2)
    note(
        at=Point(x=2.1, y=2.0),
        text=rf"area $= |\vec{{\mathbf{{w}}}}_1| * |\vec{{\mathbf{{w}}}}_2| = {tex(area)}$",
    )
fig_area

# %% [markdown]
# ## The forward map sends $\vec{\mathbf{e}}_i$ to $\vec{\mathbf{v}}_i$
#
# `to_invertible_function()` is the linear map
# $f(\vec{\mathbf{x}}) = x_1 * \vec{\mathbf{v}}_1 + x_2 * \vec{\mathbf{v}}_2$: it sends
# $\vec{\mathbf{e}}_1$ to $\vec{\mathbf{v}}_1$ and $\vec{\mathbf{e}}_2$ to
# $\vec{\mathbf{v}}_2$, so the unit square (gray) lands on the frame's parallelogram
# (purple). Its matrix has the $\vec{\mathbf{v}}_i$ as columns:

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
F: sympy.Matrix = sympy.Matrix(
    f.to_matrix(G, n=2, backend=MatrixBackend.SYMPY)
).extract([0, 1], [0, 1])
F

# %% [markdown]
# $f(\vec{\mathbf{e}}_1)$:

# %%
f(1 * e_1 + 0 * e_2)

# %% [markdown]
# minus $\vec{\mathbf{v}}_1$:

# %%
(f(1 * e_1 + 0 * e_2) - v_1).simplified()

# %% [markdown]
# $f(\vec{\mathbf{e}}_2)$:

# %%
f(0 * e_1 + 1 * e_2)

# %% [markdown]
# minus $\vec{\mathbf{v}}_2$:

# %%
(f(0 * e_1 + 1 * e_2) - v_2).simplified()

# %% [markdown]
# Drawn at the plot values:

# %%
P_E1: Point = Point(x=1, y=0)
P_E2: Point = Point(x=0, y=1)
fig_forward: PendingFigure
with scene_2d(
    lower_left=Point(x=-0.6, y=-0.6), upper_right=Point(x=3.4, y=3.4)
) as fig_forward:
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    patch(corners=[ORIGIN2, P_E1, P_E1 + P_E2, P_E2], color=GRAY_FILL)
    arrow(
        head=P_E1,
        text=r"$\vec{\mathbf{e}}_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_E2,
        text=r"$\vec{\mathbf{e}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_V1, color=BLUE, text=r"$f(\vec{\mathbf{e}}_1) = \vec{\mathbf{v}}_1$")
    arrow(
        head=P_V2,
        color=BLUE,
        text=r"$f(\vec{\mathbf{e}}_2) = \vec{\mathbf{v}}_2$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_forward

# %% [markdown]
# ## $f = Q \circ R$
#
# QR splits $f$ into two steps. $R$ writes each $\vec{\mathbf{v}}_i$ in the orthonormal
# coordinates $\vec{\mathbf{u}}_j \cdot \vec{\mathbf{v}}_i$: it keeps
# $\vec{\mathbf{e}}_1$'s line, and its matrix is upper triangular because
# $\vec{\mathbf{v}}_1$ has no $\vec{\mathbf{u}}_2$ part. $Q$ then turns the plane so the
# $\vec{\mathbf{e}}_j$ land on the $\vec{\mathbf{u}}_j$: a rotation. $Q$ is itself a
# frame's function, the frame of the $\vec{\mathbf{u}}_j$, and $R = Q^{-1} \circ f$.
# $R$'s matrix:

# %%
Q: InvertibleFunction[MultiVectorBase] = Frame((u_1, u_2)).to_invertible_function()
R: InvertibleFunction[MultiVectorBase] = inverse(Q) @ f
R_matrix: sympy.Matrix = (
    sympy.Matrix(R.to_matrix(G, n=2, backend=MatrixBackend.SYMPY))
    .extract([0, 1], [0, 1])
    .applyfunc(sympy.simplify)
)
R_matrix

# %% [markdown]
# $Q$'s matrix:

# %%
Q_matrix: sympy.Matrix = (
    sympy.Matrix(Q.to_matrix(G, n=2, backend=MatrixBackend.SYMPY))
    .extract([0, 1], [0, 1])
    .applyfunc(sympy.simplify)
)
Q_matrix

# %% [markdown]
# Their product $Q * R$:

# %%
QR_product: sympy.Matrix = (Q_matrix * R_matrix).applyfunc(sympy.simplify)
QR_product

# %% [markdown]
# minus $f$'s matrix:

# %%
(QR_product - F).applyfunc(sympy.simplify)

# %% [markdown]
# Drawn at the plot values:

# %%
P_R1: Point = point(coordinates=list(at_values(R(1 * e_1 + 0 * e_2), values)))
P_R2: Point = point(coordinates=list(at_values(R(0 * e_1 + 1 * e_2), values)))
fig_r: PendingFigure
with scene_2d(
    lower_left=Point(x=-0.6, y=-0.6), upper_right=Point(x=4.6, y=2.2)
) as fig_r:
    patch(corners=[ORIGIN2, P_R1, P_R1 + P_R2, P_R2], color=PURPLE_FILL)
    patch(corners=[ORIGIN2, P_E1, P_E1 + P_E2, P_E2], color=GRAY_FILL)
    arrow(
        head=P_R1,
        color=BLUE,
        text=r"$R(\vec{\mathbf{e}}_1)$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_R2,
        color=BLUE,
        text=r"$R(\vec{\mathbf{e}}_2)$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_r

# %% [markdown]
# Drawn at the plot values:

# %%
fig_qr: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=4.6, y=3.4)
) as fig_qr:
    patch(corners=[ORIGIN2, P_R1, P_R1 + P_R2, P_R2], color=GRAY_FILL)
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    arrow(
        head=P_U1,
        color=PURPLE,
        width=2.6,
        text=r"$\vec{\mathbf{u}}_1$",
        offset=Point(x=4, y=-8),
    )
    arrow(
        head=P_U2,
        color=PURPLE,
        width=2.6,
        text=r"$\vec{\mathbf{u}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(
        head=P_V1, color=BLUE, text=r"$Q(R(\vec{\mathbf{e}}_1)) = \vec{\mathbf{v}}_1$"
    )
    arrow(
        head=P_V2,
        color=BLUE,
        text=r"$Q(R(\vec{\mathbf{e}}_2)) = \vec{\mathbf{v}}_2$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_qr

# %% [markdown]
# ## The inverse, one peel at a time
#
# `f.inverse` recovers the coordinates $\vec{\mathbf{x}}$ from
# $\vec{\mathbf{y}} = f(\vec{\mathbf{x}})$ by peeling the frame from its last vector.
# The steps below use a second frame $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$ and a
# target $\vec{\mathbf{y}}$, every coordinate a symbol:

# %%
m_1: sympy.Symbol
m_2: sympy.Symbol
n_1: sympy.Symbol
n_2: sympy.Symbol
y_1: sympy.Symbol
y_2: sympy.Symbol
m_1, m_2, n_1, n_2, y_1, y_2 = sympy.symbols("m_1 m_2 n_1 n_2 y_1 y_2", real=True)
a_1: Vector = Scalar(m_1) * e_1 + Scalar(m_2) * e_2
a_1

# %% [markdown]
# and $\vec{\mathbf{a}}_2$:

# %%
a_2: Vector = Scalar(n_1) * e_1 + Scalar(n_2) * e_2
a_2

# %% [markdown]
# and $\vec{\mathbf{y}}$:

# %%
y: Vector = Scalar(y_1) * e_1 + Scalar(y_2) * e_2
y

# %% [markdown]
# The plot values for this part are the frame from the reference text,
# $\vec{\mathbf{v}}_1 = 2 * \vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{v}}_2 = 1 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$, with
# $\vec{\mathbf{y}} = 3 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$, so every number
# in the figures is small and exact; the figures' frames are sized for them.

# %%
peel_values: list[tuple[sympy.Symbol, Real]] = [
    (m_1, 2),
    (m_2, 0),
    (n_1, 1),
    (n_2, 3),
    (y_1, 3),
    (y_2, 3),
]


def peel_tex(value: Real) -> str:
    """``value`` at the peel's plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, peel_values))


# %% [markdown]
# The orthogonal set of this frame: $\vec{\mathbf{w}}_1$,

# %%
peel_frame: Frame = Frame((a_1, a_2))
b_1: MultiVectorBase
b_2: MultiVectorBase
b_1, b_2 = peel_frame.orthogonal_vectors()
b_1

# %% [markdown]
# and $\vec{\mathbf{w}}_2$:

# %%
b_2 = b_2.simplified()
b_2

# %% [markdown]
# $\vec{\mathbf{w}}_2$ is perpendicular to *every other* frame vector,
# $\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{v}}_1 = 0$, so it can read off $x_2$ alone:

# %%
sympy.simplify(sympy.sympify(b_2.dot(a_1).scalar_part()))

# %% [markdown]
# $\vec{\mathbf{w}}_1$ is not perpendicular to $\vec{\mathbf{v}}_2$, so
# $\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{y}}$ mixes both coordinates: the peel cannot
# start with $x_1$. $\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{v}}_2$:

# %%
w_1_dot_v_2: Real = b_1.dot(a_2).scalar_part()
w_1_dot_v_2

# %% [markdown]
# **Step 0, the setup.** The frame (blue) and its parallelogram, the target
# $\vec{\mathbf{y}}$ (red), and the orthogonal set (green):
# $\vec{\mathbf{w}}_1 = \vec{\mathbf{v}}_1$, and $\vec{\mathbf{w}}_2$ at a right angle
# to $\vec{\mathbf{v}}_1$'s line.

# %%
P_A1: Point = point(coordinates=list(at_values(a_1, peel_values)))
P_A2: Point = point(coordinates=list(at_values(a_2, peel_values)))
P_B2: Point = point(coordinates=list(at_values(b_2, peel_values)))
P_Y: Point = point(coordinates=list(at_values(y, peel_values)))
PEEL_LOWER_LEFT: Point = Point(x=-0.6, y=-0.6)
PEEL_UPPER_RIGHT: Point = Point(x=4.0, y=3.8)
fig_step_0: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_0:
    patch(corners=[ORIGIN2, P_A1, P_A1 + P_A2, P_A2], color=PURPLE_FILL)
    arrow(
        head=P_A1,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_1 = \vec{\mathbf{w}}_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(
        head=P_B2,
        color=GREEN,
        text=r"$\vec{\mathbf{w}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
        width=2.2,
    )
    right_angle(corner=ORIGIN2, toward_a=P_A1, toward_b=P_B2)
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
    note(
        at=Point(x=2.0, y=3.5),
        text=rf"$\vec{{\mathbf{{w}}}}_2 \cdot \vec{{\mathbf{{v}}}}_1 = 0$, but $\vec{{\mathbf{{w}}}}_1 \cdot \vec{{\mathbf{{v}}}}_2 = {peel_tex(w_1_dot_v_2)}$",
    )
fig_step_0

# %% [markdown]
# **Step 1, read $x_2$.** Project $\vec{\mathbf{y}}$ onto $\vec{\mathbf{w}}_2$. Every
# earlier frame vector is perpendicular to $\vec{\mathbf{w}}_2$ and drops out, so the
# projection is $x_2$ copies of $\vec{\mathbf{w}}_2$: dividing it by
# $\vec{\mathbf{w}}_2$ reads $x_2$. The projection's length is $\vec{\mathbf{y}}$'s
# height above $\vec{\mathbf{v}}_1$'s line, and $|\vec{\mathbf{w}}_2|$ is
# $\vec{\mathbf{v}}_2$'s own height, so $x_2$ is two heights, one divided by the other.
# The projection:

# %%
y_onto_w_2: MultiVectorBase = y.projected_onto(onto=b_2).simplified()
y_onto_w_2

# %% [markdown]
# $x_2$:

# %%
x_2: Real = sympy.simplify(sympy.sympify((y_onto_w_2 / b_2).scalar_part()))
x_2

# %% [markdown]
# At the plot values:

# %%
at_values(x_2, peel_values)

# %% [markdown]
# Drawn at the plot values:

# %%
w_2_dot_y: Real = b_2.dot(y).scalar_part()
fig_step_1: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_1:
    arrow(
        head=P_A1,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
    dashed_arrow(
        tail=P_A2,
        head=Point(x=P_A2.x1(), y=0),
        color=BLUE,
        text=rf"$|\vec{{\mathbf{{w}}}}_2| = {peel_tex(b_2.magnitude())}$",
        offset=Point(x=-6, y=24),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=0),
        color=RED,
        text=(
            r"$\frac{\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{y}}}{|\vec{\mathbf{w}}_2|} = "
            rf"{peel_tex(w_2_dot_y / b_2.magnitude())}$"
        ),
        offset=Point(x=6, y=24),
    )
    note(
        at=Point(x=2.0, y=3.5),
        text=(
            r"$x_2 = \frac{\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{y}}}{|\vec{\mathbf{w}}_2|^2} = "
            rf"\frac{{{peel_tex(w_2_dot_y)}}}{{{peel_tex(b_2.magnitude_squared())}}}"
            rf" = {peel_tex(x_2)}$"
        ),
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_2 * \vec{\mathbf{v}}_2$.** Subtract $\vec{\mathbf{v}}_2$'s share:
# $\vec{\mathbf{y}}$ slides back along $\vec{\mathbf{v}}_2$ (dashed) and lands on
# $\vec{\mathbf{v}}_1$'s line. The remainder
# $\vec{\mathbf{r}} = \vec{\mathbf{y}} - x_2 * \vec{\mathbf{v}}_2$ is built from
# $\vec{\mathbf{v}}_1$ alone:

# %%
remainder: Vector = (y - Scalar(x_2) * a_2).simplified()
remainder

# %% [markdown]
# At the plot values:

# %%
at_values(remainder, peel_values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_R: Point = point(coordinates=list(at_values(remainder, peel_values)))
fig_step_2: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_2:
    arrow(
        head=P_A2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
    dashed_arrow(tail=P_Y, head=P_R, color=BLUE)
    note(
        at=0.5 * (P_Y + P_R),
        text=r"$-x_2 * \vec{\mathbf{v}}_2$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    arrow(
        head=P_R,
        color=RED,
        text=r"$\vec{\mathbf{r}} = \vec{\mathbf{y}} - x_2 * \vec{\mathbf{v}}_2$",
        offset=Point(x=0, y=-20),
        align=LabelPos.b,
        width=2.2,
    )
fig_step_2

# %% [markdown]
# **Step 3, read $x_1$.** The one-vector frame $\vec{\mathbf{v}}_1$ is left, and its
# last orthogonal vector $\vec{\mathbf{w}}_1$ is perpendicular to every *other* vector
# in it (there are none). The same rule reads $x_1$:

# %%
x_1: Real = sympy.simplify(
    sympy.sympify((remainder.projected_onto(onto=b_1) / b_1).scalar_part())
)
x_1

# %% [markdown]
# The recovered coordinates $\vec{\mathbf{x}}$:

# %%
x: Vector = Scalar(x_1) * e_1 + Scalar(x_2) * e_2
x

# %% [markdown]
# At the plot values:

# %%
at_values(x, peel_values)

# %% [markdown]
# gacalc's inverse of the frame's map, applied to $\vec{\mathbf{y}}$:

# %%
g: InvertibleFunction[MultiVectorBase] = peel_frame.to_invertible_function()
g.inverse(y).simplified()

# %% [markdown]
# Its difference from the peeled $\vec{\mathbf{x}}$:

# %%
(g.inverse(y) - x).simplified()

# %% [markdown]
# The map sends $\vec{\mathbf{x}}$ back to:

# %%
g(x).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{y}}$:

# %%
(g(x) - y).simplified()

# %% [markdown]
# The recovered $\vec{\mathbf{x}}$ (black) is the point $f$ sends to $\vec{\mathbf{y}}$:
# $x_1 * \vec{\mathbf{v}}_1 + x_2 * \vec{\mathbf{v}}_2$, drawn tip to tail in blue, ends
# on $\vec{\mathbf{y}}$.

# %%
P_X: Point = point(coordinates=list(at_values(x, peel_values)))
fig_step_3: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_3:
    P_X1_A1: Point = point(coordinates=list(at_values(Scalar(x_1) * a_1, peel_values)))
    P_X2_A2: Point = point(coordinates=list(at_values(Scalar(x_2) * a_2, peel_values)))
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}} = f(\vec{\mathbf{x}})$")
    arrow(
        head=P_X1_A1,
        color=BLUE,
        text=r"$x_1 * \vec{\mathbf{v}}_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    dashed_arrow(tail=P_X1_A1, head=P_X1_A1 + P_X2_A2, color=BLUE)
    note(
        at=P_X1_A1 + 0.5 * P_X2_A2,
        text=r"$x_2 * \vec{\mathbf{v}}_2$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    # x can lie along y, so it is drawn after y, thicker, to stay visible
    arrow(
        head=P_X,
        text=r"$\vec{\mathbf{x}}$",
        offset=Point(x=-6, y=4),
        align=LabelPos.l,
        width=3.0,
    )
    note(
        at=Point(x=2.0, y=3.5),
        text=(
            r"$x_1 = \frac{\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{r}}}{|\vec{\mathbf{w}}_1|^2} = "
            rf"\frac{{{peel_tex(b_1.dot(remainder).scalar_part())}}}"
            rf"{{{peel_tex(b_1.magnitude_squared())}}} = {peel_tex(x_1)}$"
        ),
    )
fig_step_3

# %% [markdown]
# ## The round trip, for every input
#
# For a symbolic $\vec{\mathbf{x}}$, `inverse(f) @ f` gives $\vec{\mathbf{x}}$ back
# unchanged, and `f @ inverse(f)` does the same for a symbolic $\vec{\mathbf{y}}$: the
# peel is exact, with no rounding. A general $\vec{\mathbf{x}}$:

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_1, s_2 = sympy.symbols("x_1 x_2", real=True)
general: Vector = Scalar(s_1) * e_1 + Scalar(s_2) * e_2
general

# %% [markdown]
# $f^{-1}(f(\vec{\mathbf{x}}))$, for the first frame:

# %%
(inverse(f) @ f)(general).simplified()

# %% [markdown]
# minus $\vec{\mathbf{x}}$:

# %%
((inverse(f) @ f)(general) - general).simplified()

# %% [markdown]
# $f(f^{-1}(\vec{\mathbf{y}}))$, for a general $\vec{\mathbf{y}}$:

# %%
(f @ inverse(f))(general).simplified()

# %% [markdown]
# minus $\vec{\mathbf{y}}$:

# %%
((f @ inverse(f))(general) - general).simplified()

# %% [markdown]
# ## The last reciprocal vector
#
# $\vec{\mathbf{v}}^2 = \vec{\mathbf{w}}_2 / |\vec{\mathbf{w}}_2|^2$ dots to 0 with
# $\vec{\mathbf{v}}_1$ and to 1 with $\vec{\mathbf{v}}_2$: it reads $x_2$ in a single
# dot product, which is exactly step 1. The whole reciprocal frame, one such vector per
# coordinate, comes from Hestenes and is a separate chapter. $\vec{\mathbf{v}}^2$:

# %%
reciprocal_2: MultiVectorBase = (b_2 / b_2.magnitude_squared()).simplified()
reciprocal_2

# %% [markdown]
# $\vec{\mathbf{v}}^2 \cdot \vec{\mathbf{v}}_1$:

# %%
sympy.simplify(sympy.sympify(reciprocal_2.dot(a_1).scalar_part()))

# %% [markdown]
# $\vec{\mathbf{v}}^2 \cdot \vec{\mathbf{v}}_2$:

# %%
sympy.simplify(sympy.sympify(reciprocal_2.dot(a_2).scalar_part()))

# %% [markdown]
# Drawn at the plot values:

# %%
fig_reciprocal: PendingFigure
with scene_2d(
    lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT
) as fig_reciprocal:
    arrow(
        head=P_A1,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(
        head=point(coordinates=list(at_values(reciprocal_2, peel_values))),
        color=GREEN,
        text=r"$\vec{\mathbf{v}}^2 = \frac{\vec{\mathbf{w}}_2}{|\vec{\mathbf{w}}_2|^2}$",
        offset=Point(x=-6, y=6),
        align=LabelPos.l,
        width=2.4,
    )
    right_angle(corner=ORIGIN2, toward_a=P_A1, toward_b=P_B2, size=0.12)
fig_reciprocal
