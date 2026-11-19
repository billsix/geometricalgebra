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
# # The cross product by standard position — calculations
#
# Companion to the *Proof: The Cross Product by Rotating to Standard Position* chapter.
# The projection chapters made a hard problem easy by turning the picture until one
# vector lay on an axis. The cross product works the same way. Three plane rotations
# turn the pair so that $\vec{\mathbf{a}}$ lies on $\vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{b}}$ in the $\mathbf{e}_{12}$ plane; there the cross product is a
# multiple of $\vec{\mathbf{e}}_3$ you can read off; turning back gives the cross
# product of the original pair. This notebook works each step with symbolic coordinates,
# so every result is a formula for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, and
# compares the result with gacalc's cross product, `gacalc.vectorcalc.cross`. Numbers
# appear only to draw the figures.
#
# This is the runnable, symbolic twin of the Lean capstone `cross_via_reduction`
# (and its explicit-angle form `cross_via_reduction_of_vectors`) in
# `proofs/GacalcProofs/CrossStandardPosition.lean`, whose engine is the three
# elementary cross-equivariances assembled by `cross_reduceToPlane_equivariant`.

# %%
import sympy

from gacalc import g2
from gacalc.base import Real
from gacalc.epixscene.frame_scene import (
    ORIGIN3,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    point,
    scene_3d,
)
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g3 import Scalar, Vector, e_1, e_2, e_3
from gacalc.nbdisplay import at_values
from gacalc.standardposition import in_plane, rotation_from_to
from gacalc.vectorcalc import cross

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2 + Scalar(a_3) * e_3
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2 + Scalar(b_3) * e_3
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 1),
    (a_2, 2),
    (a_3, 2),
    (b_1, 0),
    (b_2, 2),
    (b_3, 1),
]
LOWER_LEFT: Point = Point(x=-2.6, y=-2.2)
UPPER_RIGHT: Point = Point(x=5.4, y=3.6)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_given:
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, text=r"$\vec{\mathbf{b}}$")
fig_given

# %% [markdown]
# ## Rotating in a coordinate plane
#
# Each of the three turns is the rotation from one direction to another of *Proof:
# Rotate from the Direction of a to the Direction of b* (`rotation_from_to`), applied in
# one coordinate plane by `in_plane(rotation, first, second, v)`: it copies
# $\vec{\mathbf{v}}$'s coordinates along the two basis vectors into a 2D vector, rotates
# it, and writes the pair back, leaving the third coordinate alone.

# %% [markdown]
# ## Step 1: swing $\vec{\mathbf{a}}$'s shadow in the $\mathbf{e}_{12}$ plane onto the x-axis
#
# The rotation from $\vec{\mathbf{a}}$'s shadow
# $a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2$ to $\vec{\mathbf{e}}_1$:

# %%
R_xy: InvertibleFunction[g2.Vector] = rotation_from_to(
    g2.Scalar(a_1) * g2.e_1 + g2.Scalar(a_2) * g2.e_2, g2.e_1
)
R_xy

# %% [markdown]
# It leaves $\vec{\mathbf{a}}$ in the $\mathbf{e}_{13}$ plane:

# %%
a_step_1: Vector = in_plane(R_xy, e_1, e_2, a).simplified()
a_step_1

# %% [markdown]
# ## Step 2: swing $\vec{\mathbf{a}}$ down onto $\vec{\mathbf{e}}_1$
#
# The rotation, in the $\mathbf{e}_{13}$ plane, from $\vec{\mathbf{a}}$'s new direction
# to $\vec{\mathbf{e}}_1$:

# %%
R_xz: InvertibleFunction[g2.Vector] = rotation_from_to(
    g2.Scalar(a_step_1.coefficient(e_1)) * g2.e_1
    + g2.Scalar(a_step_1.coefficient(e_3)) * g2.e_2,
    g2.e_1,
)
R_xz


# %% [markdown]
# Steps 1 and 2 together, applied to any vector:


# %%
def align_a(v: Vector) -> Vector:
    """Steps 1 and 2: the two turns that put ``a`` on ``e_1``."""
    return in_plane(R_xz, e_1, e_3, in_plane(R_xy, e_1, e_2, v))


# %% [markdown]
# $\vec{\mathbf{a}}$ lands on $\vec{\mathbf{e}}_1$ at its length $|\vec{\mathbf{a}}|$:

# %%
a_aligned: Vector = align_a(a).simplified()
a_aligned

# %% [markdown]
# and $\vec{\mathbf{b}}$ rides along to $\vec{\mathbf{b}}'$:

# %%
b_aligned: Vector = align_a(b).simplified()
b_aligned

