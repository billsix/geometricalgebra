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
# # The dual of a plane is perpendicular to it — calculations
#
# Companion to *The Dual in Space*. In the plane, the dual of a vector was the vector
# times $I^{-1}$, and the proof that it is perpendicular used only associativity and
# the fact that a vector times itself is a plain number. In space the unit volume is
# $I = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$, and the same
# multiplication by $I^{-1}$ sends a *plane* to a *vector*. Here the plane is the one
# spanned by $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, and we prove its dual is
# perpendicular to both.
#
# (The dual of a vector in space is a plane, not a vector, so "the angle between a
# vector and its dual" has no meaning there. The claim is about the dual of a plane.)
#
# Every coordinate is a symbol. Numbers appear only to draw the figure. The Lean
# theorems are `dual_wedge_perp_left_dot` and `dual_wedge_perp_right_dot`
# (`proofs/GacalcProofs/Projection3D.lean`).

# %%
# twin: GacalcProofs.G3.dual_wedge_perp_left_dot
# twin: GacalcProofs.G3.dual_wedge_perp_right_dot
import sympy

from gacalc.base import Real
from gacalc.epixscene.frame_scene import (
    BLUE,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    patch,
    point,
    scene_3d,
)
from gacalc.g3 import Bivector, Scalar, Trivector, Vector, Versor, e_1, e_2, e_3, e_123
from gacalc.nbdisplay import at_values, show_difference

# %% [markdown]
# ## The vectors, and the plane they span
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
# The proof is easiest with two vectors in the plane that are perpendicular to each
# other. Keep $\vec{\mathbf{a}}$, and replace $\vec{\mathbf{b}}$ by its rejection from
# $\vec{\mathbf{a}}$, the part of $\vec{\mathbf{b}}$ across $\vec{\mathbf{a}}$
# (chapter *Projection*):
#
# $$
# \vec{\mathbf{r}} = \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
#   = \vec{\mathbf{b}} - \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}).
# $$

# %%
r: Vector = b.rejected_away_from(a).simplified()
r

# %% [markdown]
# It is perpendicular to $\vec{\mathbf{a}}$: their dot product is $0$.

# %%
sympy.simplify(sympy.sympify(a.dot(r).scalar_part()))

# %% [markdown]
# It spans the same plane: $\vec{\mathbf{a}} \wedge \vec{\mathbf{r}}$ is
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$, because the part of $\vec{\mathbf{b}}$
# along $\vec{\mathbf{a}}$ adds no area. First
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$:

# %%
plane: Bivector = (a ^ b).simplified()
plane

# %% [markdown]
# then $\vec{\mathbf{a}} \wedge \vec{\mathbf{r}}$:

# %%
(a ^ r).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(a ^ r, plane)

# %% [markdown]
# Because $\vec{\mathbf{a}}$ and $\vec{\mathbf{r}}$ are perpendicular, their product
# has no plain-number part, so it is the wedge alone,
# $\vec{\mathbf{a}} * \vec{\mathbf{r}} = \vec{\mathbf{a}} \wedge \vec{\mathbf{r}}$:

# %%
(a * r - (a ^ r)).simplified()

# %% [markdown]
# and swapping the two flips the sign,
# $\vec{\mathbf{r}} * \vec{\mathbf{a}} = -\vec{\mathbf{a}} * \vec{\mathbf{r}}$. Their
# sum:

# %%
(r * a + a * r).simplified()

# %% [markdown]
# ## The dual of the plane
#
# The unit volume $I$ squares to $-1$, so its inverse is
# $I^{-1} = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$:

# %%
I_inverse: Trivector = e_123.inverse()
I_inverse

# %% [markdown]
# The dual of the plane is
# $\vec{\mathbf{d}} = (\vec{\mathbf{a}} * \vec{\mathbf{r}}) * I^{-1}$. gacalc computes
# it as `plane.dual(3)`:

# %%
d: Vector = plane.dual(3).simplified()
d

