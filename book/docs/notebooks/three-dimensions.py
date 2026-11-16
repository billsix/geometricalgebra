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
# In the plane, the product of two vectors split into a plain-number part, the dot
# product, and a bivector part, the wedge. The first thing to check is that it still
# splits that way in space. The code for the dot and the wedge is the same code as in
# 𝒢₂: nothing in `inner_product` or `outer_product` mentions the dimension. Each check
# cell subtracts two things and shows the difference, $0$ when they agree.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.nbdisplay import show_mult

# %% [markdown]
# Two vectors in space, every coordinate a symbol:

# %%
p_1: sympy.Symbol
p_2: sympy.Symbol
p_3: sympy.Symbol
q_1: sympy.Symbol
q_2: sympy.Symbol
q_3: sympy.Symbol
p_1, p_2, p_3, q_1, q_2, q_3 = sympy.symbols("p_1 p_2 p_3 q_1 q_2 q_3", real=True)
p: g3.Vector = (
    g3.Scalar(p_1) * g3.Vector.e_1
    + g3.Scalar(p_2) * g3.Vector.e_2
    + g3.Scalar(p_3) * g3.Vector.e_3
)
q: g3.Vector = (
    g3.Scalar(q_1) * g3.Vector.e_1
    + g3.Scalar(q_2) * g3.Vector.e_2
    + g3.Scalar(q_3) * g3.Vector.e_3
)

# %% [markdown]
# ## The product
#
# A plain number plus three bivector parts, one for each coordinate plane:

# %%
product_3d: g3.Versor = p * q
product_3d

# %% [markdown]
# The product term by term: nine pairs now, three of them a direction times itself.
# Those three rows add to the dot; the other six pair up, $e_i * e_j$ with $e_j * e_i$,
# into the three bivector parts of the wedge.

# %%
show_mult(p, q)

# %% [markdown]
# ## The two parts
#
# The grade-0 part, $\langle p * q \rangle_0$, is the dot product:

# %%
product_3d.r_vector_part(0) - p.inner_product(q)

# %% [markdown]
# and the grade-2 part, $\langle p * q \rangle_2$, is the wedge:

# %%
product_3d.r_vector_part(2) - p.outer_product(q)
