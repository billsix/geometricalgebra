# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection in space, one plane at a time — calculations
#
# Companion to the *Proof: Projection in Space, One Plane at a Time* chapter. In the
# plane, projecting $a$ onto $b$ took one rotation: turn $b$ onto the x-axis, keep the
# x-coordinate, turn back. In space one rotation is not enough, so the construction
# turns one plane at a time: first the $xy$-shadow of $b$ onto the x-axis, then the
# $z$-part down. This notebook checks that the result is still the projection, and
# that projection and rejection still add back to $a$. The Lean theorems are
# `projectSP_eq_proj` and `rejectSP_eq_reject` in
# `proofs/GacalcProofs/StandardPosition.lean`.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.g3 import Scalar, e_1, e_2, e_3
from gacalc.standardposition import project_sp, reject_sp

# %% [markdown]
# ## The vectors
#
# $a$ is fully symbolic, so the checks hold for every $a$. The vector
# $b = 3 * e_1 + 4 * e_2 + 12 * e_3$ has an exact length: its $xy$-shadow has length
# $\sqrt{3^2 + 4^2} = 5$, and $|b| = \sqrt{5^2 + 12^2} = 13$. Both rotations then
# have rational cosines and sines, and the symbolic results stay short.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
a: g3.Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2 + Scalar(a_3) * e_3
b: g3.Vector = 3 * e_1 + 4 * e_2 + 12 * e_3

# %% [markdown]
# ## The construction
#
# `project_sp(a, b)` is the plane-at-a-time construction:

# %%
projection: MultiVectorBase = project_sp(a, b).simplified()
projection

# %% [markdown]
# ## Checks
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The construction is the projection $\operatorname{proj}_b(a) = (a \cdot b) * b^{-1}$:

# %%
(projection - a.projected_onto(b)).simplified()

# %% [markdown]
# The projection plus the rejection is $a$ again:

# %%
(project_sp(a, b) + reject_sp(a, b) - a).simplified()
