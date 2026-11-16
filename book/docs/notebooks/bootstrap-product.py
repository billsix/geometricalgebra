# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 4, the geometric product — worked example
#
# Companion to *Step 4: The Geometric Product, from Projection*. The next cell sets two
# vectors. Every step after it is computed from them and drawn: `b` measured against
# `a` (Step 2) gives `x` and `y`, and the product is `|a| * (x + y * e_12)`. Then the
# quarter turn as a product, and the dot and wedge as `a` times the projection and the
# rejection. Change the vectors and rerun the notebook to see the same steps for others.
# The last section repeats the checks with every coordinate a symbol, so they hold for
# all vectors.

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

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2, e_12

# %% [markdown]
# ## The vectors
#
# Change these and rerun.

# %%
a: Vector = 2 * e_1 + 1 * e_2
b: Vector = 1 * e_1 + 2 * e_2


# %%
def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def product_from_projection(a: Vector, b: Vector) -> Versor:
    """``|a| * (x + y * e_12)``, with ``(x, y)`` the coordinates of ``b`` in ``a``'s
    standard position (Step 2)."""
    measured: Vector = rotate(
        a.coefficient(e_1) / a.magnitude(), -a.coefficient(e_2) / a.magnitude(), b
    )
    return Scalar(a.magnitude()) * (
        Scalar(measured.coefficient(e_1)) + Scalar(measured.coefficient(e_2)) * e_12
    )


# %% [markdown]
# ## The product from projection
#
# `x` is the signed length of `b`'s shadow on `a` and `y` its height above `a`. The
# product keeps both, times `|a|`: the plain-number part is the dot product and the
# `e_12` part, the signed area of the parallelogram, is the wedge.

# %%
product: Versor = product_from_projection(a, b).simplified()
product

# %%
P_A: Point = point(coordinates=list(a))
P_B: Point = point(coordinates=list(b))
P_FOOT: Point = point(coordinates=list(b.projected_onto(a)))
fig_product: PendingFigure
with scene_around(points=[P_A, P_B, P_A + P_B]) as fig_product:
    dashed_arrow(tail=P_A, head=P_A + P_B, color=BLACK)
    dashed_arrow(tail=P_B, head=P_A + P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_FOOT, color=GREEN, width=2.4)
    note(
        at=0.5 * P_FOOT,
        text=r"$x$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_FOOT, color=BLUE)
    note(
        at=0.5 * (P_FOOT + P_B),
        text=r"$y$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_FOOT, toward_a=P_A, toward_b=P_B - P_FOOT)
fig_product

# %% [markdown]
# ## The quarter turn is a product
#
# Multiplying by `e_12` on the right turns a vector a quarter turn: `b * e_12` is Step
# 1's `r(b; π/2)`.

# %%
quarter_turn: MultiVectorBase = b * e_12
quarter_turn

# %%
P_QUARTER: Point = point(coordinates=list(b.rotate_90_degrees()))
fig_quarter: PendingFigure
with scene_around(points=[P_B, P_QUARTER]) as fig_quarter:
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{b} * e_{12}$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
    right_angle(corner=Point(x=0, y=0), toward_a=P_B, toward_b=P_QUARTER)
fig_quarter

# %% [markdown]
# ## Dot and wedge through projection and rejection
#
# `a` times the projection of `b` onto `a` is a plain number, the dot product. `a` times
# the rejection is pure area, the wedge.

# %%
projection: Vector = b.projected_onto(a)
rejection: Vector = b.rejected_away_from(a)
along: MultiVectorBase = (a * projection).simplified()
along

# %%
across: MultiVectorBase = (a * rejection).simplified()
across

# %% [markdown]
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, `0` when they agree.
#
# The product from projection is the product of the multiplication rules:

# %%
(product - a * b).simplified()

# %% [markdown]
# Its parts are the dot product and the wedge:

# %%
(a * b - (a.dot(b) + a.wedge(b))).simplified()

# %% [markdown]
# A vector times itself is its length squared:

# %%
(b * b - Scalar(b.magnitude_squared())).simplified()

# %% [markdown]
# The quarter turn as a product matches Step 1's:

# %%
(quarter_turn - b.rotate_90_degrees()).simplified()

# %% [markdown]
# `a * proj_a(b)` is the dot product:

# %%
(along - a.dot(b)).simplified()

# %% [markdown]
# `a * rej_a(b)` is the wedge:

# %%
(across - a.wedge(b)).simplified()

# %% [markdown]
# The two add up to the product:

# %%
(a * b - (along + across)).simplified()

# %% [markdown]
# Measured the other way, the dot keeps its value:

# %%
(b * a.projected_onto(b) - a.dot(b)).simplified()

# %% [markdown]
# and the wedge changes sign:

# %%
(b * a.rejected_away_from(b) + a.wedge(b)).simplified()

# %% [markdown]
# ## For all vectors
#
# The same steps with every coordinate a symbol. Each cell checks one fact.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a_symbolic: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b_symbolic: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
projection_symbolic: Vector = b_symbolic.projected_onto(a_symbolic)
rejection_symbolic: Vector = b_symbolic.rejected_away_from(a_symbolic)

# %% [markdown]
# The product from projection is the product of the multiplication rules:

# %%
(product_from_projection(a_symbolic, b_symbolic) - a_symbolic * b_symbolic).simplified()

# %% [markdown]
# Its parts are the dot product and the wedge:

# %%
(
    a_symbolic * b_symbolic
    - (a_symbolic.dot(b_symbolic) + a_symbolic.wedge(b_symbolic))
).simplified()

# %% [markdown]
# A vector times itself is its length squared:

# %%
(b_symbolic * b_symbolic - Scalar(b_1**2 + b_2**2)).simplified()

# %% [markdown]
# The quarter turn is a product:

# %%
(b_symbolic * e_12 - b_symbolic.rotate_90_degrees()).simplified()

# %% [markdown]
# `a * proj_a(b)` is the dot product:

# %%
(a_symbolic * projection_symbolic - a_symbolic.dot(b_symbolic)).simplified()

# %% [markdown]
# `a * rej_a(b)` is the wedge:

# %%
(a_symbolic * rejection_symbolic - a_symbolic.wedge(b_symbolic)).simplified()

# %% [markdown]
# Measured the other way, the dot keeps its value:

# %%
(
    b_symbolic * a_symbolic.projected_onto(b_symbolic) - a_symbolic.dot(b_symbolic)
).simplified()

# %% [markdown]
# and the wedge changes sign:

# %%
(
    b_symbolic * a_symbolic.rejected_away_from(b_symbolic)
    + a_symbolic.wedge(b_symbolic)
).simplified()

# %% [markdown]
# Two unit vectors at angles `α` and `β` multiply to the cosine and sine of the angle
# `θ = β - α` from the first to the second:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
(
    a_hat * b_hat
    - (Scalar(sympy.cos(beta - alpha)) + Scalar(sympy.sin(beta - alpha)) * e_12)
).simplified()
