# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 5, projection through the product — calculations
#
# Companion to *Step 5: Projection, through the Product*. The projection of `b` onto `a`
# is `(b · a) * a⁻¹` and the rejection `(b ∧ a) * a⁻¹`; both equal Step 2's rotate,
# keep a coordinate, rotate back. Each check prints zeros when it holds.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, e_1, e_2


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def project_and_reject_by_rotation(a: Vector, b: Vector) -> tuple[Vector, Vector]:
    """Step 2: rotate ``a`` onto the x-axis, keep a coordinate of ``b``, rotate back."""
    cos: Real = a.coefficient(e_1) / a.magnitude()
    sin: Real = -a.coefficient(e_2) / a.magnitude()
    b_rotated: Vector = rotate(cos, sin, b)
    return (
        rotate(cos, -sin, Scalar(b_rotated.coefficient(e_1)) * e_1),
        rotate(cos, -sin, Scalar(b_rotated.coefficient(e_2)) * e_2),
    )


def zeros(value: MultiVectorBase) -> list[sympy.Expr]:
    """Each coefficient of ``value``, simplified -- all zeros when it is zero."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in value]


# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
by_rotation_projection: Vector
by_rotation_rejection: Vector
by_rotation_projection, by_rotation_rejection = project_and_reject_by_rotation(a, b)

# %% [markdown]
# ## The inverse of a vector
#
# `a⁻¹ = a / |a|^2`, and `a * a⁻¹ = 1`.

# %%
zeros(a.inverse() - Scalar(1 / (a_1**2 + a_2**2)) * a)  # -> [0, 0]

# %%
zeros(a * a.inverse() - Scalar(1))  # -> [0, 0]

# %% [markdown]
# ## Projection: `(b · a) * a⁻¹`, the plain-number part of `b * a` times `a⁻¹`

# %%
projection: Vector = Scalar((b * a).scalar_part()) * a.inverse()
zeros(projection - by_rotation_projection)  # -> [0, 0]

# %% [markdown]
# ## Rejection: `(b ∧ a) * a⁻¹`

# %%
rejection: MultiVectorBase = b.wedge(a) * a.inverse()
zeros(rejection - by_rotation_rejection)  # -> [0, 0]

# %% [markdown]
# ## Together they give back `b`: `b * a * a⁻¹ = b`

# %%
zeros(b * a * a.inverse() - b)  # -> [0, 0]

# %% [markdown]
# ## The library's projection and rejection agree

# %%
zeros(projection - b.projected_onto(a))  # -> [0, 0]

# %%
zeros(rejection - b.rejected_away_from(a))  # -> [0, 0]
