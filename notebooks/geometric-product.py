# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The Geometric Product — rotation is a multiplication
#
# In the complex numbers, multiplying by $i$ turns a point a quarter turn, and
# multiplying by $\cos(\theta) + \sin(\theta) * i$ turns it by $\theta$. The chapter
# claims the same for vectors in the plane: rotating $\vec{\mathbf{a}}$ by $\theta$ is
# multiplying it, on the right, by the full-angle rotor
# $R = \cos(\theta) + \sin(\theta) * \mathbf{e}_{12}$. (This is 2D only: nothing lies
# outside the plane.) This notebook checks that claim, with the coordinates left as
# symbols, against the coordinate formula and the rotation of *Proof: Rotate*. Numbers
# appear only to draw the figure. Each check shows both sides, then their difference.

# %%
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    BLUE,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    point,
    right_angle,
    scene_around,
)
from gacalc.g2 import Bivector, Scalar, Vector, Versor
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# A general vector $\vec{\mathbf{a}}$ and an angle $\theta$:

# %%
theta: sympy.Symbol = sympy.Symbol("theta", real=True)
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2
a

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (theta, sympy.pi / 3)]

# %% [markdown]
# ## The quarter turn
#
# Multiplying by the unit bivector $\mathbf{e}_{12}$, the role $i$ plays for complex
# numbers, turns $\vec{\mathbf{a}}$ a quarter turn. Before running the cell, predict its
# coordinates.

# %%
quarter_turn: Vector = a * Bivector.e_12
quarter_turn

# %% [markdown]
# ## The rotation by $\theta$
#
# The full-angle rotor:

# %%
R: Versor = Scalar(sympy.cos(theta)) + Scalar(sympy.sin(theta)) * Bivector.e_12
R

# %% [markdown]
# The product term by term: each coordinate of $\vec{\mathbf{a}}$ times $\cos(\theta)$
# stays put, and times $\sin(\theta) * \mathbf{e}_{12}$ turns a quarter turn. First at
# the plot values:

# %%
show_mult(at_values(a, values), at_values(R, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, R)

# %% [markdown]
# The sum, $\vec{\mathbf{a}} * R$:

# %%
full_angle_result: Vector = (a * R).simplified()
full_angle_result

# %% [markdown]
# At the plot values, the quarter turn:

# %%
at_values(quarter_turn, values)

# %% [markdown]
# and $\vec{\mathbf{a}} * R$:

# %%
at_values(full_angle_result, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_QUARTER: Point = point(coordinates=list(at_values(quarter_turn, values)))
P_ROTATED: Point = point(coordinates=list(at_values(full_angle_result, values)))
fig_rotor: PendingFigure
with scene_around(points=[P_A, P_QUARTER, P_ROTATED]) as fig_rotor:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(
        head=P_QUARTER,
        color=BLUE,
        text=r"$\vec{\mathbf{a}} * \mathbf{e}_{12}$",
        align=LabelPos.l,
    )
    right_angle(corner=Point(x=0, y=0), toward_a=P_A, toward_b=P_QUARTER)
    arrow(head=P_ROTATED, color=PURPLE, text=r"$\vec{\mathbf{a}} * R$")
fig_rotor

# %% [markdown]
# ## Checks
#
# ### The coordinate formula
#
# The coordinate formula from *Proof: Rotate*,
# $(a_1 * \cos(\theta) - a_2 * \sin(\theta), a_1 * \sin(\theta) + a_2 * \cos(\theta))$:

# %%
coordinate_formula: Vector = (
    Scalar(a_1 * sympy.cos(theta) - a_2 * sympy.sin(theta))
) * Vector.e_1 + (Scalar(a_1 * sympy.sin(theta) + a_2 * sympy.cos(theta))) * Vector.e_2
coordinate_formula

# %% [markdown]
# The multiplication gave:

# %%
full_angle_result

# %% [markdown]
# Their difference:

# %%
(full_angle_result - coordinate_formula).simplified()

# %% [markdown]
# ### The rotation of *Proof: Rotate*
#
# `Vector.rotate(θ)`, the blend
# $\cos(\theta) * \vec{\mathbf{a}} + \sin(\theta) * r(\vec{\mathbf{a}}; \pi/2)$:

# %%
a.rotate(theta).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} * R$:

# %%
(full_angle_result - a.rotate(theta)).simplified()

# %% [markdown]
# ### Rotation is distributive
#
# To rotate is to multiply by $R$, and the geometric product distributes over $+$, so
# rotating a sum is rotating each piece and adding:
# $(\vec{\mathbf{a}} + \vec{\mathbf{b}}) * R = \vec{\mathbf{a}} * R + \vec{\mathbf{b}} * R$.
# A second vector $\vec{\mathbf{b}}$:

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
b

# %% [markdown]
# $(\vec{\mathbf{a}} + \vec{\mathbf{b}}) * R$:

# %%
((a + b) * R).simplified()

# %% [markdown]
# $\vec{\mathbf{a}} * R + \vec{\mathbf{b}} * R$:

# %%
(a * R + b * R).simplified()

# %% [markdown]
# Their difference:

# %%
(((a + b) * R) - (a * R + b * R)).simplified()

# %% [markdown]
# So a rotation is fixed by what it does to the two basis vectors:
# $\vec{\mathbf{a}} * R$ is
# $a_1 * (\vec{\mathbf{e}}_1 * R) + a_2 * (\vec{\mathbf{e}}_2 * R)$:

# %%
basis_decomposition: Vector = (
    Scalar(a_1) * (Vector.e_1 * R) + Scalar(a_2) * (Vector.e_2 * R)
).simplified()
basis_decomposition

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} * R$:

# %%
((a * R) - basis_decomposition).simplified()
