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
# Companion to the *Geometric Product from Projection and Rejection* chapter. Measured
# against $b$, the vector $a$ has two numbers: how far it reaches along $b$ and how far
# across. Rotate $b$ onto the x-axis, as in the projection proof, and those are the
# coordinates $(x, y)$ where $a$ lands. This notebook checks, with every coordinate a
# symbol, that
#
# $$b * a = |b| * (x + y * e_{12}),$$
#
# and that this is the same product the multiplication rules of the geometric-product
# chapter give. Each check cell subtracts two things and shows the difference, $0$ when
# they agree.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Bivector, Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import show_mult

# %% [markdown]
# Two general vectors:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2

# %% [markdown]
# ## Where $a$ lands when $b$ is rotated onto the x-axis
#
# The rotation's cosine and sine are read off $b$: $\cos(-\theta) = b_1 / |b|$ and
# $\sin(-\theta) = -b_2 / |b|$, with $\theta$ the angle of $b$. Rotating $a$ by them
# gives its coordinates in that position: $x$, how far $a$ reaches along $b$ (the
# projection), and $y$, how far it reaches across $b$ (the rejection).

# %%
magnitude: Real = b.magnitude()
cos: Real = b_1 / magnitude
sin: Real = -b_2 / magnitude
x: Real = cos * a_1 - sin * a_2
y: Real = sin * a_1 + cos * a_2
x, y

# %% [markdown]
# ## Times $|b|$, they are the dot product and the signed area
#
# $|b| * x = a_1 * b_1 + a_2 * b_2$:

# %%
sympy.simplify(sympy.sympify(magnitude * x - (a_1 * b_1 + a_2 * b_2)))

# %% [markdown]
# and $|b| * y = b_1 * a_2 - b_2 * a_1$:

# %%
sympy.simplify(sympy.sympify(magnitude * y - (b_1 * a_2 - b_2 * a_1)))

# %% [markdown]
# ## The product built from them is gacalc's geometric product
#
# Put the two numbers into one object, the projection part as a plain number and the
# rejection part as a multiple of $e_{12}$:

# %%
built: Versor = Scalar(magnitude) * (Versor.from_real(x) + Scalar(y) * Bivector.e_12)
built.simplified()

# %% [markdown]
# That object is $b * a$:

# %%
product: Versor = b * a
(product - built).simplified()

# %% [markdown]
# The same product by the multiplication rules, term by term:

# %%
show_mult(b, a)

# %% [markdown]
# ## The two parts are the dot and the wedge
#
# The plain-number part is the dot product $b \cdot a$:

# %%
dot: Real = b.dot(a).scalar_part()
sympy.simplify(sympy.sympify(dot - magnitude * x))

# %% [markdown]
# the $e_{12}$ part is the wedge $b \wedge a$:

# %%
wedge: Bivector = b ^ a
(wedge - Scalar(magnitude * y) * Bivector.e_12).simplified()

# %% [markdown]
# and together they are the product, $b * a = b \cdot a + b \wedge a$:

# %%
(product - (Scalar(dot) + wedge)).simplified()
