# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 4, the product from projection — calculations
#
# Companion to *Step 4: The Geometric Product, from Projection*. Measure `b` in `a`'s
# standard position (Step 2), get `x` along and `y` across, and build
# `|a| * (x + y * e_12)`. It is gacalc's geometric product `a * b`. Each check prints
# zeros when it holds.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2, e_12


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def product_from_projection(a: Vector, b: Vector) -> Versor:
    """``|a| * (x + y * e_12)``, with ``(x, y)`` the coordinates of ``b`` in ``a``'s
    standard position."""
    b_measured: Vector = rotate(
        a.coefficient(e_1) / a.magnitude(), -a.coefficient(e_2) / a.magnitude(), b
    )
    return Scalar(a.magnitude()) * (
        Scalar(b_measured.coefficient(e_1)) + Scalar(b_measured.coefficient(e_2)) * e_12
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

# %% [markdown]
# ## The product from projection
#
# `(a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * e_12`:

# %%
product: Versor = product_from_projection(a, b).simplified()
product

# %% [markdown]
# ## It is the product of the multiplication rules

# %%
zeros(product - a * b)  # -> [0, 0]

# %% [markdown]
# ## Its parts are the dot product and the wedge

# %%
zeros(a * b - (a.dot(b) + a.wedge(b)))  # -> [0, 0]

# %% [markdown]
# ## A vector times itself is its length squared

# %%
zeros(b * b - Scalar(b_1**2 + b_2**2))  # -> [0, 0]

# %% [markdown]
# ## Two unit vectors multiply to the cosine and sine of the angle between them
#
# Unit vectors at angles `α` and `β`; the angle from the first to the second is
# `θ = β - α`.

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
theta: sympy.Expr = beta - alpha
zeros(
    a_hat * b_hat - (Scalar(sympy.cos(theta)) + Scalar(sympy.sin(theta)) * e_12)
)  # -> [0, 0]

# %% [markdown]
# ## The quarter turn is a product
#
# `v * e_12` is Step 1's quarter turn `(-v_2, v_1)`.

# %%
zeros(b * e_12 - b.rotate_90_degrees())  # -> [0, 0]

# %% [markdown]
# ## Dot and wedge through projection and rejection
#
# `a * proj_a(b)` is the dot product and `a * rej_a(b)` is the wedge. gacalc's
# `projected_onto` and `rejected_away_from` compute the projection and rejection; the
# Step 2 notebook checks that they agree with Step 2's construction.

# %%
projection: Vector = b.projected_onto(a)
rejection: Vector = b.rejected_away_from(a)
zeros(a * projection - a.dot(b))  # -> [0, 0]

# %%
zeros(a * rejection - a.wedge(b))  # -> [0, 0]

# %%
zeros(a * b - (a * projection + a * rejection))  # -> [0, 0]

# %% [markdown]
# ## Measuring the other way: the dot keeps its value, the wedge changes sign

# %%
zeros(b * a.projected_onto(b) - a.dot(b))  # -> [0, 0]

# %%
zeros(b * a.rejected_away_from(b) + a.wedge(b))  # -> [0, 0]
