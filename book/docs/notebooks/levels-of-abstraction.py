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
# A recurring idea in this book: the dot product, the wedge, the sine and cosine of an
# angle can each be written at several *levels of abstraction* — from a fully
# **coordinate** formula you could compute by hand, up to a **coordinate-free,
# dimension-independent** one. The coordinate-free form is the one we prefer and
# teach as canonical; the coordinate and intermediate forms are kept as teaching
# aids. Showing several forms is safe because we **prove them equal** — here,
# symbolically.
#
# The three rungs for the product of two vectors `a`, `b`:
#
# 1. **Coordinate** — write the numbers out (e.g. `a_1*b_1 + a_2*b_2`).
# 2. **Fixed-grade** — Hestenes' definition with the grade *bound to a literal*: for two
#    vectors the dot is the grade-0 part of the product `⟨ab⟩₀`, the wedge the grade-2
#    part `⟨ab⟩₂`.
# 3. **Coordinate-free** — `a.inner_product(b)` / `a.outer_product(b)`: picks the grade
#    from each homogeneous pair, so the *same* code works in any dimension.

# %%
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import Real
from gacalc.g2 import Vector

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = a_1 * Vector.e_1 + a_2 * Vector.e_2
b: Vector = b_1 * Vector.e_1 + b_2 * Vector.e_2
product: g2.Versor = a * b
product  # the full geometric product: a scalar part + an e_12 (bivector) part

# %% [markdown]
# ## Dot product — the grade-0 part
#
# Rung 1 (coordinate) vs rung 2 (fixed-grade `⟨ab⟩₀`) vs rung 3 (coordinate-free
# `inner_product`). All three are the same scalar.

# %%
dot_coordinate: g2.Scalar = g2.Scalar.from_real(a_1 * b_1 + a_2 * b_2)
dot_fixed_grade: g2.Scalar = product.r_vector_part(0)  # <ab>_0, the bound grade 0
dot_coordinate_free: g2.Scalar = a.inner_product(
    b
)  # the canonical, dimension-free form

assert dot_coordinate == dot_fixed_grade == dot_coordinate_free
dot_coordinate_free

# %% [markdown]
# ## Wedge product — the grade-2 part
#
# The same three rungs, now for `a ∧ b = ⟨ab⟩₂`.

# %%
wedge_coordinate: g2.Bivector = (a_1 * b_2 - a_2 * b_1) * g2.Bivector.e_12
wedge_fixed_grade: g2.Bivector = product.r_vector_part(2)  # <ab>_2, the bound grade 2
wedge_coordinate_free: g2.Bivector = a.outer_product(b)  # canonical; also a ^ b

assert wedge_coordinate == wedge_fixed_grade == wedge_coordinate_free == (a ^ b)
wedge_coordinate_free

# %% [markdown]
# ## The fundamental identity: `ab = a·b + a∧b`
#
# The two bound-grade parts reassemble the whole product.

# %%
assert product == product.r_vector_part(0) + product.r_vector_part(2)

# %% [markdown]
# ## Coordinate-free is dimension-independent
#
# The *same* `inner_product` / `outer_product` calls work in 𝒢₃ — nothing about them
# mentions 2 or 3. That is the point of the coordinate-free rung.

# %%
p_1: sympy.Symbol
p_2: sympy.Symbol
p_3: sympy.Symbol
q_1: sympy.Symbol
q_2: sympy.Symbol
q_3: sympy.Symbol
p_1, p_2, p_3, q_1, q_2, q_3 = sympy.symbols("p_1 p_2 p_3 q_1 q_2 q_3", real=True)
p: g3.Vector = p_1 * g3.Vector.e_1 + p_2 * g3.Vector.e_2 + p_3 * g3.Vector.e_3
q: g3.Vector = q_1 * g3.Vector.e_1 + q_2 * g3.Vector.e_2 + q_3 * g3.Vector.e_3
product_3d: g3.Versor = p * q

assert product_3d.r_vector_part(0) == p.inner_product(q)  # dot = <pq>_0, still
assert product_3d.r_vector_part(2) == p.outer_product(q)  # wedge = <pq>_2, still
p.inner_product(q)

# %% [markdown]
# ## Sine and cosine — the same idea
#
# `cosine` is coordinate-free and works in any dimension. For the sine there are
# two rungs worth naming:
#
# - **`abs_sin`** — the unsigned, any-dimension sine `|a∧b| / (|a| * |b|)` (the
#   companion to `cosine`); and
# - the signed **`sine`**, 𝒢₂ only — `(a∧b)·e₁₂ / (|a| * |b|)`, whose sign is the
#   turn direction, so swapping the arguments negates it.
#
# They agree in magnitude, and `cosine² + sine² = 1` (Lagrange's identity, <https://en.wikipedia.org/wiki/Lagrange%27s_identity>).

# %%
u: Vector = 3.0 * g2.e_1 + 4.0 * g2.e_2
v: Vector = -1.0 * g2.e_1 + 2.0 * g2.e_2
u.cosine(v)  # coordinate-free, any dimension

# %%
u.abs_sin(v)  # the unsigned sine |a∧b|/(|a| * |b|), any dimension

# %%
# The signed 𝒢₂ sine: its sign is the turn direction, so swapping negates it.
u.sine(v), v.sine(u)

# %%
# Signed and unsigned agree in magnitude; Lagrange gives cos²(θ) + sin²(θ) = 1.
cos_squared_plus_sin_squared: Real = u.cosine(v) ** 2 + u.sine(v) ** 2
assert abs(u.sine(v)) == u.abs_sin(v)
assert round(cos_squared_plus_sin_squared, 10) == 1.0
cos_squared_plus_sin_squared  # == 1
