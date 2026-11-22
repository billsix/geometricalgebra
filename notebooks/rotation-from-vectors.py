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
# # A Rotation from Two Vectors — No Angle
#
# In precalculus,
#
# $$\cos(\beta - \alpha) = \cos(\alpha) * \cos(\beta) + \sin(\alpha) * \sin(\beta)$$
#
# is an identity to memorize. The chapter claims that the geometric product of two
# vectors *is* the rotation from one to the other, with no angle ever named, and that
# identity falls out of the multiplication. This notebook checks it with gacalc and
# sympy, every coordinate a symbol: the product of two unit vectors is the full-angle
# rotor, multiplying the first by it on the right lands on the second, and the versor,
# projection and three-turn routes to a rotation agree. Numbers appear only to draw the
# figures. Each check shows both sides, then their difference.

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
    point,
    scene_around,
)
from gacalc.g2 import Scalar, Vector, Versor
from gacalc.nbdisplay import at_values, show_difference, show_mult
from gacalc.standardposition import rotation_from_to
from gacalc.transforms import projection_rotation, versor_rotation

# %% [markdown]
# ## Two unit vectors
#
# $\hat{\mathbf{a}}$ at angle $\alpha$ from the x-axis:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = (
    Scalar(sympy.cos(alpha)) * Vector.e_1 + Scalar(sympy.sin(alpha)) * Vector.e_2
)
a_hat

# %% [markdown]
# and $\hat{\mathbf{b}}$ at angle $\beta$:

# %%
b_hat: Vector = (
    Scalar(sympy.cos(beta)) * Vector.e_1 + Scalar(sympy.sin(beta)) * Vector.e_2
)
b_hat

# %% [markdown]
# The values used to draw the first figure. Change them and rerun.

# %%
angle_values: list[tuple[sympy.Symbol, Real]] = [
    (alpha, sympy.pi / 6),
    (beta, sympy.pi / 2),
]

# %% [markdown]
# ## Their product
#
# A plain number plus a bivector, the dot and the wedge. The product term by term: the
# plain-number rows add to $\cos(\alpha) * \cos(\beta) + \sin(\alpha) * \sin(\beta)$,
# which is $\cos(\beta - \alpha)$, and the $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$
# rows to $\sin(\beta - \alpha)$: the angle-difference identities, from multiplying.

# %%
show_mult(a_hat, b_hat)

# %% [markdown]
# Before running the next cell, predict the sum: it is the full-angle rotor
# $\cos(\theta) + \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ with
# $\theta = \beta - \alpha$. We multiplied the vectors, and the cosine and sine
# appeared.

# %%
R: Versor = (a_hat * b_hat).simplified()
R

# %% [markdown]
# ## The rotor carries $\hat{\mathbf{a}}$ to $\hat{\mathbf{b}}$
#
# Multiply $\hat{\mathbf{a}}$ on the right by $\hat{\mathbf{a}} * \hat{\mathbf{b}}$. By
# associativity and $\hat{\mathbf{a}} * \hat{\mathbf{a}} = 1$ (a unit vector squares to
# one), the first vector cancels and $\hat{\mathbf{b}}$ is left:
# $\hat{\mathbf{a}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}}) = \hat{\mathbf{b}}$. No
# angle is named. $\hat{\mathbf{a}} * R$:

# %%
a_hat_rotated: MultiVectorBase = (a_hat * R).simplified()
a_hat_rotated

# %% [markdown]
# Its difference from $\hat{\mathbf{b}}$:

# %%
show_difference(a_hat * R, b_hat)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_HAT: Point = point(coordinates=list(at_values(a_hat, angle_values)))
P_B_HAT: Point = point(coordinates=list(at_values(b_hat, angle_values)))
fig_unit: PendingFigure
with scene_around(points=[P_A_HAT, P_B_HAT]) as fig_unit:
    arrow(head=P_A_HAT, color=BLACK, text=r"$\hat{\mathbf{a}}$")
    arrow(
        head=P_B_HAT,
        color=PURPLE,
        text=r"$\hat{\mathbf{a}} * R = \hat{\mathbf{b}}$",
        align=LabelPos.l,
    )
