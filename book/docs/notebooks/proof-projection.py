# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection by standard position — calculations
#
# Companion to the *Proof: Projection by Rotating to Standard Position* chapter.
# Projecting onto the x-axis is easy: keep the x-coordinate. The chapter projects onto
# any $b$ by making $b$ the x-axis for a moment: rotate so that $b$ lies on the x-axis,
# keep the x-coordinate (the projection) and the y-coordinate (the rejection), then
# rotate back. This notebook runs that construction and checks it against gacalc's
# projection, first on numbers and then for every $a$ and $b$. The Lean theorem is
# `projectSP_eq_proj` in `proofs/GacalcProofs/StandardPosition.lean`.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2

# %% [markdown]
# ## The construction
#
# The cosine and sine of the rotation are read straight off $b$'s coordinates:
# $\cos(-\theta) = b_1 / |b|$ and $\sin(-\theta) = -b_2 / |b|$, with $\theta$ the angle
# of $b$. The rotation is the plain 2D one,
# $\cos(\theta) * v + \sin(\theta) * r(v; \pi/2)$: no dot product and no geometric
# product.


# %%
def project_and_reject_sp(a: Vector, b: Vector) -> tuple[Vector, Vector]:
    """Project and reject ``a`` onto ``b`` by reduction to standard position."""
    magnitude: Real = b.magnitude()
    cos: Real = b.coefficient(e_1) / magnitude
    sin: Real = -b.coefficient(e_2) / magnitude

    def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
        """The plain 2D rotation: a blend of ``v`` and its quarter turn."""
        return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()

    a_aligned: Vector = rotate(cos, sin, a)
    projection: Vector = rotate(cos, -sin, Scalar(a_aligned.coefficient(e_1)) * e_1)
    rejection: Vector = rotate(cos, -sin, Scalar(a_aligned.coefficient(e_2)) * e_2)
    return projection, rejection


# %% [markdown]
# ## A worked example
#
# Two ordinary vectors:

# %%
a: Vector = 2 * e_1 + 5 * e_2
b: Vector = 1 * e_1 + 2 * e_2

# %% [markdown]
# Rotating by $-\theta$ puts $b$ on the x-axis, and $a$ rides along. Its coordinates
# there are how far $a$ reaches along $b$ and how far across it:

# %%
magnitude_b: Real = b.magnitude()
a_aligned: Vector = (
    Scalar(b.coefficient(e_1) / magnitude_b) * a
    + Scalar(-b.coefficient(e_2) / magnitude_b) * a.rotate_90_degrees()
).simplified()
a_aligned

# %% [markdown]
# Keeping the x-coordinate and rotating back gives the projection of $a$ onto $b$:

# %%
projection: Vector
rejection: Vector
projection, rejection = project_and_reject_sp(a, b)
projection.simplified()

# %% [markdown]
# and keeping the y-coordinate gives the rejection:

# %%
rejection.simplified()

# %% [markdown]
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The construction is gacalc's projection, $(a \cdot b) * b^{-1}$:

# %%
(projection - a.projected_onto(b)).simplified()

# %% [markdown]
# The projection plus the rejection is $a$ again:

# %%
(projection + rejection - a).simplified()

# %% [markdown]
# ## For any $a$
#
# Now $a$ is symbolic. $b = 3 * e_1 + 4 * e_2$ has length $5$ exactly, so the cosine
# and sine of its angle are the fractions $3/5$ and $4/5$, and the result stays short.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2")
a_symbolic: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b_exact: Vector = 3 * e_1 + 4 * e_2
projection_symbolic: Vector
rejection_symbolic: Vector
projection_symbolic, rejection_symbolic = project_and_reject_sp(a_symbolic, b_exact)

# %% [markdown]
# The construction is gacalc's projection for every $a$:

# %%
(projection_symbolic - a_symbolic.projected_onto(b_exact)).simplified()

# %% [markdown]
# The projection plus the rejection is $a$:

# %%
(projection_symbolic + rejection_symbolic - a_symbolic).simplified()

# %% [markdown]
# ## For any $a$ and $b$
#
# Nothing above depended on $b = 3 * e_1 + 4 * e_2$; it only kept the results short.
# With $b$ symbolic too, $|b| = \sqrt{b_1^2 + b_2^2}$ appears inside the cosine and
# sine, and the difference is still zero: the rotate, keep-x, rotate-back construction
# is the projection for every $a$ and $b$.

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b_symbolic: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
projection_general: Vector
projection_general, _ = project_and_reject_sp(a_symbolic, b_symbolic)
(projection_general - a_symbolic.projected_onto(b_symbolic)).simplified()
