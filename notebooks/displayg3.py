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
# $\mathcal{G}_3$: multiplying in space
# =====================================
#
# `displayg2.py` ran the multiplication rules in the plane. This notebook adds a third
# arrow, $\vec{\mathbf{e}}_3$, and runs them in space with `g3.G`, the class written
# for three dimensions. Nothing in the rules changes; there are just more pieces.
#
# Space has eight building blocks: a plain number $1$; three arrows
# $\vec{\mathbf{e}}_1, \vec{\mathbf{e}}_2, \vec{\mathbf{e}}_3$; three pieces of plane
# $\mathbf{e}_{12}, \mathbf{e}_{13}, \mathbf{e}_{23}$, one for each pair of arrows; and
# one piece of space, $\mathbf{e}_{123} = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 *
# \vec{\mathbf{e}}_3$. The companion `displayg3measures.py` turns the wedges into
# areas and volumes.

# %%
import warnings

from IPython.display import Math, display

from gacalc.base import MultiVectorBase
from gacalc.g3 import G
from gacalc.nbdisplay import show_difference, show_mult
from gacalc.nbplotutils import plot_multivector

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# Bare names for the full-G basis constants, so the code reads like the math.
# These are the FULL 𝒢₃ constants (e_1 here is G.e_1), not the graded Vector that
# `from gacalc.g3 import e_1` gives; every value in this notebook is a G.
e_1: G = G.e_1
e_2: G = G.e_2
e_3: G = G.e_3
e_12: G = G.e_12
e_13: G = G.e_13
e_23: G = G.e_23
e_123: G = G.e_123

# %% [markdown]
# What does the piece of space square to?
# ---------------------------------------
#
# Multiply all three arrows:

# %%
pseudoscalar: G = e_1 * e_2 * e_3
pseudoscalar

# %% [markdown]
# Squaring it means sorting six arrows with a sign and cancelling pairs. Predict the
# answer before running the cell:

# %%
pseudoscalar * pseudoscalar

# %% [markdown]
# It is $-1$, like the plane's $\mathbf{e}_{12}$ in `displayg2.py`. The class names it
# `e_123`, the same value as the product of the three arrows.

# %% [markdown]
# The three pieces of plane, one per pair of arrows. The $\vec{\mathbf{e}}_1
# \vec{\mathbf{e}}_2$ plane,

# %%
e_12

# %% [markdown]
# the $\vec{\mathbf{e}}_1 \vec{\mathbf{e}}_3$ plane,

# %%
e_13

# %% [markdown]
# and the $\vec{\mathbf{e}}_2 \vec{\mathbf{e}}_3$ plane:

# %%
e_23

# %% [markdown]
# Sums collect like terms
# -----------------------
#
# $2 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2 + 4 * \vec{\mathbf{e}}_3 + 5 *
# \vec{\mathbf{e}}_1$ collects into $7 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2 +
# 4 * \vec{\mathbf{e}}_3$:

# %%
2 * e_1 + 3 * e_2 + 4 * e_3 + 5 * e_1

# %% [markdown]
# Zero and one are in the class too. Zero,

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
# A general element, a symbol on each of the eight building blocks:

# %%
A_full: G = G.symbolic_multivector(prefix="a")
A_full

# %% [markdown]
# Its arrow part is a general vector $\vec{\mathbf{a}}$,

# %%
a_vec: G = G.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec

# %% [markdown]
# and a second one is $\vec{\mathbf{b}}$:

# %%
b_vec: G = G.symbolic_multivector(prefix="b").r_vector_part(1)
b_vec

# %% [markdown]
# What is the product of two vectors in space made of?
# ----------------------------------------------------
#
# The same two parts as in the plane: a plain number and pieces of plane. But now
# there are three planes for the wedge to have parts in.

# %%
a_vec * b_vec

# %% [markdown]
# The plain-number part is the dot product,

# %%
a_vec.dot(b_vec)

