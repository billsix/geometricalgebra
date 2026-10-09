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
# Companion to the *Proof: Projection by Rotating to Standard Position* chapter. We
# check that the standard-position construction — rotate `b` onto the x-axis with a
# single elementary 2D rotation, keep the x-coordinate, rotate back — lands on the same
# answer as gacalc's geometric-algebra projection `projected_onto`.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Vector, e_1, e_2
from gacalc.g3 import e_1 as e3_1
from gacalc.g3 import e_2 as e3_2
from gacalc.g3 import e_3 as e3_3
from gacalc.standardposition import project_sp, reject_sp

# %% [markdown]
# ## The construction, in two dimensions
#
# One plane, one rotation. Read the cosine and sine straight off `b`'s coordinates
# (`cos(-θ) = b_1 / |b|`, `sin(-θ) = -b_2 / |b|`), rotate both `a` and `b` by `-θ` so
# `b` lands on the x-axis, keep `a`'s x-coordinate (projection) and y-coordinate
# (rejection), then
# rotate back. No dot product, no geometric product — only the 2D rotation.


# %%
def project_and_reject_sp(a: Vector, b: Vector) -> tuple[Vector, Vector]:
    """Project and reject `a` onto `b` by reduction to standard position."""
    b_1: Real = b.coefficient(e_1)
    b_2: Real = b.coefficient(e_2)
    magnitude: Real = b.magnitude()
    cos: Real = b_1 / magnitude
    sin: Real = -b_2 / magnitude

    def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
        """The plain 2D rotation on the (e_1, e_2) components."""
        x: Real = v.coefficient(e_1)
        y: Real = v.coefficient(e_2)
        return (cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2

    a_aligned: Vector = rotate(cos, sin, a)  # b is now on the x-axis; a rides along
    a_aligned_1: Real = a_aligned.coefficient(e_1)
    a_aligned_2: Real = a_aligned.coefficient(e_2)
    # rotate back (negate the sine): the kept x-part is the projection, the
    # y-part the rejection
    projection: Vector = rotate(cos, -sin, a_aligned_1 * e_1)
    rejection: Vector = rotate(cos, -sin, a_aligned_2 * e_2)
    return projection, rejection


# %% [markdown]
# ## A concrete example
#
# Project `a` onto `b`, both ordinary plane vectors. The standard-position
# projection and the canonical Hestenes projection agree.

# %%
a: Vector = 2.0 * e_1 + 5.0 * e_2
b: Vector = 1.0 * e_1 + 2.0 * e_2
projection: Vector
rejection: Vector
projection, rejection = project_and_reject_sp(a, b)
projection  # rotate b to the x-axis, keep a's x, rotate back

# %%
a.projected_onto(b)  # the canonical (a . b) b^-1 -- same vector

# %% [markdown]
# ## Symbolically, for any `a`
#
# We keep `b = 3 * e_1 + 4 * e_2`, whose length is `5` — exact — so the rotation has
# rational cosine and sine and the symbolic comparison stays clean. For a fully
# general `a`, the difference between the two projections is zero in every coordinate.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2")
a_symbolic: Vector = a_1 * e_1 + a_2 * e_2
b_exact: Vector = 3 * e_1 + 4 * e_2

projection_symbolic: Vector
rejection_symbolic: Vector
projection_symbolic, rejection_symbolic = project_and_reject_sp(a_symbolic, b_exact)
difference: Vector = projection_symbolic - a_symbolic.projected_onto(b_exact)
[sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference]  # -> [0, 0]

# %% [markdown]
# ## ...and for any `b` too
#
# Nothing above depended on `b = 3 * e_1 + 4 * e_2`; it only kept the printing short.
# With `b` symbolic as well, `|b| = sqrt(b_1^2 + b_2^2)` appears inside the cosine and
# sine, and the difference between the two projections still simplifies to zero in
# both coordinates — so the rotate / keep-x / rotate-back construction equals the
# geometric-algebra projection for *every* `a` and `b`.

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b_symbolic: Vector = b_1 * e_1 + b_2 * e_2
projection_general: Vector
projection_general, _ = project_and_reject_sp(a_symbolic, b_symbolic)
difference_general: Vector = projection_general - a_symbolic.projected_onto(b_symbolic)
[
    sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference_general
]  # -> [0, 0]

# %% [markdown]
# ## Projection plus rejection rebuild the vector
#
# The part of `a` along `b` (projection) plus the part across `b` (rejection) is `a`
# again — split by standard position and reassembled.

# %%
[
    sympy.simplify(sympy.sympify(c))
    for c in (projection_symbolic + rejection_symbolic - a_symbolic)
]  # -> [0, 0]

# %% [markdown]
# ## Stepping up to three dimensions
#
# In space one rotation is not enough, so `gacalc.standardposition.project_sp` does
# it one plane at a time (swing the `xy`-shadow onto the x-axis, then fold the
# `z`-part down). The same equivalence holds: the standard-position projection equals
# the Hestenes one. Here `b = 3 * e_1 + 4 * e_2 + 12 * e_3` has an exact length `13`,
# so the symbolic check stays clean.

# %%
a_3: sympy.Symbol = sympy.symbols("a_3")
a_3d: g3.Vector = a_1 * e3_1 + a_2 * e3_2 + a_3 * e3_3
b_3d: g3.Vector = 3 * e3_1 + 4 * e3_2 + 12 * e3_3
difference_3d: MultiVectorBase = project_sp(a_3d, b_3d) - a_3d.projected_onto(b_3d)
[
    sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference_3d
]  # -> [0, 0, 0]

# %%
project_sp(a_3d, b_3d) + reject_sp(a_3d, b_3d) == a_3d
