# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Levels of abstraction — the same operation, three ways, all equal
#
# In algebra class, $x^2 - 1$ and $(x - 1) * (x + 1)$ are the same polynomial written
# two ways, and you can use whichever helps. This book does the same with the dot
# product, the wedge, and the sine and cosine of an angle: each can be written at
# several *levels of abstraction*, from a fully **coordinate** formula you could compute
# by hand, up to a **coordinate-free** one that works in any dimension. The
# coordinate-free form is the one we prefer and teach as canonical; the others are kept
# as teaching aids. Showing several forms is safe because we **prove them equal**,
# here symbolically.
#
# The three rungs for the product of two vectors $a$, $b$:
#
# 1. **Coordinate**: write the numbers out, $a_1 * b_1 + a_2 * b_2$.
# 2. **Fixed-grade**: Hestenes' definition with the grade written in. For two vectors
#    the dot is the grade-0 part of the product, $\langle a * b \rangle_0$, and the
#    wedge the grade-2 part, $\langle a * b \rangle_2$.
# 3. **Coordinate-free**: `a.inner_product(b)` / `a.outer_product(b)`, which pick the
#    grade from the inputs, so the same code works in any dimension.
#
# Each check cell subtracts two forms and shows the difference, $0$ when they agree.

# %%
import sympy

import gacalc.g2 as g2
from gacalc.g2 import Scalar, Vector
from gacalc.nbdisplay import show_mult

# %% [markdown]
# Two general vectors and their geometric product, a plain-number part plus an
# $e_{12}$ part:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
product: g2.Versor = a * b
product

# %% [markdown]
# The product term by term: the $e_1 * e_1$ and $e_2 * e_2$ rows make the grade-0
# part, the other two rows the grade-2 part.

# %%
show_mult(a, b)

# %% [markdown]
# ## Dot product: the grade-0 part
#
# The three rungs for the dot product:

# %%
dot_coordinate: g2.Scalar = g2.Scalar.from_real(a_1 * b_1 + a_2 * b_2)
dot_fixed_grade: g2.Scalar = product.r_vector_part(0)
dot_coordinate_free: g2.Scalar = a.inner_product(b)
dot_coordinate_free

# %% [markdown]
# Rung 1 is rung 2:

# %%
dot_coordinate - dot_fixed_grade

# %% [markdown]
# and rung 2 is rung 3:

# %%
dot_fixed_grade - dot_coordinate_free

# %% [markdown]
# ## Wedge product: the grade-2 part
#
# The same three rungs for $a \wedge b = \langle a * b \rangle_2$:

# %%
wedge_coordinate: g2.Bivector = (g2.Scalar(a_1 * b_2 - a_2 * b_1)) * g2.Bivector.e_12
wedge_fixed_grade: g2.Bivector = product.r_vector_part(2)
wedge_coordinate_free: g2.Bivector = a.outer_product(b)
wedge_coordinate_free

# %% [markdown]
# Rung 1 is rung 2:

# %%
wedge_coordinate - wedge_fixed_grade

# %% [markdown]
# rung 2 is rung 3:

# %%
wedge_fixed_grade - wedge_coordinate_free

# %% [markdown]
# and the operator `a ^ b` is the same wedge:

# %%
wedge_coordinate_free - (a ^ b)

# %% [markdown]
# ## The fundamental identity: $a * b = a \cdot b + a \wedge b$
#
# The two parts put back together are the whole product:

# %%
product - (product.r_vector_part(0) + product.r_vector_part(2))

# %% [markdown]
# ## Sine and cosine: the same idea
#
# `cosine` is coordinate-free and works in any dimension. For the sine there are two
# rungs worth naming:
#
# - **`abs_sin`**, the unsigned sine in any dimension, $|a \wedge b| / (|a| * |b|)$,
#   the companion to `cosine`; and
# - the signed **`sine`**, 𝒢₂ only, $((a \wedge b) \cdot e_{12}) / (|a| * |b|)$,
#   whose sign is the turn direction, so swapping the arguments negates it.
#
# They agree in size, and $\cos(\theta)^2 + \sin(\theta)^2 = 1$ (Lagrange's identity,
# <https://en.wikipedia.org/wiki/Lagrange%27s_identity>). The coordinates below are
# whole numbers, so every value stays exact.

# %%
u: Vector = 3 * g2.e_1 + 4 * g2.e_2
v: Vector = -1 * g2.e_1 + 2 * g2.e_2
u.cosine(v)

# %% [markdown]
# The unsigned sine:

# %%
u.abs_sin(v)

# %% [markdown]
# The signed 𝒢₂ sine, both ways round; swapping the vectors negates it:

# %%
u.sine(v), v.sine(u)

# %% [markdown]
# The signed and unsigned sines agree in size:

# %%
sympy.simplify(sympy.sympify(abs(u.sine(v)) - u.abs_sin(v)))

# %% [markdown]
# and $\cos(\theta)^2 + \sin(\theta)^2 - 1$ is $0$:

# %%
sympy.simplify(sympy.sympify(u.cosine(v) ** 2 + u.sine(v) ** 2 - 1))
