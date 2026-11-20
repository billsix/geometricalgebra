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
# # Projection and rejection in space — calculations
#
# Companion to *Projection and Rejection in 3D*. In space a vector can be projected onto
# a plane as well as onto a line. Onto a plane, the projection is the part of
# $\vec{\mathbf{a}}$ lying in the plane and the rejection is the part sticking straight
# out of it. This notebook starts with the three coordinate planes, where the answer can
# be read off the coordinates, goes on to any plane, and ends with the 3D version of the
# product split from *Projection*:
# $\vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}} (\vec{\mathbf{b}})$ is the
# dot product and
# $\vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$ is the
# wedge.
#
# Every coordinate is a symbol; numbers appear only to draw the figures. The Lean
# theorems are `project_add_reject` and `reject_eq_proj_normal`
# (`proofs/GacalcProofs/Projection3D.lean`), and `mul_proj_eq_dot` and
# `mul_eq_proj_dot_add_reject_wedge` (`proofs/GacalcProofs/StandardPosition.lean`).

# %%
# twin: GacalcProofs.G3.project_add_reject
# twin: GacalcProofs.G3.mul_proj_eq_dot
# twin: GacalcProofs.G3.mul_eq_proj_dot_add_reject_wedge
import sympy

from gacalc.base import Real
from gacalc.epixscene.frame_scene import (
    BLUE,
    GREEN,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    note,
    patch,
    point,
    scene_3d,
)
from gacalc.g3 import Bivector, Scalar, Vector, Versor, e_1, e_2, e_3, e_12, e_13, e_23
from gacalc.nbdisplay import at_values, show_difference

# %% [markdown]
# ## Onto a coordinate plane: keep two coordinates
#
# $\vec{\mathbf{a}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2 + Scalar(a_3) * e_3
a

# %% [markdown]
# Projecting onto the floor, the $\mathbf{e}_{12}$ plane, keeps the $\vec{\mathbf{e}}_1$
# and $\vec{\mathbf{e}}_2$ coordinates. Predict the result, then run:

# %%
a.projected_onto(e_12)

# %% [markdown]
# The rejection is the rest, straight up out of the floor:

# %%
a.rejected_away_from(e_12)

# %% [markdown]
# Onto the $\mathbf{e}_{23}$ plane, the projection keeps $a_2$ and $a_3$:

# %%
a.projected_onto(e_23)

# %% [markdown]
# and the rejection is the $\vec{\mathbf{e}}_1$ part:

# %%
a.rejected_away_from(e_23)

# %% [markdown]
# Onto the $\mathbf{e}_{31}$ plane (gacalc writes it
# $\mathbf{e}_{13} = -\mathbf{e}_{31}$; the sign does not change which plane it is), the
# projection keeps $a_1$ and $a_3$:

# %%
a.projected_onto(e_13)

# %% [markdown]
# and the rejection is the $\vec{\mathbf{e}}_2$ part:

# %%
a.rejected_away_from(e_13)

# %% [markdown]
# ## Onto any plane
#
# A plane through the origin is the wedge of two vectors in it,
# $B = \vec{\mathbf{p}} \wedge \vec{\mathbf{q}}$:

# %%
p_1: sympy.Symbol
p_2: sympy.Symbol
p_3: sympy.Symbol
q_1: sympy.Symbol
q_2: sympy.Symbol
q_3: sympy.Symbol
p_1, p_2, p_3, q_1, q_2, q_3 = sympy.symbols("p_1 p_2 p_3 q_1 q_2 q_3", real=True)
p: Vector = Scalar(p_1) * e_1 + Scalar(p_2) * e_2 + Scalar(p_3) * e_3
q: Vector = Scalar(q_1) * e_1 + Scalar(q_2) * e_2 + Scalar(q_3) * e_3
B: Bivector = (p ^ q).simplified()
B

# %% [markdown]
# The projection of $\vec{\mathbf{a}}$ onto the plane:

# %%
projection_plane: Vector = a.projected_onto(B).simplified()
projection_plane

# %% [markdown]
# and the rejection from it:

# %%
rejection_plane: Vector = a.rejected_away_from(B).simplified()
rejection_plane

# %% [markdown]
# They add back to $\vec{\mathbf{a}}$; the difference:

# %%
show_difference(projection_plane + rejection_plane, a)

# %% [markdown]
# The rejection sticks straight out of the plane: it is perpendicular to both
# $\vec{\mathbf{p}}$ and $\vec{\mathbf{q}}$. Its dot product with $\vec{\mathbf{p}}$:

# %%
sympy.simplify(sympy.sympify(rejection_plane.dot(p).scalar_part()))

# %% [markdown]
# and with $\vec{\mathbf{q}}$:

# %%
sympy.simplify(sympy.sympify(rejection_plane.dot(q).scalar_part()))

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 1),
    (a_2, 1),
    (a_3, 2),
    (p_1, 2),
    (p_2, 0),
    (p_3, 0),
    (q_1, 0),
    (q_2, 2),
    (q_3, 1),
]
LOWER_LEFT: Point = Point(x=-3.0, y=-2.4)
UPPER_RIGHT: Point = Point(x=4.6, y=3.6)


# %% [markdown]
# Drawn at the plot values: the plane shaded, the projection in green lying in it, and
# the rejection in blue standing out of it.

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_P: Point = point(coordinates=list(at_values(p, values)))
P_Q: Point = point(coordinates=list(at_values(q, values)))
P_PROJECTION: Point = point(coordinates=list(at_values(projection_plane, values)))
fig_plane: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_plane:
    patch(corners=[-1 * P_P - P_Q, P_P - P_Q, P_P + P_Q, P_Q - P_P])
    arrow(
        head=P_PROJECTION,
        color=GREEN,
        text=r"$\operatorname{proj}_{B}(\vec{\mathbf{a}})$",
        offset=Point(x=6, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_A, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_A + P_PROJECTION),
        text=r"$\operatorname{rej}_{B}(\vec{\mathbf{a}})$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$")
fig_plane

# %% [markdown]
# ## The product split, in space
#
# *Projection* split the product of two vectors in the plane: the part of
# $\vec{\mathbf{b}}$ along $\vec{\mathbf{a}}$ gave a plain number, the dot product, and
# the part across gave the wedge. The same split works in space. With $\vec{\mathbf{b}}$
# a second vector:

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3", real=True)
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2 + Scalar(b_3) * e_3
b

# %% [markdown]
# $\vec{\mathbf{a}}$ times the projection of $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$
# is a plain number:

# %%
along: Versor = (a * b.projected_onto(a)).simplified()
along

# %% [markdown]
# and it is the dot product; the difference:

# %%
show_difference(along.scalar_part(), a.dot(b).scalar_part())

# %% [markdown]
# $\vec{\mathbf{a}}$ times the rejection is a piece of plane, with a part in each of the
# three coordinate planes:

# %%
across: Versor = (a * b.rejected_away_from(a)).simplified()
across

# %% [markdown]
# and it is the wedge; the difference:

# %%
show_difference(across, a ^ b)

# %% [markdown]
# Together they are the whole product $\vec{\mathbf{a}} * \vec{\mathbf{b}}$; the
# difference:

# %%
show_difference(a * b - along, across)
