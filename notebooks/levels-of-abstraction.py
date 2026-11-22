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
# The three rungs for the product of two vectors $\vec{\mathbf{a}}$, $\vec{\mathbf{b}}$:
#
# 1. **Coordinate**: write the numbers out, $a_1 * b_1 + a_2 * b_2$.
# 2. **Fixed-grade**: Hestenes' definition with the grade written in. For two vectors
#    the dot is the grade-0 part of the product,
#    $\langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0$, and the wedge the grade-2
#    part, $\langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2$.
# 3. **Coordinate-free**: `a.inner_product(b)` / `a.outer_product(b)`, which pick the
#    grade from the inputs, so the same code works in any dimension.
#
# Every coordinate is a symbol, so each equality holds for all vectors. Numbers appear
# only to draw the figure. Each check shows the forms, then their difference.

# %%
import sympy

import gacalc.g2 as g2
from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    GREEN,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    scene_around,
)
from gacalc.g2 import Scalar, Vector
from gacalc.nbdisplay import at_values, show_difference, show_mult

# %% [markdown]
# Two general vectors:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
b

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# The product term by term: the $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2$ rows make the grade-0 part, the other two
# rows the grade-2 part. First at the plot values:

# %%
show_mult(at_values(a, values), at_values(b, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, b)

# %% [markdown]
# The geometric product, a plain-number part plus an
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ part:

# %%
product: g2.Versor = a * b
product

# %% [markdown]
# Drawn at the plot values: the plain-number part measures $\vec{\mathbf{b}}$'s shadow
# along $\vec{\mathbf{a}}$ (green), the $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ part
# the signed area of the parallelogram (dashed).

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_SHADOW: Point = point(coordinates=list(at_values(b.projected_onto(a), values)))
fig_parts: PendingFigure
with scene_around(points=[P_A, P_B, P_A + P_B]) as fig_parts:
    dashed_arrow(tail=P_A, head=P_A + P_B, color=BLACK)
    dashed_arrow(tail=P_B, head=P_A + P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$", align=LabelPos.l)
    arrow(head=P_SHADOW, color=GREEN, width=2.4)
    note(
        at=0.5 * P_SHADOW,
        text=r"$\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    note(at=0.5 * (P_A + P_B), text=r"$\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$")
fig_parts

# %% [markdown]
# ## Dot product: the grade-0 part
#
# Rung 1, the coordinates:

# %%
dot_coordinate: g2.Scalar = g2.Scalar.from_real(a_1 * b_1 + a_2 * b_2)
dot_coordinate

# %% [markdown]
# rung 2, the grade-0 part of the product:

# %%
dot_fixed_grade: g2.Scalar = product.r_vector_part(0)
dot_fixed_grade

# %% [markdown]
# rung 3, the coordinate-free inner product:

# %%
dot_coordinate_free: g2.Scalar = a.inner_product(b)
dot_coordinate_free

# %% [markdown]
# Rung 1 minus rung 2:

# %%
dot_coordinate - dot_fixed_grade

# %% [markdown]
# and rung 2 minus rung 3:

# %%
dot_fixed_grade - dot_coordinate_free

# %% [markdown]
# ## Wedge product: the grade-2 part
#
# The same three rungs for
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}} = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2$.
# Rung 1:

# %%
wedge_coordinate: g2.Bivector = (g2.Scalar(a_1 * b_2 - a_2 * b_1)) * g2.Bivector.e_12
wedge_coordinate

# %% [markdown]
# rung 2:

# %%
wedge_fixed_grade: g2.Bivector = product.r_vector_part(2)
wedge_fixed_grade

# %% [markdown]
# rung 3:

# %%
wedge_coordinate_free: g2.Bivector = a.outer_product(b)
wedge_coordinate_free

# %% [markdown]
# Rung 1 minus rung 2:

# %%
wedge_coordinate - wedge_fixed_grade

# %% [markdown]
# rung 2 minus rung 3:

# %%
wedge_fixed_grade - wedge_coordinate_free

# %% [markdown]
# The operator `a ^ b`:

# %%
a ^ b

# %% [markdown]
# minus rung 3:

# %%
wedge_coordinate_free - (a ^ b)

# %% [markdown]
# ## The fundamental identity: $\vec{\mathbf{a}} * \vec{\mathbf{b}} = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$
#
# The two parts put back together:

# %%
product.r_vector_part(0) + product.r_vector_part(2)

# %% [markdown]
# Their difference from the whole product:

# %%
show_difference(product, product.r_vector_part(0) + product.r_vector_part(2))

# %% [markdown]
# ## Sine and cosine: the same idea
#
# `cosine` is coordinate-free and works in any dimension. For the sine there are two
# rungs worth naming:
#
# - **`abs_sin`**, the unsigned sine in any dimension,
#   $|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}| / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$,
#   the companion to `cosine`; and
# - the signed **`sine`**, 𝒢₂ only,
#   $((\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) \cdot (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)) / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$,
#   whose sign is the turn direction, so swapping the arguments negates it.
#
# They agree in size, and $\cos(\theta)^2 + \sin(\theta)^2 = 1$ (Lagrange's identity,
# <https://en.wikipedia.org/wiki/Lagrange%27s_identity>). The cosine of the angle from
# $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$:

# %%
a.cosine(b)

# %% [markdown]
# The unsigned sine:

# %%
a.abs_sin(b)

# %% [markdown]
# The signed 𝒢₂ sine:

# %%
a.sine(b)

# %% [markdown]
# and the other way round, from $\vec{\mathbf{b}}$ to $\vec{\mathbf{a}}$:

# %%
b.sine(a)

# %% [markdown]
# Swapping the vectors negates it. Their sum:

# %%
sympy.simplify(sympy.sympify(a.sine(b) + b.sine(a)))

# %% [markdown]
# The signed and unsigned sines agree in size. $|\sin(\theta)|$ minus the unsigned sine:

# %%
sympy.simplify(sympy.sympify(abs(a.sine(b)) - a.abs_sin(b)))

# %% [markdown]
# $\cos(\theta)^2 + \sin(\theta)^2$:

# %%
sympy.simplify(sympy.sympify(a.cosine(b) ** 2 + a.sine(b) ** 2))

# %% [markdown]
# minus $1$:

# %%
sympy.simplify(sympy.sympify(a.cosine(b) ** 2 + a.sine(b) ** 2 - 1))
