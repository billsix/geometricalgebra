# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
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
# Rotations two ways: the versor sandwich vs the projection formula
# ================================================================
#
# A rotation can be written two equivalent ways in geometric algebra:
#
# * the **versor sandwich** $R * \vec{\mathbf{v}} * R^{-1}$, where $R$ is the versor
# that carries one vector toward another, and * the **projection formula**
# (`transforms.projection_rotation`): turn the part of $\vec{\mathbf{v}}$ that lies in
# the plane of rotation, and leave the perpendicular part fixed.
#
# This notebook shows that the two agree -- *symbolically*, for an arbitrary
# vector $\vec{\mathbf{v}}$ and an arbitrary angle $\theta$ -- in $\mathcal{G}_2$ and
# $\mathcal{G}_3$, using the general `Gn` representation.

# %%

import sympy

import gacalc.g2 as g2
from gacalc.base import MultiVectorBase
from gacalc.gn import Gn, e_1, e_2, e_3, projection_rotation
from gacalc.nbdisplay import show_difference
from gacalc.nbplotutils import show_mult
from gacalc.transforms import ComposableFunction, InvertibleFunction, plane_rotation


def simplified(mv: MultiVectorBase) -> MultiVectorBase:
    """A copy of ``mv`` with each coefficient simplified for display.

    ``versor_from_vectors`` builds an *un-normalized* versor, so the raw sandwich
    coefficients carry a ``/ |R|^2`` factor; ``expand_trig`` then ``simplify``
    reduces them to the familiar ``v1*cos - v2*sin`` form.
    """
    return type(mv).from_blade_dict(
        {
            blade: sympy.simplify(sympy.expand_trig(coef))
            for blade, coef in mv.to_blade_dict().items()
        }
    )


# the angle of rotation, fully symbolic
θ: sympy.Symbol = sympy.symbols("theta", real=True)

# the rotation carries e_1 toward the unit vector at angle theta in the e_1-e_2
# plane; the same rotation is used in 2D and 3D below
a: Gn = e_1
# multivector-first so Gn.__mul__ (-> Gn) is used, not sympy's Expr.__mul__
b: Gn = e_1 * sympy.cos(θ) + e_2 * sympy.sin(θ)

# %% [markdown]
# $\mathcal{G}_2$ -- the plane
# ----------------------------
#
# A symbolic vector
# $\vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2$.

# %%
v1: sympy.Symbol
v2: sympy.Symbol
v1, v2 = sympy.symbols("v1 v2", real=True)
v_2d: Gn = Gn.from_real(v1) * e_1 + Gn.from_real(v2) * e_2
R: MultiVectorBase = Gn.versor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The versor sandwich $R * \vec{\mathbf{v}} * R^{-1}$ (simplified for display):

# %%
sandwich_2d: MultiVectorBase = R * v_2d * R.inverse()
simplified(sandwich_2d)

# %% [markdown]
# The projection formula `projection_rotation(from, to)` applied to the same
# $\vec{\mathbf{v}}$:

# %%
projection_2d: MultiVectorBase = projection_rotation(from_vector=a, to_vector=b)(v_2d)
simplified(projection_2d)

# %% [markdown]
# They are equal -- their difference is the **zero** multivector:

# %%
show_difference(sandwich_2d, projection_2d)

# %% [markdown]
# $\mathcal{G}_3$ -- space
# ------------------------
#
# A symbolic vector
# $\vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2 + v_3 * \vec{\mathbf{e}}_3$,
# rotated by the *same* rotation (in the $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$
# plane).  The $\vec{\mathbf{e}}_3$ component is perpendicular to the plane, so a
# correct rotation must leave it untouched -- both formulas do.

# %%
v3: sympy.Symbol
v1, v2, v3 = sympy.symbols("v1 v2 v3", real=True)
v_3d: Gn = Gn.from_real(v1) * e_1 + Gn.from_real(v2) * e_2 + Gn.from_real(v3) * e_3
R3: MultiVectorBase = Gn.versor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The versor sandwich (note the $\vec{\mathbf{e}}_3$ part rides through unchanged):

# %%
sandwich_3d: MultiVectorBase = R3 * v_3d * R3.inverse()
simplified(sandwich_3d)

# %% [markdown]
# The projection formula on the same $\vec{\mathbf{v}}$:

# %%
projection_3d: MultiVectorBase = projection_rotation(from_vector=a, to_vector=b)(v_3d)
simplified(projection_3d)

# %% [markdown]
# Again equal -- the difference is the zero multivector:

# %%
show_difference(sandwich_3d, projection_3d)

# %% [markdown]
# Every intermediate product along the way
# ----------------------------------------
#
# The sandwich is two geometric products -- first $R * \vec{\mathbf{v}}$, then
# $(R * \vec{\mathbf{v}}) * R^{-1}$. `show_mult` lays out *every*
# component-times-component term and sums them, the same way you can watch associativity
# term by term.  The thing to notice in $\mathcal{G}_3$: $R * \vec{\mathbf{v}}$ carries
# a **trivector** ($\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$) as
# well as a vector, and the second product makes that trivector **cancel**, leaving a
# pure vector -- which is *why* a versor sandwich of a vector is always a vector.

# %% [markdown]
# **Step 1 --- $R * \vec{\mathbf{v}}$** (a vector *and* a trivector):

# %%
show_mult(R3, v_3d)

# %% [markdown]
# **Step 2 --- $(R * \vec{\mathbf{v}}) * R^{-1}$** (the trivector cancels; a pure vector
# remains):

# %%
show_mult(R3 * v_3d, R3.inverse())

