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

from gacalc.g2 import e_1, e_2
from gacalc.g3 import e_1 as e3_1
from gacalc.g3 import e_2 as e3_2
from gacalc.g3 import e_3 as e3_3
from gacalc.standardposition import project_sp, reject_sp

# %% [markdown]
# ## The construction, in two dimensions
#
# One plane, one rotation. Read the cosine and sine straight off `b`'s coordinates
# (`cos = b_x / |b|`, `sin = -b_y / |b|`), rotate both `a` and `b` by `-φ` so `b` lands
# on the x-axis, keep `a`'s x-coordinate (projection) and y-coordinate (rejection), then
# rotate back. No dot product, no geometric product — only the 2D rotation.


# %%
def project_and_reject_sp(a, b):
    b_x, b_y = b.coefficient(e_1), b.coefficient(e_2)
    magnitude = b.magnitude()
    cos, sin = b_x / magnitude, -b_y / magnitude

    def rotate(cos, sin, v):  # the plain 2D rotation on the (e_1, e_2) components
        x, y = v.coefficient(e_1), v.coefficient(e_2)
        return (cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2

    a_aligned = rotate(cos, sin, a)  # b is now on the x-axis; a rides along
    a_x, a_y = a_aligned.coefficient(e_1), a_aligned.coefficient(e_2)
    # rotate back (negate the sine): the kept x-part is the projection, the
    # y-part the rejection
    projection = rotate(cos, -sin, a_x * e_1)
    rejection = rotate(cos, -sin, a_y * e_2)
    return projection, rejection


# %% [markdown]
# ## A concrete example
#
# Project `a` onto `b`, both ordinary plane vectors. The standard-position
# projection and the canonical Hestenes projection agree.

# %%
a = 2.0 * e_1 + 5.0 * e_2
b = 1.0 * e_1 + 2.0 * e_2
projection, rejection = project_and_reject_sp(a, b)
projection  # rotate b to the x-axis, keep a's x, rotate back

# %%
a.projected_onto(b)  # the canonical (a . b) b^-1 -- same vector

# %% [markdown]
# ## Symbolically, for any `a`
#
# We keep `b = 3 e_1 + 4 e_2`, whose length is `5` — exact — so the rotation has
# rational cosine and sine and the symbolic comparison stays clean. For a fully
# general `a`, the difference between the two projections is zero in every coordinate.

# %%
a_1, a_2 = sympy.symbols("a_1 a_2")
a_symbolic = a_1 * e_1 + a_2 * e_2
b_exact = 3 * e_1 + 4 * e_2

projection_symbolic, rejection_symbolic = project_and_reject_sp(a_symbolic, b_exact)
difference = projection_symbolic - a_symbolic.projected_onto(b_exact)
[sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference]  # -> [0, 0]

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
# the Hestenes one. Here `b = 3 e_1 + 4 e_2 + 12 e_3` has an exact length `13`, so the
# symbolic check stays clean.

# %%
a_3d = a_1 * e3_1 + a_2 * e3_2 + sympy.symbols("a_3") * e3_3
b_3d = 3 * e3_1 + 4 * e3_2 + 12 * e3_3
difference_3d = project_sp(a_3d, b_3d) - a_3d.projected_onto(b_3d)
[
    sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference_3d
]  # -> [0, 0, 0]

# %%
project_sp(a_3d, b_3d) + reject_sp(a_3d, b_3d) == a_3d
