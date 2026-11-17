# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The Geometric Product — rotation is a multiplication
#
# In the complex numbers, multiplying by $i$ turns a point a quarter turn, and
# multiplying by $\cos(\theta) + \sin(\theta) * i$ turns it by $\theta$. The chapter
# claims the same for vectors in the plane: rotating $a$ by $\theta$ is multiplying it,
# on the right, by the full-angle rotor $R = \cos(\theta) + \sin(\theta) * e_{12}$.
# (This is 2D only: nothing lies outside the plane.) This notebook checks that claim,
# with the coordinates left as symbols, against the coordinate formula and the rotation
# of *Proof: Rotate*. Numbers appear only to draw the figure. Each check shows both
# sides, then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _bootstrap_live import (
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

from gacalc.base import Real
from gacalc.g2 import Bivector, Scalar, Vector, Versor
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# A general vector $a$ and an angle $\theta$:

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
# Multiplying by the unit bivector $e_{12}$, the role $i$ plays for complex numbers,
# turns $a$ a quarter turn. Before running the cell, predict its coordinates.

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
# The product term by term: each coordinate of $a$ times $\cos(\theta)$ stays put, and
# times $\sin(\theta) * e_{12}$ turns a quarter turn.

# %%
show_mult(a, R)

# %% [markdown]
# The sum, $a * R$:

# %%
full_angle_result: Vector = (a * R).simplified()
full_angle_result

# %% [markdown]
# At the plot values, the quarter turn:

# %%
at_values(quarter_turn, values)

# %% [markdown]
# and $a * R$:

# %%
at_values(full_angle_result, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_QUARTER: Point = point(coordinates=list(at_values(quarter_turn, values)))
P_ROTATED: Point = point(coordinates=list(at_values(full_angle_result, values)))
fig_rotor: PendingFigure
with scene_around(points=[P_A, P_QUARTER, P_ROTATED]) as fig_rotor:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_QUARTER, color=BLUE, text=r"$\vec{a} * e_{12}$", align=LabelPos.l)
    right_angle(corner=Point(x=0, y=0), toward_a=P_A, toward_b=P_QUARTER)
    arrow(head=P_ROTATED, color=PURPLE, text=r"$\vec{a} * R$")
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
# `Vector.rotate(θ)`, the blend $\cos(\theta) * a + \sin(\theta) * r(a; \pi/2)$:

# %%
a.rotate(theta).simplified()

# %% [markdown]
# Its difference from $a * R$:

# %%
(full_angle_result - a.rotate(theta)).simplified()

# %% [markdown]
# ### Rotation is distributive
#
# To rotate is to multiply by $R$, and the geometric product distributes over $+$, so
# rotating a sum is rotating each piece and adding: $(a + b) * R = a * R + b * R$. A
# second vector $b$:

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
b

# %% [markdown]
# $(a + b) * R$:

# %%
((a + b) * R).simplified()

# %% [markdown]
# $a * R + b * R$:

# %%
(a * R + b * R).simplified()

# %% [markdown]
# Their difference:

# %%
(((a + b) * R) - (a * R + b * R)).simplified()

# %% [markdown]
# So a rotation is fixed by what it does to the two basis vectors: $a * R$ is
# $a_1 * (e_1 * R) + a_2 * (e_2 * R)$:

# %%
basis_decomposition: Vector = (
    Scalar(a_1) * (Vector.e_1 * R) + Scalar(a_2) * (Vector.e_2 * R)
).simplified()
basis_decomposition

# %% [markdown]
# Its difference from $a * R$:

# %%
((a * R) - basis_decomposition).simplified()
