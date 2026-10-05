# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The Geometric Product — rotation is a multiplication
#
# The chapter claims that rotating a vector `a` by an angle `theta` is the same as
# multiplying it, on one side, by the full-angle rotor
# `R = cos(theta) + sin(theta) * e_12` (2D only: nothing lies outside the plane).
# We check that, symbolically, against both the coordinate formula and gacalc's
# own rotation.

# %%
import sympy

from gacalc.g2 import Bivector, Vector
from gacalc.transforms import plane_rotation

theta = sympy.Symbol("theta", real=True)
a_x, a_y = sympy.symbols("a_x a_y", real=True)
a = a_x * Vector.e_1 + a_y * Vector.e_2

# The 90-degree rotation is multiplication by the unit bivector e_12.
a * Bivector.e_12  # -> (-a_y, a_x)

# %%
# The full-angle rotor R = cos(theta) + sin(theta) * e_12, applied one-sided, by
# multiplication on the right.
R = sympy.cos(theta) + sympy.sin(theta) * Bivector.e_12
full_angle_result = (a * R).simplified()
full_angle_result

# %%
# gacalc's own rotation, in the e_1 -> e_2 plane, by the same angle -- under the hood a
# half-angle rotor cos(theta/2) - sin(theta/2) * e_12 applied as the sandwich R v R~.
gacalc_result = plane_rotation(Vector.e_1, Vector.e_2)(theta)(a).simplified()
gacalc_result

# %%
# They agree: the difference is zero.
(full_angle_result - gacalc_result).simplified()
