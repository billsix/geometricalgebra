# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection in space, one plane at a time — calculations
#
# Companion to the *Proof: Projection in Space, One Plane at a Time* chapter.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.g3 import e_1, e_2, e_3
from gacalc.standardposition import project_sp, reject_sp

a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2")

# %% [markdown]
# ## The construction, and its check
#
# In space one rotation is not enough, so `gacalc.standardposition.project_sp` does
# it one plane at a time (swing the `xy`-shadow onto the x-axis, then fold the
# `z`-part down). The same equivalence holds: the standard-position projection equals
# the Hestenes one. Here `b = 3 * e_1 + 4 * e_2 + 12 * e_3` has an exact length `13`,
# so the symbolic check stays clean.

# %%
a_3: sympy.Symbol = sympy.symbols("a_3")
a_3d: g3.Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
b_3d: g3.Vector = 3 * e_1 + 4 * e_2 + 12 * e_3
difference_3d: MultiVectorBase = project_sp(a_3d, b_3d) - a_3d.projected_onto(b_3d)
[
    sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference_3d
]  # -> [0, 0, 0]

# %%
project_sp(a_3d, b_3d) + reject_sp(a_3d, b_3d) == a_3d
