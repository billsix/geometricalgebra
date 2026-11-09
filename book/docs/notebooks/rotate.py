# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Rotate — a first example
#
# The chapter defines a rotation by two directions: rotate from the direction of `a` to
# the direction of `b`. gacalc builds exactly that with
# `versor_rotation(from_vector=a, to_vector=b)`. No angle is passed in.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Vector, e_1, e_2
from gacalc.transforms import InvertibleFunction, plane_rotation, versor_rotation

a: Vector = 3 * e_1 + 1 * e_2
b: Vector = 1 * e_1 + 2 * e_2
rotate_a_to_b: InvertibleFunction[Vector] = versor_rotation(from_vector=a, to_vector=b)

# %% [markdown]
# Applied to `a` itself, the rotation lands on `b`'s direction and keeps `a`'s length,
# so the result is `(|a| / |b|) * b`.

# %%
rotated: Vector = rotate_a_to_b(a)
assert (rotated - (a.magnitude() / b.magnitude()) * b).simplified() == Vector.zero()
rotated.simplified()

# %% [markdown]
# **The magnitudes don't matter.** Rotating from `2 * a` toward `5 * b` is the same
# rotation, so it moves any vector, here `e_1`, to the same place.

# %%
rotate_scaled: InvertibleFunction[Vector] = versor_rotation(
    from_vector=2 * a, to_vector=5 * b
)
assert (rotate_a_to_b(1 * e_1) - rotate_scaled(1 * e_1)).simplified() == Vector.zero()
rotate_a_to_b(1 * e_1).simplified()

# %% [markdown]
# **The angle is still there, as a property.** The same rotation, given as the angle
# from `a` to `b` in the `e_1 -> e_2` plane, agrees. We never needed the angle to build
# the rotation above; here we compute it only to check.

# %%
theta: Real = sympy.atan2(b.coefficient(e_2), b.coefficient(e_1)) - sympy.atan2(
    a.coefficient(e_2), a.coefficient(e_1)
)
rotate_by_angle: InvertibleFunction[Vector] = plane_rotation(Vector.e_1, Vector.e_2)(
    theta
)
assert (rotate_by_angle(1 * e_1) - rotate_a_to_b(1 * e_1)).simplified() == Vector.zero()
