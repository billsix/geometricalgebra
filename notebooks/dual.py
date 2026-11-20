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
# # The dual of a vector is perpendicular to it — calculations
#
# Companion to *The Dual*. The dual of a vector $\vec{\mathbf{a}}$ is
# $\vec{\mathbf{a}} * I^{-1}$, the vector times the inverse of the plane's unit area
# $I = \mathbf{e}_{12}$. The chapter claims the dual always meets $\vec{\mathbf{a}}$ at
# a right angle, and proves it with three facts we already have: grouping does not
# matter (associativity), a vector times itself is a plain number, and the dot product
# of two vectors is the plain-number part of their product.
#
# Every coordinate is a symbol, so each result holds for every vector. Numbers appear
# only to draw the figure and in the first product table. The Lean theorems are
# `dual_perp_dot` (`proofs/GacalcProofs/Predicates2D.lean`) and its cosine form
# `dual_perp` (`proofs/GacalcProofs/StudentTrigForms.lean`).

# %%
# twin: GacalcProofs.G2.dual_perp_dot
# twin: GacalcProofs.G2.dual_perp
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    PURPLE,
    PendingFigure,
    Point,
    arrow,
    point,
    right_angle,
    scene_around,
)
from gacalc.functions import inverse
from gacalc.g2 import (
    Bivector,
    Scalar,
    Vector,
    Versor,
    e_1,
    e_2,
    e_12,
    rotate_90_degrees,
)
from gacalc.nbdisplay import at_values, show_difference, show_mult

# %% [markdown]
# ## The vector and its dual
#
# $\vec{\mathbf{a}}$ has symbolic coordinates:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# The plane's unit area is $I = \mathbf{e}_{12}$. It squares to $-1$, so its inverse is
# its negative, $I^{-1} = -\mathbf{e}_{12}$:

# %%
I_inverse: Bivector = e_12.inverse()
I_inverse

# %% [markdown]
# Check: $I * I^{-1}$ is $1$.

# %%
e_12 * I_inverse

# %% [markdown]
# The dual is $\vec{\mathbf{a}} * I^{-1}$. gacalc computes it as `a.dual(2)`, the $2$
# saying which plane's $I$ to use:

# %%
a_dual: Vector = a.dual(2)
a_dual

# %% [markdown]
# It is the same as multiplying by $I^{-1}$ ourselves:

# %%
a * I_inverse

# %% [markdown]
# The values used to draw the figure. Change them and rerun; the formulas do not
# change, only the picture.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 2)]

# %% [markdown]
# Drawn at the plot values, with the dual in purple:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_A_DUAL: Point = point(coordinates=list(at_values(a_dual, values)))
fig_dual: PendingFigure
with scene_around(points=[P_A, P_A_DUAL]) as fig_dual:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_A_DUAL, color=PURPLE, text=r"$\vec{\mathbf{a}} * I^{-1}$")
    right_angle(corner=Point(x=0, y=0), toward_a=P_A, toward_b=P_A_DUAL)
fig_dual

# %% [markdown]
# It looks like a right angle. The rest of the notebook proves it is one, for every
# $\vec{\mathbf{a}}$.

# %% [markdown]
# ## First: the dual is a vector, and it is not zero
#
# The cosine of an angle, $\cos(\theta) = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} /
# (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$, is defined for two vectors, and only when
# neither has length $0$. So before asking for the angle between $\vec{\mathbf{a}}$ and
# its dual, check that the dual qualifies.
#
# Multiplying out $\vec{\mathbf{a}} * I^{-1}$ term by term, first at the plot values:

# %%
show_mult(at_values(a, values), I_inverse)

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, I_inverse)

# %% [markdown]
# Each term is a basis vector times $\mathbf{e}_{12}$, which is again a basis vector
# ($\vec{\mathbf{e}}_1 * \mathbf{e}_{12} = \vec{\mathbf{e}}_2$), so the sum has no plain
# number and no area: it is a vector.

