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
# # Defining the algebra $\mathcal{G}_2$ — calculations
#
# Companion to *Defining the Algebra: G2*. Until now we have used the plane's product a
# piece at a time: rotating by multiplying, projecting, the dot and the wedge. This
# notebook writes the whole algebra down in one place: what its elements are, how to add
# and multiply them, and what kinds of element there are. Much of it repeats things you
# have seen; here they are side by side.
#
# The picture to keep in mind: 𝒢₂ is one big set, and the vectors, scalars, bivectors
# and versors are named pieces of it.

# %%
import sympy
from IPython.display import display

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    BLUE,
    GREEN,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    scene_around,
)
from gacalc.epixscene.frame_scene import patch
from gacalc.epixscene.venn_scene import g2_subsets_scene
from gacalc.g2 import Bivector, G, Scalar, Vector, Versor, e_1, e_2, e_12
from gacalc.nbdisplay import at_values, show_difference, show_mult

# %% [markdown]
# ## The kinds of element, at a glance
#
# Every element of 𝒢₂ is a plain number plus a vector plus a multiple of the unit plane
# $\mathbf{e}_{12}$. Some elements have only some of those parts, and those get names:

# %%
fig_subsets: PendingFigure
with g2_subsets_scene() as fig_subsets:
    pass
fig_subsets

# %% [markdown]
# - a **scalar** is a plain number (grade 0);
# - a **vector** has only $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$ parts (grade 1);
# - a **bivector** is a multiple of $\mathbf{e}_{12}$, a piece of plane (grade 2);
# - a **versor** is a scalar plus a bivector, the kind of element that rotates (chapter
#   *The Geometric Product*). Every scalar and every bivector is a versor whose other
#   part happens to be $0$.
#
# An element with a plain number and a vector part, like $1 + \vec{\mathbf{e}}_1$, is in
# none of these: it is a general element of 𝒢₂. And $0$ belongs to every one of them,
# the one element they share.
#
# (Elsewhere you may meet "versor" meaning a product of vectors. In the plane the two
# meanings agree: every scalar-plus-bivector other than $0$ is a product of two
# vectors.)
#
# The rest of the notebook builds these pieces up from the rules.

# %% [markdown]
# ## The basis blades are constants
#
# Everything is built from four fixed elements, the **basis blades**: the number $1$,
# the two unit arrows $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$, and the unit piece
# of plane $\mathbf{e}_{12}$. They never change; they are constants, like the digits of
# a number system.

# %%
blade: G
for blade in G.bases(2):
    display(blade)

# %% [markdown]
# A general element is a number times each blade, added up. With every coefficient a
# symbol:

# %%
A: G = G.symbolic_multivector(n=2, prefix="a")
A

# %% [markdown]
# ## Adding and subtracting: collect like blades
#
# Addition works the way you already know from collecting like terms, $2x + 3y + 5x =
# 7x + 3y$: add the numbers in front of the same blade. Two vectors:

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
# and

# %%
b

# %% [markdown]
# Their sum adds the $\vec{\mathbf{e}}_1$ numbers and the $\vec{\mathbf{e}}_2$ numbers:

# %%
a + b

# %% [markdown]
# and their difference subtracts them:

# %%
a - b

# %% [markdown]
# Unlike blades do not combine. A number plus a vector stays two terms, the way $x + y$
# stays $x + y$:

# %%
1 + 1 * e_1

# %% [markdown]
# ## Multiplying: three rules
#
# You know how to multiply $(x + 2)(x + 3)$: multiply everything by everything and add
# up the pieces. Multiplying in 𝒢₂ is the same, with two new rules for the blades and
# one familiar one for the numbers.
#
# **Rule 1: a unit arrow times itself is $1$.** Predict the result before running the
# cell.

# %%
e_1 * e_1

# %% [markdown]
# and

# %%
e_2 * e_2

# %% [markdown]
# **Rule 2: swapping two different arrows flips the sign.**
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ is the unit plane $\mathbf{e}_{12}$:

# %%
e_1 * e_2

