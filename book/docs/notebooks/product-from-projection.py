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
# chapter give. Numbers appear only to draw the figures. Each check shows both sides,
# then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _bootstrap_live import (
    BLACK,
    BLUE,
    GREEN,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    right_angle,
    scene_around,
)

from gacalc.base import Real
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Bivector, Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# Two general vectors:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 1), (a_2, 2), (b_1, 2), (b_2, 1)]

# %% [markdown]
# ## Where $a$ lands when $b$ is rotated onto the x-axis
#
# The rotation is the projection proof's $R_{\vec{b}}^{e_1}$, from $b$'s direction to
# $e_1$'s (`rotation_from_to`):

# %%
R: InvertibleFunction[Vector] = rotation_from_to(b, e_1)
R

# %% [markdown]
# It carries $a$ to $(x, y)$: $x$, how far $a$ reaches along $b$ (the projection), and
# $y$, how far it reaches across $b$ (the rejection).

# %%
a_landed: Vector = R(a).simplified()
a_landed

# %% [markdown]
# $x$:

# %%
x: Real = a_landed.coefficient(e_1)
x

# %% [markdown]
# $y$:

# %%
y: Real = a_landed.coefficient(e_2)
y

# %% [markdown]
# At the plot values, where $a$ lands:

# %%
at_values(a_landed, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_A_LANDED: Point = point(coordinates=list(at_values(a_landed, values)))
P_B_LANDED: Point = point(coordinates=list(at_values(R(b), values)))
P_X: Point = point(coordinates=list(at_values(Scalar(x) * e_1, values)))
fig_landed: PendingFigure
with scene_around(points=[P_A, P_B, P_A_LANDED, P_B_LANDED]) as fig_landed:
    dashed_arrow(tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{a}$")
    dashed_arrow(tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(
        head=P_B_LANDED,
        color=BLACK,
        text=r"$|\vec{b}| * e_1$",
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_LANDED, color=BLACK, text=r"$\vec{a}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    note(
        at=0.5 * P_X,
        text=r"$x$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_LANDED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_A_LANDED),
        text=r"$y$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_X, toward_a=P_B_LANDED, toward_b=P_A_LANDED - P_X)
fig_landed

# %% [markdown]
# ## Times $|b|$, they are the dot product and the signed area
#
# $|b| * x$:

# %%
b_times_x: Real = sympy.simplify(sympy.sympify(b.magnitude() * x))
b_times_x

# %% [markdown]
# Its difference from $a_1 * b_1 + a_2 * b_2$:

# %%
sympy.simplify(sympy.sympify(b_times_x - (a_1 * b_1 + a_2 * b_2)))

# %% [markdown]
# $|b| * y$:

# %%
b_times_y: Real = sympy.simplify(sympy.sympify(b.magnitude() * y))
b_times_y

# %% [markdown]
# Its difference from $b_1 * a_2 - b_2 * a_1$:

# %%
sympy.simplify(sympy.sympify(b_times_y - (b_1 * a_2 - b_2 * a_1)))

# %% [markdown]
# ## The product built from them is gacalc's geometric product
#
# Put the two numbers into one object, the projection part as a plain number and the
# rejection part as a multiple of $e_{12}$:

# %%
built: Versor = (
    Scalar(b.magnitude()) * (Versor.from_real(x) + Scalar(y) * Bivector.e_12)
).simplified()
built

# %% [markdown]
# The same product by the multiplication rules, term by term:

# %%
show_mult(b, a)

# %% [markdown]
# $b * a$:

# %%
product: Versor = (b * a).simplified()
product

# %% [markdown]
# Its difference from the built object:

# %%
(product - built).simplified()

# %% [markdown]
# ## The two parts are the dot and the wedge
#
# The plain-number part is the dot product $b \cdot a$:

# %%
dot: Real = b.dot(a).scalar_part()
dot

# %% [markdown]
# Its difference from $|b| * x$:

# %%
sympy.simplify(sympy.sympify(dot - b.magnitude() * x))

# %% [markdown]
# The $e_{12}$ part is the wedge $b \wedge a$:

# %%
wedge: Bivector = b ^ a
wedge

# %% [markdown]
# Its difference from $|b| * y * e_{12}$:

# %%
(wedge - Scalar(b.magnitude() * y) * Bivector.e_12).simplified()

# %% [markdown]
# Together they are the product. $b \cdot a + b \wedge a$:

# %%
(Scalar(dot) + wedge).simplified()

# %% [markdown]
# Its difference from $b * a$:

# %%
(product - (Scalar(dot) + wedge)).simplified()
