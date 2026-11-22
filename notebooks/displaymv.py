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


# %%
import warnings

import sympy
from IPython.display import Math, display
from matplotlib.figure import Figure

from gacalc.base import MultiVectorBase, MultiVectorFn, Real
from gacalc.gn import (
    MultiVector,
    a_1,
    e_1,
    e_2,
    e_3,
    e_4,
    one,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
)
from gacalc.nbdisplay import at_values, show_cancellation, show_difference, show_mult
from gacalc.nbplotutils import plot_multivector

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# How multiplication works in G_n
# ===============================
#
# You already know how to multiply things like $(x + 2)(x + 3)$: you multiply
# everything by everything and add up the pieces. Multiplying in geometric algebra is
# the *same* idea, with just a couple of new rules for the "letters".
#
# Our letters are the **basis vectors**
# $\vec{\mathbf{e}}_1, \vec{\mathbf{e}}_2, \vec{\mathbf{e}}_3, \ldots$ Think of them as
# the arrows pointing along the x-axis, the y-axis, the z-axis, and so on. A general
# object (a *multivector*) is any sum of these, with numbers out front, for example
# $3 * \vec{\mathbf{e}}_1 + 4 * \vec{\mathbf{e}}_2$. To multiply two multivectors you
# multiply every term by every term and then clean up using **three rules**.
#
# **Rule 1: an arrow times itself is 1.** $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 = 1$,
# $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 = 1$, and so on. Squaring a unit arrow gives
# the plain number 1. Before running the next cell, predict its result.

# %%
e_1 * e_1

# %% [markdown]
# **Rule 2: swapping two *different* arrows flips the sign.**
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = -(\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1)$.
# So order matters here, unlike with ordinary numbers, where $3 * 5 = 5 * 3$. The combo
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ is a brand-new object, a little piece of the
# $\vec{\mathbf{e}}_1 \vec{\mathbf{e}}_2$ *plane*, written $\mathbf{e}_{12}$. We cannot
# simplify it to a number, but we can always reorder it at the cost of a minus sign.

# %%
e_1 * e_2

# %% [markdown]
# The same two arrows in the other order: the same plane piece, with the opposite sign.

# %%
e_2 * e_1

# %% [markdown]
# **Rule 3: distribute and collect, and numbers slide freely.** Ordinary numbers (the
# coefficients out front) multiply and move around as usual; you distribute the product
# across every term and add up like terms. For example
# $2 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2 + 5 * \vec{\mathbf{e}}_1$ collects
# into $7 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2$, exactly like combining
# $2x + 3y + 5x$.

# %%
2 * e_1 + 3 * e_2 + 5 * e_1

# %% [markdown]
# Putting the rules together
# --------------------------
#
# Any product, no matter how messy, reduces to a tidy standard form by (a) multiplying
# every term by every term, (b) using Rule 2 to sort the arrows into increasing order
# ($\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1$ becomes
# $-\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$), and (c) using Rule 1 to cancel any arrow
# that meets itself.
#
# Two payoffs worth seeing.
#
# **A vector times itself gives its length squared: that's the Pythagorean theorem.**
# Watch the cross terms cancel by Rule 2 and the squares collapse by Rule 1:
#
# $$
# \begin{aligned} (3 * \vec{\mathbf{e}}_1 + 4 * \vec{\mathbf{e}}_2) * (3 *
# \vec{\mathbf{e}}_1 + 4 * \vec{\mathbf{e}}_2) &= 9 * (\vec{\mathbf{e}}_1 *
# \vec{\mathbf{e}}_1) + 12 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) + 12 *
# (\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1) + 16 * (\vec{\mathbf{e}}_2 *
# \vec{\mathbf{e}}_2) \\ &= 9 * 1 + 12 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 - 12 *
# (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) + 16 * 1 \\ &= 25 \end{aligned}
# $$
#
# and $25 = 3^2 + 4^2$, the length squared.

# %%
v: MultiVector = 3 * e_1 + 4 * e_2
v * v

# %% [markdown]
# The same product, term by term:

# %%
show_mult(v, v)

