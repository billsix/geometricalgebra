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
# Companion to *Step 6: Rotation, through the Product*. The next cell sets three
# vectors: $a$, $b$, and a $v$ to rotate. Every step after it is computed from them and
# drawn: the rotation from $a$ to $b$ applied to $v$ as the one-sided product
# $v * (\hat{a} * \hat{b})$, then as the sandwich $R * v * R^{-1}$ with
# $R = b * a + |a| * |b|$. Both match Step 3's rotation built from projection. Change
# the vectors and rerun the notebook to see the same steps for others. The last section
# repeats the checks with every coordinate a symbol, so they hold for all vectors.

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
from gacalc.nbdisplay import show_mult
from gacalc.transforms import versor_rotation

# %% [markdown]
# ## The vectors
#
# Change these and rerun.

# %%
a: Vector = 2 * e_1 + 1 * e_2
b: Vector = 1 * e_1 + 2 * e_2
v: Vector = -1 * e_1 + 2 * e_2


# %%
def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def rotation_from_to(a: Vector, b: Vector, v: Vector) -> Vector:
    """Step 3: ``b`` measured against ``a`` gives the cosine and sine of the angle from
    ``a`` to ``b``; the same angle applied to ``v``."""
    measured: Vector = rotate(
        a.coefficient(e_1) / a.magnitude(), -a.coefficient(e_2) / a.magnitude(), b
    )
    return rotate(
        measured.coefficient(e_1) / b.magnitude(),
        measured.coefficient(e_2) / b.magnitude(),
        v,
    )


# %% [markdown]
# ## The one-sided form
#
# The product of the two unit vectors is $\cos(\theta) + \sin(\theta) * e_{12}$, with
# $\theta$ the angle from $a$ to $b$:

# %%
unit_product: Versor = (a.normalize() * b.normalize()).simplified()
unit_product

# %% [markdown]
# and multiplying $v$ by it on the right rotates $v$ by $\theta$:

# %% [markdown]
# Term by term: each term of $v$ times the plain-number part keeps its direction,
# and times the $e_{12}$ part turns a quarter turn:

# %%
show_mult(v, unit_product)

# %%
one_sided: MultiVectorBase = (v * unit_product).simplified()
one_sided

# %%
P_A: Point = point(coordinates=list(a))
P_B: Point = point(coordinates=list(b))
P_V: Point = point(coordinates=list(v))
P_ROTATED: Point = point(coordinates=list(one_sided))
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
R: Versor = b * a + Scalar(a.magnitude() * b.magnitude())
R

# %% [markdown]
# The sandwich is two products. First $R * v$, term by term:

# %%
show_mult(R, v)

# %% [markdown]
# then that result times $R^{-1}$:

# %%
show_mult((R * v).simplified(), R.inverse())

# %%
h: Vector = Scalar(b.magnitude()) * a + Scalar(a.magnitude()) * b
sandwich: MultiVectorBase = (R * v * R.inverse()).simplified()
sandwich

# %%
P_H: Point = point(coordinates=list(h.normalize()))
P_SANDWICH: Point = point(coordinates=list(sandwich))
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
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The one-sided form is Step 3's rotation, built from projection:

# %%
(one_sided - rotation_from_to(a, b, v)).simplified()

# %% [markdown]
# The other order turns the other way: it is the rotation from $b$ to $a$:

# %%
(unit_product * v - rotation_from_to(b, a, v)).simplified()

# %% [markdown]
# $R$ turns $a$ onto the bisector: $R * a = |a| * h$:

# %%
(R * a - Scalar(a.magnitude()) * h).simplified()

# %% [markdown]
# The sandwich is the one-sided form:

# %%
(sandwich - one_sided).simplified()

# %% [markdown]
# gacalc's `versor_rotation` agrees:

# %%
(versor_rotation(from_vector=a, to_vector=b)(v) - one_sided).simplified()

# %% [markdown]
# ## For all vectors
#
# The same steps with every coordinate a symbol. Each cell checks one fact.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
v_1: sympy.Symbol
v_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2 = sympy.symbols("a_1 a_2 b_1 b_2 v_1 v_2", real=True)
a_symbolic: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b_symbolic: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
v_symbolic: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
unit_product_symbolic: Versor = a_symbolic.normalize() * b_symbolic.normalize()

# %% [markdown]
# The one-sided form term by term for every $v$, with the $a$ and $b$ set at the top:
# each coordinate of the result is a combination of $v_1$ and $v_2$.

# %%
show_mult(v_symbolic, unit_product)

# %% [markdown]
# The one-sided form is Step 3's rotation:

# %%
(
    v_symbolic * unit_product_symbolic
    - rotation_from_to(a_symbolic, b_symbolic, v_symbolic)
).simplified()

# %% [markdown]
# The other order is the rotation from $b$ to $a$:

# %%
(
    unit_product_symbolic * v_symbolic
    - rotation_from_to(b_symbolic, a_symbolic, v_symbolic)
).simplified()

# %% [markdown]
# The step that makes the sandwich agree, $\tilde{R} * R^{-1} = \hat{a} * \hat{b}$,
# checked with unit vectors at angles $\alpha$ and $\beta$:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
R_unit: Versor = b_hat * a_hat + Scalar(1)
(R_unit.reverse() * R_unit.inverse() - a_hat * b_hat).simplified()

# %% [markdown]
# With the $a$ and $b$ set at the top (a fully symbolic $R$ makes $R^{-1}$ slow) and $v$
# symbolic, the sandwich is the one-sided form for every $v$:

# %%
(R * v_symbolic * R.inverse() - v_symbolic * unit_product).simplified()

# %% [markdown]
# and gacalc's `versor_rotation` is Step 3's rotation for every $v$:

# %%
(
    versor_rotation(from_vector=a, to_vector=b)(v_symbolic)
    - rotation_from_to(a, b, v_symbolic)
).simplified()