# %% [markdown]
# It is a vector: each of the three plane parts times $I^{-1}$ is a basis vector, as in
# $\mathbf{e}_{12} * I^{-1} = \vec{\mathbf{e}}_3$.

# %%
d.is_vector()

# %% [markdown]
# It is also $\vec{\mathbf{a}} * \vec{\mathbf{r}} * I^{-1}$, built from the
# perpendicular pair. Its difference from the dual:

# %%
show_difference(a * r * I_inverse, d)

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 2),
    (a_2, 0),
    (a_3, 0),
    (b_1, 1),
    (b_2, 2),
    (b_3, 0),
]
LOWER_LEFT: Point = Point(x=-3.8, y=-2.2)
UPPER_RIGHT: Point = Point(x=4.0, y=4.6)

# %% [markdown]
# Drawn at the plot values: the plane of $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$
# shaded, $\vec{\mathbf{r}}$ in blue, and the dual in purple, standing straight out of
# the plane.

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_R: Point = point(coordinates=list(at_values(r, values)))
P_D: Point = point(coordinates=list(at_values(d, values)))
fig_dual: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_dual:
    patch(corners=[Point(x=0, y=0, z=0), P_A, P_A + P_B, P_B])
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$", align=LabelPos.b)
    arrow(head=P_B, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_R, color=BLUE, text=r"$\vec{\mathbf{r}}$", align=LabelPos.l)
    arrow(head=P_D, color=PURPLE, text=r"$\vec{\mathbf{d}}$")
fig_dual

# %% [markdown]
# ## The dual is perpendicular to $\vec{\mathbf{a}}$
#
# The same three facts as in the plane: the dot product of two vectors is the
# plain-number part of their product, grouping does not matter, and a vector times
# itself is its squared length.
#
# $$
# \begin{aligned} \vec{\mathbf{a}} \cdot \vec{\mathbf{d}} &= \langle \vec{\mathbf{a}} *
# (\vec{\mathbf{a}} * \vec{\mathbf{r}} * I^{-1}) \rangle_0 && \text{— the dot product is
# the plain-number part} \\ &= \langle (\vec{\mathbf{a}} * \vec{\mathbf{a}}) *
# (\vec{\mathbf{r}} * I^{-1}) \rangle_0 && \text{— regroup (associativity)} \\ &=
# |\vec{\mathbf{a}}|^2 * \langle \vec{\mathbf{r}} * I^{-1} \rangle_0 && \text{— a vector
# times itself is its squared length} \\ &= 0 && \text{— a vector times } I^{-1} \text{
# is a plane, no plain number} \end{aligned}
# $$
#
# The last step: $\vec{\mathbf{r}} * I^{-1}$ is a plane (each basis vector times
# $I^{-1}$ is a basis plane), so it has no plain-number part.

# %%
r_dual: Bivector = (r * I_inverse).simplified()
r_dual

# %% [markdown]
# The regrouped product, $(\vec{\mathbf{a}} * \vec{\mathbf{a}}) * (\vec{\mathbf{r}} *
# I^{-1})$, a number times that plane:

# %%
regrouped_a: Versor = ((a * a) * r_dual).simplified()
regrouped_a

# %% [markdown]
# and the product as first written, $\vec{\mathbf{a}} * \vec{\mathbf{d}}$:

# %%
product_a: Versor = (a * d).simplified()
product_a

# %% [markdown]
# Their difference:

# %%
show_difference(product_a, regrouped_a)

# %% [markdown]
# So the plain-number part, the dot product, is $0$:

# %%
sympy.simplify(sympy.sympify(a.dot(d).scalar_part()))

