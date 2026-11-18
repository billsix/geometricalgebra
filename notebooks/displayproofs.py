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
# Proofs you can check, term by term
# ==================================
#
# A law of the geometric product, shown so that a reader can verify every step
# rather than derive it. The computer does the tedious part, multiplying out every
# term. The reader checks each row and watches the two sides cancel. Lean, a proof
# assistant, has proved the same law for every multivector; this notebook shows the
# computation that Lean's proof certifies.
#
# The method is written up in `tasks/reference/lean-python-notebook-workflow.md`.

# %%
# twin: GacalcProofs.G2.mul_add
from gacalc.gn import MultiVector
from gacalc.nbdisplay import show_cancellation, show_mult

# %% [markdown]
# The product distributes over addition
# -------------------------------------
#
# The law to check: for every three multivectors $a$, $b$, $c$ of 𝒢₂,
#
# $$ a * (b + c) = a * b + a * c $$
#
# Lean states it as `mul_add` in `proofs/GacalcProofs/G2.lean`. Here are three
# general multivectors of the plane, every coefficient its own symbol, so what
# follows holds for all of them at once:

# %%
a: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="a")
b: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="b")
c: MultiVector = MultiVector.symbolic_multivector(n=2, prefix="c")
a, b, c  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **The left side.** First add $b$ and $c$, then multiply by $a$ term by term:

# %%
show_mult(a, b + c)

# %% [markdown]
# **The right side.** Multiply $a$ by $b$, and $a$ by $c$, term by term:

# %%
show_mult(a, b)

# %%
show_mult(a, c)

# %% [markdown]
# **The two sides cancel.** For each blade, every term of $a * (b + c)$ meets the same
# term in $a * b + a * c$. A pair carries the same number, and no term is left over:

# %%
show_cancellation(
    a * (b + c),
    a * b + a * c,
    left_name="a * (b + c)",
    right_name="a * b + a * c",
)

# %% [markdown]
# Every coefficient is a symbol, so this is not one example: the product of 𝒢₂
# distributes over addition for **every** $a$, $b$ and $c$. Lean's proof of
# `mul_add` multiplies out the same definitions and checks the same cancellation,
# all at once (its `ring` tactic). That is why it shows no steps, and why this
# notebook spells them out.