# %% [markdown]
# **The unit plane $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ squares to $-1$, just like
# the imaginary number $i$.** The geometric algebra of the plane contains the complex
# numbers. Predict the result before running the cell.

# %%
i: MultiVector = e_1 * e_2
i * i

# %% [markdown]
# The same rules, written as math
# -------------------------------
#
# *(A little more formal: the same rules, stated the way a math class would put them.
# Skip it if you like; nothing later depends on it.)*
#
# The entire geometric product is pinned down by **two identities about the basis
# vectors**, together with the ordinary algebra you already trust: it distributes over
# $+$, it is associative, and plain numbers factor out freely.
#
# > $\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1$: each basis vector squares to $1$.
# **(R1)** > >
# $\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i$
# for $i \neq j$: swapping two *different* ones flips the > sign.  **(R2)**
#
# Everything else is bookkeeping. Any product of basis vectors
# $\vec{\mathbf{e}}_{i_1} * \vec{\mathbf{e}}_{i_2} * \cdots * \vec{\mathbf{e}}_{i_k}$ is
# brought to **standard form** (indices in increasing order, no repeats) using just two
# moves:
#
# 1. **Sort, with a sign.** By (R2), slide a smaller index to the left past a larger
#    neighbor; each swap of two neighbors multiplies the whole term by $-1$. It is
#    ordinary sorting, except every swap costs a factor of $-1$.
# 2. **Cancel repeats.** By (R1), whenever two equal indices end up next to each other,
#    erase the pair.
#
# A worked example is then just a chain of equalities:
#
# $$
# \begin{aligned} \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 *
# \vec{\mathbf{e}}_1 &= \vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3) *
# \vec{\mathbf{e}}_1 && \text{regroup (associativity)} \\ &= \vec{\mathbf{e}}_1 * 1 *
# \vec{\mathbf{e}}_1 && \text{(R1) on the middle pair} \\ &= \vec{\mathbf{e}}_1 *
# \vec{\mathbf{e}}_1 \\ &= 1 && \text{(R1) again} \end{aligned}
# $$
#
# and one that only sorts, with nothing to cancel:
#
# $$\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \qquad \text{one swap of } \vec{\mathbf{e}}_2 \text{ past }
# \vec{\mathbf{e}}_1 \text{, by (R2)}$$
#
# These two moves, sort with a sign and then cancel repeats, are exactly what `Gn`'s
# geometric product carries out: in the code, the recursive `decrease_grade` helper in
# `src/gacalc/gn.py`.

# %% [markdown]
# Where do the plain numbers go? Scalars first.
# ---------------------------------------------
#
# So far every factor was a bare basis vector like $\vec{\mathbf{e}}_1$. In real life a
# term also has a **number** out front: $3 * \vec{\mathbf{e}}_1$,
# $-2 * \vec{\mathbf{e}}_2$, and so on. Where do those numbers go when we multiply?
#
# The happy answer: **numbers are ordinary numbers.** They commute with everything
# ($3 * \vec{\mathbf{e}}_1 = \vec{\mathbf{e}}_1 * 3$) and they multiply among themselves
# the usual way. So the recipe grows just one opening step:
#
# 1. **Scalars first.** Sweep every numeric factor to the front and multiply them
#    together into a single number.
# 2. Then reduce the leftover string of basis vectors exactly as before: sort with a
#    sign (R2), cancel repeats (R1).
#
# For instance, gather the four numbers up front, then reuse the reduction we just did
# ($\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1 = 1$):
#
# $$
# \begin{aligned} (2 * \vec{\mathbf{e}}_1) * (3 * \vec{\mathbf{e}}_3) * (4 *
# \vec{\mathbf{e}}_3) * (5 * \vec{\mathbf{e}}_1) &= (2 * 3 * 4 * 5) *
# (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1) &&
# \text{scalars to the front} \\ &= 120 * 1 && \text{reduce the basis vectors} \\ &= 120
# \end{aligned}
# $$

# %%
(2 * e_1) * (3 * e_3) * (4 * e_3) * (5 * e_1)

