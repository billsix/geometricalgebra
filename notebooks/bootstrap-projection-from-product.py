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
# # Step 5, projection through the product — worked example
#
# Companion to *Step 5: Projection, through the Product*. Every step is computed with
# symbolic coordinates, so each result is a formula for every $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$: the inverse of $\vec{\mathbf{a}}$, then the projection
# $(\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$ and the rejection
# $(\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$, which match Step
# 2's construction by rotation. Numbers appear only to draw the figure; change them and
# rerun. Each check shows both sides, then their difference.

# %%
import sympy

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
    note,
    point,
    right_angle,
    scene_around,
)
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference, show_mult

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
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# ## The inverse of a vector
#
# $\vec{\mathbf{a}} * \vec{\mathbf{a}} = |\vec{\mathbf{a}}|^2$ is a plain number, so
# $\vec{\mathbf{a}}^{-1} = \vec{\mathbf{a}} / |\vec{\mathbf{a}}|^2$: along
# $\vec{\mathbf{a}}$, at length $1 / |\vec{\mathbf{a}}|$.

# %%
a_inverse: Vector = a.inverse().simplified()
a_inverse

# %% [markdown]
# At the plot values:

# %%
at_values(a_inverse, values)

# %% [markdown]
# ## The projection through the product
#
# $\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) = (\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$,
# where $\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}$ is the plain-number part of
# $\vec{\mathbf{b}} * \vec{\mathbf{a}}$. $\vec{\mathbf{b}} * \vec{\mathbf{a}}$ term by
# term; its plain-number part, the sum of the $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1$
# and $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2$ rows, is
# $\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}$. First at the plot values:

# %%
show_mult(at_values(b, values), at_values(a, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(b, a)

# %% [markdown]
# The projection:

# %%
b_dot_a: Real = (b * a).scalar_part()
projection: Vector = (Scalar(b_dot_a) * a_inverse).simplified()
projection

# %% [markdown]
# At the plot values:

# %%
at_values(projection, values)

# %% [markdown]
# ## The rejection, the same way
#
# $\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) = (\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$.
# Term by term: $\mathbf{e}_{12}$ times each term of $\vec{\mathbf{a}}^{-1}$ is a
# quarter turn of that term, so the result is a vector again. First at the plot values:

# %%
show_mult(at_values(b.wedge(a), values), at_values(a_inverse, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(b.wedge(a), a_inverse)

# %% [markdown]
# The rejection:

# %%
rejection: MultiVectorBase = (b.wedge(a) * a_inverse).simplified()
rejection

# %% [markdown]
# At the plot values:

# %%
at_values(rejection, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_INVERSE: Point = point(coordinates=list(at_values(a_inverse, values)))
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_product: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_product:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    note(
        at=0.75 * P_PROJECTION,
        text=r"$(\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_B),
        text=r"$(\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_A, toward_b=P_B - P_PROJECTION)
    arrow(head=P_INVERSE, color=PURPLE, width=3.0)
    note(
        at=P_INVERSE,
        text=r"$\vec{\mathbf{a}}^{-1}$",
        color=PURPLE,
        offset=Point(x=-2, y=6),
        align=LabelPos.t,
    )
fig_product

# %% [markdown]
# ## Checks, for all vectors
#
# Step 2 built the projection and rejection by rotating, with Step 1's rotation by minus
# the angle of $\vec{\mathbf{a}}$ and back. Here it is as one function, to compare
# against.


# %%
def project_and_reject_by_rotation(onto: Vector, v: Vector) -> tuple[Vector, Vector]:
    """Step 2's construction: rotate ``onto`` to the x-axis, apply the base cases,
    rotate back."""
    angle: sympy.Expr = sympy.atan2(onto.coefficient(e_2), onto.coefficient(e_1))
    v_rotated: Vector = v.rotate(-angle)
    return (
        (Scalar(v_rotated.coefficient(e_1)) * e_1).rotate(angle).simplified(),
        (Scalar(v_rotated.coefficient(e_2)) * e_2).rotate(angle).simplified(),
    )


# %% [markdown]
# ### $\vec{\mathbf{a}}^{-1} = \vec{\mathbf{a}} / |\vec{\mathbf{a}}|^2$
#
# $\vec{\mathbf{a}}^{-1}$ was:

# %%
a_inverse

# %% [markdown]
# $\vec{\mathbf{a}} / |\vec{\mathbf{a}}|^2$:

# %%
(Scalar(1 / (a_1**2 + a_2**2)) * a).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(a_inverse, Scalar(1 / (a_1**2 + a_2**2)) * a)

# %% [markdown]
# ### $\vec{\mathbf{a}} * \vec{\mathbf{a}}^{-1} = 1$
#
# $\vec{\mathbf{a}} * \vec{\mathbf{a}}^{-1}$:

# %%
(a * a_inverse).simplified()

# %% [markdown]
# Its difference from $1$:

# %%
show_difference(a * a_inverse, Scalar(1))

# %% [markdown]
# ### The product's projection and rejection are Step 2's
#
# Step 2's projection, by rotating:

# %%
by_rotation_projection: Vector
by_rotation_rejection: Vector
by_rotation_projection, by_rotation_rejection = project_and_reject_by_rotation(a, b)
by_rotation_projection

# %% [markdown]
# The projection through the product was:

# %%
projection

# %% [markdown]
# Their difference:

# %%
show_difference(projection, by_rotation_projection)

# %% [markdown]
# Step 2's rejection, by rotating:

# %%
by_rotation_rejection

# %% [markdown]
# The rejection through the product was:

# %%
rejection

# %% [markdown]
# Their difference:

# %%
show_difference(rejection, by_rotation_rejection)

# %% [markdown]
# ### Together they give back $\vec{\mathbf{b}}$, since $\vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{a}}^{-1} = \vec{\mathbf{b}}$
#
# Their sum:

# %%
(projection + rejection).simplified()

# %% [markdown]
# The projection and the rejection add back up to $\vec{\mathbf{b}}$.

# %% [markdown]
# ### gacalc agrees
#
# gacalc's projection:

# %%
b.projected_onto(a).simplified()

# %% [markdown]
# It is the same as the product's.

# %% [markdown]
# gacalc's rejection:

# %%
b.rejected_away_from(a).simplified()

# %% [markdown]
# It is the same as the product's.