# %%
a_dual.is_vector()

# %% [markdown]
# Its length is the length of $\vec{\mathbf{a}}$. First the squared length of the dual:

# %%
a_dual.magnitude_squared()

# %% [markdown]
# and that of $\vec{\mathbf{a}}$:

# %%
a.magnitude_squared()

# %% [markdown]
# Their difference:

# %%
show_difference(a_dual.magnitude_squared(), a.magnitude_squared())

# %% [markdown]
# So whenever $\vec{\mathbf{a}}$ is not zero, neither is its dual, and the cosine of the
# angle between them makes sense.

# %% [markdown]
# ## The proof: regroup, square, read off the plain number
#
# The dot product of two vectors is the plain-number part of their product (chapter
# *The Product from Projection*). So the dot product of $\vec{\mathbf{a}}$ and its dual
# is the plain-number part of $\vec{\mathbf{a}} * (\vec{\mathbf{a}} * I^{-1})$. Writing
# $\langle X \rangle_0$ for the plain-number part of $X$:
#
# $$
# \begin{aligned}
# \vec{\mathbf{a}} \cdot (\vec{\mathbf{a}} * I^{-1})
#   &= \langle \vec{\mathbf{a}} * (\vec{\mathbf{a}} * I^{-1}) \rangle_0
#     && \text{— the dot product is the plain-number part} \\
#   &= \langle (\vec{\mathbf{a}} * \vec{\mathbf{a}}) * I^{-1} \rangle_0
#     && \text{— regroup (associativity)} \\
#   &= \langle |\vec{\mathbf{a}}|^2 * I^{-1} \rangle_0
#     && \text{— a vector times itself is its squared length} \\
#   &= 0
#     && \text{— a number times } I^{-1} \text{ is all area, no plain number}
# \end{aligned}
# $$
#
# Each line in turn. The product, grouped as written:

# %%
product: Versor = (a * a_dual).simplified()
product

# %% [markdown]
# Grouped the other way, $(\vec{\mathbf{a}} * \vec{\mathbf{a}}) * I^{-1}$:

# %%
regrouped: Versor = ((a * a) * I_inverse).simplified()
regrouped

# %% [markdown]
# Their difference:

# %%
show_difference(product, regrouped)

# %% [markdown]
# The middle factor, $\vec{\mathbf{a}} * \vec{\mathbf{a}}$, is a plain number, the
# squared length (no area part):

# %%
(a * a).simplified()

# %% [markdown]
# So the product is that number times $I^{-1}$: an area and nothing else. Its
# plain-number part, the dot product, is $0$:

# %%
product.scalar_part()

# %% [markdown]
# gacalc's own dot product agrees:

# %%
a.dot(a_dual).scalar_part()

# %% [markdown]
# ## So the angle is a right angle
#
# With the dot product $0$ and both lengths nonzero, the cosine of the angle
# $\theta$ between $\vec{\mathbf{a}}$ and its dual is $0$, so $\theta = 90°$:

# %%
sympy.simplify(sympy.sympify(a.cosine(a_dual)))

# %% [markdown]
# ## A second look: the dual is a quarter turn
#
# In the plane there is a second way to see this. The chapter *Rotate* turned a vector
# by $90°$ by multiplying by $\mathbf{e}_{12}$. Multiplying by
# $I^{-1} = -\mathbf{e}_{12}$ instead turns it $90°$ the other way, clockwise. So the
# dual of $\vec{\mathbf{a}}$ is $\vec{\mathbf{a}}$ turned back a quarter turn:

# %%
inverse(rotate_90_degrees())(a)

# %% [markdown]
# Its difference from the dual:

# %%
show_difference(inverse(rotate_90_degrees())(a), a_dual)

# %% [markdown]
# The quarter-turn argument works only in the plane. The algebraic proof above never
# used the plane's shape, only associativity and grades, and it carries over to space.
# *The Dual in Space* takes it there.