# %% [markdown]
# The cross product, derived as a composed pipeline
# =================================================
#
# The cross product $\vec{\mathbf{a}} \times \vec{\mathbf{b}}$ is the vector
# perpendicular to both $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, with length
# $|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| * \sin(\theta)$. We can *build* it out of
# nothing but `projection_rotation` and `project`, composed — no cross-product formula
# needed.
#
# Take two **symbolic** 3D vectors (the grade-1 part of a symbolic multivector):

# %%
a: Gn = Gn.symbolic_multivector(3, "a").r_vector_part(1)
b: Gn = Gn.symbolic_multivector(3, "b").r_vector_part(1)

# %% [markdown]
# The first is $\vec{\mathbf{a}}$,

# %%
a

# %% [markdown]
# and the second $\vec{\mathbf{b}}$:

# %%
b

# %% [markdown]
# Now compose four steps. Read them in **order of application** (which is
# right-to-left in the `@` chain — the last one written is applied first):
#
# 1. **rotate $\vec{\mathbf{a}} \to \vec{\mathbf{e}}_1$** — spin space so
#    $\vec{\mathbf{a}}$ lies along $\vec{\mathbf{e}}_1$.
# 2. **project onto the $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$ plane** — drop the
#    part along $\vec{\mathbf{a}}$ (now $\vec{\mathbf{e}}_1$), keeping only the
#    component of $\vec{\mathbf{b}}$ *perpendicular* to $\vec{\mathbf{a}}$.
# 3. **rotate $\vec{\mathbf{e}}_2 \to \vec{\mathbf{e}}_3$** — a quarter turn *in that
#    perpendicular plane*: this is the $90^\circ$ turn that makes a cross product a
#    cross product.
# 4. **rotate $\vec{\mathbf{e}}_1 \to \vec{\mathbf{a}}$** — undo step 1, carrying the
#    result back to the original frame.
#
# Every rotation here is a *pure* `projection_rotation` (magnitude-preserving), and the
# projection only drops a component (no scaling) — so the pipeline never multiplies in
# the $|\vec{\mathbf{a}}|$ that a real cross product carries. The result is therefore
# $\vec{\mathbf{a}} \times \vec{\mathbf{b}}$ **divided by $|\vec{\mathbf{a}}|$**.

# %%
# label convention: subscript = "from", superscript = "to"
align: ComposableFunction[MultiVectorBase] = ComposableFunction(
    projection_rotation(from_vector=a, to_vector=e_1), r"R_{a}^{e_1}"
)
perp: ComposableFunction[MultiVectorBase] = ComposableFunction(
    Gn.project(e_2 ^ e_3), r"P_{e_{23}}"
)
turn: ComposableFunction[MultiVectorBase] = ComposableFunction(
    projection_rotation(from_vector=e_2, to_vector=e_3), r"R_{e_2}^{e_3}"
)
unalign: ComposableFunction[MultiVectorBase] = ComposableFunction(
    projection_rotation(from_vector=e_1, to_vector=a), r"R_{e_1}^{a}"
)

cross_over_norm_a: ComposableFunction[MultiVectorBase] = unalign @ turn @ perp @ align
# the whole pipeline, rendered as one LaTeX expression
cross_over_norm_a

# %% [markdown]
# Apply it to $\vec{\mathbf{b}}$. Out come the cross-product components
# $(a_2 b_3 - a_3 b_2,\; a_3 b_1 - a_1 b_3,\; a_1 b_2 - a_2 b_1)$ — each divided by
# $|\vec{\mathbf{a}}| = \sqrt{a_1^2 + a_2^2 + a_3^2}$:

# %%
result: MultiVectorBase = cross_over_norm_a(b)
result

# %% [markdown]
# Confirm it: multiplying back by $|\vec{\mathbf{a}}|$ recovers the cross product
# exactly, which in geometric algebra is the dual of the wedge,
# $\vec{\mathbf{a}} \times \vec{\mathbf{b}} = (\vec{\mathbf{a}} \wedge \vec{\mathbf{b}})^{*}$:

# %%
(result * abs(a)).simplified() == (a ^ b).dual(n=3)

# %% [markdown]
# A rotor is the exponential of a bivector
# ========================================
#
# There is a third way to write the same rotation: the **exponential map**.
# A unit bivector $i$ squares to $-1$, so the power series
# $e^{A} = \sum A^k / k!$ closes into trig — for the scaled plane
# $A = -(\theta/2)\, i$ it sums to exactly the half-angle rotor:
#
# $$ e^{-(\theta/2)\, i} \;=\; \cos(\theta/2) \;-\; \sin(\theta/2) * i $$
#
# The angle here is declared *positive*: `exp` computes $|A| = \sqrt{\theta^2}/2$,
# which collapses to $\theta/2$ only once sympy knows the sign.

# %%
φ: sympy.Symbol = sympy.symbols("phi", positive=True)

i: g2.Bivector = g2.Bivector.e_12
R_exp: g2.Versor = (i * (-φ / 2)).exp()
R_exp

# %% [markdown]
# Note the *type*: exponentiating a `g2.Bivector` lands in `g2.Versor` — the
# exponential map carries the plane onto the rotor group, and the graded types
# say so.  The rotor is automatically unit ($\cos^2 + \sin^2 = 1$), and its
# sandwich agrees with the rotation `plane_rotation` builds from the same
# plane and angle (their difference is $0$):

# %%
f: InvertibleFunction[g2.Vector] = plane_rotation(g2.Vector.e_1, g2.Vector.e_2)(φ)
v_exp: g2.Vector = g2.Scalar(v1) * g2.Vector.e_1 + g2.Scalar(v2) * g2.Vector.e_2
show_difference(R_exp.sandwich(v_exp), f(v_exp))