fig_unit

# %% [markdown]
# ## Vectors of any length
#
# Three routes build a rotation from two vectors alone, with no angle argument:
# `versor_rotation` (the versor sandwich $R * \vec{\mathbf{v}} * R^{-1}$),
# `projection_rotation` (projection, rejection and the geometric product), and
# `rotation_from_to` (the three turns of *Proof: Rotate from a to b*). They give the
# same rotation whatever the lengths of the inputs. Take $\vec{\mathbf{a}}$,
# $\vec{\mathbf{b}}$ and $\vec{\mathbf{v}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
v_1: sympy.Symbol
v_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2 = sympy.symbols("a_1 a_2 b_1 b_2 v_1 v_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
b

# %% [markdown]
# and $\vec{\mathbf{v}}$:

# %%
v: Vector = Scalar(v_1) * Vector.e_1 + Scalar(v_2) * Vector.e_2
v

# %% [markdown]
# The values used to draw the second figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 2),
    (a_2, 0),
    (b_1, 1),
    (b_2, 1),
    (v_1, 1),
    (v_2, 0),
]

# %% [markdown]
# The versor route on $\vec{\mathbf{v}}$:

# %%
rotated_versor: Vector = versor_rotation(from_vector=a, to_vector=b)(v).simplified()
rotated_versor

# %% [markdown]
# the projection route:

# %%
rotated_projection: MultiVectorBase = projection_rotation(from_vector=a, to_vector=b)(
    v
).simplified()
rotated_projection

# %% [markdown]
# and the three turns:

# %%
rotated_three_turns: Vector = rotation_from_to(a, b)(v).simplified()
rotated_three_turns

# %% [markdown]
# The versor and projection routes differ by:

# %%
(rotated_versor - rotated_projection).simplified()

# %% [markdown]
# and the versor route and the three turns by:

# %%
(rotated_versor - rotated_three_turns).simplified()

# %% [markdown]
# At the plot values, the rotated $\vec{\mathbf{v}}$:

# %%
at_values(rotated_versor, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_V: Point = point(coordinates=list(at_values(v, values)))
P_V_ROTATED: Point = point(coordinates=list(at_values(rotated_versor, values)))
fig_any_length: PendingFigure
with scene_around(points=[P_A, P_B, P_V, P_V_ROTATED]) as fig_any_length:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(
        head=P_V,
        color=BLACK,
        text=r"$\vec{\mathbf{v}}$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_V_ROTATED,
        color=PURPLE,
        text=r"$R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})$",
        offset=Point(x=-6, y=4),
        align=LabelPos.l,
    )
fig_any_length

# %% [markdown]
# ## It carries $\vec{\mathbf{a}}$ onto the direction of $\vec{\mathbf{b}}$
#
# Applied to $\vec{\mathbf{a}}$ itself, the rotation gives:

# %%
carried: MultiVectorBase = projection_rotation(from_vector=a, to_vector=b)(
    a
).simplified()
carried

# %% [markdown]
# $\vec{\mathbf{b}}$'s direction with $\vec{\mathbf{a}}$'s length,
# $(|\vec{\mathbf{a}}| / |\vec{\mathbf{b}}|) * \vec{\mathbf{b}}$ (the Lean
# `projRotation_carries_from_to`):

# %%
expected: Vector = (Scalar(a.magnitude() / b.magnitude()) * b).simplified()
expected

# %% [markdown]
# Their difference:

# %%
show_difference(carried, expected)

# %% [markdown]
# So the versor route, the projection route, and the angle-free three-turn
# construction of *Proof: Rotate from a to b* are one and the same rotation, a fact the
# Lean proofs state directly: the product route is `rotPlane_fromTo_eq_vec_mul`
# (`Bootstrap2D.lean`), the projection route is `projRotation_eq_vec_mul` and
# `projRotation_eq_sandwich` (`ProjectionRotation2D.lean`). The angle was
# scaffolding; the two vectors, multiplied, are the rotation.
