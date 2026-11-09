# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Into Three Dimensions — calculations
#
# Part II starts again from the geometric product, now with three basis directions.
# The first thing to check is that the product of two vectors still splits the same
# way it did in the plane: a plain-number part (the dot) and a bivector part (the
# wedge). The code for the dot and the wedge is the same code as in 𝒢₂; nothing in
# `inner_product` or `outer_product` mentions the dimension.

# %%
import sympy

import gacalc.g3 as g3

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

assert product_3d.r_vector_part(0) == p.inner_product(q)  # the dot: the grade-0 part
assert product_3d.r_vector_part(2) == p.outer_product(q)  # the wedge: the grade-2 part
product_3d
