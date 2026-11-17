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
# Every coordinate is a symbol, so each equality holds for all vectors. Numbers appear
# only to draw the figure. Each check shows the forms, then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _bootstrap_live import (
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

import gacalc.g2 as g2
from gacalc.base import Real
from gacalc.g2 import Scalar, Vector
from gacalc.nbdisplay import at_values, show_mult

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

# %%
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
b

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# The product term by term: the $e_1 * e_1$ and $e_2 * e_2$ rows make the grade-0
# part, the other two rows the grade-2 part.

# %%
show_mult(a, b)

# %% [markdown]
# The geometric product, a plain-number part plus an $e_{12}$ part:

# %%
product: g2.Versor = a * b
product

# %% [markdown]
# Drawn at the plot values: the plain-number part measures $b$'s shadow along $a$
# (green), the $e_{12}$ part the signed area of the parallelogram (dashed).

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_SHADOW: Point = point(coordinates=list(at_values(b.projected_onto(a), values)))
fig_parts: PendingFigure
with scene_around(points=[P_A, P_B, P_A + P_B]) as fig_parts:
    dashed_arrow(tail=P_A, head=P_A + P_B, color=BLACK)
    dashed_arrow(tail=P_B, head=P_A + P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$", align=LabelPos.l)
    arrow(head=P_SHADOW, color=GREEN, width=2.4)
    note(
        at=0.5 * P_SHADOW,
        text=r"$\operatorname{proj}_{\vec{a}}(\vec{b})$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    note(at=0.5 * (P_A + P_B), text=r"$\vec{a} \wedge \vec{b}$")
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
# The same three rungs for $a \wedge b = \langle a * b \rangle_2$. Rung 1:

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
# ## The fundamental identity: $a * b = a \cdot b + a \wedge b$
#
# The two parts put back together:

# %%
product.r_vector_part(0) + product.r_vector_part(2)

# %% [markdown]
# Their difference from the whole product:

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
# <https://en.wikipedia.org/wiki/Lagrange%27s_identity>). The cosine of the angle from
# $a$ to $b$:

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
# and the other way round, from $b$ to $a$:

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