# %% [markdown]
# and the other order is its negative:

# %%
e_2 * e_1

# %% [markdown]
# **Rule 3: numbers slide to the front and multiply as usual.**
# $(2 * \vec{\mathbf{e}}_2) * (3 * \vec{\mathbf{e}}_1) = 6 * (\vec{\mathbf{e}}_2 *
# \vec{\mathbf{e}}_1) = -6 * \mathbf{e}_{12}$:

# %%
(2 * e_2) * (3 * e_1)

# %% [markdown]
# ### The same rules, written as math
#
# *(A little more formal; skip it if you like.)* The whole product is fixed by two
# identities about the basis vectors, together with the algebra you already trust: it
# distributes over $+$, it is associative, and numbers factor out.
#
# - (R1) $\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1$;
# - (R2) $\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\vec{\mathbf{e}}_j *
#   \vec{\mathbf{e}}_i$ for $i \neq j$.
#
# Any product of basis vectors reduces by two moves: sort the indices, with a factor of
# $-1$ for each swap of neighbours (R2), and erase any pair of equal neighbours (R1).
#
# $$
# \begin{aligned}
# \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2
#   &= -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2
#     && \text{— (R2) on the first pair} \\
#   &= -\vec{\mathbf{e}}_1 * 1
#     && \text{— (R1) on the last pair} \\
#   &= -\vec{\mathbf{e}}_1
# \end{aligned}
# $$

# %%
e_2 * e_1 * e_2

# %% [markdown]
# ### Two payoffs
#
# **A vector times itself is its squared length**, the Pythagorean theorem: the cross
# terms cancel by Rule 2 and the squares collapse by Rule 1. First at the values
# $a_1 = 3$, $a_2 = 4$:

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 4)]
show_mult(at_values(a, values), at_values(a, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, a)

# %% [markdown]
# **The unit plane squares to $-1$**, like the imaginary unit $i$:
# $\mathbf{e}_{12} * \mathbf{e}_{12} = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 *
# \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 *
# \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 = -1$. Predict, then run:

# %%
e_12 * e_12

# %% [markdown]
# ## Grouping does not matter: associativity
#
# The reduction above quietly regrouped the factors. Were we allowed to? Here is
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1$ grouped left first:

# %%
(e_1 * e_2) * e_1

# %% [markdown]
# and right first:

# %%
e_1 * (e_2 * e_1)

# %% [markdown]
# They agree, and they agree for every three elements of 𝒢₂, not just blades. Three
# general elements, every coefficient a symbol:

# %%
B_1: G = G.symbolic_multivector(n=2, prefix="b")
C: G = G.symbolic_multivector(n=2, prefix="c")
D: G = G.symbolic_multivector(n=2, prefix="d")
(B_1 * C) * D

# %% [markdown]
# grouped the other way:

# %%
B_1 * (C * D)

# %% [markdown]
# Their difference:

# %%
show_difference((B_1 * C) * D, B_1 * (C * D))

# %% [markdown]
# So we may write a product of several elements with no parentheses at all. (That this
# holds in every dimension is a theorem, proved in the Lean files and in
# `tasks/reference/geometric-product-associativity.md`.)

# %% [markdown]
# ## One of each kind
#
# Back to the diagram. gacalc gives each named kind its own type, and every value
# knows which one it is.
#
# A **scalar**, grade 0:

# %%
s: Scalar = Scalar(3)
type(s).__name__

# %% [markdown]
# A **vector**, grade 1:

# %%
type(a).__name__

# %% [markdown]
# A **bivector**, grade 2:

# %%
B: Bivector = 2 * e_12
type(B).__name__

# %% [markdown]
# A **versor**, a scalar plus a bivector:

# %%
theta: sympy.Symbol = sympy.Symbol("theta", real=True)
R: Versor = Scalar(sympy.cos(theta)) + Scalar(sympy.sin(theta)) * e_12
R

# %% [markdown]
# Its type:

# %%
type(R).__name__

# %% [markdown]
# And the general element $1 + \vec{\mathbf{e}}_1$, which is none of the named kinds:

# %%
type(1 + 1 * e_1).__name__

# %% [markdown]
# ## What kind is a product?
#
# The kind of a product follows from the rules, and it is worth predicting each one
# before running it.
#
# A vector times a vector has a plain number (the dot product) and a plane part (the
# wedge): a versor.

# %%
type(a * b).__name__

# %% [markdown]
# That product, written out:

# %%
a * b

# %% [markdown]
# A vector times the plane is a vector again, turned a quarter turn (chapter *Rotate*):

# %%
type(a * e_12).__name__

# %% [markdown]
# A bivector times a bivector is a plain number, since
# $\mathbf{e}_{12} * \mathbf{e}_{12} = -1$:

# %%
type(B * B).__name__

# %% [markdown]
# A versor times a vector is a vector: this is how a versor rotates.

# %%
type(R * a).__name__

# %% [markdown]
# A versor times a versor is a versor: two rotations make a rotation.

# %%
type(R * R).__name__

# %% [markdown]
# Adding a vector and a scalar leaves every named kind:

# %%
type(a + s).__name__

# %% [markdown]
# ## Reading off the parts: grades
#
# The **grade** of a blade is how many arrows it is made of: $1$ has grade 0,
# $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$ grade 1, $\mathbf{e}_{12}$ grade 2.
# `r_vector_part(r)` picks out the grade-$r$ part of any element. For the general
# element $A$: its plain number (grade 0),

# %%
A.r_vector_part(0)

# %% [markdown]
# its vector part (grade 1),

# %%
A.r_vector_part(1)

# %% [markdown]
# and its plane part (grade 2):

# %%
A.r_vector_part(2)

# %% [markdown]
# The parts add back up to $A$.

# %% [markdown]
# ## How the blades resolve when we plot
#
# In school, the point $(3, 2)$ meant "3 to the right, 2 up", and the directions were
# hidden in the notation: the first slot is right, the second is up. In 𝒢₂ the
# directions are written down. $3 * \vec{\mathbf{e}}_1 + 2 * \vec{\mathbf{e}}_2$ says
# "3 steps of the arrow $\vec{\mathbf{e}}_1$, then 2 steps of the arrow
# $\vec{\mathbf{e}}_2$". To plot it, we resolve each blade to the arrow it names and
# walk.
#
# The vector to draw, at its plot values:

# %%
plot_values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 2)]
at_values(a, plot_values)