# %% [markdown]
# ## The dual is perpendicular to $\vec{\mathbf{r}}$
#
# This time $\vec{\mathbf{r}}$ meets the product from the left, with $\vec{\mathbf{a}}$
# in the way. Swap $\vec{\mathbf{r}}$ past $\vec{\mathbf{a}}$, which flips the sign, and
# then $\vec{\mathbf{r}}$ meets itself:
#
# $$
# \begin{aligned} \vec{\mathbf{r}} \cdot \vec{\mathbf{d}} &= \langle \vec{\mathbf{r}} *
# \vec{\mathbf{a}} * \vec{\mathbf{r}} * I^{-1} \rangle_0 && \text{— the dot product is
# the plain-number part} \\ &= -\langle \vec{\mathbf{a}} * \vec{\mathbf{r}} *
# \vec{\mathbf{r}} * I^{-1} \rangle_0 && \text{— } \vec{\mathbf{r}} * \vec{\mathbf{a}} =
# -\vec{\mathbf{a}} * \vec{\mathbf{r}} \\ &= -|\vec{\mathbf{r}}|^2 * \langle
# \vec{\mathbf{a}} * I^{-1} \rangle_0 && \text{— regroup; a vector times itself} \\ &= 0
# && \text{— } \vec{\mathbf{a}} * I^{-1} \text{ is a plane} \end{aligned}
# $$
#
# The product as first written, $\vec{\mathbf{r}} * \vec{\mathbf{d}}$:

# %%
product_r: Versor = (r * d).simplified()
product_r

# %% [markdown]
# and after the swap and the regrouping,
# $-|\vec{\mathbf{r}}|^2 * (\vec{\mathbf{a}} * I^{-1})$:

# %%
swapped_r: Versor = (-(r * r) * (a * I_inverse)).simplified()
swapped_r

# %% [markdown]
# So the dot product is $0$:

# %%
sympy.simplify(sympy.sympify(r.dot(d).scalar_part()))

# %% [markdown]
# ## The dual is perpendicular to $\vec{\mathbf{b}}$
#
# $\vec{\mathbf{b}}$ is its projection onto $\vec{\mathbf{a}}$, which is a number
# $\lambda$ times $\vec{\mathbf{a}}$, plus $\vec{\mathbf{r}}$. The dot product
# distributes, so
#
# $$
# \vec{\mathbf{b}} \cdot \vec{\mathbf{d}} = (\lambda * \vec{\mathbf{a}} +
# \vec{\mathbf{r}}) \cdot \vec{\mathbf{d}} = \lambda * (\vec{\mathbf{a}} \cdot
# \vec{\mathbf{d}}) + \vec{\mathbf{r}} \cdot \vec{\mathbf{d}} = \lambda * 0 + 0 = 0.
# $$
#
# The projection plus the rejection is $\vec{\mathbf{b}}$.

# %% [markdown]
# and the dot product of $\vec{\mathbf{b}}$ with the dual:

# %%
sympy.simplify(sympy.sympify(b.dot(d).scalar_part()))

# %% [markdown]
# ## As cosines
#
# With both dot products $0$, the cosine of the angle from the dual to
# $\vec{\mathbf{a}}$ is $0$:

# %%
sympy.simplify(sympy.sympify(d.cosine(a)))

# %% [markdown]
# and to $\vec{\mathbf{b}}$:

# %%
sympy.simplify(sympy.sympify(d.cosine(b)))

# %% [markdown]
# Both angles are $90°$.

# %% [markdown]
# ## The dual of the plane is the cross product
#
# The vector perpendicular to both $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$ is the one
# vector calculus calls the cross product $\vec{\mathbf{a}} \times \vec{\mathbf{b}}$.
# *Proof: The Cross Product* builds it by rotating to standard position; here it falls
# out of one multiplication. gacalc's `cross`:

# %%
a.cross(b)

# %% [markdown]
# Its difference from the dual:

# %%
show_difference(a.cross(b), d)

# %% [markdown]
# ## Why the vector's dual is not a vector here
#
# Multiplying a vector by $I^{-1}$ in space gives a plane, as $\vec{\mathbf{r}} *
# I^{-1}$ above showed. gacalc gives every product a definite type:

# %%
type(a * I_inverse).__name__

# %% [markdown]
# a plane (`Bivector`), while a plane times $I^{-1}$ is a vector:

# %%
type(plane * I_inverse).__name__
