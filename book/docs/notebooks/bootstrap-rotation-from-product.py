# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 6, rotation through the product — worked example
#
# Companion to *Step 6: Rotation, through the Product*. There are three vectors: $a$,
# $b$, and a $v$ to rotate, every coordinate a symbol, so each result is a formula for
# all vectors. The rotation from $a$ to $b$ is applied to $v$ as the one-sided product
# $v * (\hat{a} * \hat{b})$, then as the sandwich $R * v * R^{-1}$ with
# $R = b * a + |a| * |b|$. Both match Step 3's rotation built from projection. Numbers
# appear only to draw the figures; change them and rerun. Each check shows both sides,
# then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _bootstrap_live import (
    BLACK,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    point,
    scene_around,
)

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult
from gacalc.transforms import versor_rotation

# %% [markdown]
# ## The vectors
#
# $a$, $b$ and $v$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
v_1: sympy.Symbol
v_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2 = sympy.symbols("a_1 a_2 b_1 b_2 v_1 v_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %%
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 2),
    (a_2, 1),
    (b_1, 1),
    (b_2, 2),
    (v_1, -1),
    (v_2, 2),
]

# %% [markdown]
# ## The one-sided form
#
# The product of the two unit vectors is $\cos(\theta) + \sin(\theta) * e_{12}$, with
# $\theta$ the angle from $a$ to $b$:

# %%
unit_product: Versor = (a.normalize() * b.normalize()).simplified()
unit_product

# %% [markdown]
# Multiplying $v$ by it on the right rotates $v$ by $\theta$. Term by term: each term of
# $v$ times the plain-number part keeps its direction, and times the $e_{12}$ part turns
# a quarter turn:

# %%
show_mult(v, unit_product)

# %% [markdown]
# The sum, the rotated $v$:

# %%
one_sided: MultiVectorBase = (v * unit_product).simplified()
one_sided

# %% [markdown]
# At the plot values:

# %%
at_values(one_sided, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_V: Point = point(coordinates=list(at_values(v, values)))
P_ROTATED: Point = point(coordinates=list(at_values(one_sided, values)))
fig_one_sided: PendingFigure
with scene_around(points=[P_A, P_B, P_V, P_ROTATED]) as fig_one_sided:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_V, color=BLACK, text=r"$\vec{v}$")
    arrow(
        head=P_ROTATED,
        color=PURPLE,
        text=r"$\vec{v} * (\hat{a} * \hat{b})$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
fig_one_sided

# %% [markdown]
# ## The sandwich
#
# $R = b * a + |a| * |b|$ turns $a$ halfway, onto the bisector
# $h = |b| * a + |a| * b$ (scaled by $|a|$), and $R * v * R^{-1}$ is the whole rotation.

# %%
R: Versor = (b * a + Scalar(a.magnitude() * b.magnitude())).simplified()
R

# %% [markdown]
# The sandwich is two products. First $R * v$, term by term:

# %%
show_mult(R, v)

# %% [markdown]
# then that result times $R^{-1}$. With every coordinate a symbol, the table for this
# second product is pages of nested square roots, so it is left out; the sandwich's
# result is below, and the checks compare it with the one-sided form.

# %%
sandwich: MultiVectorBase = (R * v * R.inverse()).simplified()
sandwich

# %% [markdown]
# At the plot values:

# %%
at_values(sandwich, values)

# %%
h: Vector = Scalar(b.magnitude()) * a + Scalar(a.magnitude()) * b
P_H: Point = point(coordinates=list(at_values(h.normalize(), values)))
P_SANDWICH: Point = point(coordinates=list(at_values(sandwich, values)))
fig_sandwich: PendingFigure
with scene_around(points=[P_A, P_B, P_V, P_SANDWICH]) as fig_sandwich:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    dashed_arrow(tail=Point(x=0, y=0), head=P_H, color=PURPLE, text=r"$\hat{h}$")
    arrow(head=P_V, color=BLACK, text=r"$\vec{v}$")
    arrow(
        head=P_SANDWICH,
        color=PURPLE,
        text=r"$R * \vec{v} * R^{-1}$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
fig_sandwich

# %% [markdown]
# ## Checks, for all vectors
#
# Step 3 built the rotation from projection: $b$ measured against $a$ (Step 2, by Step
# 1's rotation by minus the angle of $a$) gives the cosine and sine, and the same angle
# is applied to $v$. Here is that construction, to compare against.


# %%
def rotation_by_projection(a: Vector, b: Vector, v: Vector) -> Vector:
    """Step 3's construction: ``b`` measured against ``a`` gives the cosine and sine
    of the angle from ``a`` to ``b``; the same angle applied to ``v``."""
    measured: Vector = b.rotate(-sympy.atan2(a.coefficient(e_2), a.coefficient(e_1)))
    cos: Real = measured.coefficient(e_1) / b.magnitude()
    sin: Real = measured.coefficient(e_2) / b.magnitude()
    return (Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()).simplified()


# %% [markdown]
# ### The one-sided form is Step 3's rotation
#
# Step 3's rotation of $v$:

# %%
by_projection: Vector = rotation_by_projection(a, b, v)
by_projection

# %% [markdown]
# The one-sided form was:

# %%
one_sided

# %% [markdown]
# Their difference:

# %%
(one_sided - by_projection).simplified()

# %% [markdown]
# ### The other order turns the other way
#
# $(\hat{a} * \hat{b}) * v$:

# %%
(unit_product * v).simplified()

# %% [markdown]
# Step 3's rotation from $b$ to $a$:

# %%
rotation_by_projection(b, a, v)

# %% [markdown]
# Their difference:

# %%
(unit_product * v - rotation_by_projection(b, a, v)).simplified()

# %% [markdown]
# ### $R$ turns $a$ onto the bisector
#
# $R * a$:

# %%
(R * a).simplified()

# %% [markdown]
# $|a| * h$:

# %%
(Scalar(a.magnitude()) * h).simplified()

# %% [markdown]
# Their difference:

# %%
(R * a - Scalar(a.magnitude()) * h).simplified()

# %% [markdown]
# ### The sandwich is the one-sided form
#
# The sandwich and the one-sided form were shown above. Their difference:

# %%
(sandwich - one_sided).simplified()

# %% [markdown]
# ### The step that makes the sandwich agree
#
# $\tilde{R} * R^{-1} = \hat{a} * \hat{b}$, checked with unit vectors at angles $\alpha$
# and $\beta$, where $R = \hat{b} * \hat{a} + 1$:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
R_unit: Versor = b_hat * a_hat + Scalar(1)
(R_unit.reverse() * R_unit.inverse()).simplified()

# %% [markdown]
# $\hat{a} * \hat{b}$:

# %%
(a_hat * b_hat).simplified()

# %% [markdown]
# Their difference:

# %%
(R_unit.reverse() * R_unit.inverse() - a_hat * b_hat).simplified()

# %% [markdown]
# ### gacalc agrees
#
# gacalc's `versor_rotation`, applied to $v$:

# %%
versor_rotation(from_vector=a, to_vector=b)(v).simplified()

# %% [markdown]
# Its difference from the one-sided form:

# %%
(versor_rotation(from_vector=a, to_vector=b)(v) - one_sided).simplified()