# %% [markdown]
# and the plane parts are the wedge, one coefficient for each pair of arrows:

# %%
a_vec ^ b_vec

# %% [markdown]
# The dot plus the wedge, minus the product, is $0$:

# %%
a_vec.dot(b_vec) + a_vec.wedge(b_vec) - a_vec * b_vec

# %% [markdown]
# Every term times every term
# ---------------------------
#
# Two general elements of space: eight terms times eight terms, sixty-four rows. The
# table shows that the method scales; reading one row is the same check as in the
# plane.

# %%
G3_1: G = G.symbolic_multivector(prefix="a")
G3_2: G = G.symbolic_multivector(prefix="b")
show_mult(G3_1, G3_2)

# %% [markdown]
# Does grouping matter?
# ---------------------
#
# Multiply three general elements both ways and subtract. Every coefficient is a
# symbol, so a zero difference proves the product is associative for every three
# elements of space. (`displayg2.py` lays the same proof out term by term in the plane;
# in space each blade has sixty-four terms a side, too many to read.)

# %%
G3_3: G = G.symbolic_multivector(prefix="c")
show_difference((G3_1 * G3_2) * G3_3, G3_1 * (G3_2 * G3_3))

# %% [markdown]
# Pulling out one kind of part
# ----------------------------
#
# Space has four grades: plain number (0), arrows (1), pieces of plane (2) and the
# piece of space (3). A general element,

# %%
C: G = G.symbolic_multivector(prefix="c")
C

# %% [markdown]
# its plain-number part,

# %%
C.r_vector_part(0)

# %% [markdown]
# its arrows,

# %%
C.r_vector_part(1)

# %% [markdown]
# its pieces of plane,

# %%
C.r_vector_part(2)

# %% [markdown]
# and its piece of space:

# %%
C.r_vector_part(3)

# %% [markdown]
# All eight building blocks, in grade order:

# %%
x: G
for x in G.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Which arrow stands straight out of a plane?
# -------------------------------------------
#
# The *dual* multiplies by the inverse of the piece of space. In space it turns a
# piece of plane into the arrow perpendicular to it: the geometric-algebra version of
# the cross product. The wedge of $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$,

# %%
B: G = a_vec ^ b_vec
B

# %% [markdown]
# and its dual, an arrow pointing the way $\vec{\mathbf{a}} \times \vec{\mathbf{b}}$
# does:

# %%
B.dual()

# %% [markdown]
# A plane times its own dual is a piece of space,

# %%
B * B.dual()

# %% [markdown]
# and a plane times itself is a plain number, negative, like
# $(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -1$:

# %%
B * B

# %% [markdown]
# Length, inverse, reverse and dual of a vector
# ---------------------------------------------
#
# Take $\vec{\mathbf{m}} = 1 * \vec{\mathbf{e}}_1 + 2 * \vec{\mathbf{e}}_2 + 2 *
# \vec{\mathbf{e}}_3$. Predict its length from $1 + 4 + 4$:

# %%
m: G = 1 * e_1 + 2 * e_2 + 2 * e_3
m.magnitude()

# %% [markdown]
# Its square is the length squared,

# %%
m * m

# %% [markdown]
# its unit vector $\hat{\mathbf{m}}$ has length $1$,

# %%
m.normalize()

# %% [markdown]
# and its inverse is itself over its length squared:

# %%
m.inverse()

# %% [markdown]
# A vector times its inverse, minus $1$, is $0$:

# %%
m * m.inverse() - G.from_real(1)

# %% [markdown]
# The reverse writes $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$
# backwards, which takes three swaps, so it flips the sign:

# %%
pseudoscalar.reverse()

# %% [markdown]
# The dual of a vector is the piece of plane perpendicular to it:

# %%
m.dual()

