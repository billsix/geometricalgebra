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
# 𝒢₃ — the geometric algebra of three-dimensional space
# =====================================================
#
# This notebook demonstrates the **specialized `g3.G` class** (𝒢₃), the fast,
# named-field representation of the geometric algebra of ℝ³. It mirrors
# `displaymv.py` (which uses the general `Gn`), but every value here is a `g3.G`:
# its closed-form geometric product is code-generated from `Gn`, so it is
# provably consistent with the reference while being much faster.
#
# 𝒢₃ has 2³ = 8 basis blades: the scalar `1`, three vectors `e_1`, `e_2`, `e_3`,
# three bivectors `e_12`, `e_13`, `e_23`, and the trivector / pseudoscalar
# `e_123 = e_1 e_2 e_3`.

# %%
import warnings

import sympy
from IPython.display import Math, display

from gacalc.g3 import G, Vector
from gacalc.measure import area, signed_volume, volume
from gacalc.nbplotutils import plot_multivector, show_mult

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# Bare names for the full-G basis constants, so the code reads like the math.
# These are the FULL 𝒢₃ constants (e_1 here is G.e_1) -- not the graded Vector
# that `from gacalc.g3 import e_1` gives; every value in this notebook is a G.
e_1: G = G.e_1
e_2: G = G.e_2
e_3: G = G.e_3
e_12: G = G.e_12
e_13: G = G.e_13
e_23: G = G.e_23
e_123: G = G.e_123

# %% [markdown]
# Basis blades and the pseudoscalar
# ---------------------------------
#
# The product of the three basis vectors is the trivector `e_123`, the
# pseudoscalar of 𝒢₃. Like the bivector in 𝒢₂, it squares to −1.

# %%
pseudoscalar: G = e_1 * e_2 * e_3
pseudoscalar  # pyright: ignore[reportUnusedExpression]

# %%
pseudoscalar * pseudoscalar  # pyright: ignore[reportUnusedExpression]

# %%
e_123 == e_1 * e_2 * e_3

# %%
# the three unit bivectors
e_12  # pyright: ignore[reportUnusedExpression]

# %%
# the three unit bivectors
e_13  # pyright: ignore[reportUnusedExpression]

# %%
# the three unit bivectors
e_23  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Linear combinations
# -------------------

# %%
2 * e_1 + 3 * e_2 + 4 * e_3 + 5 * e_1  # pyright: ignore[reportUnusedExpression]

# %%
G.from_scalar(0)  # pyright: ignore[reportUnusedExpression]

# %%
G.from_scalar(1)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Symbolic vectors
# ----------------
#
# `symbolic_multivector` builds a full multivector of `sympy` symbols;
# `r_vector_part(1)` keeps only the grade-1 (vector) part.

# %%
a: G = G.symbolic_multivector(prefix="a")
a  # pyright: ignore[reportUnusedExpression]

# %%
a_vec: G = G.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec  # pyright: ignore[reportUnusedExpression]

# %%
b_vec: G = G.symbolic_multivector(prefix="b").r_vector_part(1)
b_vec  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The geometric product of two vectors
# ------------------------------------
#
# $$ ab = a\cdot b + a\wedge b $$
#
# In 𝒢₃ the wedge of two vectors is a bivector with three components
# (the `e_12`, `e_13`, `e_23` planes).

# %%
a_vec * b_vec  # pyright: ignore[reportUnusedExpression]

# %%
a_vec.dot(b_vec)

# %%
a_vec.wedge(b_vec)

# %%
a_vec ^ b_vec  # pyright: ignore[reportUnusedExpression]

# %%
a_vec.dot(b_vec) + a_vec.wedge(b_vec) == a_vec * b_vec

