# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 2, projection from rotation — calculations
#
# Companion to *Step 2: Projection, from Rotation*. Rotate `a` onto the x-axis (the
# cosine and sine read off `a`), keep `b`'s x-coordinate (projection) or y-coordinate
# (rejection), rotate back. Only the rotation of Step 1 is used. Each check prints
# `[0, 0]` when it holds.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def project_and_reject(a: Vector, b: Vector) -> tuple[Vector, Vector]:
    """Project and reject ``b`` onto ``a``: rotate ``a`` to the x-axis and back."""
    cos: Real = a.coefficient(e_1) / a.magnitude()
    sin: Real = -a.coefficient(e_2) / a.magnitude()
    b_rotated: Vector = rotate(cos, sin, b)  # a now lies on the x-axis
    projection: Vector = rotate(cos, -sin, Scalar(b_rotated.coefficient(e_1)) * e_1)
    rejection: Vector = rotate(cos, -sin, Scalar(b_rotated.coefficient(e_2)) * e_2)
    return projection, rejection


def zeros(v: Vector) -> list[sympy.Expr]:
    """Each coordinate of ``v``, simplified -- ``[0, 0]`` when ``v`` is zero."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in v]


# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
projection: Vector
rejection: Vector
projection, rejection = project_and_reject(a, b)

# %% [markdown]
# ## The formula
#
# The projection of `b` onto `a` is `(a_1 * b_1 + a_2 * b_2) / (a_1^2 + a_2^2)` times
# `a`.

# %%
formula: Vector = Scalar((a_1 * b_1 + a_2 * b_2) / (a_1**2 + a_2**2)) * a
zeros(projection - formula)  # -> [0, 0]

# %% [markdown]
# ## The two parts add back to `b`

# %%
zeros(projection + rejection - b)  # -> [0, 0]

# %% [markdown]
# ## Projecting twice changes nothing, and `a` projects to itself

# %%
projection_again: Vector
projection_again, _ = project_and_reject(a, projection)
zeros(projection_again - projection)  # -> [0, 0]

# %%
a_projected: Vector
a_projected, _ = project_and_reject(a, a)
zeros(a_projected - a)  # -> [0, 0]

# %% [markdown]
# ## The rejection has no part along `a`

# %%
rejection_along_a: Vector
rejection_along_a, _ = project_and_reject(a, rejection)
zeros(rejection_along_a)  # -> [0, 0]

# %% [markdown]
# ## The library's projection agrees
#
# gacalc's `projected_onto` computes `(b · a) * a⁻¹`, the form Step 5 derives.

# %%
zeros(projection - b.projected_onto(a))  # -> [0, 0]
