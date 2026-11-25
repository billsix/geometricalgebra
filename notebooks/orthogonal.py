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
# # Orthogonal — calculations
#
# Companion to *Orthogonal*. Two vectors are **orthogonal** when their dot product
# is zero, which is the right angle of *Angle, area and perpendicular*:
# $\cos(\theta) = 0$. This notebook checks, with symbolic coordinates, the three facts
# the page builds on that definition.
#
# 1. The quarter turn of a vector is orthogonal to it.
# 2. The rejection of $\vec{\mathbf{a}}$ from $\vec{\mathbf{b}}$ is orthogonal to
#    $\vec{\mathbf{b}}$, so $\vec{\mathbf{a}}$ splits into two orthogonal parts, and their
#    squared lengths add up (Pythagoras).
# 3. Two orthogonal vectors form a frame, and the projections onto them put any vector
#    back together.
#
# Every step is computed with symbolic coordinates; numbers appear only to draw the
# figures.

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
    dashed_arrow,
    point,
    scene_around,
)
from gacalc.frame import make_orthogonal_frame
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ is the vector to split, and $\vec{\mathbf{b}}$ is the direction
# to split it along. Both have symbolic coordinates:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 3), (b_1, 4), (b_2, 1)]

# %% [markdown]
# ## 1. The quarter turn is orthogonal
#
# The quarter turn of $\vec{\mathbf{b}}$ from *Proof: Rotate by an Angle* points a
# right angle away from it. Its dot product with $\vec{\mathbf{b}}$:

# %%
b_turned: Vector = b.rotate_90_degrees()
b_turned

# %% [markdown]
# The dot product, read out as a number:

# %%
turn_dot: Real = b.dot(b_turned).scalar_part()
turn_dot

# %% [markdown]
# Its difference from zero:

# %%
show_difference(turn_dot, 0)

# %% [markdown]
# ## 2. The rejection is orthogonal to what it was rejected from
#
# *The Geometric Product from Projection and Rejection* split $\vec{\mathbf{a}}$ into
# its projection onto $\vec{\mathbf{b}}$ and its rejection from $\vec{\mathbf{b}}$:

# %%
projection: Vector = a.projected_onto(b).simplified()
projection

# %% [markdown]
# and the rejection:

# %%
rejection: Vector = a.rejected_away_from(b).simplified()
rejection

# %% [markdown]
# Drawn at the plot values, with the projection in blue and the rejection in purple:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
P_REJECTION: Point = point(coordinates=list(at_values(rejection, values)))
fig_split: PendingFigure
with scene_around(points=[P_A, P_B, -1 * P_B, P_PROJECTION, P_REJECTION]) as fig_split:
    dashed_arrow(tail=-1 * P_B, head=P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$", align=LabelPos.b)
    arrow(
        head=P_PROJECTION,
        color=BLUE,
        text=r"$proj_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        align=LabelPos.b,
    )
    arrow(
        head=P_REJECTION,
        color=PURPLE,
        text=r"$rej_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
    )
fig_split

# %% [markdown]
# The rejection's dot product with $\vec{\mathbf{b}}$, the check that the two are
# orthogonal:

# %%
rejection_dot: Real = rejection.dot(b).simplified().scalar_part()
rejection_dot

# %% [markdown]
# Its difference from zero:

# %%
show_difference(rejection_dot, 0)

# %% [markdown]
# So the two parts are orthogonal, and Pythagoras applies. The squared length of
# $\vec{\mathbf{a}}$, which is its dot product with itself:

# %%
a_squared: Real = a.dot(a).scalar_part()
a_squared

# %% [markdown]
# The squared lengths of the projection and the rejection, added:

# %%
parts_squared: Real = (
    (projection.dot(projection) + rejection.dot(rejection)).simplified().scalar_part()
)
parts_squared

# %% [markdown]
# Their difference:

# %%
show_difference(a_squared, parts_squared)

# %% [markdown]
# ## 3. An orthogonal frame
#
# Start with two vectors that are not parallel, $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$. Keep the first, and replace the second by its rejection from the
# first. That is what `make_orthogonal_frame` does:

# %%
frame: list[MultiVectorBase] = make_orthogonal_frame([a, b])
w_1: MultiVectorBase = frame[0].simplified()
w_2: MultiVectorBase = frame[1].simplified()
w_1

# %% [markdown]
# and the second vector of the frame:

# %%
w_2

# %% [markdown]
# They are orthogonal. Their dot product:

# %%
frame_dot: Real = w_1.dot(w_2).simplified().scalar_part()
frame_dot

# %% [markdown]
# Its difference from zero:

# %%
show_difference(frame_dot, 0)

# %% [markdown]
# Drawn at the plot values:

# %%
P_W_1: Point = point(coordinates=list(at_values(w_1, values)))
P_W_2: Point = point(coordinates=list(at_values(w_2, values)))
fig_frame: PendingFigure
with scene_around(points=[P_W_1, P_W_2, -1 * P_W_1, -1 * P_W_2]) as fig_frame:
    arrow(head=P_W_1, color=GREEN, text=r"$\vec{\mathbf{w}}_1$")
    arrow(head=P_W_2, color=PURPLE, text=r"$\vec{\mathbf{w}}_2$")
fig_frame

# %% [markdown]
# Because the frame is orthogonal, any vector $\vec{\mathbf{c}}$ is the sum of its
# projections onto the two vectors, with no cross terms:

# %%
c_1: sympy.Symbol
c_2: sympy.Symbol
c_1, c_2 = sympy.symbols("c_1 c_2", real=True)
c: Vector = Scalar(c_1) * e_1 + Scalar(c_2) * e_2
put_back: MultiVectorBase = (c.projected_onto(w_1) + c.projected_onto(w_2)).simplified()
put_back

# %% [markdown]
# Its difference from $\vec{\mathbf{c}}$:

# %%
show_difference(put_back, c)
