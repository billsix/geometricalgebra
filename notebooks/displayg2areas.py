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
# $\mathcal{G}_2$: angles and areas
# =================================
#
# `displayg2.py` split the product of two vectors into a plain-number part, the dot
# product, and a piece-of-plane part, the wedge. This notebook asks what the two
# parts *measure*. The dot product measures how much two vectors point the same way,
# $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|
# * \cos(\theta)$. The size of the wedge turns out to be the matching sine formula,
# and that is the area of a parallelogram.

# %%
import warnings

import sympy

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector
from gacalc.measure import area, signed_area
from gacalc.nbdisplay import show_mult

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# Is the size of the wedge a sine?
# --------------------------------
#
# Take two general vectors of the plane,
# $\vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2$ and
# $\vec{\mathbf{b}} = b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2$. The symbols
# are declared *real*, so that $\sqrt{x^2} = |x|$ behaves.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2

# %% [markdown]
# Their dot product is a plain number,

# %%
a.inner_product(b)

# %% [markdown]
# and their wedge is a piece of plane:

# %%
a ^ b

# %% [markdown]
# **Lagrange's identity.** Because $\cos^2(\theta) + \sin^2(\theta) = 1$,
#
# $$|\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|^2 = |\vec{\mathbf{a}}|^2 *
# |\vec{\mathbf{b}}|^2 * (\cos^2(\theta) + \sin^2(\theta)).$$
#
# The cosine half of the right side is $(\vec{\mathbf{a}} \cdot \vec{\mathbf{b}})^2$.
# If the wedge is the sine half, then
#
# $$|\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|^2 - (\vec{\mathbf{a}} \cdot
# \vec{\mathbf{b}})^2 = |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|^2 .$$
#
# (This is Lagrange's identity, <https://en.wikipedia.org/wiki/Lagrange%27s_identity>.)
# The left side minus the right side, simplified:

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
# It is $0$ for every pair of vectors.
#
# **From the squares to the sizes.** Write
# $\cos(\theta) = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} / (|\vec{\mathbf{a}}| *
# |\vec{\mathbf{b}}|)$ and $\sin(\theta) = \sqrt{1 - \cos^2(\theta)}$, which is never
# negative for an angle $\theta$ between $0$ and $\pi$. Then
# $|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| * \sin(\theta)$ is a square root of a sum.
# Factoring what is under the root exposes a perfect square, $(a_1 * b_2 - a_2 *
# b_1)^2$, whose root is the size of the wedge:

# %%
cos: Real = a.cosine(b)
sin: Real = sympy.sqrt(1 - cos**2)
wedge_magnitude_from_sin: Real = sympy.sqrt(
    sympy.factor(
        sympy.simplify(sympy.sympify((a.magnitude() * b.magnitude() * sin) ** 2))
    )
)
wedge_magnitude_from_sin

# %% [markdown]
# The size of the wedge, computed directly:

# %%
(a ^ b).magnitude()

# %% [markdown]
# The two sides, subtracted:

# %%
sympy.simplify(sympy.sympify(wedge_magnitude_from_sin - (a ^ b).magnitude()))

# %% [markdown]
# So $|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}| = |\vec{\mathbf{a}}| *
# |\vec{\mathbf{b}}| * \sin(\theta)$.
#
# **What it buys.** The dot and the wedge are different grades, so their squares
# add: $|\vec{\mathbf{a}} * \vec{\mathbf{b}}|^2 = (\vec{\mathbf{a}} \cdot
# \vec{\mathbf{b}})^2 + |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|^2 =
# |\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|^2$. The size of a product of two vectors
# is the product of their sizes. The product itself,

# %%
a * b

# %% [markdown]
# and $|\vec{\mathbf{a}} * \vec{\mathbf{b}}|^2 - |\vec{\mathbf{a}}|^2 *
# |\vec{\mathbf{b}}|^2$, simplified:

# %%
sympy.simplify(
    sympy.sympify(
        (a * b).magnitude_squared() - a.magnitude_squared() * b.magnitude_squared()
    )
)

# %% [markdown]
# The size of the wedge is an area
# --------------------------------
#
# $|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| * \sin(\theta)$ is the area of the
# parallelogram the two vectors span: the base times the height. `measure.area` names
# it (Williamson and Trotter call the higher-dimensional version the *content*):

