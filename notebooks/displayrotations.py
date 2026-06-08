# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: gacalc
#     language: python
#     name: gacalc
# ---

# %%

# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# %% [markdown]
# Rotations two ways: the rotor sandwich vs the projection formula
# ================================================================
#
# A rotation can be written two equivalent ways in geometric algebra:
#
# * the **rotor sandwich**  $R\,v\,R^{-1}$, where $R$ is the rotor that carries
#   one vector toward another, and
# * the **projection formula** (`AbstractMultiVector.rotate`): turn the part of
#   $v$ that lies in the plane of rotation, and leave the perpendicular part fixed.
#
# This notebook shows that the two agree -- *symbolically*, for an arbitrary
# vector $v$ and an arbitrary angle $\theta$ -- in $\mathcal{G}_2$ and
# $\mathcal{G}_3$, using the general `Gn` representation.

# %%
import sympy

from gacalc.gn import Gn, e_1, e_2, e_3
from gacalc.nbplotutils import show_mult


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
a = e_1
b = sympy.cos(theta) * e_1 + sympy.sin(theta) * e_2

# %% [markdown]
# $\mathcal{G}_2$ -- the plane
# ----------------------------
#
# A symbolic vector $v = v_1 e_1 + v_2 e_2$.

# %%
v1, v2 = sympy.symbols("v1 v2", real=True)
v_2d = v1 * e_1 + v2 * e_2

R = Gn.rotor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The rotor sandwich $R\,v\,R^{-1}$ (simplified for display):

# %%
sandwich_2d = R * v_2d * R.inverse()
simplified(sandwich_2d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The projection formula `Gn.rotate(from, to)` applied to the same $v$:

# %%
projection_2d = Gn.rotate(from_vector=a, to_vector=b)(v_2d)
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
v_3d = v1 * e_1 + v2 * e_2 + v3 * e_3

R3 = Gn.rotor_from_vectors(from_vector=a, to_vector=b)

# %% [markdown]
# The rotor sandwich (note the $e_3$ part rides through unchanged):

# %%
sandwich_3d = R3 * v_3d * R3.inverse()
simplified(sandwich_3d)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The projection formula on the same $v$:

# %%
projection_3d = Gn.rotate(from_vector=a, to_vector=b)(v_3d)
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
