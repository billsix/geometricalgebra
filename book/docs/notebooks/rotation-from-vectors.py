# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # A Rotation from Two Vectors — No Angle
#
# In precalculus,
#
# $$\cos(\beta - \alpha) = \cos(\alpha) * \cos(\beta) + \sin(\alpha) * \sin(\beta)$$
#
# is an identity to memorize. The chapter claims that the
# geometric product of two vectors *is* the rotation from one to the other, with no
# angle ever named, and that identity falls out of the multiplication. This notebook
# checks it with gacalc and sympy: the product of two unit vectors is the full-angle
# rotor, multiplying the first by it on the right lands on the second, and the versor
# and projection routes to a rotation agree. Each check cell subtracts two things and
# shows the difference, $0$ when they agree.

# %%
import sympy

from gacalc.base import MultiVectorBase
from gacalc.g2 import Scalar, Vector, Versor
from gacalc.nbdisplay import show_mult
from gacalc.transforms import projection_rotation, versor_rotation

# %% [markdown]
# ## Two unit vectors
#
# $\hat{a}$ at angle $\alpha$ from the x-axis and $\hat{b}$ at angle $\beta$:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = (
    Scalar(sympy.cos(alpha)) * Vector.e_1 + Scalar(sympy.sin(alpha)) * Vector.e_2
)
b_hat: Vector = (
    Scalar(sympy.cos(beta)) * Vector.e_1 + Scalar(sympy.sin(beta)) * Vector.e_2
)

# %% [markdown]
# ## Their product
#
# A plain number plus a bivector, the dot and the wedge. Before running the cell,
# predict it: it is the full-angle rotor $\cos(\theta) + \sin(\theta) * e_{12}$ with
# $\theta = \beta - \alpha$. We multiplied the vectors, and the cosine and sine
# appeared.

# %%
R: Versor = (a_hat * b_hat).simplified()
R

# %% [markdown]
# The same product term by term. The plain-number rows add to
# $\cos(\alpha) * \cos(\beta) + \sin(\alpha) * \sin(\beta)$, which is
# $\cos(\beta - \alpha)$, and the $e_{12}$ rows to $\sin(\beta - \alpha)$: the
# angle-difference identities, from multiplying.

# %%
show_mult(a_hat, b_hat)

# %% [markdown]
# ## The rotor carries $\hat{a}$ to $\hat{b}$
#
# Multiply $\hat{a}$ on the right by $\hat{a} * \hat{b}$. By associativity and
# $\hat{a} * \hat{a} = 1$ (a unit vector squares to one), the first vector cancels
# and $\hat{b}$ is left: $\hat{a} * (\hat{a} * \hat{b}) = \hat{b}$. No angle is
# named.

# %%
(a_hat * R - b_hat).simplified()

# %% [markdown]
# ## Vectors of any length
#
# Two routes build a rotation from two vectors alone, with no angle argument:
# `versor_rotation` (the versor sandwich $R * v * R^{-1}$) and `projection_rotation`
# (projection, rejection and the geometric product). They give the same rotation
# whatever the lengths of the inputs. Take two vectors that are not unit length:

# %%
frm: Vector = 2 * Vector.e_1
to: Vector = 1 * Vector.e_1 + 1 * Vector.e_2
v: Vector = 1 * Vector.e_1

# %% [markdown]
# The two routes agree on $v$:

# %%
rotated_versor: Vector = versor_rotation(from_vector=frm, to_vector=to)(v)
rotated_projection: MultiVectorBase = projection_rotation(
    from_vector=frm, to_vector=to
)(v)
(rotated_versor - rotated_projection).simplified()

# %% [markdown]
# ## It carries `frm` onto the direction of `to`
#
# Applied to `frm` itself, the rotation lands on $(|frm| / |to|) * to$: `to`'s
# direction, with `frm`'s length (the Lean `projRotation_carries_from_to`).

# %%
carried: MultiVectorBase = projection_rotation(from_vector=frm, to_vector=to)(frm)
expected: Vector = Scalar(frm.magnitude() / to.magnitude()) * to
(carried - expected).simplified()

# %% [markdown]
# So the versor route, the projection route, and the angle-based three-turn
# construction of *Proof: Rotate from a to b* are one and the same rotation, a fact
# the Lean proofs state directly (`fullAngleRotorFromTo_carry`,
# `projRotation_carries_from_to` / `projRotation_eq_sandwich`). The angle was
# scaffolding; the two vectors, multiplied, are the rotation.
