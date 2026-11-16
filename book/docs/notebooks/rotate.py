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
# In precalculus a rotation is given by an angle. The chapter gives it instead by two
# directions: rotate from the direction of $a$ to the direction of $b$. gacalc builds
# exactly that with `versor_rotation(from_vector=a, to_vector=b)`, and no angle is
# passed in. This notebook applies it, then checks it against the rotation by the angle.
# Each check cell subtracts two things and shows the difference, $0$ when they agree.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Vector, e_1, e_2
from gacalc.transforms import InvertibleFunction, plane_rotation, versor_rotation

# %% [markdown]
# ## The vectors

# %%
a: Vector = 3 * e_1 + 1 * e_2
b: Vector = 1 * e_1 + 2 * e_2
rotate_a_to_b: InvertibleFunction[Vector] = versor_rotation(from_vector=a, to_vector=b)

# %% [markdown]
# ## Rotating $a$ itself
#
# Applied to $a$, the rotation lands on $b$'s direction and keeps $a$'s length:

# %%
rotated: Vector = rotate_a_to_b(a).simplified()
rotated

# %% [markdown]
# so the result is $(|a| / |b|) * b$:

# %%
(rotated - (a.magnitude() / b.magnitude()) * b).simplified()

# %% [markdown]
# ## The lengths don't matter
#
# Rotating from $2 * a$ toward $5 * b$ is the same rotation, so it moves any vector,
# here $e_1$, to the same place:

# %%
rotate_scaled: InvertibleFunction[Vector] = versor_rotation(
    from_vector=2 * a, to_vector=5 * b
)
rotate_a_to_b(1 * e_1).simplified()

# %%
(rotate_a_to_b(1 * e_1) - rotate_scaled(1 * e_1)).simplified()

# %% [markdown]
# ## The angle is still there, as a property
#
# The same rotation, given as the angle $\theta$ from $a$ to $b$ in the
# $e_1 \to e_2$ plane, agrees. We never needed $\theta$ to build the rotation above;
# here we compute it only to check.

# %%
theta: Real = sympy.atan2(b.coefficient(e_2), b.coefficient(e_1)) - sympy.atan2(
    a.coefficient(e_2), a.coefficient(e_1)
)
rotate_by_angle: InvertibleFunction[Vector] = plane_rotation(Vector.e_1, Vector.e_2)(
    theta
)
(rotate_by_angle(1 * e_1) - rotate_a_to_b(1 * e_1)).simplified()