# %% [markdown]
# The scalars ride along untouched by the sign-flipping; only the basis vectors produce
# minus signs. A shorter one where the arrows *do* create a sign:
#
# $$
# \begin{aligned}
# (2 * \vec{\mathbf{e}}_2) * (3 * \vec{\mathbf{e}}_1)
#   &= 6 * (\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1) && \text{scalars to the front} \\
#   &= 6 * (-\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) && \text{one swap, by (R2)} \\
#   &= -6 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2
# \end{aligned}
# $$

# %%
(2 * e_2) * (3 * e_1)

# %% [markdown]
# A longer example, and why grouping is about to matter
# -----------------------------------------------------
#
# Let's do a messier one and reduce it by hand with the three rules:
# $(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3) * (\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1)$.
#
# Written out, that's the four arrows
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1$ in
# a row. Nothing here is a plain number yet, so we lean on the rules. The trick is to
# notice the two $\vec{\mathbf{e}}_3$'s sitting next to each other in the middle:
#
# $$
# \begin{aligned} \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 *
# \vec{\mathbf{e}}_1 &= \vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3) *
# \vec{\mathbf{e}}_1 && \text{group the middle pair} \\ &= \vec{\mathbf{e}}_1 * 1 *
# \vec{\mathbf{e}}_1 && \text{Rule 1: } \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 = 1 \\
# &= \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 \\ &= 1 && \text{Rule 1 again}
# \end{aligned}
# $$
#
# So the whole four-arrow product collapses to the number $1$.

# %%
(e_1 * e_3) * (e_3 * e_1)

# %% [markdown]
# But wait: reducing that by hand, we quietly *re-grouped* the arrows. The original was
# $(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3) * (\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1)$,
# yet we chose to first multiply the middle $\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3$.
# Were we *allowed* to do that? What if we had grouped it a different way? Would we
# still get $1$?
#
# Here are three different ways of parenthesizing the same four arrows
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1$.
# Predict each before running it. Left to right:

# %%
((e_1 * e_3) * e_3) * e_1

# %% [markdown]
# Right to left:

# %%
e_1 * (e_3 * (e_3 * e_1))

# %% [markdown]
# Middle pair first, what we did by hand:

# %%
e_1 * ((e_3 * e_3) * e_1)

# %% [markdown]
# They all agree. That is **associativity**: for a product of several things, *how you
# parenthesize does not change the answer*, so we can safely write
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1$
# with no parentheses at all. We relied on it the moment we chose to reduce the middle
# pair first, and we'll rely on it constantly from here on.
#
# It is worth pausing on *why* this is not obvious. Remember Rule 2: order is **not**
# free here ($\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3$ is the *negative* of
# $\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1$). When even the order of two things flips
# the sign, it is a fair question whether the *grouping* of many things might change the
# answer too. It doesn't, but that is something to *prove* from the rules, not take on
# faith. The section "Associativity in 𝒢₂, as a proof" below proves it for every pair of
# elements of the plane; the proof for every dimension is
# `tasks/reference/geometric-product-associativity.md`.

# %% [markdown]
# Dot and wedge of two vectors
# ----------------------------
#
# Two general vectors in the plane, every coordinate a symbol:

# %%
sym_vec2_1

# %% [markdown]
# and the second:

# %%
sym_vec2_2

# %% [markdown]
# Their product has a plain-number part and a plane part:

# %%
sym_vec2_1 * sym_vec2_2

# %% [markdown]
# term by term:

# %%
show_mult(sym_vec2_1, sym_vec2_2)

# %% [markdown]
# The plain-number part is the dot product,

# %%
sym_vec2_1.dot(sym_vec2_2)

# %% [markdown]
# and the plane part is the wedge:

# %%
sym_vec2_1.wedge(sym_vec2_2)

# %% [markdown]
# Wedging two vectors just to *name the plane they span* is common enough to have
# helpers: `bivector_from_vectors(a, b)` is exactly $\vec{\mathbf{a}} \wedge
# \vec{\mathbf{b}}$, and `i(a, b)` is that plane's *unit* bivector ($i * i = -1$), the
# same as $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$ divided by its size.