# %% [markdown]
# Drawn: the two steps dashed, the vector solid, and the unit plane $\mathbf{e}_{12}$ as
# the unit square that $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$ span.

# %%
P_A: Point = point(coordinates=list(at_values(a, plot_values)))
P_STEP: Point = point(coordinates=list(at_values(Scalar(a_1) * e_1, plot_values)))
P_E1: Point = point(coordinates=list(e_1))
P_E2: Point = point(coordinates=list(e_2))
fig_resolve: PendingFigure
with scene_around(points=[P_A, P_E2], basis=False) as fig_resolve:
    patch(corners=[Point(x=0, y=0), P_E1, P_E1 + P_E2, P_E2])
    note(at=0.5 * (P_E1 + P_E2), text=r"$\mathbf{e}_{12}$", color=BLUE)
    dashed_arrow(tail=Point(x=0, y=0), head=P_STEP, color=GREEN)
    dashed_arrow(tail=P_STEP, head=P_A, color=GREEN)
    arrow(head=P_E1, color=BLACK, text=r"$\vec{\mathbf{e}}_1$", offset=Point(x=0, y=-8))
    arrow(head=P_E2, color=BLACK, text=r"$\vec{\mathbf{e}}_2$")
    arrow(head=P_A, color=BLACK, text=at_values(a, plot_values)._repr_latex_())
fig_resolve

# %% [markdown]
# The same element on tilted graph paper would use tilted arrows; the coefficients
# would not change. That is the advantage of naming the directions in the object
# itself: the numbers say *how far*, the blades say *which way*.
