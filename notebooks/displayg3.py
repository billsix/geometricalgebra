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
# 𝒢₃ — the geometric algebra of three-dimensional space
# =====================================================
#
# This notebook demonstrates the **specialized `G3` class** (𝒢₃), the fast,
# named-field representation of the geometric algebra of ℝ³. It mirrors
# `displaymv.py` (which uses the general `Gn`), but every value here is a `G3`:
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

from gacalc.g3 import (
    G3,
    Vector3,
    e_1,
    e_2,
    e_3,
    e_12,
    e_13,
    e_23,
    e_123,
    one,
    zero,
)
from gacalc.nbplotutils import plot_multivector, show_mult

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# Basis blades and the pseudoscalar
# ---------------------------------
#
# The product of the three basis vectors is the trivector `e_123`, the
# pseudoscalar of 𝒢₃. Like the bivector in 𝒢₂, it squares to −1.

# %%
pseudoscalar: G3 = e_1 * e_2 * e_3
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
zero  # pyright: ignore[reportUnusedExpression]

# %%
one  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Symbolic vectors
# ----------------
#
# `symbolic_multivector` builds a full multivector of `sympy` symbols;
# `r_vector_part(1)` keeps only the grade-1 (vector) part.

# %%
a = G3.symbolic_multivector(prefix="a")
a  # pyright: ignore[reportUnusedExpression]

# %%
a_vec = G3.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec  # pyright: ignore[reportUnusedExpression]

# %%
b_vec = G3.symbolic_multivector(prefix="b").r_vector_part(1)
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
# Distributing a full product
# ---------------------------

# %%
g3_1 = G3.symbolic_multivector(prefix="a")
g3_2 = G3.symbolic_multivector(prefix="b")
show_mult(g3_1, g3_2)

# %% [markdown]
# Associativity
# -------------

# %%
g3_3 = G3.symbolic_multivector(prefix="c")
((g3_1 * g3_2) * g3_3) - (g3_1 * (g3_2 * g3_3))

# %% [markdown]
# Grade projection
# ----------------
#
# 𝒢₃ has grades 0–3: scalar, vector, bivector, trivector.

# %%
c = G3.symbolic_multivector(prefix="c")
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
for x in G3.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Duality: the bivector and its dual axis
# ---------------------------------------
#
# In 𝒢₃ the dual of a bivector (a plane) is the vector orthogonal to it — this
# is the geometric-algebra counterpart of the cross product. Below, the bivector
# $a\wedge b$ and its dual; the dual is parallel to $a\times b$.

# %%
biv = a_vec ^ b_vec
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
m = 1 * e_1 + 2 * e_2 + 2 * e_3
m.magnitude()

# %%
m * m  # pyright: ignore[reportUnusedExpression]

# %%
m.normalize()

# %%
m.inverse()

# %%
m * m.inverse() == one

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
# accepts any representation — here, `G3` values.

# %%
plot_multivector(2 * one + 3 * e_1 - 1.5 * e_2 + 4 * e_3 + 0.7 * (e_1 * e_2))

# %%
u = 3 * e_1 - 1.5 * e_2 + 2 * e_3
plot_multivector(u)

# %%
v = 1.5 * e_1 + 5 * e_2 - e_3
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
a = a_1 * Vector3.e_1 + a_2 * Vector3.e_2 + a_3 * Vector3.e_3
b = b_1 * Vector3.e_1 + b_2 * Vector3.e_2 + b_3 * Vector3.e_3

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
# $|ab| = |a||b|$. Here $ab$ is a `Rotor3` (scalar + bivector):

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
