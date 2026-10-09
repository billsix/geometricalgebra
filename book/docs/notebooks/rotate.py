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
from collections.abc import Callable

import sympy

from gacalc.base import Real
from gacalc.g2 import Vector
from gacalc.transforms import InvertibleFunction, plane_rotation

# A rotation in the e_1 -> e_2 plane (counterclockwise): hand it an angle, get back
# the function that rotates by that angle.
rotate: Callable[[Real], InvertibleFunction[Vector]] = plane_rotation(
    Vector.e_1, Vector.e_2
)

# Rotate e_1 by 90 degrees: it should become e_2.
rotate(sympy.pi / 2)(Vector.e_1).simplified()
