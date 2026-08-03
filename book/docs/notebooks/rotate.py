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
# The chapter derives rotation from high-school trigonometry. Here we just *use* it:
# gacalc rotates in the plane of two vectors. Magnitudes don't matter — only the
# directions set the rotation.

# %%
import sympy

from gacalc.g2 import Vector2
from gacalc.transforms import plane_rotation

# A rotation in the e_1 -> e_2 plane (counterclockwise).
rotate = plane_rotation(Vector2.e_1, Vector2.e_2)

# Rotate e_1 by 90 degrees: it should become e_2.
rotate(sympy.pi / 2)(Vector2.e_1).simplified()
