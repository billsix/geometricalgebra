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
# # The geometric product from projection and rejection — calculations
#
# Companion to the *Geometric Product from Projection and Rejection* chapter. Measured
# against $\vec{\mathbf{b}}$, the vector $\vec{\mathbf{a}}$ has two numbers: how far it
# reaches along $\vec{\mathbf{b}}$ and how far across. Rotate $\vec{\mathbf{b}}$ onto
# the x-axis, as in the projection proof, and those are the coordinates $(x, y)$ where
# $\vec{\mathbf{a}}$ lands. This notebook checks, with every coordinate a symbol, that
#
# $$\vec{\mathbf{b}} * \vec{\mathbf{a}} = |\vec{\mathbf{b}}| * (x + y * \mathbf{e}_{12}),$$
#
# and that this is the same product the multiplication rules of the geometric-product
# chapter give. Numbers appear only to draw the figures. Each check shows both sides,
# then their difference.

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
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Bivector, Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# Two general vectors:

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
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 1), (a_2, 2), (b_1, 2), (b_2, 1)]

# %% [markdown]
# ## Where $\vec{\mathbf{a}}$ lands when $\vec{\mathbf{b}}$ is rotated onto the x-axis
#
# The rotation is the projection proof's $R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}$,
# from $\vec{\mathbf{b}}$'s direction to $\vec{\mathbf{e}}_1$'s (`rotation_from_to`):

# %%
R: InvertibleFunction[Vector] = rotation_from_to(b, e_1)
R

# %% [markdown]
# It carries $\vec{\mathbf{a}}$ to $(x, y)$: $x$, how far $\vec{\mathbf{a}}$ reaches
# along $\vec{\mathbf{b}}$ (the projection), and $y$, how far it reaches across
# $\vec{\mathbf{b}}$ (the rejection).

# %%
a_landed: Vector = R(a).simplified()
a_landed

# %% [markdown]
# $x$:

# %%
x: Real = a_landed.coefficient(e_1)
x

# %% [markdown]
# $y$:

# %%
y: Real = a_landed.coefficient(e_2)
y

# %% [markdown]
# At the plot values, where $\vec{\mathbf{a}}$ lands:

# %%
at_values(a_landed, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_A_LANDED: Point = point(coordinates=list(at_values(a_landed, values)))
P_B_LANDED: Point = point(coordinates=list(at_values(R(b), values)))
P_X: Point = point(coordinates=list(at_values(Scalar(x) * e_1, values)))
fig_landed: PendingFigure
with scene_around(points=[P_A, P_B, P_A_LANDED, P_B_LANDED]) as fig_landed:
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$"
    )
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$"
    )
    arrow(
        head=P_B_LANDED,
        color=BLACK,
        text=r"$|\vec{\mathbf{b}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_LANDED, color=BLACK, text=r"$\vec{\mathbf{a}}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    note(
        at=0.5 * P_X,
        text=r"$x$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_LANDED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_A_LANDED),
        text=r"$y$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_X, toward_a=P_B_LANDED, toward_b=P_A_LANDED - P_X)
fig_landed

# %% [markdown]
# ## Times $|\vec{\mathbf{b}}|$, they are the dot product and the signed area
#
# $|\vec{\mathbf{b}}| * x$:

# %%
b_times_x: Real = sympy.simplify(sympy.sympify(b.magnitude() * x))
b_times_x

# %% [markdown]
# Its difference from $a_1 * b_1 + a_2 * b_2$:

# %%
sympy.simplify(sympy.sympify(b_times_x - (a_1 * b_1 + a_2 * b_2)))

# %% [markdown]
# $|\vec{\mathbf{b}}| * y$:

# %%
b_times_y: Real = sympy.simplify(sympy.sympify(b.magnitude() * y))
b_times_y

# %% [markdown]
# Its difference from $b_1 * a_2 - b_2 * a_1$:

# %%
sympy.simplify(sympy.sympify(b_times_y - (b_1 * a_2 - b_2 * a_1)))

# %% [markdown]
# ## The product built from them is gacalc's geometric product
#
# Put the two numbers into one object, the projection part as a plain number and the
# rejection part as a multiple of $\mathbf{e}_{12}$:

# %%
built: Versor = (
    Scalar(b.magnitude()) * (Versor.from_real(x) + Scalar(y) * Bivector.e_12)
).simplified()
built

# %% [markdown]
# The same product by the multiplication rules, term by term. First at the plot
# values:

# %%
show_mult(at_values(b, values), at_values(a, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(b, a)

# %% [markdown]
# $\vec{\mathbf{b}} * \vec{\mathbf{a}}$:

# %%
product: Versor = (b * a).simplified()
product

# %% [markdown]
# Its difference from the built object:

# %%
(product - built).simplified()

# %% [markdown]
# ## The two parts are the dot and the wedge
#
# The plain-number part is the dot product $\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}$:

# %%
dot: Real = b.dot(a).scalar_part()
dot

# %% [markdown]
# Its difference from $|\vec{\mathbf{b}}| * x$:

# %%
sympy.simplify(sympy.sympify(dot - b.magnitude() * x))

# %% [markdown]
# The $\mathbf{e}_{12}$ part is the wedge $\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}$:

# %%
wedge: Bivector = b ^ a
wedge

# %% [markdown]
# Its difference from $|\vec{\mathbf{b}}| * y * \mathbf{e}_{12}$:

# %%
(wedge - Scalar(b.magnitude() * y) * Bivector.e_12).simplified()

# %% [markdown]
# Together they are the product.
# $\vec{\mathbf{b}} \cdot \vec{\mathbf{a}} + \vec{\mathbf{b}} \wedge \vec{\mathbf{a}}$:

# %%
(Scalar(dot) + wedge).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{b}} * \vec{\mathbf{a}}$:

# %%
(product - (Scalar(dot) + wedge)).simplified()