# %% [markdown]
# Wedges in space, one coordinate plane at a time
# -----------------------------------------------
#
# In space, the wedge of two vectors has a part in each coordinate plane. Project both
# vectors onto one coordinate plane and wedge the shadows, and you get that plane's
# part. Onto the $\vec{\mathbf{e}}_1 \vec{\mathbf{e}}_2$ plane:

# %%
onto_e1e2: MultiVectorFn = MultiVector.project(onto=e_1 * e_2)
onto_e1e2(sym_vec3_1) ^ onto_e1e2(sym_vec3_2)

# %% [markdown]
# onto the $\vec{\mathbf{e}}_2 \vec{\mathbf{e}}_3$ plane:

# %%
onto_e2e3: MultiVectorFn = MultiVector.project(onto=e_2 * e_3)
onto_e2e3(sym_vec3_1) ^ onto_e2e3(sym_vec3_2)

# %% [markdown]
# and onto the $\vec{\mathbf{e}}_1 \vec{\mathbf{e}}_3$ plane:

# %%
onto_e1e3: MultiVectorFn = MultiVector.project(onto=e_1 * e_3)
onto_e1e3(sym_vec3_1) ^ onto_e1e3(sym_vec3_2)

# %% [markdown]
# The order in which the plane is named does not matter:
# $\vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1$ is the same plane as
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3$, so projecting onto it gives the same
# shadow. The difference:

# %%
onto_e3e1: MultiVectorFn = MultiVector.project(onto=e_3 * e_1)
show_difference(onto_e3e1(sym_vec3_1), onto_e1e3(sym_vec3_1))

# %% [markdown]
# The three parts together are the wedge of the two vectors:

# %%
sym_vec3_1.wedge(sym_vec3_2)

# %% [markdown]
# and the full product adds the dot product to it:

# %%
sym_vec3_1 * sym_vec3_2

# %% [markdown]
# A bivector times its inverse
# ----------------------------
#
# A bivector $B = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$ has an inverse, $B^{-1}$:

# %%
B_ab: MultiVector = sym_vec3_1.wedge(sym_vec3_2)
B_ab.inverse()

# %% [markdown]
# Every coefficient has the same denominator, the squared size of $B$,
# $|B|^2 = \tilde{B} * B$ (the reverse $\tilde{B}$ of a bivector is $-B$):

# %%
B_squared_value: Real = (B_ab.reverse() * B_ab).scalar_part()
B_squared_value

# %% [markdown]
# Give it a name, $|B|^2$, so the inverse reads $B^{-1} = \tilde{B} / |B|^2$:

# %%
B_squared: sympy.Symbol = sympy.Symbol("|B|^2", positive=True)
B_inverse: MultiVector = B_ab.reverse() * MultiVector.from_real(1 / B_squared)
B_inverse

# %% [markdown]
# This is gacalc's inverse: $|B|^2 * B^{-1}$ is $\tilde{B}$, so the difference is $0$:

# %%
show_difference(B_squared_value * B_ab.inverse(), B_ab.reverse())

# %% [markdown]
# Term by term, $B^{-1} * B$: every plane part cancels, and the like terms add to
# $|B|^2$ written out, over $|B|^2$.

# %%
show_mult(B_inverse, B_ab)

# %% [markdown]
# Put the value of $|B|^2$ back, and the product is $1$:

# %%
show_difference(at_values(B_inverse * B_ab, [(B_squared, B_squared_value)]), one)

# %% [markdown]
# An aside: units as basis vectors
# --------------------------------
#
# The same algebra can carry units. Let $\vec{\mathbf{e}}_1$ stand for one gram of iron
# and $\vec{\mathbf{e}}_2$ for one mole of iron. The ratio "1 mole per 55.85 grams" is
# $(55.85 * \vec{\mathbf{e}}_1)^{-1} * \vec{\mathbf{e}}_2$, and multiplying a mass in
# grams by it gives moles: the $\vec{\mathbf{e}}_1$ cancels by Rule 1, as units cancel
# in chemistry.

