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
# # Frames and QR in three dimensions — calculations
#
# The two-dimensional notebook, one dimension up. Each section computes with gacalc's
# `Frame`, then draws the result with ePiX, live, from one fixed camera so a reader can
# follow a vector from figure to figure. The colours match the 2D notebook: the frame
# $\vec{\mathbf{v}}_i$ is blue, the orthogonal $\vec{\mathbf{w}}_i$ green, and the
# target $\vec{\mathbf{y}}$ and its remainders red. The axes are drawn light and
# unlabelled: here $\vec{\mathbf{x}}$ and $\vec{\mathbf{y}}$ are vectors, the
# coordinates and the target of the frame's map.
#
# The frame here has numbers, not symbols: with all nine frame coordinates symbolic,
# each check takes minutes (`tasks/reference/frames-qr-and-reciprocal-frames.md`). The
# target $\vec{\mathbf{y}}$ of the peel is symbolic, so the peel's steps are formulas
# for every $\vec{\mathbf{y}}$, and numbers for $\vec{\mathbf{y}}$ appear only to draw
# the figures. Each check shows both sides, then their difference.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.epixscene.frame_scene import (
    BLUE,
    GRAY_EDGE,
    GREEN,
    ORIGIN3,
    PLANE_FILL,
    RED,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    box_edges,
    dashed_arrow,
    note,
    patch,
    point,
    right_angle,
    scene_3d,
)
from gacalc.frame import Frame
from gacalc.functions import InvertibleFunction, MatrixBackend, inverse
from gacalc.g3 import G, Scalar, Vector, e_1, e_2, e_3
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## A frame and its orthogonal set
#
# $\vec{\mathbf{v}}_1$ lies along $\vec{\mathbf{e}}_1$, $\vec{\mathbf{v}}_2$ leans over
# it in the $\mathbf{e}_{12}$ plane, and $\vec{\mathbf{v}}_3$ leans over that plane.
# Orthogonalizing in frame order rejects from each vector its part in the span of the
# earlier ones: $\vec{\mathbf{w}}_2$ is $\vec{\mathbf{v}}_2$ with its
# $\vec{\mathbf{v}}_1$ part removed, and $\vec{\mathbf{w}}_3$ is $\vec{\mathbf{v}}_3$
# with its part in the plane of $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$ removed, so
# $\vec{\mathbf{w}}_3$ is normal to that plane.

# %%
v_1: Vector = 2 * e_1 + 0 * e_2 + 0 * e_3
v_2: Vector = 1 * e_1 + 2 * e_2 + 0 * e_3
v_3: Vector = 1 * e_1 + 1 * e_2 + 2 * e_3
frame: Frame = Frame((v_1, v_2, v_3))
w_1: MultiVectorBase
w_2: MultiVectorBase
w_3: MultiVectorBase
w_1, w_2, w_3 = frame.orthogonal_vectors()
w_1

# %% [markdown]
# $\vec{\mathbf{w}}_2$:

# %%
w_2

# %% [markdown]
# $\vec{\mathbf{w}}_3$:

# %%
w_3

# %% [markdown]
# The coefficient table
# $(\vec{\mathbf{w}}_j \cdot \vec{\mathbf{v}}_i) / |\vec{\mathbf{w}}_j|^2$, triangular
# with ones on the diagonal:

# %%
sympy.Matrix(frame.coefficients())

# %% [markdown]
# Drawn at the plot values:

# %%
P_V1: Point = point(coordinates=list(v_1))
P_V2: Point = point(coordinates=list(v_2))
P_V3: Point = point(coordinates=list(v_3))
P_W2: Point = point(coordinates=list(w_2))
P_W3: Point = point(coordinates=list(w_3))
# the projected extent of the parallelepiped and axes from CAMERA, plus room for labels
LOWER_LEFT: Point = Point(x=-0.8, y=-1.9)
UPPER_RIGHT: Point = Point(x=6.0, y=3.6)
# where a step's equation goes: high on the z axis, the text running to the right
EQUATION_AT: Point = Point(x=0, y=0, z=3.4)
fig: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V1,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_1 = \vec{\mathbf{w}}_1$",
        offset=Point(x=12, y=4),
    )
    arrow(head=P_V2, color=BLUE, text=r"$\vec{\mathbf{v}}_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text=r"$\vec{\mathbf{v}}_3$", offset=Point(x=4, y=4))
    arrow(
        head=P_W2,
        color=GREEN,
        text=r"$\vec{\mathbf{w}}_2$",
        offset=Point(x=8, y=-10),
        align=LabelPos.r,
    )
    arrow(
        head=P_W3,
        color=GREEN,
        text=r"$\vec{\mathbf{w}}_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN3, toward_a=P_V1, toward_b=P_W2)
    right_angle(corner=ORIGIN3, toward_a=P_W2, toward_b=P_W3)
    # w_3 is v_3 minus its shadow in the plane: the dashed drop from v_3 to the plane
    dashed_arrow(tail=P_V3, head=P_V3 + (-1) * P_W3, color=GREEN)
fig

# %% [markdown]
# ## Volume is base times height times height
#
# The parallelepiped of $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2, \vec{\mathbf{v}}_3$ has
# a parallelogram base of area $|\vec{\mathbf{w}}_1| * |\vec{\mathbf{w}}_2|$ (the 2D
# result) and height $|\vec{\mathbf{w}}_3|$ above it. The product is the volume, the
# magnitude of $\vec{\mathbf{v}}_1 \wedge \vec{\mathbf{v}}_2 \wedge \vec{\mathbf{v}}_3$.

# %%
base_area: Real = w_1.magnitude() * w_2.magnitude()
base_area

# %% [markdown]
# The height $|\vec{\mathbf{w}}_3|$:

# %%
height: Real = w_3.magnitude()
height

# %% [markdown]
# Base times height:

# %%
base_area * height

# %% [markdown]
# The volume $|\vec{\mathbf{v}}_1 \wedge \vec{\mathbf{v}}_2 \wedge \vec{\mathbf{v}}_3|$:

# %%
volume: Real = (v_1 ^ v_2 ^ v_3).magnitude()
volume

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(base_area * height - volume))

# %% [markdown]
# Drawn at the plot values:

# %%
fig_volume: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_volume:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    box_edges(a=P_V1, b=P_V2, c=P_V3, color=BLUE, width=0.8)
    dashed_arrow(tail=P_V3 + (-1) * P_W3, head=P_V3, color=GREEN)
    # Left of the box's top corner and below its front corner: the open parts of the plot.
    note(
        at=P_V3,
        text=rf"$|\vec{{\mathbf{{w}}}}_3| = {sympy.latex(height)}$",
        color=GREEN,
        offset=Point(x=-10, y=0),
        align=LabelPos.l,
    )
    note(
        at=P_V1,
        offset=Point(x=-10, y=-20),
        align=LabelPos.bl,
        text=rf"$|\vec{{\mathbf{{w}}}}_1| * |\vec{{\mathbf{{w}}}}_2| = {sympy.latex(base_area)}$",
    )
fig_volume

# %% [markdown]
# ## The forward map sends the unit cube to the parallelepiped
#
# $f(\vec{\mathbf{x}}) = x_1 * \vec{\mathbf{v}}_1 + x_2 * \vec{\mathbf{v}}_2 + x_3 * \vec{\mathbf{v}}_3$
# sends each $\vec{\mathbf{e}}_i$ to $\vec{\mathbf{v}}_i$, so the unit cube (gray) lands
# on the frame's parallelepiped (blue). Its matrix has the $\vec{\mathbf{v}}_i$ as
# columns.

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
sympy.Matrix(f.to_matrix(G, n=3, backend=MatrixBackend.SYMPY))[:3, :3]

# %% [markdown]
# Drawn at the plot values:

# %%
fig_forward: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_forward:
    box_edges(
        a=Point(x=1, y=0, z=0),
        b=Point(x=0, y=1, z=0),
        c=Point(x=0, y=0, z=1),
        color=GRAY_EDGE,
        width=1.2,
    )
    box_edges(a=P_V1, b=P_V2, c=P_V3, color=BLUE, width=0.8)
    arrow(
        head=P_V1,
        color=BLUE,
        text=r"$f(\vec{\mathbf{e}}_1)$",
        offset=Point(x=4, y=-10),
        align=LabelPos.br,
    )
    arrow(
        head=P_V2,
        color=BLUE,
        text=r"$f(\vec{\mathbf{e}}_2)$",
        offset=Point(x=8, y=-14),
        align=LabelPos.r,
    )
    arrow(
        head=P_V3,
        color=BLUE,
        text=r"$f(\vec{\mathbf{e}}_3)$",
        offset=Point(x=-6, y=4),
        align=LabelPos.l,
    )
fig_forward


# %% [markdown]
# ## The inverse, one peel at a time
#
# Recover $\vec{\mathbf{x}}$ from $\vec{\mathbf{y}} = f(\vec{\mathbf{x}})$ by peeling
# the frame from its last vector. The target $\vec{\mathbf{y}}$, every coordinate a
# symbol:

# %%
y_1: sympy.Symbol
y_2: sympy.Symbol
y_3: sympy.Symbol
y_1, y_2, y_3 = sympy.symbols("y_1 y_2 y_3", real=True)
y: Vector = Scalar(y_1) * e_1 + Scalar(y_2) * e_2 + Scalar(y_3) * e_3
y

# %% [markdown]
# The plot values make
# $\vec{\mathbf{y}} = \vec{\mathbf{v}}_1 + \vec{\mathbf{v}}_2 + \vec{\mathbf{v}}_3$, so
# every coordinate comes out 1 in the figures. Change them and rerun; the figures'
# scenes are sized for these values.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(y_1, 4), (y_2, 3), (y_3, 2)]


def tex(value: Real) -> str:
    """``value`` at the plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, values))


P_Y: Point = point(coordinates=list(at_values(y, values)))

# %% [markdown]
# $\vec{\mathbf{w}}_3$ is normal to the plane of
# $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$, so it is perpendicular to every frame vector
# but $\vec{\mathbf{v}}_3$: it reads $x_3$ alone. $\vec{\mathbf{w}}_1$ and
# $\vec{\mathbf{w}}_2$ are not perpendicular to $\vec{\mathbf{v}}_3$, so the peel cannot
# start with them. $\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{v}}_3$:

# %%
w_1.dot(v_3).scalar_part()

# %% [markdown]
# $\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{v}}_3$:

# %%
w_2.dot(v_3).scalar_part()

# %% [markdown]
# **Step 0, the setup.** The plane of $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$ (shaded),
# $\vec{\mathbf{v}}_3$ leaning over it, and the target $\vec{\mathbf{y}}$.

# %%
fig_step_0: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_0:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(head=P_V1, color=BLUE, text=r"$\vec{\mathbf{v}}_1$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text=r"$\vec{\mathbf{v}}_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text=r"$\vec{\mathbf{v}}_3$", offset=Point(x=4, y=4))
    arrow(
        head=P_W3,
        color=GREEN,
        text=r"$\vec{\mathbf{w}}_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN3, toward_a=P_V1, toward_b=P_W3)
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
fig_step_0

# %% [markdown]
# **Step 1, read $x_3$.** Project $\vec{\mathbf{y}}$ onto $\vec{\mathbf{w}}_3$:
# $\vec{\mathbf{v}}_1$ and $\vec{\mathbf{v}}_2$ drop out, and the projection is $x_3$
# copies of $\vec{\mathbf{w}}_3$. Its length is $\vec{\mathbf{y}}$'s height above the
# plane and $|\vec{\mathbf{w}}_3|$ is $\vec{\mathbf{v}}_3$'s height, so $x_3$ is two
# heights, one divided by the other. The projection:

# %%
y_onto_w_3: MultiVectorBase = y.projected_onto(onto=w_3).simplified()
y_onto_w_3

# %% [markdown]
# $x_3$:

# %%
x_3: Real = sympy.simplify(sympy.sympify((y_onto_w_3 / w_3).scalar_part()))
x_3

# %% [markdown]
# At the plot values:

# %%
at_values(x_3, values)

# %% [markdown]
# Drawn at the plot values:

# %%
w_3_dot_y: Real = w_3.dot(y).scalar_part()
fig_step_1: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_1:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V3,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
    dashed_arrow(
        tail=P_V3,
        head=P_V3 + (-1) * P_W3,
        color=BLUE,
        text=rf"$|\vec{{\mathbf{{w}}}}_3| = {sympy.latex(height)}$",
        offset=Point(x=-6, y=-14),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=P_Y.x2(), z=0),
        color=RED,
        text=rf"$\frac{{\vec{{\mathbf{{w}}}}_3 \cdot \vec{{\mathbf{{y}}}}}}{{|\vec{{\mathbf{{w}}}}_3|}} = {tex(w_3_dot_y / height)}$",
        offset=Point(x=6, y=-14),
    )
    note(
        at=EQUATION_AT,
        text=(
            r"$x_3 = \frac{\vec{\mathbf{w}}_3 \cdot \vec{\mathbf{y}}}{|\vec{\mathbf{w}}_3|^2} = "
            rf"\frac{{{tex(w_3_dot_y)}}}{{{sympy.latex(height**2)}}} = {tex(x_3)}$"
        ),
        align=LabelPos.r,
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_3 * \vec{\mathbf{v}}_3$.** $\vec{\mathbf{y}}$ slides back along
# $\vec{\mathbf{v}}_3$ (dashed) into the plane of
# $\vec{\mathbf{v}}_1, \vec{\mathbf{v}}_2$. What is left, $\vec{\mathbf{r}}_1$, is a 2D
# problem in that plane:

# %%
r_1: Vector = (y - Scalar(x_3) * v_3).simplified()
r_1

# %% [markdown]
# At the plot values:

# %%
at_values(r_1, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_R1: Point = point(coordinates=list(at_values(r_1, values)))
fig_step_2: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_2:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V3,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}}$")
    dashed_arrow(
        tail=P_Y,
        head=P_R1,
        color=BLUE,
        text=r"$-x_3 * \vec{\mathbf{v}}_3$",
        offset=Point(x=8, y=10),
    )
    arrow(
        head=P_R1,
        color=RED,
        text=r"$\vec{\mathbf{r}}_1$",
        offset=Point(x=6, y=-10),
        width=2.2,
    )
fig_step_2

# %% [markdown]
# **Steps 3 and 4, the 2D peel inside the plane.** The camera stays put.
# $\vec{\mathbf{w}}_2$ is the normal to $\vec{\mathbf{v}}_1$'s line within the plane, so
# projecting $\vec{\mathbf{r}}_1$ onto it reads $x_2$:

# %%
x_2: Real = sympy.simplify(
    sympy.sympify((r_1.projected_onto(onto=w_2) / w_2).scalar_part())
)
x_2

# %% [markdown]
# Removing $x_2 * \vec{\mathbf{v}}_2$ leaves $\vec{\mathbf{r}}_2$ on
# $\vec{\mathbf{v}}_1$'s line:

# %%
r_2: Vector = (r_1 - Scalar(x_2) * v_2).simplified()
r_2

# %% [markdown]
# and projecting $\vec{\mathbf{r}}_2$ onto $\vec{\mathbf{w}}_1$ reads $x_1$:

# %%
x_1: Real = sympy.simplify(
    sympy.sympify((r_2.projected_onto(onto=w_1) / w_1).scalar_part())
)
x_1

# %% [markdown]
# At the plot values, $\vec{\mathbf{r}}_2$:

# %%
at_values(r_2, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_R2: Point = point(coordinates=list(at_values(r_2, values)))
w_2_dot_r_1: Real = w_2.dot(r_1).scalar_part()
fig_step_3: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_3:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V2,
        color=BLUE,
        text=r"$\vec{\mathbf{v}}_2$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_R1, color=RED, text=r"$\vec{\mathbf{r}}_1$", offset=Point(x=6, y=4))
    P_DROP: Point = Point(x=P_R1.x1(), y=0, z=0)
    dashed_arrow(tail=P_R1, head=P_DROP, color=RED)
    note(
        at=0.5 * (P_R1 + P_DROP),
        text=(
            r"$\frac{\vec{\mathbf{w}}_2 \cdot \vec{\mathbf{r}}_1}{|\vec{\mathbf{w}}_2|} = "
            rf"{tex(w_2_dot_r_1 / w_2.magnitude())}$"
        ),
        color=RED,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    dashed_arrow(tail=P_R1, head=P_R2, color=BLUE)
    note(
        at=0.2 * P_R1 + 0.8 * P_R2,
        text=r"$-x_2 * \vec{\mathbf{v}}_2$",
        color=BLUE,
        offset=Point(x=0, y=4),
        align=LabelPos.tl,
    )
    arrow(
        head=P_R2,
        color=RED,
        text=r"$\vec{\mathbf{r}}_2 = x_1 * \vec{\mathbf{v}}_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
        width=2.2,
    )
    note(
        at=EQUATION_AT,
        text=(
            rf"$x_2 = \frac{{{tex(w_2_dot_r_1)}}}"
            rf"{{{sympy.latex(w_2.magnitude_squared())}}} = {tex(x_2)}, \quad"
            r" x_1 = \frac{\vec{\mathbf{w}}_1 \cdot \vec{\mathbf{r}}_2}{|\vec{\mathbf{w}}_1|^2} = "
            rf"\frac{{{tex(w_1.dot(r_2).scalar_part())}}}"
            rf"{{{sympy.latex(w_1.magnitude_squared())}}} = {tex(x_1)}$"
        ),
        align=LabelPos.r,
    )
fig_step_3

# %% [markdown]
# **The result.** The recovered coordinates $\vec{\mathbf{x}}$:

# %%
x: Vector = Scalar(x_1) * e_1 + Scalar(x_2) * e_2 + Scalar(x_3) * e_3
x

# %% [markdown]
# gacalc's inverse of the frame's map, applied to $\vec{\mathbf{y}}$:

# %%
f.inverse(y).simplified()

# %% [markdown]
# Its difference from the peeled $\vec{\mathbf{x}}$:

# %%
(f.inverse(y) - x).simplified()

# %% [markdown]
# The map sends $\vec{\mathbf{x}}$ back to:

# %%
f(x).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{y}}$:

# %%
(f(x) - y).simplified()

# %% [markdown]
# At the plot values, $\vec{\mathbf{x}}$ (black);
# $x_1 * \vec{\mathbf{v}}_1 + x_2 * \vec{\mathbf{v}}_2 + x_3 * \vec{\mathbf{v}}_3$, tip
# to tail (blue), ends on $\vec{\mathbf{y}}$:

# %%
at_values(x, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_X: Point = point(coordinates=list(at_values(x, values)))
P_X1_V1: Point = point(coordinates=list(at_values(Scalar(x_1) * v_1, values)))
P_X2_V2: Point = point(coordinates=list(at_values(Scalar(x_2) * v_2, values)))
fig_result: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_result:
    arrow(head=P_Y, color=RED, text=r"$\vec{\mathbf{y}} = f(\vec{\mathbf{x}})$")
    arrow(
        head=P_X1_V1,
        color=BLUE,
        text=r"$x_1 * \vec{\mathbf{v}}_1$",
        offset=Point(x=4, y=-8),
    )
    dashed_arrow(tail=P_X1_V1, head=P_X1_V1 + P_X2_V2, color=BLUE)
    dashed_arrow(tail=P_X1_V1 + P_X2_V2, head=P_Y, color=BLUE)
    arrow(
        head=P_X,
        text=r"$\vec{\mathbf{x}}$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
        width=2.2,
    )
fig_result

# %% [markdown]
# ## The round trip, for every input
#
# For a symbolic $\vec{\mathbf{x}}$, `inverse(f) @ f` gives $\vec{\mathbf{x}}$ back
# unchanged, and `f @ inverse(f)` does the same for a symbolic $\vec{\mathbf{y}}$. A
# general $\vec{\mathbf{x}}$:

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_3: sympy.Symbol
s_1, s_2, s_3 = sympy.symbols("x_1 x_2 x_3", real=True)
general: Vector = Scalar(s_1) * e_1 + Scalar(s_2) * e_2 + Scalar(s_3) * e_3
general

# %% [markdown]
# $f^{-1}(f(\vec{\mathbf{x}}))$:

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
# $\vec{\mathbf{v}}^3 = \vec{\mathbf{w}}_3 / |\vec{\mathbf{w}}_3|^2$ dots to 0 with
# $\vec{\mathbf{v}}_1$ and $\vec{\mathbf{v}}_2$ and to 1 with $\vec{\mathbf{v}}_3$: step
# 1 as a single dot product. $\vec{\mathbf{v}}^3$:

# %%
reciprocal_3: MultiVectorBase = w_3 / w_3.magnitude_squared()
reciprocal_3

# %% [markdown]
# $\vec{\mathbf{v}}^3 \cdot \vec{\mathbf{v}}_1$:

# %%
reciprocal_3.dot(v_1).scalar_part()

# %% [markdown]
# $\vec{\mathbf{v}}^3 \cdot \vec{\mathbf{v}}_2$:

# %%
reciprocal_3.dot(v_2).scalar_part()

# %% [markdown]
# $\vec{\mathbf{v}}^3 \cdot \vec{\mathbf{v}}_3$:

# %%
reciprocal_3.dot(v_3).scalar_part()

# %% [markdown]
# Drawn at the plot values:

# %%
fig_reciprocal: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_reciprocal:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(head=P_V1, color=BLUE, text=r"$\vec{\mathbf{v}}_1$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text=r"$\vec{\mathbf{v}}_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text=r"$\vec{\mathbf{v}}_3$", offset=Point(x=4, y=4))
    arrow(
        head=point(coordinates=list(reciprocal_3)),
        color=GREEN,
        text=r"$\vec{\mathbf{v}}^3 = \frac{\vec{\mathbf{w}}_3}{|\vec{\mathbf{w}}_3|^2}$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
        width=2.4,
    )
fig_reciprocal
