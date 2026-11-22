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
# $\mathcal{G}_2$: multiplying in the plane
# =========================================
#
# `displaymv.py` taught the rules of geometric multiplication with the general
# class `Gn`. This notebook runs the same rules in the plane with `g2.G`, a class
# written just for two dimensions. Its products are formulas generated from `Gn`,
# so they give the same answers, much faster.
#
# The plane has four building blocks: a plain number $1$, the two unit arrows
# $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$, and the piece of plane they span,
# $\mathbf{e}_{12} = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$. The companion notebooks
# take the same algebra further: `displayg2areas.py` (angles and areas) and
# `displayg2transforms.py` (moving the plane around).

# %%
import warnings

from IPython.display import Math, display

from gacalc.g2 import G
from gacalc.nbdisplay import show_difference, show_mult

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# Bare names for the full-G basis constants, so the code reads like the math.
# These are the FULL 𝒢₂ constants (e_1 here is G.e_1), not the graded Vector that
# `from gacalc.g2 import e_1` gives; every value in this notebook is a G.
e_1: G = G.e_1
e_2: G = G.e_2
e_12: G = G.e_12

# %% [markdown]
# What does a piece of plane square to?
# -------------------------------------
#
# Multiply the two arrows and you get the piece of plane between them:

# %%
i: G = e_1 * e_2
i

# %% [markdown]
# Now multiply that piece of plane by itself. By the rules of `displaymv.py`
# (swap the middle pair with a sign, then cancel each arrow against itself), predict
# the answer before running the cell:

# %%
i * i

# %% [markdown]
# It is $-1$, exactly like the imaginary number $i$. So the plain numbers together with
# $\mathbf{e}_{12}$ behave like the complex numbers. The class names that piece of plane
# `e_12`; it is the same value as the product $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$.

# %% [markdown]
# Sums collect like terms
# -----------------------
#
# Values in the plane add and scale like the expressions you already know:
# $2 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2 + 5 * \vec{\mathbf{e}}_1$ collects
# into $7 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$, just as $2x + 3y + 5x$ is
# $7x + 3y$.

# %%
2 * e_1 + 3 * e_2 + 5 * e_1

# %% [markdown]
# The plain numbers live in the same class. Zero,

# %%
G.from_real(0)

# %% [markdown]
# and one:

# %%
G.from_real(1)

# %% [markdown]
# Letters instead of numbers
# --------------------------
#
# Every coefficient can be a symbol, so one computation covers every value at once.
# `symbolic_multivector` builds a general element with a symbol on each of the four
# building blocks:

# %%
A_full: G = G.symbolic_multivector(prefix="a")
A_full

# %% [markdown]
# Keeping only the arrow part (`r_vector_part(1)`) gives a general vector
# $\vec{\mathbf{a}}$,

# %%
a_vec: G = G.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec

# %% [markdown]
# and a second one, $\vec{\mathbf{b}}$:

# %%
b_vec: G = G.symbolic_multivector(prefix="b").r_vector_part(1)
b_vec

# %% [markdown]
# What is the product of two vectors made of?
# -------------------------------------------
#
# Multiply them:

# %%
a_vec * b_vec

# %% [markdown]
# The answer has a plain-number part and a piece-of-plane part. The plain-number part
# is the dot product,

# %%
a_vec.dot(b_vec)

# %% [markdown]
# and the piece-of-plane part is the wedge, written `^` in code:

# %%
a_vec ^ b_vec

# %% [markdown]
# So $\vec{\mathbf{a}} * \vec{\mathbf{b}} = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} +
# \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$. Both sides, then their difference, which
# is $0$:

# %%
show_difference(a_vec.dot(b_vec) + a_vec.wedge(b_vec), a_vec * b_vec)

# %% [markdown]
# Every term times every term
# ---------------------------
#
# The product of two general elements is the multiply-everything-by-everything grid
# from `displaymv.py`: four terms times four terms, sixteen rows, then the sum.

# %%
G2_1: G = G.symbolic_multivector(prefix="a")
G2_2: G = G.symbolic_multivector(prefix="b")
show_mult(G2_1, G2_2)

# %% [markdown]
# Does grouping matter? No
# ------------------------
#
# Take a third general element. Multiplying the first two first, or the last two
# first, gives the same answer: that is associativity. `displaymv.py` lays the two
# answers out term by term and matches every term of one with a partner in the other,
# and because every coefficient is a symbol, that proves it for **every** three
# elements.

# %% [markdown]
# Pulling out one kind of part
# ----------------------------
#
# `r_vector_part(r)` keeps only the parts of one *grade*: grade 0 is the plain
# number, grade 1 the arrows, grade 2 the piece of plane. A general element,

# %%
C: G = G.symbolic_multivector(prefix="c")
C

# %% [markdown]
# its plain-number part,

# %%
C.r_vector_part(0)

# %% [markdown]
# its arrow part,

# %%
C.r_vector_part(1)

# %% [markdown]
# and its piece-of-plane part:

# %%
C.r_vector_part(2)

# %% [markdown]
# All four building blocks, in grade order:

# %%
x: G
for x in G.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Length, inverse, reverse and dual
# ---------------------------------
#
# A vector times itself is its length squared (the Pythagorean theorem from
# `displaymv.py`). Take $\vec{\mathbf{m}} = 3 * \vec{\mathbf{e}}_1 + 4 *
# \vec{\mathbf{e}}_2$ and predict its length:

# %%
m: G = 3 * e_1 + 4 * e_2
m.magnitude()

# %% [markdown]
# Its square is the length squared, a plain number:

# %%
m * m

# %% [markdown]
# Dividing by the length gives the unit vector $\hat{\mathbf{m}}$, pointing the same
# way with length $1$:

# %%
m.normalize()

# %% [markdown]
# Because $\vec{\mathbf{m}} * \vec{\mathbf{m}}$ is a plain number, a vector has an
# inverse: itself divided by its length squared,

# %%
m.inverse()

# %% [markdown]
# and a vector times its inverse is $1$, so their product minus $1$ is $0$:

# %%
m * m.inverse() - G.from_real(1)

# %% [markdown]
# The *reverse* writes each product of arrows in the opposite order. For the piece of
# plane that is one swap, so it flips the sign:

# %%
i.reverse()

# %% [markdown]
# The *dual* multiplies by the inverse of $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$. In
# the plane that turns a vector a quarter turn:

# %%
m.dual()

# %% [markdown]
# An aside: units as arrows
# -------------------------
#
# As in `displaymv.py`, the arrows can carry units: let $\vec{\mathbf{e}}_1$ be one
# gram of iron and $\vec{\mathbf{e}}_2$ one mole. The conversion "1 mole per 55.85
# grams" is $(55.85 * \vec{\mathbf{e}}_1)^{-1} * \vec{\mathbf{e}}_2$, and multiplying
# a mass by it cancels the grams by Rule 1, as units cancel in chemistry.


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> G:
    unit_gram_fe: G = e_1
    unit_mol_fe: G = e_2

    ratio: G = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)