# %%
gram_fe: MultiVector = e_1
mol_fe: MultiVector = e_2
grams_to_moles: MultiVector = (55.85 * gram_fe).inverse() * (1 * mol_fe)
95.8 * gram_fe * grams_to_moles

# %% [markdown]
# The basis blades
# ----------------
#
# Every multivector is a sum of numbers times *blades*: products of distinct basis
# vectors in increasing order. In one dimension there are two blades:

# %%
x: MultiVector
for x in MultiVector.bases(1):
    display(Math(x._repr_latex_()))

# %% [markdown]
# so a general multivector in 𝒢₁ has two coefficients:

# %%
MultiVector.symbolic_multivector(n=1, prefix="a")

# %% [markdown]
# In two dimensions, four blades: a plain number, two vectors and the plane:

# %%
for x in MultiVector.bases(2):
    display(Math(x._repr_latex_()))

# %% [markdown]
# so a general multivector in 𝒢₂ has four coefficients:

# %%
MultiVector.symbolic_multivector(n=2, prefix="b")

# %% [markdown]
# Multiplying two general multivectors of 𝒢₂ uses all the rules at once:

# %%
MultiVector.symbolic_multivector(n=2, prefix="b") * MultiVector.symbolic_multivector(
    n=2, prefix="d"
)

# %% [markdown]
# `r_vector_part(r)` picks out the grade-$r$ part: the plain number (grade 0),

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(0)

# %% [markdown]
# the vector part (grade 1),

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(1)

# %% [markdown]
# and the plane part (grade 2):

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(2)

# %% [markdown]
# In three dimensions there are eight blades:

# %%
for x in MultiVector.bases(3):
    display(Math(x._repr_latex_()))

# %% [markdown]
# Associativity in 𝒢₂, as a proof
# --------------------------------
#
# Three general multivectors of the plane, every coefficient its own symbol:

# %%
G2_1: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="a")
G2_1

# %% [markdown]
# the second,

# %%
G2_2: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="b")
G2_2

# %% [markdown]
# and the third:

# %%
G2_3: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="c")
G2_3

# %% [markdown]
# **Grouping the first two first.** $G_1 * G_2$, term by term:

# %%
show_mult(G2_1, G2_2)

# %% [markdown]
# then that result times $G_3$, giving $(G_1 * G_2) * G_3$:

# %%
show_mult(G2_1 * G2_2, G2_3)

# %% [markdown]
# **Grouping the last two first.** $G_2 * G_3$:

# %%
show_mult(G2_2, G2_3)

# %% [markdown]
# then $G_1$ times that result, giving $G_1 * (G_2 * G_3)$:

# %%
show_mult(G2_1, G2_2 * G2_3)

# %% [markdown]
# The two sums are the same. Below, each blade's terms from the first grouping are
# matched with the same terms from the second: a pair carries the same number, and
# every term has a partner, so the difference is $0$. Because every coefficient is a
# symbol, this is not one example: it is a proof that the geometric product of 𝒢₂ is
# associative for **every** three elements. Lean proves the same law as
# `GacalcProofs.G2.mul_assoc`.

# %%
# twin: GacalcProofs.G2.mul_assoc
show_cancellation(
    (G2_1 * G2_2) * G2_3,
    G2_1 * (G2_2 * G2_3),
    left_name="(G_1 * G_2) * G_3",
    right_name="G_1 * (G_2 * G_3)",
)

# %% [markdown]
# Grade parts in 𝒢₃
# -----------------
#
# A general multivector of 𝒢₃,

# %%
MultiVector.symbolic_multivector(n=3, prefix="c")

# %% [markdown]
# its plain number (grade 0),

# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(0)

# %% [markdown]
# its vector (grade 1),

# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(1)

# %% [markdown]
# its bivector, with a part in each of the three planes (grade 2),

# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(2)

# %% [markdown]
# and its trivector, the volume (grade 3):

# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(3)

# %% [markdown]
# The rules work in any dimension. A symbolic coefficient times three distinct basis
# vectors of 𝒢₄ is already in standard form, a grade-3 blade:

# %%
MultiVector.from_real(a_1) * e_1 * e_2 * e_4

