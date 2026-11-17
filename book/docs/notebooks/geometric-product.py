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
# with the coordinates left as symbols, against the coordinate formula and gacalc's own
# rotation. Each check cell subtracts two things and shows the difference, $0$ when they
# agree.

# %%
import sympy

from gacalc.g2 import Bivector, Scalar, Vector, Versor
from gacalc.nbdisplay import show_mult
from gacalc.transforms import plane_rotation

# %% [markdown]
# A general vector $a$ and an angle $\theta$:

# %%
theta: sympy.Symbol = sympy.Symbol("theta", real=True)
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2", real=True)
a: Vector = Scalar(a_1) * Vector.e_1 + Scalar(a_2) * Vector.e_2

# %% [markdown]
# ## The quarter turn
#
# Multiplying by the unit bivector $e_{12}$, the role $i$ plays for complex numbers,
# turns $a$ a quarter turn. Before running the cell, predict its coordinates.

# %%
a * Bivector.e_12

# %% [markdown]
# ## The rotation by $\theta$
#
# Multiplying on the right by $R$:

# %%
R: Versor = Scalar(sympy.cos(theta)) + Scalar(sympy.sin(theta)) * Bivector.e_12
full_angle_result: Vector = (a * R).simplified()
full_angle_result

# %% [markdown]
# The same product term by term: each coordinate of $a$ times $\cos(\theta)$ stays
# put, and times $\sin(\theta) * e_{12}$ turns a quarter turn.

# %%
show_mult(a, R)

# %% [markdown]
# ## Checks
#
# The coordinate formula from *Proof: Rotate*,
# $(a_1 * \cos(\theta) - a_2 * \sin(\theta), a_1 * \sin(\theta) + a_2 * \cos(\theta))$.
# The multiplication lands on exactly those two coordinates:

# %%
coordinate_formula: Vector = (
    Scalar(a_1 * sympy.cos(theta) - a_2 * sympy.sin(theta))
) * Vector.e_1 + (Scalar(a_1 * sympy.sin(theta) + a_2 * sympy.cos(theta))) * Vector.e_2
(full_angle_result - coordinate_formula).simplified()

# %% [markdown]
# gacalc's own rotation in the $e_1 \to e_2$ plane, by the same angle, agrees. (It
# uses the half-angle rotor $\cos(\theta/2) - \sin(\theta/2) * e_{12}$ applied on
# both sides, $R * v * \tilde{R}$.)

# %%
gacalc_result: Vector = plane_rotation(Vector.e_1, Vector.e_2)(theta)(a).simplified()
(full_angle_result - gacalc_result).simplified()

# %% [markdown]
# ## Rotation is distributive
#
# To rotate is to multiply by $R$, and the geometric product distributes over $+$, so
# rotating a sum is rotating each piece and adding: $(a + b) * R = a * R + b * R$.

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b: Vector = Scalar(b_1) * Vector.e_1 + Scalar(b_2) * Vector.e_2
(((a + b) * R) - (a * R + b * R)).simplified()

# %% [markdown]
# So a rotation is fixed by what it does to the two basis vectors: $a * R$ is
# $a_1 * (e_1 * R) + a_2 * (e_2 * R)$.

# %%
basis_decomposition: Vector = Scalar(a_1) * (Vector.e_1 * R) + Scalar(a_2) * (
    Vector.e_2 * R
)
((a * R) - basis_decomposition).simplified()
