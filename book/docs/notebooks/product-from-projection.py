# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The geometric product from projection and rejection — calculations
#
# Companion to the *Geometric Product from Projection and Rejection* chapter. Rotate
# `b` onto the x-axis, as in the projection proof, and read off where `a` lands:
# `(x, y)`. Then check, with every coordinate left as a symbol, that
#
# $$b * a = |b| * (x + y * e_{12}),$$
#
# and that this is the same product the multiplication rules of the
# geometric-product chapter give.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Bivector, Scalar, Vector, Versor, e_1, e_2

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2

# %% [markdown]
# ## Where `a` lands when `b` is rotated onto the x-axis
#
# The rotation's cosine and sine are read off `b`: `cos = b_1 / |b|`,
# `sin = -b_2 / |b|`. Rotating `a` by them gives its standard-position coordinates.
# `x` is how far `a` reaches along `b` (the projection), and `y` how far it reaches
# across `b` (the rejection).

# %%
magnitude: Real = b.magnitude()
cos: Real = b_1 / magnitude
sin: Real = -b_2 / magnitude
x: Real = cos * a_1 - sin * a_2
y: Real = sin * a_1 + cos * a_2
x, y

# %% [markdown]
# ## Times `|b|`, they are the dot product and the signed area
#
# `|b| * x = a_1 * b_1 + a_2 * b_2`, and `|b| * y = b_1 * a_2 - b_2 * a_1`.

# %%
assert sympy.simplify(magnitude * x - (a_1 * b_1 + a_2 * b_2)) == 0
assert sympy.simplify(magnitude * y - (b_1 * a_2 - b_2 * a_1)) == 0
(
    sympy.simplify(sympy.sympify(magnitude * x)),
    sympy.simplify(sympy.sympify(magnitude * y)),
)

# %% [markdown]
# ## The product built from them is gacalc's geometric product
#
# Put the two numbers into one object, the projection part as a plain number and the
# rejection part as a multiple of `e_12`. That object is `b * a`.

# %%
built: Versor = Scalar(magnitude) * (Versor.from_real(x) + Scalar(y) * Bivector.e_12)
product: Versor = b * a
assert (product - built).simplified() == Versor.zero()
product

# %% [markdown]
# ## The two parts are the dot and the wedge
#
# The plain-number part is the dot product `b·a`, and the `e_12` part is the wedge
# `b ∧ a`.

# %%
dot: Real = b.dot(a).scalar_part()
wedge: Bivector = b ^ a
assert sympy.simplify(sympy.sympify(dot - magnitude * x)) == 0
assert (wedge - (magnitude * y) * Bivector.e_12).simplified() == Bivector.zero()
assert product == dot + wedge
dot, wedge
