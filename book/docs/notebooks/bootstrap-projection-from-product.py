# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 5, projection through the product — worked example
#
# Companion to *Step 5: Projection, through the Product*. Every step is computed with
# symbolic coordinates, so each result is a formula for every $a$ and $b$: the inverse
# of $a$, then the projection $(b \cdot a) * a^{-1}$ and the rejection
# $(b \wedge a) * a^{-1}$, which match Step 2's construction by rotation. Numbers appear
# only to draw the figure; change them and rerun. Each check shows both sides, then
# their difference.

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
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    note,
    point,
    right_angle,
    scene_around,
)

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# ## The vectors
#
# $a$ and $b$, every coordinate a symbol:

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
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# ## The inverse of a vector
#
# $a * a = |a|^2$ is a plain number, so $a^{-1} = a / |a|^2$: along $a$, at length
# $1 / |a|$.

# %%
a_inverse: Vector = a.inverse().simplified()
a_inverse

# %% [markdown]
# At the plot values:

# %%
at_values(a_inverse, values)

# %% [markdown]
# ## The projection through the product
#
# $\operatorname{proj}_a(b) = (b \cdot a) * a^{-1}$, where $b \cdot a$ is the
# plain-number part of $b * a$. $b * a$ term by term; its plain-number part, the sum of
# the $e_1 * e_1$ and $e_2 * e_2$ rows, is $b \cdot a$:

# %%
show_mult(b, a)

# %% [markdown]
# The projection:

# %%
b_dot_a: Real = (b * a).scalar_part()
projection: Vector = (Scalar(b_dot_a) * a_inverse).simplified()
projection

# %% [markdown]
# At the plot values:

# %%
at_values(projection, values)

# %% [markdown]
# ## The rejection, the same way
#
# $\operatorname{rej}_a(b) = (b \wedge a) * a^{-1}$. Term by term: $e_{12}$ times each
# term of $a^{-1}$ is a quarter turn of that term, so the result is a vector again.

# %%
show_mult(b.wedge(a), a_inverse)

# %% [markdown]
# The rejection:

# %%
rejection: MultiVectorBase = (b.wedge(a) * a_inverse).simplified()
rejection

# %% [markdown]
# At the plot values:

# %%
at_values(rejection, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_INVERSE: Point = point(coordinates=list(at_values(a_inverse, values)))
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_product: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_product:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    note(
        at=0.75 * P_PROJECTION,
        text=r"$(\vec{b} \cdot \vec{a}) * \vec{a}^{-1}$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_B),
        text=r"$(\vec{b} \wedge \vec{a}) * \vec{a}^{-1}$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_A, toward_b=P_B - P_PROJECTION)
    arrow(head=P_INVERSE, color=PURPLE, width=3.0)
    note(
        at=P_INVERSE,
        text=r"$\vec{a}^{-1}$",
        color=PURPLE,
        offset=Point(x=-2, y=6),
        align=LabelPos.t,
    )
fig_product

# %% [markdown]
# ## Checks, for all vectors
#
# Step 2 built the projection and rejection by rotating, with Step 1's rotation by minus
# the angle of $a$ and back. Here it is as one function, to compare against.


# %%
def project_and_reject_by_rotation(onto: Vector, v: Vector) -> tuple[Vector, Vector]:
    """Step 2's construction: rotate ``onto`` to the x-axis, apply the base cases,
    rotate back."""
    angle: sympy.Expr = sympy.atan2(onto.coefficient(e_2), onto.coefficient(e_1))
    v_rotated: Vector = v.rotate(-angle)
    return (
        (Scalar(v_rotated.coefficient(e_1)) * e_1).rotate(angle).simplified(),
        (Scalar(v_rotated.coefficient(e_2)) * e_2).rotate(angle).simplified(),
    )


# %% [markdown]
# ### $a^{-1} = a / |a|^2$
#
# $a^{-1}$ was:

# %%
a_inverse

# %% [markdown]
# $a / |a|^2$:

# %%
(Scalar(1 / (a_1**2 + a_2**2)) * a).simplified()

# %% [markdown]
# Their difference:

# %%
(a_inverse - Scalar(1 / (a_1**2 + a_2**2)) * a).simplified()

# %% [markdown]
# ### $a * a^{-1} = 1$
#
# $a * a^{-1}$:

# %%
(a * a_inverse).simplified()

# %% [markdown]
# Its difference from $1$:

# %%
(a * a_inverse - Scalar(1)).simplified()

# %% [markdown]
# ### The product's projection and rejection are Step 2's
#
# Step 2's projection, by rotating:

# %%
by_rotation_projection: Vector
by_rotation_rejection: Vector
by_rotation_projection, by_rotation_rejection = project_and_reject_by_rotation(a, b)
by_rotation_projection

# %% [markdown]
# The projection through the product was:

# %%
projection

# %% [markdown]
# Their difference:

# %%
(projection - by_rotation_projection).simplified()

# %% [markdown]
# Step 2's rejection, by rotating:

# %%
by_rotation_rejection

# %% [markdown]
# The rejection through the product was:

# %%
rejection

# %% [markdown]
# Their difference:

# %%
(rejection - by_rotation_rejection).simplified()

# %% [markdown]
# ### Together they give back $b$, since $b * a * a^{-1} = b$
#
# Their sum:

# %%
(projection + rejection).simplified()

# %% [markdown]
# Its difference from $b$:

# %%
(projection + rejection - b).simplified()

# %% [markdown]
# ### gacalc agrees
#
# gacalc's projection:

# %%
b.projected_onto(a).simplified()

# %% [markdown]
# Its difference from the product's:

# %%
(projection - b.projected_onto(a)).simplified()

# %% [markdown]
# gacalc's rejection:

# %%
b.rejected_away_from(a).simplified()

# %% [markdown]
# Its difference from the product's:

# %%
(rejection - b.rejected_away_from(a)).simplified()