# %% [markdown]
# At the plot values, $\vec{\mathbf{a}}$ on $\vec{\mathbf{e}}_1$:

# %%
at_values(a_aligned, values)

# %% [markdown]
# and $\vec{\mathbf{b}}'$:

# %%
at_values(b_aligned, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_ALIGNED: Point = point(coordinates=list(at_values(a_aligned, values)))
P_B_ALIGNED: Point = point(coordinates=list(at_values(b_aligned, values)))
fig_aligned: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_aligned:
    dashed_arrow(tail=ORIGIN3, head=P_A, text=r"$\vec{\mathbf{a}}$")
    dashed_arrow(tail=ORIGIN3, head=P_B, text=r"$\vec{\mathbf{b}}$")
    arrow(
        head=P_A_ALIGNED,
        text=r"$|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
    )
    arrow(head=P_B_ALIGNED, text=r"$\vec{\mathbf{b}}'$")
fig_aligned

# %% [markdown]
# ## Step 3: swing $\vec{\mathbf{b}}'$ into the $\mathbf{e}_{12}$ plane
#
# The rotation, in the $\mathbf{e}_{23}$ plane, from $\vec{\mathbf{b}}'$'s shadow there
# to $\vec{\mathbf{e}}_2$. It leaves the $\vec{\mathbf{e}}_1$ axis, and so
# $\vec{\mathbf{a}}$, where they are.

# %%
R_yz: InvertibleFunction[g2.Vector] = rotation_from_to(
    g2.Scalar(b_aligned.coefficient(e_2)) * g2.e_1
    + g2.Scalar(b_aligned.coefficient(e_3)) * g2.e_2,
    g2.e_1,
)
R_yz

# %% [markdown]
# $\vec{\mathbf{b}}'$ lands in the $\mathbf{e}_{12}$ plane, as $\vec{\mathbf{b}}''$:

# %%
b_reduced: Vector = in_plane(R_yz, e_2, e_3, b_aligned).simplified()
b_reduced

# %% [markdown]
# At the plot values:

# %%
at_values(b_reduced, values)

# %% [markdown]
# ## In standard position, the cross product is a multiple of $\vec{\mathbf{e}}_3$
#
# With $\vec{\mathbf{a}}$ at $|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{b}}''$ in the $\mathbf{e}_{12}$ plane,
# $\vec{\mathbf{a}} \times \vec{\mathbf{b}}''$ is
# $|\vec{\mathbf{a}}| * b''_2 * \vec{\mathbf{e}}_3$:

# %%
cross_reduced: Vector = (
    Scalar(a_aligned.coefficient(e_1) * b_reduced.coefficient(e_2)) * e_3
).simplified()
cross_reduced

# %% [markdown]
# At the plot values:

# %%
at_values(cross_reduced, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_B_REDUCED: Point = point(coordinates=list(at_values(b_reduced, values)))
P_CROSS_REDUCED: Point = point(coordinates=list(at_values(cross_reduced, values)))
fig_reduced: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_reduced:
    arrow(
        head=P_A_ALIGNED,
        text=r"$|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
    )
    arrow(head=P_B_REDUCED, text=r"$\vec{\mathbf{b}}''$")
    arrow(
        head=P_CROSS_REDUCED,
        color=PURPLE,
        text=r"$|\vec{\mathbf{a}}| * b''_2 * \vec{\mathbf{e}}_3$",
        align=LabelPos.l,
    )
fig_reduced

# %% [markdown]
# ## Rotate back
#
# Undo the three turns in reverse order, each by its inverse:

# %%
by_standard_position: Vector = in_plane(
    inverse(R_xy),
    e_1,
    e_2,
    in_plane(inverse(R_xz), e_1, e_3, in_plane(inverse(R_yz), e_2, e_3, cross_reduced)),
).simplified()
by_standard_position

# %% [markdown]
# At the plot values:

# %%
at_values(by_standard_position, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_CROSS: Point = point(coordinates=list(at_values(by_standard_position, values)))
fig_back: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_back:
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, text=r"$\vec{\mathbf{b}}$")
    arrow(
        head=P_CROSS,
        color=PURPLE,
        text=r"$\vec{\mathbf{a}} \times \vec{\mathbf{b}}$",
        align=LabelPos.l,
    )
fig_back

# %% [markdown]
# ## Check, for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$
#
# The construction gave:

# %%
by_standard_position

# %% [markdown]
# gacalc's cross product, $(\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) * I_3^{-1}$,
# gives:

# %%
cross(a, b).simplified()

# %% [markdown]
# Their difference:

# %%
(by_standard_position - cross(a, b)).simplified()