# %% [markdown]
# A bivector and its dual
# -----------------------
#
# A bivector $B$, the wedge of two general vectors of space:

# %%
vec_a: MultiVector = MultiVector.symbolic_multivector(n=3, prefix="e").r_vector_part(1)
vec_b: MultiVector = MultiVector.symbolic_multivector(n=3, prefix="f").r_vector_part(1)
B: MultiVector = MultiVector.bivector_from_vectors(vec_a, vec_b)
B

# %% [markdown]
# Like $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$, it squares to a negative number:

# %%
B * B

# %% [markdown]
# Its dual in 𝒢₃ is the vector perpendicular to its plane:

# %%
B_dual: MultiVectorBase = B.dual(3)
B_dual

# %% [markdown]
# That vector is perpendicular to the plane, so its dot product with $B$ is $0$:

# %%
B_dual.dot(B)

# %% [markdown]
# Term by term, $B$ times its dual: what is left is a pure volume, a multiple of
# $\mathbf{e}_{123}$.

# %%
show_mult(B, B.dual(3))

# %% [markdown]
# A vector's inverse is the vector over its squared size. The dual is as big as $B$, so
# its inverse is the dual over $|B|^2$, with $|B|^2$ now this $B$'s squared size:

# %%
B_squared_value = (B.reverse() * B).scalar_part()
show_difference(B_squared_value * B.dual(3).inverse(), B_dual)

# %% [markdown]
# Term by term, $B$ times the inverse of its dual, with $|B|^2$ by name:

# %%
B_dual_inverse: MultiVectorBase = B_dual * MultiVector.from_real(1 / B_squared)
show_mult(B, B_dual_inverse)

# %% [markdown]
# With the value put back, the product is the unit volume $\mathbf{e}_{123}$:

# %%
show_difference(
    at_values(B * B_dual_inverse, [(B_squared, B_squared_value)]), e_1 * e_2 * e_3
)

# %% [markdown]
# Vectors in any dimension
# ------------------------
#
# The product of two vectors is a dot plus a wedge in every dimension. The 2D table is
# in "Dot and wedge of two vectors" above. In 3D, term by term:

# %%
show_mult(sym_vec3_1, sym_vec3_2)

# %% [markdown]
# and, to see that the method scales, an 8-dimensional vector times a 9-dimensional
# one: 72 rows. Read only the pattern: the eight rows where an index meets itself add
# to the dot product, and every other row is one plane part of the wedge.

# %%
show_mult(
    MultiVector.symbolic_multivector(n=8, prefix="a").r_vector_part(1),
    MultiVector.symbolic_multivector(n=9, prefix="b").r_vector_part(1),
)

# %% [markdown]
# Pictures of multivectors
# ------------------------
#
# `plot_multivector` draws a multivector as a stack of number lines, one per blade,
# with a dot at each coefficient. A mixed multivector of 𝒢₃:

# %%
figure: Figure = plot_multivector(
    2 * one + 3 * e_1 - 1.5 * e_2 + 4 * e_3 + 0.7 * (e_1 * e_2)
)

# %% [markdown]
# A symbolic coefficient has no value to mark, so its dot sits at a small arbitrary
# position near $0$, labelled with the symbol. An 8-dimensional symbolic vector:

# %%
figure = plot_multivector(
    MultiVector.symbolic_multivector(n=8, prefix="a").r_vector_part(1)
)

# %% [markdown]
# Two vectors in the plane, and their product. Before running the third cell, predict
# which blades it has: a plain number (the dot) and
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ (the wedge).

# %%
p: MultiVector = 3 * e_1 - 1.5 * e_2
figure = plot_multivector(p)

# %% [markdown]
# the second vector,

# %%
q: MultiVector = 1.5 * e_1 + 5 * e_2
figure = plot_multivector(q)

# %% [markdown]
# and their product:

# %%
figure = plot_multivector(p * q)

# %% [markdown]
# Transforms (`translate`, `scale_non_uniform`, rotations) and the graph-paper pictures
# are in `notebooks/displaytransforms.py`.
