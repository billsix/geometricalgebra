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
# # Step 2, projection from rotation — worked example
#
# Companion to *Step 2: Projection, from Rotation*. Every step is computed with symbolic
# coordinates, so each result is a formula for every $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$: rotate $\vec{\mathbf{a}}$ onto the x-axis, carrying
# $\vec{\mathbf{b}}$ along; apply the base cases there (keep the x-coordinate for the
# projection, the y-coordinate for the rejection); rotate back. The only rotation used
# is Step 1's rotation by an angle, `Vector.rotate`. Numbers appear only to draw the
# figures; change them and rerun. Each check shows both sides, then their difference.

# %%
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    BLUE,
    GREEN,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    right_angle,
    scene_around,
)
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference

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
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_given:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
fig_given

# %% [markdown]
# ## Rotate $\vec{\mathbf{a}}$ onto the x-axis, carrying $\vec{\mathbf{b}}$ along
#
# Let $\theta$ be the angle of $\vec{\mathbf{a}}$ from the x-axis,
# $\operatorname{atan2}(a_2, a_1)$. Rotating by $-\theta$ lays $\vec{\mathbf{a}}$ on the
# x-axis, and the rotation's cosine and sine come straight from $\vec{\mathbf{a}}$'s
# coordinates. The cosine, $\cos(-\theta) = a_1 / |\vec{\mathbf{a}}|$:

# %%
theta: sympy.Expr = sympy.atan2(a_2, a_1)
sympy.cos(-theta)

# %% [markdown]
# the sine, $\sin(-\theta) = -a_2 / |\vec{\mathbf{a}}|$:

# %%
sympy.sin(-theta)

# %% [markdown]
# $\vec{\mathbf{a}}$ lands on the x-axis at its length:

# %%
a_rotated: Vector = a.rotate(-theta).simplified()
a_rotated

# %% [markdown]
# and $\vec{\mathbf{b}}$ rides along to $\vec{\mathbf{b}}'$:

# %%
b_rotated: Vector = b.rotate(-theta).simplified()
b_rotated

# %% [markdown]
# At the plot values, $\vec{\mathbf{a}}$ on the x-axis:

# %%
at_values(a_rotated, values)

# %% [markdown]
# and $\vec{\mathbf{b}}'$:

# %%
at_values(b_rotated, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_ROTATED: Point = point(coordinates=list(at_values(a_rotated, values)))
P_B_ROTATED: Point = point(coordinates=list(at_values(b_rotated, values)))
fig_rotated: PendingFigure
with scene_around(points=[P_A, P_B, P_A_ROTATED, P_B_ROTATED]) as fig_rotated:
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$"
    )
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$"
    )
    arrow(head=P_A_ROTATED, color=BLACK, text=r"$\vec{\mathbf{a}}'$", align=LabelPos.b)
    arrow(head=P_B_ROTATED, color=BLACK, text=r"$\vec{\mathbf{b}}'$")
fig_rotated

# %% [markdown]
# ## The base cases, on the x-axis
#
# $\operatorname{proj}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}') = x * \vec{\mathbf{e}}_1$
# keeps $\vec{\mathbf{b}}'$'s x-coordinate and
# $\operatorname{rej}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}') = y * \vec{\mathbf{e}}_2$
# keeps its y-coordinate. $x$ and $y$ are the signed lengths of $\vec{\mathbf{b}}$'s
# projection onto $\vec{\mathbf{a}}$ and of its rejection. $x$:

# %%
x: Real = b_rotated.coefficient(e_1)
x

# %% [markdown]
# $y$:

# %%
y: Real = b_rotated.coefficient(e_2)
y

# %% [markdown]
# At the plot values, $x$:

# %%
at_values(x, values)

# %% [markdown]
# and $y$:

# %%
at_values(y, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_X: Point = point(coordinates=list(at_values(Scalar(x) * e_1, values)))
fig_base: PendingFigure
with scene_around(points=[P_A_ROTATED, P_B_ROTATED]) as fig_base:
    arrow(head=P_B_ROTATED, color=BLACK, text=r"$\vec{\mathbf{b}}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    arrow(head=P_A_ROTATED, color=BLACK, text=r"$\vec{\mathbf{a}}'$", align=LabelPos.b)
    note(
        at=0.5 * P_X,
        text=r"$x * \vec{\mathbf{e}}_1$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_B_ROTATED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_B_ROTATED),
        text=r"$y * \vec{\mathbf{e}}_2$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_X, toward_a=P_A_ROTATED, toward_b=P_B_ROTATED - P_X)
fig_base

# %% [markdown]
# ## Rotate back
#
# The rotation back is by $+\theta$. It carries $x * \vec{\mathbf{e}}_1$ to the
# projection of $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$:

# %%
projection: Vector = (Scalar(x) * e_1).rotate(theta).simplified()
projection

# %% [markdown]
# and $y * \vec{\mathbf{e}}_2$ to the rejection:

# %%
rejection: Vector = (Scalar(y) * e_2).rotate(theta).simplified()
rejection

# %% [markdown]
# At the plot values, the projection:

# %%
at_values(projection, values)

# %% [markdown]
# and the rejection:

# %%
at_values(rejection, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_back: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_back:
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_B),
        text=r"$\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_A, toward_b=P_B - P_PROJECTION)
fig_back

# %% [markdown]
# ## Checks, for all vectors
#
# Some checks run the construction again on other vectors, so here it is as one
# function, the steps above in order.


# %%
def project_and_reject(onto: Vector, v: Vector) -> tuple[Vector, Vector]:
    """Step 2's construction: rotate ``onto`` to the x-axis, apply the base cases,
    rotate back."""
    angle: sympy.Expr = sympy.atan2(onto.coefficient(e_2), onto.coefficient(e_1))
    v_rotated: Vector = v.rotate(-angle)
    return (
        (Scalar(v_rotated.coefficient(e_1)) * e_1).rotate(angle).simplified(),
        (Scalar(v_rotated.coefficient(e_2)) * e_2).rotate(angle).simplified(),
    )


# %% [markdown]
# ### On the x-axis the construction gives back the base cases
#
# Projecting $\vec{\mathbf{b}}$ onto $\vec{\mathbf{e}}_1$ by the construction:

# %%
onto_e_1: tuple[Vector, Vector] = project_and_reject(1 * e_1, b)
onto_e_1[0]

# %% [markdown]
# The base case
# $\operatorname{proj}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}) = b_1 * \vec{\mathbf{e}}_1$:

# %%
Scalar(b_1) * e_1

# %% [markdown]
# Their difference:

# %%
show_difference(onto_e_1[0], Scalar(b_1) * e_1)

# %% [markdown]
# Rejecting $\vec{\mathbf{b}}$ from $\vec{\mathbf{e}}_1$ by the construction:

# %%
onto_e_1[1]

# %% [markdown]
# The base case
# $\operatorname{rej}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}) = b_2 * \vec{\mathbf{e}}_2$:

# %%
Scalar(b_2) * e_2

# %% [markdown]
# Their difference:

# %%
show_difference(onto_e_1[1], Scalar(b_2) * e_2)

# %% [markdown]
# ### The projection formula
#
# The construction gave:

# %%
projection

# %% [markdown]
# The formula $(a_1 * b_1 + a_2 * b_2) / (a_1^2 + a_2^2) * \vec{\mathbf{a}}$:

# %%
projection_formula: Vector = (
    Scalar((a_1 * b_1 + a_2 * b_2) / (a_1**2 + a_2**2)) * a
).simplified()
projection_formula

# %% [markdown]
# Their difference:

# %%
show_difference(projection, projection_formula)

# %% [markdown]
# ### The rejection formula
#
# The construction gave:

# %%
rejection

# %% [markdown]
# The formula $(a_1 * b_2 - a_2 * b_1) / (a_1^2 + a_2^2) * r(\vec{\mathbf{a}}; \pi/2)$:

# %%
rejection_formula: Vector = (
    Scalar((a_1 * b_2 - a_2 * b_1) / (a_1**2 + a_2**2)) * a.rotate_90_degrees()
).simplified()
rejection_formula

# %% [markdown]
# Their difference:

# %%
show_difference(rejection, rejection_formula)

# %% [markdown]
# ### The two parts add back to $\vec{\mathbf{b}}$
#
# Their sum:

# %%
(projection + rejection).simplified()

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b

# %% [markdown]
# Their difference:

# %%
show_difference(projection + rejection, b)

# %% [markdown]
# ### Projecting twice changes nothing
#
# The projection, projected onto $\vec{\mathbf{a}}$ again:

# %%
projected_twice: Vector = project_and_reject(a, projection)[0]
projected_twice

# %% [markdown]
# Its difference from the projection:

# %%
show_difference(projected_twice, projection)

# %% [markdown]
# ### The rejection has no part along $\vec{\mathbf{a}}$
#
# The rejection, projected onto $\vec{\mathbf{a}}$, is $0$:

# %%
project_and_reject(a, rejection)[0]

# %% [markdown]
# ### gacalc agrees
#
# gacalc's projection,
# $(\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$:

# %%
b.projected_onto(a).simplified()

# %% [markdown]
# Its difference from the construction's:

# %%
show_difference(projection, b.projected_onto(a))

# %% [markdown]
# gacalc's rejection:

# %%
b.rejected_away_from(a).simplified()

# %% [markdown]
# Its difference from the construction's:

# %%
show_difference(rejection, b.rejected_away_from(a))