# %% [markdown]
# Which part of $\vec{\mathbf{b}}$ makes the dot, and which the wedge?
# --------------------------------------------------------------------
#
# `displayg2areas.py` split the product in the plane. The split works in space too. Cut
# $\vec{\mathbf{b}}$ against $\vec{\mathbf{a}}$ into the part along $\vec{\mathbf{a}}$
# (its projection, $\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$) and the
# part perpendicular to it (its rejection,
# $\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$). Multiplied by
# $\vec{\mathbf{a}}$ on the left, each part makes exactly one half of the product:
#
# $$\vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) =
# \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} \qquad\qquad \vec{\mathbf{a}} *
# \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) = \vec{\mathbf{a}} \wedge
# \vec{\mathbf{b}}$$
#
# The proof is in `tasks/reference/dot-wedge-projection-rejection.md`; the Lean
# theorems are `G3.mul_proj_eq_dot` and `G3.mul_eq_proj_dot_add_reject_wedge`. Take
# $\vec{\mathbf{a}} = 1 * \vec{\mathbf{e}}_1 + 2 * \vec{\mathbf{e}}_2 + 2 *
# \vec{\mathbf{e}}_3$,

# %%
# twin: GacalcProofs.G3.mul_proj_eq_dot
# twin: GacalcProofs.G3.mul_eq_proj_dot_add_reject_wedge
a_num: G = 1 * e_1 + 2 * e_2 + 2 * e_3
a_num

# %% [markdown]
# and a $\vec{\mathbf{b}}$ that leans on no axis or plane:

# %%
b_num: G = 2 * e_1 + 1 * e_2 + 3 * e_3
b_num

# %% [markdown]
# The projection is a multiple of $\vec{\mathbf{a}}$,

# %%
b_par: MultiVectorBase = b_num.projected_onto(a_num)
b_par

# %% [markdown]
# the rejection is the rest,

# %%
b_perp: MultiVectorBase = b_num.rejected_away_from(a_num)
b_perp

# %% [markdown]
# and the two add back up to $\vec{\mathbf{b}}$ (their sum minus $\vec{\mathbf{b}}$ is
# $0$):

# %%
b_par + b_perp - b_num

# %% [markdown]
# **$\vec{\mathbf{a}}$ times the projection is the dot product.** Predict the answer
# from $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = 1 * 2 + 2 * 1 + 2 * 3$, then run:

# %%
a_num * b_par

# %% [markdown]
# The dot product itself:

# %%
a_num.dot(b_num)

# %% [markdown]
# Term by term, the plane contributions cancel and leave only the number:

# %%
show_mult(a_num, b_par)

# %% [markdown]
# **$\vec{\mathbf{a}}$ times the rejection is the wedge.** In space the wedge has a part
# in each of the three coordinate planes:

# %%
a_num * b_perp

# %% [markdown]
# The wedge itself:

# %%
a_num.wedge(b_num)

# %% [markdown]
# Here the number contributions cancel, leaving only the pieces of plane:

# %%
show_mult(a_num, b_perp)

# %% [markdown]
# **Putting it back together.** The two products add up to the whole product. Their sum
# minus $\vec{\mathbf{a}} * \vec{\mathbf{b}}$:

# %%
a_num * b_par + a_num * b_perp - a_num * b_num

# %% [markdown]
# Each part on its own number line
# --------------------------------
#
# `plot_multivector` draws each building block's coefficient on its own number line.
# An element with a number, three arrows and one plane part,

# %%
plot_multivector(2 * G.from_real(1) + 3 * e_1 - 1.5 * e_2 + 4 * e_3 + 0.7 * (e_1 * e_2))

# %% [markdown]
# a vector,

# %%
u: G = 3 * e_1 - 1.5 * e_2 + 2 * e_3
plot_multivector(u)

# %% [markdown]
# a second vector,

# %%
v: G = 1.5 * e_1 + 5 * e_2 - 1 * e_3
plot_multivector(v)

# %% [markdown]
# and their product, a number and three plane parts:

# %%
plot_multivector(u * v)
