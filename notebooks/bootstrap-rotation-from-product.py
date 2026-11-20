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
# # Step 6, rotation through the product — worked example
#
# Companion to *Step 6: Rotation, through the Product*. There are three vectors:
# $\vec{\mathbf{a}}$, $\vec{\mathbf{b}}$, and a $\vec{\mathbf{v}}$ to rotate, every
# coordinate a symbol, so each result is a formula for all vectors. The rotation from
# $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$ is applied to $\vec{\mathbf{v}}$ as the
# one-sided product $\vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})$, then as
# the sandwich $R * \vec{\mathbf{v}} * R^{-1}$ with
# $R = \vec{\mathbf{b}} * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|$.
# Both match Step 3's rotation built from projection. Numbers appear only to draw the
# figures; change them and rerun. Each check shows both sides, then their difference.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    point,
    scene_around,
)
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference, show_mult
from gacalc.transforms import versor_rotation

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$, $\vec{\mathbf{b}}$ and $\vec{\mathbf{v}}$, every coordinate a
# symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
v_1: sympy.Symbol
v_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2 = sympy.symbols("a_1 a_2 b_1 b_2 v_1 v_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# and $\vec{\mathbf{v}}$:

# %%
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 2),
    (a_2, 1),
    (b_1, 1),
    (b_2, 2),
    (v_1, -1),
    (v_2, 2),
]

# %% [markdown]
# ## The one-sided form
#
# The product of the two unit vectors is
# $\cos(\theta) + \sin(\theta) * \mathbf{e}_{12}$, with $\theta$ the angle from
# $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$:

# %%
unit_product: Versor = (a.normalize() * b.normalize()).simplified()
unit_product

# %% [markdown]
# Multiplying $\vec{\mathbf{v}}$ by it on the right rotates $\vec{\mathbf{v}}$ by
# $\theta$. Term by term: each term of $\vec{\mathbf{v}}$ times the plain-number part
# keeps its direction, and times the $\mathbf{e}_{12}$ part turns a quarter turn. First
# at the plot values:

# %%
show_mult(at_values(v, values), at_values(unit_product, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(v, unit_product)

# %% [markdown]
# The sum, the rotated $\vec{\mathbf{v}}$:

# %%
one_sided: MultiVectorBase = (v * unit_product).simplified()
one_sided

# %% [markdown]
# At the plot values:

# %%
at_values(one_sided, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_V: Point = point(coordinates=list(at_values(v, values)))
P_ROTATED: Point = point(coordinates=list(at_values(one_sided, values)))
fig_one_sided: PendingFigure
with scene_around(points=[P_A, P_B, P_V, P_ROTATED]) as fig_one_sided:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
    arrow(
        head=P_ROTATED,
        color=PURPLE,
        text=r"$\vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
fig_one_sided

# %% [markdown]
# ## The sandwich
#
# $R = \vec{\mathbf{b}} * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|$
# turns $\vec{\mathbf{a}}$ halfway, onto the bisector
# $\vec{\mathbf{h}} = |\vec{\mathbf{b}}| * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * \vec{\mathbf{b}}$
# (scaled by $|\vec{\mathbf{a}}|$), and $R * \vec{\mathbf{v}} * R^{-1}$ is the whole
# rotation.

# %%
R: Versor = (b * a + Scalar(a.magnitude() * b.magnitude())).simplified()
R

# %% [markdown]
# The sandwich is two products. First $R * \vec{\mathbf{v}}$, term by term, at the plot
# values:

# %%
show_mult(at_values(R, values), at_values(v, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(R, v)

# %% [markdown]
# Then that result times $R^{-1}$, at the plot values:

# %%
show_mult(at_values(R * v, values), at_values(R.inverse(), values))

# %% [markdown]
# With every coordinate a symbol, the table for this second product is pages of nested
# square roots, so it is left out; the sandwich's result is below, and the checks
# compare it with the one-sided form.

# %%
sandwich: MultiVectorBase = (R * v * R.inverse()).simplified()
sandwich

# %% [markdown]
# At the plot values:

# %%
at_values(sandwich, values)

# %% [markdown]
# Drawn at the plot values:

# %%
h: Vector = Scalar(b.magnitude()) * a + Scalar(a.magnitude()) * b
P_H: Point = point(coordinates=list(at_values(h.normalize(), values)))
P_SANDWICH: Point = point(coordinates=list(at_values(sandwich, values)))
fig_sandwich: PendingFigure
with scene_around(points=[P_A, P_B, P_V, P_SANDWICH]) as fig_sandwich:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_H, color=PURPLE, text=r"$\hat{\mathbf{h}}$"
    )
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
    arrow(
        head=P_SANDWICH,
        color=PURPLE,
        text=r"$R * \vec{\mathbf{v}} * R^{-1}$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
fig_sandwich

# %% [markdown]
# ## Checks, for all vectors
#
# Step 3 built the rotation from projection: $\vec{\mathbf{b}}$ measured against
# $\vec{\mathbf{a}}$ (Step 2, by Step 1's rotation by minus the angle of
# $\vec{\mathbf{a}}$) gives the cosine and sine, and the same angle is applied to
# $\vec{\mathbf{v}}$. Here is that construction, to compare against.


# %%
def rotation_by_projection(a: Vector, b: Vector, v: Vector) -> Vector:
    """Step 3's construction: ``b`` measured against ``a`` gives the cosine and sine
    of the angle from ``a`` to ``b``; the same angle applied to ``v``."""
    measured: Vector = b.rotate(-sympy.atan2(a.coefficient(e_2), a.coefficient(e_1)))
    cos: Real = measured.coefficient(e_1) / b.magnitude()
    sin: Real = measured.coefficient(e_2) / b.magnitude()
    return (Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()).simplified()


# %% [markdown]
# ### The one-sided form is Step 3's rotation
#
# Step 3's rotation of $\vec{\mathbf{v}}$:

# %%
by_projection: Vector = rotation_by_projection(a, b, v)
by_projection

# %% [markdown]
# The one-sided form was:

# %%
one_sided

# %% [markdown]
# Their difference:

# %%
show_difference(one_sided, by_projection)

# %% [markdown]
# ### The other order turns the other way
#
# $(\hat{\mathbf{a}} * \hat{\mathbf{b}}) * \vec{\mathbf{v}}$:

# %%
(unit_product * v).simplified()

# %% [markdown]
# Step 3's rotation from $\vec{\mathbf{b}}$ to $\vec{\mathbf{a}}$:

# %%
rotation_by_projection(b, a, v)

# %% [markdown]
# Their difference:

# %%
show_difference(unit_product * v, rotation_by_projection(b, a, v))

# %% [markdown]
# ### $R$ turns $\vec{\mathbf{a}}$ onto the bisector
#
# $R * \vec{\mathbf{a}}$:

# %%
(R * a).simplified()

# %% [markdown]
# $|\vec{\mathbf{a}}| * \vec{\mathbf{h}}$:

# %%
(Scalar(a.magnitude()) * h).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(R * a, Scalar(a.magnitude()) * h)

# %% [markdown]
# ### The sandwich is the one-sided form
#
# The sandwich and the one-sided form were shown above. Their difference:

# %%
show_difference(sandwich, one_sided)

# %% [markdown]
# ### The step that makes the sandwich agree
#
# $\tilde{R} * R^{-1} = \hat{\mathbf{a}} * \hat{\mathbf{b}}$, checked with unit vectors
# at angles $\alpha$ and $\beta$, where $R = \hat{\mathbf{b}} * \hat{\mathbf{a}} + 1$:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
R_unit: Versor = b_hat * a_hat + Scalar(1)
(R_unit.reverse() * R_unit.inverse()).simplified()

# %% [markdown]
# $\hat{\mathbf{a}} * \hat{\mathbf{b}}$:

# %%
(a_hat * b_hat).simplified()

# %% [markdown]
# Their difference:

# %%
show_difference(R_unit.reverse() * R_unit.inverse(), a_hat * b_hat)

# %% [markdown]
# ### gacalc agrees
#
# gacalc's `versor_rotation`, applied to $\vec{\mathbf{v}}$:

# %%
versor_rotation(from_vector=a, to_vector=b)(v).simplified()

# %% [markdown]
# Its difference from the one-sided form:

# %%
show_difference(versor_rotation(from_vector=a, to_vector=b)(v), one_sided)