# %%
area(a, b)

# %% [markdown]
# An area has no direction, so the order of the sides should not matter. Predict
# `area(b, a)` before running it:

# %%
area(b, a)

# %% [markdown]
# The two orders, subtracted:

# %%
area(a, b) - area(b, a)

# %% [markdown]
# **A signed area remembers the order.** `signed_area` is the 2-D determinant
# $a_1 * b_2 - a_2 * b_1$: positive when $\vec{\mathbf{b}}$ is a counterclockwise turn
# from $\vec{\mathbf{a}}$, negative when it is clockwise.

# %%
signed_area(a, b)

# %% [markdown]
# Swapping the two vectors flips its sign:

# %%
signed_area(b, a)

# %% [markdown]
# so `signed_area(b, a) + signed_area(a, b)` is $0$,

# %%
signed_area(b, a) + signed_area(a, b)

# %% [markdown]
# and the unsigned area is its absolute value; their difference is $0$:

# %%
area(a, b) - abs(signed_area(a, b))

# %% [markdown]
# Which part of $\vec{\mathbf{a}}$ makes the dot, and which the wedge?
# ---------------------------------------------------------------------
#
# Split $\vec{\mathbf{a}}$ against $\vec{\mathbf{b}}$ into the part along
# $\vec{\mathbf{b}}$ (its projection, $\vec{\mathbf{a}}_\parallel$) and the part
# perpendicular to it (its rejection, $\vec{\mathbf{a}}_\perp$). Then each part makes
# exactly one half of the product:
#
# $$\vec{\mathbf{a}}_\parallel * \vec{\mathbf{b}} = \vec{\mathbf{a}} \cdot
# \vec{\mathbf{b}} \qquad\qquad \vec{\mathbf{a}}_\perp * \vec{\mathbf{b}} =
# \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$$
#
# The parallel part spans no area with $\vec{\mathbf{b}}$, so its wedge is zero; the
# perpendicular part has no dot product with it. Numbers make this easy to check by
# hand. The proof is in `tasks/reference/dot-wedge-projection-rejection.md`.
# Take $\vec{\mathbf{a}} = 2 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$,

# %%
a_num: Vector = 2 * Vector.e_1 + 3 * Vector.e_2
a_num

# %% [markdown]
# and a $\vec{\mathbf{b}}$ along the diagonal, so the split does not lean on an axis:

# %%
b_num: Vector = 1 * Vector.e_1 + 1 * Vector.e_2
b_num

# %% [markdown]
# The projection has fractions in it,

# %%
a_par: Vector = Vector.project(onto=b_num)(a_num)
a_par

# %% [markdown]
# so does the rejection,

# %%
a_perp: Vector = Vector.reject(away_from=b_num)(a_num)
a_perp

# %% [markdown]
# and the two add back up to $\vec{\mathbf{a}}$ (their sum minus $\vec{\mathbf{a}}$ is
# $0$):

# %%
a_par + a_perp - a_num

# %% [markdown]
# **The projection times $\vec{\mathbf{b}}$ is the dot product.** Predict the answer
# from $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = 2 * 1 + 3 * 1$, then run:

# %%
a_par * b_num

# %% [markdown]
# The dot product itself:

# %%
a_num.dot(b_num)

# %% [markdown]
# Term by term, the two piece-of-plane contributions cancel and leave only the
# number:

# %%
show_mult(a_par, b_num)

# %% [markdown]
# **The rejection times $\vec{\mathbf{b}}$ is the wedge.**

# %%
a_perp * b_num

# %% [markdown]
# The wedge itself:

# %%
a_num.wedge(b_num)

# %% [markdown]
# Here the two number contributions cancel, leaving only the piece of plane:

# %%
show_mult(a_perp, b_num)

# %% [markdown]
# **Putting it back together.** The two products add up to the whole product, so the
# along-and-across split of $\vec{\mathbf{a}}$ *is* the number-and-plane split of
# $\vec{\mathbf{a}} * \vec{\mathbf{b}}$. Their sum minus the product:

# %%
a_par * b_num + a_perp * b_num - a_num * b_num