# %% [markdown]
# The wedge magnitudes are area and volume — `area`, `volume`, `signed_volume`
# ---------------------------------------------------------------------------
#
# In 𝒢₃ the magnitudes of the wedges are the high-school measures: $|a \wedge b|$
# is the **area** of the parallelogram on `a`, `b`, and $|a \wedge b \wedge c|$ is
# the **volume** of the parallelepiped on `a`, `b`, `c`. `gacalc.measure` names
# them (the general k-dimensional version is the *content*, Williamson & Trotter
# p. 308).

# %%
# area of the parallelogram on the two vectors: |a ∧ b|
area(a_vec, b_vec)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **`area` is unsigned — switching the two vectors changes nothing:**

# %%
area(a_vec, b_vec) == area(b_vec, a_vec)

# %% [markdown]
# There is **no signed area in 𝒢₃**: two vectors span only a plane (`k = 2 < 3`),
# so the orientation is the whole bivector `a ∧ b`, not a scalar `±`. A *signed*
# scalar needs the vectors to span the full space (`k = n`) — in 𝒢₃ that means
# **three** vectors, giving a signed **volume**. (`signed_area(a, b)` is defined
# only in 𝒢₂; calling it here would raise.)

# %%
# a third vector, so we have a full 3-vector frame spanning 𝒢₃
c_vec: G = G.symbolic_multivector(prefix="c").r_vector_part(1)
c_vec  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **`volume(a, b, c)`** is the parallelepiped volume $|a \wedge b \wedge c|$:

# %%
volume(a_vec, b_vec, c_vec)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **`signed_volume` keeps the orientation — it is the 3×3 determinant — and
# switching the first two vectors flips its sign**, while the unsigned `volume`
# above is its absolute value:

# %%
signed_volume(a_vec, b_vec, c_vec)  # pyright: ignore[reportUnusedExpression]

