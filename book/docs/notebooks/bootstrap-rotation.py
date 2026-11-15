# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 1, rotation — calculations
#
# Companion to *Step 1: Rotation, from Precalculus*. The rotation is the blend
# `cos(θ) * v + sin(θ) * r(v; π/2)`, where `r(v; π/2) = (-v_2, v_1)` is the quarter
# turn (`Vector.rotate_90_degrees()`, a swap of the coordinates). Every check below
# leaves the coordinates and angles as symbols, and each prints `[0, 0]` (or `0`)
# when it holds.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle whose cosine and sine are ``cos`` and ``sin``."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def zeros(v: Vector) -> list[sympy.Expr]:
    """Each coordinate of ``v``, simplified -- ``[0, 0]`` when ``v`` is zero."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in v]


# %%
r: sympy.Symbol
beta: sympy.Symbol
theta: sympy.Symbol
phi: sympy.Symbol
r, beta, theta, phi = sympy.symbols("r beta theta phi", real=True)
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2

# %% [markdown]
# ## The formula
#
# A vector of length `r` at angle `β`, rotated by `θ`, lands at length `r` and angle
# `β + θ`.

# %%
polar: Vector = Scalar(r * sympy.cos(beta)) * e_1 + Scalar(r * sympy.sin(beta)) * e_2
expected: Vector = (
    Scalar(r * sympy.cos(beta + theta)) * e_1
    + Scalar(r * sympy.sin(beta + theta)) * e_2
)
zeros(rotate(sympy.cos(theta), sympy.sin(theta), polar) - expected)  # -> [0, 0]

# %% [markdown]
# ## A rotation keeps length

# %%
rotated: Vector = rotate(sympy.cos(theta), sympy.sin(theta), v)
sympy.simplify(
    sympy.sympify(rotated.magnitude_squared() - v.magnitude_squared())
)  # -> 0

# %% [markdown]
# ## Rotations add their angles, and the negated sine undoes a rotation

# %%
twice: Vector = rotate(sympy.cos(phi), sympy.sin(phi), rotated)
once: Vector = rotate(sympy.cos(theta + phi), sympy.sin(theta + phi), v)
zeros(twice - once)  # -> [0, 0]

# %%
zeros(rotate(sympy.cos(theta), -sympy.sin(theta), rotated) - v)  # -> [0, 0]

# %% [markdown]
# ## A rotation is linear

# %%
w_1: sympy.Symbol
w_2: sympy.Symbol
k: sympy.Symbol
w_1, w_2, k = sympy.symbols("w_1 w_2 k", real=True)
w: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
c: sympy.Expr = sympy.cos(theta)
s: sympy.Expr = sympy.sin(theta)
zeros(rotate(c, s, v + w) - (rotate(c, s, v) + rotate(c, s, w)))  # -> [0, 0]

# %%
zeros(rotate(c, s, Scalar(k) * v) - Scalar(k) * rotate(c, s, v))  # -> [0, 0]

# %% [markdown]
# ## The library's rotation agrees
#
# gacalc's `Vector.rotate(θ)` is the same blend.

# %%
zeros(v.rotate(theta) - rotated)  # -> [0, 0]
