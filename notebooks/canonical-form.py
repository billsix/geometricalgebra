# ---
# jupyter:
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

# %% [markdown]
# # Exact answers, not decimals — calculations
#
# Companion to *Exact Answers, Not Decimals*. A calculator turns $\sqrt{2}$ into
# $1.4142135623730951$ and carries on. That decimal is not $\sqrt{2}$: it is a nearby
# number, and the small error rides along through every later step. This book keeps
# answers exact, as $\sqrt{2}$ or $\frac{1}{3}$, and writes each one in a single
# standard way, its **canonical form**, so that two answers are equal exactly when they
# look the same. A decimal comes last, and only if it is really needed.
#
# The notebooks use sympy, a library that does algebra with exact numbers and symbols.

# %%
import sympy

from gacalc.nbdisplay import show_difference

# %% [markdown]
# ## A decimal is a nearby number
#
# The decimal a computer stores for $\sqrt{2}$:

# %%
root_2_decimal: float = 2**0.5
root_2_decimal

# %% [markdown]
# Squaring it should give $2$. Predict, then run:

# %%
root_2_decimal**2

# %% [markdown]
# Not quite $2$. The exact $\sqrt{2}$, squared:

# %%
root_2: sympy.Expr = sympy.sqrt(2)
root_2**2

# %% [markdown]
# Exactly $2$. The same thing happens with fractions written as decimals. One tenth plus
# two tenths, as decimals:

# %%
0.1 + 0.2

# %% [markdown]
# and as fractions:

# %%
sympy.Rational(1, 10) + sympy.Rational(2, 10)

# %% [markdown]
# A decimal answer that is "almost" right cannot be tested for equality: is
# $0.30000000000000004$ equal to $0.3$? The exact answer can.

# %%
sympy.Rational(1, 10) + sympy.Rational(2, 10) == sympy.Rational(3, 10)

# %% [markdown]
# ## One way to write each answer
#
# Exact answers can be written many ways: $\sqrt{8}$, $2\sqrt{2}$ and
# $\frac{4}{\sqrt{2}}$ are the same number. The canonical form picks one. sympy writes
# $\sqrt{8}$ as

# %%
sympy.sqrt(8)

# %% [markdown]
# and $\frac{4}{\sqrt{2}}$, with the square root moved out of the bottom, as

# %%
4 / sympy.sqrt(2)

# %% [markdown]
# Both come out as $2\sqrt{2}$, so they are equal.

# %% [markdown]
# Multiplying out is part of the form too. $(1 + \sqrt{2})^2$, expanded the way you
# expand $(x + 1)^2$, with $\sqrt{2} * \sqrt{2} = 2$:
#
# $$
# (1 + \sqrt{2})^2 = 1 + 2 * \sqrt{2} + 2 = 3 + 2 * \sqrt{2}.
# $$

# %%
sympy.expand((1 + root_2) ** 2)

# %% [markdown]
# The page's example, $1 + \sqrt{2}$, is already in canonical form: a whole number plus
# a whole number times $\sqrt{2}$. It is the answer as it stands, with nothing left to
# round.

# %% [markdown]
# ## Keep it whole by choosing the order
#
# A six-pack of crackers costs $5$ cents, so one cracker costs $\frac{5}{6}$ of a cent,
# and you cannot pay $\frac{5}{6}$ of a cent. But if you buy $12$, you never have to:
# $12 * 6^{-1}$ is $2$ packs, and $2$ packs cost $2 * 5 = 10$ cents. Multiplying in that
# order, no fraction ever appears.

# %%
(12 * sympy.Rational(1, 6)) * 5

# %% [markdown]
# Multiplying in the other order passes through the awkward $\frac{5}{6}$ but lands in
# the same place, because exact arithmetic loses nothing on the way:

# %%
12 * (sympy.Rational(1, 6) * 5)

# %% [markdown]
# With decimals the detour costs something. The price of one cracker as a decimal:

# %%
cracker_decimal: float = 5 / 6
cracker_decimal

# %% [markdown]
# That decimal is not $\frac{5}{6}$. The exact fraction the computer actually stored:

# %%
sympy.Rational(cracker_decimal)

# %% [markdown]
# Its difference from $\frac{5}{6}$:

# %%
show_difference(sympy.Rational(cracker_decimal), sympy.Rational(5, 6))

# %% [markdown]
# Times $12$ crackers, the rounding happens to land back on $10$:

# %%
cracker_decimal * 12

# %% [markdown]
# This time the error rounded away. It will not always: $0.1 + 0.2$ above did not. With
# exact numbers there is nothing to hope for.

# %% [markdown]
# The geometric product works the same way later in the book: order the multiplications
# so that they resolve cleanly, and keep everything exact.

# %% [markdown]
# ## A decimal, only when asked
#
# When a decimal really is needed, to measure a board or to draw a picture, ask for it
# at the end, with as many digits as you like:

# %%
sympy.N(1 + root_2, 30)

# %% [markdown]
# The exact answer stays the answer; the decimal is a reading of it.
