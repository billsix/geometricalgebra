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
# $\mathcal{G}_3$: areas and volumes
# ==================================
#
# In `displayg2areas.py` the size of the wedge of two vectors was the area of their
# parallelogram. Space adds one more step: the wedge of *three* vectors, whose size is
# the volume of the slanted box they span. This notebook names both measures, then
# checks that the sine formula for the area still holds when the wedge has three
# plane parts.

# %%
import warnings

import sympy

from gacalc.base import Real
from gacalc.g3 import G, Scalar, Vector
from gacalc.measure import area, signed_volume, volume
from gacalc.nbdisplay import show_difference

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# Areas in space
# --------------
#
# Two general vectors of space, $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$:

# %%
a_vec: G = G.symbolic_multivector(prefix="a").r_vector_part(1)
b_vec: G = G.symbolic_multivector(prefix="b").r_vector_part(1)
a_vec

# %% [markdown]
# The area of their parallelogram, $|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|$ (the
# general version in any dimension is the *content*, Williamson and Trotter, p. 308):

# %%
area(a_vec, b_vec)

# %% [markdown]
# An area has no direction, so swapping the sides changes nothing.

# %% [markdown]
# Why is there no signed area in space?
# -------------------------------------
#
# In the plane, `signed_area` gave a plus or minus sign for the turn from
# $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$. In space, two vectors span just one plane
# among many, so their orientation is the whole piece of plane
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$, not a single sign. A signed number needs
# vectors that fill the whole space: three of them, giving a signed *volume*.
# (`signed_area` exists only in 𝒢₂.) A third vector, $\vec{\mathbf{c}}$:

# %%
c_vec: G = G.symbolic_multivector(prefix="c").r_vector_part(1)
c_vec

# %% [markdown]
# The volume of the slanted box on the three vectors,
# $|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}|$. Simplified, it
# is the square root of a square: the size of the signed number in the next cell.

# %%
sympy.simplify(sympy.sympify(volume(a_vec, b_vec, c_vec)))

# %% [markdown]
# **A signed volume remembers the order.** `signed_volume` is the 3-by-3 determinant:

# %%
signed_volume(a_vec, b_vec, c_vec)

# %% [markdown]
# Swap the first two vectors and predict what happens before running the cell:

# %%
signed_volume(b_vec, a_vec, c_vec)

# %% [markdown]
# The two are negatives of each other, so their sum simplifies to $0$:

# %%
sympy.simplify(
    sympy.sympify(
        signed_volume(b_vec, a_vec, c_vec) + signed_volume(a_vec, b_vec, c_vec)
    )
)

# %% [markdown]
# Is the size of the wedge still a sine?
# --------------------------------------
#
# Two vectors in space always lie in one plane, so the plane's formula
# $|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}| = |\vec{\mathbf{a}}| *
# |\vec{\mathbf{b}}| * \sin(\theta)$ should still hold. What changes is that the
# wedge has three parts, so Lagrange's identity
# (<https://en.wikipedia.org/wiki/Lagrange%27s_identity>) becomes a sum of three
# squares:
#
# $$|\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|^2 - (\vec{\mathbf{a}} \cdot
# \vec{\mathbf{b}})^2 = (a_1 * b_2 - a_2 * b_1)^2 + (a_1 * b_3 - a_3 * b_1)^2 + (a_2 *
# b_3 - a_3 * b_2)^2 = |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|^2 .$$
#
# The vectors, with real symbols so that $\sqrt{x^2} = |x|$ behaves:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3", real=True)
a: Vector = (
    Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2 + Scalar(a_3) * Vector.e_3
)
b: Vector = (
    Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2 + Scalar(b_3) * Vector.e_3
)

# %% [markdown]
# Their dot product,

# %%
a.inner_product(b)

# %% [markdown]
# and their wedge, with its three plane parts:

# %%
a ^ b

# %% [markdown]
# Lagrange's identity, left side minus right side, simplified:

# %%
dot: Real = a.inner_product(b).scalar_part()
sympy.simplify(
    sympy.sympify(
        a.magnitude_squared() * b.magnitude_squared()
        - dot**2
        - (a ^ b).magnitude_squared()
    )
)

# %% [markdown]
# **From the squares to the sizes.** With $\cos(\theta) = \vec{\mathbf{a}} \cdot
# \vec{\mathbf{b}} / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$ and $\sin(\theta) =
# \sqrt{1 - \cos^2(\theta)}$, both sides are the square root of the same sum of three
# squares. The sine side,

# %%
cos: Real = a.cosine(b)
sin: Real = sympy.sqrt(1 - cos**2)
wedge_magnitude_from_sin: Real = a.magnitude() * b.magnitude() * sin
wedge_magnitude_from_sin

# %% [markdown]
# the size of the wedge,

# %%
(a ^ b).magnitude()

# %% [markdown]
# and their difference:

# %%
show_difference(wedge_magnitude_from_sin, (a ^ b).magnitude())

# %% [markdown]
# **The size of a product is the product of the sizes.** As in the plane, the dot and
# the wedge are different grades, so $|\vec{\mathbf{a}} * \vec{\mathbf{b}}|^2 =
# |\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|^2$. The product, a number plus three plane
# parts (a `g3.Versor`):

# %%
a * b

# %% [markdown]
# and the squared sizes, subtracted:

# %%
sympy.simplify(
    sympy.sympify(
        (a * b).magnitude_squared() - a.magnitude_squared() * b.magnitude_squared()
    )
)
