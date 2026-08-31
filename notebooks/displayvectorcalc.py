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
# Vector calculus in 𝒢₃ — i, j, k and the cross product
# ======================================================
#
# Calc-3 notation, on top of the geometric algebra that computes it. Two
# one-time moves in the setup cell give a whole notebook the familiar look:
#
# - `set_blade_symbols(...)` makes every LaTeX **display** render the basis
#   vectors e₁/e₂/e₃ as **i**/**j**/**k** (display only — the stored blade
#   tuples and `repr` never change);
# - `i, j, k = e_1, e_2, e_3` gives the same names on the **input** side, with
#   no library support needed — they are ordinary Python aliases of the graded
#   `g3.Vector` basis constants.

# %%
import sympy
from IPython.display import display

from gacalc.base import set_blade_symbols
from gacalc.g3 import Vector, e_1, e_2, e_3
from gacalc.measure import signed_volume
from gacalc.vectorcalc import cross

set_blade_symbols({(1,): r"\mathbf{i}", (2,): r"\mathbf{j}", (3,): r"\mathbf{k}"})

# Input-side aliases -- sanctioned for this notebook (maintainer, 2026-08-31) as
# the deliberate pairing with the display symbols above; elsewhere the house
# rule is to reference the basis constants by their own names.
i: Vector = e_1
j: Vector = e_2
k: Vector = e_3

# %% [markdown]
# A vector now reads — and renders — the calc-3 way (a cell's last expression
# displays itself; no helper needed):

# %%
a: Vector = 2 * i + 3 * j + 1 * k
a  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The cross product — the dual of the wedge
# -----------------------------------------
#
# In geometric algebra the honest product of two vectors' plane is the wedge
# `a ∧ b`, a *bivector* (an oriented parallelogram). Only in 3 dimensions does
# its dual — multiplication by the inverse unit pseudoscalar, `(a ∧ b) I₃⁻¹` —
# land back on a *vector*: the right-hand-rule cross product. `cross` is that
# one line; the cyclic identities come out of the algebra:

# %%
display(cross(1 * i, 1 * j))  # = k
display(cross(1 * j, 1 * k))  # = i
display(cross(1 * k, 1 * i))  # = j

# %% [markdown]
# Symbolically, the classic coordinate formula falls out:

# %%
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
sym_a: Vector = a_1 * i + a_2 * j + a_3 * k
sym_b: Vector = b_1 * i + b_2 * j + b_3 * k
cross(sym_a, sym_b)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Dot and the scalar triple product — already here under their GA names
# ---------------------------------------------------------------------
#
# The **dot product** is `scalar_product` (`a · b = ⟨a b⟩`), and the **scalar
# triple product** `a · (b × c)` is `measure.signed_volume(a, b, c)` — the 3-D
# determinant. No aliases needed; the identity holds on the nose:

# %%
b: Vector = 1 * i + 1 * j
c: Vector = 1 * j + 2 * k
# b.cross(c) is g3.Vector's generated closed form, typed Vector -> Vector.
display(a.scalar_product(b.cross(c)))
display(signed_volume(a, b, c))
