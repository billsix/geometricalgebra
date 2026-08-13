# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: gacalc
#     language: python
#     name: gacalc
# ---

# %%

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
# Rotations two ways: the rotor sandwich vs the projection formula
# ================================================================
#
# A rotation can be written two equivalent ways in geometric algebra:
#
# * the **rotor sandwich**  $R\,v\,R^{-1}$, where $R$ is the rotor that carries
#   one vector toward another, and
# * the **projection formula** (`transforms.projection_rotation`): turn the part
#   of $v$ that lies in the plane of rotation, and leave the perpendicular part fixed.
#
# This notebook shows that the two agree -- *symbolically*, for an arbitrary
# vector $v$ and an arbitrary angle $\theta$ -- in $\mathcal{G}_2$ and
# $\mathcal{G}_3$, using the general `Gn` representation.

# %%
import sympy

import gacalc.g2 as g2
from gacalc.gn import Gn, e_1, e_2, e_3, projection_rotation
from gacalc.nbplotutils import show_mult
from gacalc.transforms import ComposableFunction, plane_rotation


def simplified(mv: Gn) -> Gn:
    """A copy of ``mv`` with each coefficient simplified for display.

    ``rotor_from_vectors`` builds an *un-normalized* rotor, so the raw sandwich
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
theta = sympy.symbols("theta", real=True)

# the rotation carries e_1 toward the unit vector at angle theta in the e_1-e_2
# plane; the same rotation is used in 2D and 3D below
a: Gn = e_1
b: Gn = sympy.cos(theta) * e_1 + sympy.sin(theta) * e_2

# %% [markdown]
# $\mathcal{G}_2$ -- the plane
# ----------------------------
#
# A symbolic vector $v = v_1 e_1 + v_2 e_2$.

# %%
v1, v2 = sympy.symbols("v1 v2", real=True)
v_2d: Gn = v1 * e_1 + v2 * e_2

R: Gn = Gn.rotor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The rotor sandwich $R\,v\,R^{-1}$ (simplified for display):

# %%
sandwich_2d: Gn = R * v_2d * R.inverse()
simplified(sandwich_2d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The projection formula `projection_rotation(from, to)` applied to the same $v$:

# %%
projection_2d: Gn = projection_rotation(from_vector=a, to_vector=b)(v_2d)
simplified(projection_2d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# They are equal -- their difference is the **zero** multivector:

# %%
sandwich_2d - projection_2d  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# $\mathcal{G}_3$ -- space
# ------------------------
#
# A symbolic vector $v = v_1 e_1 + v_2 e_2 + v_3 e_3$, rotated by the *same*
# rotation (in the $e_1 e_2$ plane).  The $e_3$ component is perpendicular to the
# plane, so a correct rotation must leave it untouched -- both formulas do.

# %%
v1, v2, v3 = sympy.symbols("v1 v2 v3", real=True)
v_3d: Gn = v1 * e_1 + v2 * e_2 + v3 * e_3

R3: Gn = Gn.rotor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The rotor sandwich (note the $e_3$ part rides through unchanged):

# %%
sandwich_3d: Gn = R3 * v_3d * R3.inverse()
simplified(sandwich_3d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The projection formula on the same $v$:

# %%
projection_3d: Gn = projection_rotation(from_vector=a, to_vector=b)(v_3d)
simplified(projection_3d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Again equal -- the difference is the zero multivector:

# %%
sandwich_3d - projection_3d  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Every intermediate product along the way
# ----------------------------------------
#
# The sandwich is two geometric products -- first $R\,v$, then $(R\,v)\,R^{-1}$.
# `show_mult` lays out *every* component-times-component term and sums them, the
# same way you can watch associativity term by term.  The thing to notice in
# $\mathcal{G}_3$: $R\,v$ carries a **trivector** ($e_1 e_2 e_3$) as well as a
# vector, and the second product makes that trivector **cancel**, leaving a pure
# vector -- which is *why* a rotor sandwich of a vector is always a vector.

# %% [markdown]
# **Step 1 --- $R\,v$** (a vector *and* a trivector):

# %%
show_mult(R3, v_3d)

# %% [markdown]
# **Step 2 --- $(R\,v)\,R^{-1}$** (the trivector cancels; a pure vector remains):

# %%
show_mult(R3 * v_3d, R3.inverse())

# %% [markdown]
# The cross product, derived as a composed pipeline
# =================================================
#
# The cross product $a \times b$ is the vector perpendicular to both $a$ and $b$,
# with length $|a||b|\sin\theta$. We can *build* it out of nothing but
# `projection_rotation` and `project`, composed — no cross-product formula needed.
#
# Take two **symbolic** 3D vectors (the grade-1 part of a symbolic multivector):

# %%
a: Gn = Gn.symbolic_multivector(3, "a").r_vector_part(1)
b: Gn = Gn.symbolic_multivector(3, "b").r_vector_part(1)

# %%
a

# %%
b

# %% [markdown]
# Now compose four steps. Read them in **order of application** (which is
# right-to-left in the `@` chain — the last one written is applied first):
#
# 1. **rotate $a \to e_1$** — spin space so $a$ lies along $e_1$.
# 2. **project onto the $e_2 e_3$ plane** — drop the part along $a$ (now $e_1$),
#    keeping only the component of $b$ *perpendicular* to $a$.
# 3. **rotate $e_2 \to e_3$** — a quarter turn *in that perpendicular plane*: this
#    is the $90^\circ$ turn that makes a cross product a cross product.
# 4. **rotate $e_1 \to a$** — undo step 1, carrying the result back to the
#    original frame.
#
# Every rotation here is a *pure* `projection_rotation` (magnitude-preserving), and
# the projection only drops a component (no scaling) — so the pipeline never
# multiplies in the $|a|$ that a real cross product carries. The result is
# therefore $a \times b$ **divided by $|a|$**.

# %%
# label convention: subscript = "from", superscript = "to"
align: ComposableFunction = ComposableFunction(
    projection_rotation(from_vector=a, to_vector=e_1), r"R_{a}^{e_1}"
)
perp: ComposableFunction = ComposableFunction(Gn.project(e_2 ^ e_3), r"P_{e_{23}}")
turn: ComposableFunction = ComposableFunction(
    projection_rotation(from_vector=e_2, to_vector=e_3), r"R_{e_2}^{e_3}"
)
unalign: ComposableFunction = ComposableFunction(
    projection_rotation(from_vector=e_1, to_vector=a), r"R_{e_1}^{a}"
)

cross_over_norm_a: ComposableFunction = unalign @ turn @ perp @ align
# the whole pipeline, rendered as one LaTeX expression
cross_over_norm_a  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Apply it to $b$. Out come the cross-product components
# $(a_2 b_3 - a_3 b_2,\; a_3 b_1 - a_1 b_3,\; a_1 b_2 - a_2 b_1)$ — each divided by
# $|a| = \sqrt{a_1^2 + a_2^2 + a_3^2}$:

# %%
result: Gn = cross_over_norm_a(b)
result  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Confirm it: multiplying back by $|a|$ recovers the cross product exactly, which
# in geometric algebra is the dual of the wedge, $a \times b = (a \wedge b)^{*}$:

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
# $$ e^{-(\theta/2)\, i} \;=\; \cos(\theta/2) \;-\; \sin(\theta/2)\, i $$
#
# The angle here is declared *positive*: `exp` computes $|A| = \sqrt{\theta^2}/2$,
# which collapses to $\theta/2$ only once sympy knows the sign.

# %%
phi = sympy.symbols("phi", positive=True)

i: g2.Bivector = g2.Bivector.e_12
R_exp: g2.Rotor = (i * (-phi / 2)).exp()
R_exp  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Note the *type*: exponentiating a `g2.Bivector` lands in `g2.Rotor` — the
# exponential map carries the plane onto the rotor group, and the graded types
# say so.  The rotor is automatically unit ($\cos^2 + \sin^2 = 1$), and its
# sandwich agrees with the rotation `plane_rotation` builds from the same
# plane and angle:

# %%
f = plane_rotation(g2.Vector.e_1, g2.Vector.e_2)(phi)
v_exp: g2.Vector = v1 * g2.Vector.e_1 + v2 * g2.Vector.e_2
R_exp.sandwich(v_exp) == f(v_exp)
