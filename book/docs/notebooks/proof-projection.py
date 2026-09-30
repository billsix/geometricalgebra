# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection by standard position — calculations
#
# Companion to the *Proof: Projection by Rotating to Standard Position* chapter. We
# check that `project_sp` — rotate `b` onto the x-axis with elementary 2D rotations,
# project there, rotate back — lands on the same answer as gacalc's geometric-algebra
# projection `projected_onto`.
#
# (DRAFT, agent-drafted 2026-09-30, for the maintainer to refine.)

# %%
import sympy

from gacalc.g3 import e_1, e_2, e_3
from gacalc.standardposition import project_sp, reject_sp

# %% [markdown]
# ## A concrete example
#
# Project `a` onto `b`, both ordinary 3D vectors. The standard-position projection and
# the canonical Hestenes projection agree.

# %%
a = 2.0 * e_1 + 5.0 * e_2 - 1.0 * e_3
b = 1.0 * e_1 + 2.0 * e_2 + 2.0 * e_3
project_sp(a, b)  # rotate b to the x-axis, project, rotate back

# %%
a.projected_onto(b)  # the canonical (A . B) B^-1 -- same vector

# %% [markdown]
# ## Symbolically, for any `a`
#
# We keep `b = 3 e_1 + 4 e_2 + 12 e_3`, whose xy-part has length `5` and whose total
# length is `13` — both exact — so the two plane rotations have rational cosines and
# sines and the symbolic comparison stays clean. For a fully general `a`, the difference
# between the two projections is zero in every coordinate.

# %%
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
a_symbolic = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
b_exact = 3 * e_1 + 4 * e_2 + 12 * e_3

difference = project_sp(a_symbolic, b_exact) - a_symbolic.projected_onto(b_exact)
[sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference]  # -> [0,0,0]

# %% [markdown]
# ## Projection plus rejection rebuild the vector
#
# The part of `a` along `b` (projection) plus the part across `b` (rejection) is `a`
# again — split by standard position and reassembled.

# %%
project_sp(a_symbolic, b_exact) + reject_sp(a_symbolic, b_exact) == a_symbolic