# %%
signed_volume(b_vec, a_vec, c_vec)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The two are negatives of each other. (The 3×3 determinant and its negation are
# mathematically equal but not *structurally* identical, so we ask sympy to
# simplify their sum to `0` rather than comparing with `==`.)

# %%
sympy.simplify(
    signed_volume(b_vec, a_vec, c_vec) + signed_volume(a_vec, b_vec, c_vec)
) == 0

# %% [markdown]
# Distributing a full product
# ---------------------------

# %%
g3_1: G = G.symbolic_multivector(prefix="a")
g3_2: G = G.symbolic_multivector(prefix="b")
show_mult(g3_1, g3_2)

# %% [markdown]
# Associativity
# -------------

# %%
g3_3: G = G.symbolic_multivector(prefix="c")
((g3_1 * g3_2) * g3_3) - (g3_1 * (g3_2 * g3_3))

# %% [markdown]
# Grade projection
# ----------------
#
# 𝒢₃ has grades 0–3: scalar, vector, bivector, trivector.

# %%
c: G = G.symbolic_multivector(prefix="c")
c.r_vector_part(0)

# %%
c.r_vector_part(1)

# %%
c.r_vector_part(2)

# %%
c.r_vector_part(3)

# %% [markdown]
# The basis of 𝒢₃
# ---------------
#
# All 2³ = 8 basis blades, in grade order.

# %%
for x in G.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Duality: the bivector and its dual axis
# ---------------------------------------
#
# In 𝒢₃ the dual of a bivector (a plane) is the vector orthogonal to it — this
# is the geometric-algebra counterpart of the cross product. Below, the bivector
# $a\wedge b$ and its dual; the dual is parallel to $a\times b$.

# %%
biv: G = a_vec ^ b_vec
biv  # pyright: ignore[reportUnusedExpression]

# %%
biv.dual()

# %%
biv * biv.dual()  # pyright: ignore[reportUnusedExpression]

# %%
# a bivector squares to a (negative) scalar — it has a magnitude
biv * biv  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Magnitude, inverse, reverse, dual of a vector
# ---------------------------------------------

# %%
m: G = 1 * e_1 + 2 * e_2 + 2 * e_3
m.magnitude()

# %%
m * m  # pyright: ignore[reportUnusedExpression]

# %%
m.normalize()

# %%
m.inverse()

# %%
m * m.inverse() == G.from_scalar(1)

# %%
# reverse of the pseudoscalar
pseudoscalar.reverse()

# %%
# the dual of a vector is a bivector (the orthogonal plane)
m.dual()

# %% [markdown]
# Plotting a multivector
# ----------------------
#
# `plot_multivector` draws each blade's coefficient on its own number line. It
# accepts any representation — here, `g3.G` values.

# %%
plot_multivector(
    2 * G.from_scalar(1) + 3 * e_1 - 1.5 * e_2 + 4 * e_3 + 0.7 * (e_1 * e_2)
)

# %%
u: G = 3 * e_1 - 1.5 * e_2 + 2 * e_3
plot_multivector(u)

# %%
v: G = 1.5 * e_1 + 5 * e_2 - 1 * e_3
plot_multivector(v)

# %%
plot_multivector(u * v)

# %% [markdown]
# The wedge magnitude: $|a \wedge b| = |a|\,|b|\,\sin\theta$ (in 𝒢₃)
# ================================================================
#
# The 𝒢₂ derivation carries over: two vectors always span a single 2-plane, so
# $|a\wedge b| = |a||b|\sin\theta$ holds in 𝒢₃ too. The only difference is that
# $a\wedge b$ is now a **three-component** bivector, and the Lagrange identity is
# a *sum* of squares
#
# $$|a|^2|b|^2 - (a\cdot b)^2
#   = (a_1b_2-a_2b_1)^2 + (a_1b_3-a_3b_1)^2 + (a_2b_3-a_3b_2)^2 = |a\wedge b|^2 .$$
#
# Symbols are declared **real** so that $\sqrt{x^2}=|x|$ behaves.

# %%
a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3", real=True)
a: Vector = a_1 * Vector.e_1 + a_2 * Vector.e_2 + a_3 * Vector.e_3
b: Vector = b_1 * Vector.e_1 + b_2 * Vector.e_2 + b_3 * Vector.e_3

# %% [markdown]
# The dot product (a scalar) and the wedge (a three-component bivector):

# %%
a.inner_product(b)

# %%
a ^ b

# %% [markdown]
# **The Lagrange step.** The residual collapses to $0$ symbolically:

# %%
dot = a.inner_product(b).scalar_part()
lagrange_residual = sympy.simplify(
    a.magnitude_squared() * b.magnitude_squared() - dot**2 - (a ^ b).magnitude_squared()
)
lagrange_residual

# %%
assert lagrange_residual == 0

# %% [markdown]
# **From the squared form to the magnitude.** With
# $\cos\theta = a\cdot b/(|a||b|)$ and $\sin\theta = \sqrt{1-\cos^2\theta}\ge 0$,
# both $|a\wedge b|$ and $|a||b|\sin\theta$ are the square root of the *same* sum
# of squares. So, unlike the 𝒢₂ case (a single perfect square needing `factor`),
# sympy closes the difference directly:

# %%
cos = a.cosine(b)
sin = sympy.sqrt(1 - cos**2)  # sinθ ≥ 0 for θ in [0, π]
wedge_magnitude_from_sin = a.magnitude() * b.magnitude() * sin
wedge_magnitude_from_sin

# %%
(a ^ b).magnitude()

# %%
assert sympy.simplify(wedge_magnitude_from_sin - (a ^ b).magnitude()) == 0

# %% [markdown]
# **Rotor capstone.** As in 𝒢₂, $ab = a\cdot b + a\wedge b$ splits into
# orthogonal grades, so $|ab|^2 = (a\cdot b)^2 + |a\wedge b|^2 = |a|^2|b|^2$ and
# $|ab| = |a||b|$. Here $ab$ is a `g3.Rotor` (scalar + bivector):

# %%
a * b

# %%
assert (
    sympy.simplify(
        (a * b).magnitude_squared() - a.magnitude_squared() * b.magnitude_squared()
    )
    == 0
)

# %%
