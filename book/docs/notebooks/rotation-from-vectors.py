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
# The chapter claims that the geometric product of two vectors *is* the rotation
# from one to the other, with no angle ever named. We check that symbolically in
# gacalc: the product of two unit vectors is the full-angle rotor, right-multiplying
# the first by it lands on the second, and the versor and projection routes agree.

# %%
import sympy

from gacalc.base import MultiVectorBase
from gacalc.g2 import Vector, Versor
from gacalc.transforms import projection_rotation, versor_rotation

# Two unit vectors, at angles alpha and beta from the x-axis.
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)

a_hat: Vector = sympy.cos(alpha) * Vector.e_1 + sympy.sin(alpha) * Vector.e_2
b_hat: Vector = sympy.cos(beta) * Vector.e_1 + sympy.sin(beta) * Vector.e_2

# %%
# Their geometric product is a scalar plus a bivector -- the dot product and the
# wedge -- which is exactly the full-angle rotor cos(theta) + sin(theta) * e_12,
# with theta = beta - alpha. We multiplied the vectors; the cos and sin appeared.
R: Versor = (a_hat * b_hat).simplified()
R

# %% [markdown]
# **The rotor carries `a_hat` to `b_hat`.** Right-multiply `a_hat` by the product
# `a_hat * b_hat`; by associativity and `a_hat * a_hat == 1` (a unit vector squares
# to one), the first vector cancels and `b_hat` is left. No angle is named.

# %%
# a_hat * (a_hat * b_hat) - b_hat  ==  0
(a_hat * R - b_hat).simplified()

# %% [markdown]
# **Vectors of any length.** The two routes `transforms.versor_rotation` (the versor
# sandwich `R * v * R^-1`) and `transforms.projection_rotation` (project/reject +
# the geometric product) both build the rotation from the two vectors alone -- no
# angle argument -- and give the same rotation whatever the inputs' magnitudes. Take
# two vectors that are *not* unit length.

# %%
frm: Vector = 2 * Vector.e_1
to: Vector = 1 * Vector.e_1 + 1 * Vector.e_2
v: Vector = 1 * Vector.e_1

rotated_versor: Vector = versor_rotation(from_vector=frm, to_vector=to)(v)
rotated_projection: MultiVectorBase = projection_rotation(
    from_vector=frm, to_vector=to
)(v)

# the versor route and the projection route agree -- the difference is zero.
(rotated_versor - rotated_projection).simplified()

# %% [markdown]
# **It carries `frm` onto the direction of `to`.** Applied to `frm` itself, the
# rotation lands on `(|frm| / |to|) * to` -- `to`'s direction, with `frm`'s length
# (the Lean `projRotation_carries_from_to`).

# %%
carried: MultiVectorBase = projection_rotation(from_vector=frm, to_vector=to)(frm)
expected: Vector = (frm.magnitude() / to.magnitude()) * to

(carried - expected).simplified()

# %% [markdown]
# So the versor route, the projection route, and the angle-based three-turn
# construction of *Proof: Rotate from a to b* are one and the same rotation -- a
# fact the Lean proofs state directly (`fullAngleRotorFromTo_carry`,
# `projRotation_carries_from_to` / `projRotation_eq_sandwich`). The angle was
# scaffolding; the two vectors, multiplied, are the rotation.
