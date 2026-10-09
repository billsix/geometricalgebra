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

from gacalc.g2 import Bivector, Vector, Versor
from gacalc.transforms import plane_rotation

theta: sympy.Symbol = sympy.Symbol("theta", real=True)
a_x: sympy.Symbol
a_y: sympy.Symbol
a_x, a_y = sympy.symbols("a_x a_y", real=True)
a: Vector = a_x * Vector.e_1 + a_y * Vector.e_2

# The 90-degree rotation is multiplication by the unit bivector e_12.
a * Bivector.e_12  # -> (-a_y, a_x)

# %%
# The full-angle rotor R = cos(theta) + sin(theta) * e_12, applied one-sided, by
# multiplication on the right.
R: Versor = sympy.cos(theta) + sympy.sin(theta) * Bivector.e_12
full_angle_result: Vector = (a * R).simplified()
full_angle_result

# %%
# The coordinate formula from *Proof: Rotate*, written out component by component:
# (a_x cos(theta) - a_y sin(theta), a_x sin(theta) + a_y cos(theta)). The one-sided
# multiplication lands on exactly those two coordinates.
coordinate_formula: Vector = (
    a_x * sympy.cos(theta) - a_y * sympy.sin(theta)
) * Vector.e_1 + (a_x * sympy.sin(theta) + a_y * sympy.cos(theta)) * Vector.e_2
full_angle_result == coordinate_formula  # -> True

# %%
# gacalc's own rotation, in the e_1 -> e_2 plane, by the same angle -- under the hood a
# half-angle rotor cos(theta/2) - sin(theta/2) * e_12 applied as the sandwich R v R~.
gacalc_result: Vector = plane_rotation(Vector.e_1, Vector.e_2)(theta)(a).simplified()
gacalc_result

# %%
# They agree: the difference is zero.
(full_angle_result - gacalc_result).simplified()
