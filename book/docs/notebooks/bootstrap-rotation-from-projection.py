# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 3, rotation from projection — worked example
#
# Companion to *Step 3: Rotation from One Vector to Another, from Projection*. There
# are three vectors: $a$, $b$, and a $v$ to rotate, every coordinate a symbol, so each
# result is a formula for all vectors. One right triangle is drawn twice. The first
# measures $b$ against $a$ (Step 2) and gives the cosine and sine of the angle from $a$
# to $b$. The second is the same triangle on $v$, and its hypotenuse is the rotated
# $v'$. Numbers appear only to draw the figures; change them and rerun. Each check shows
# both sides, then their difference.

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

from gacalc.base import MultiVectorFn, Real
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.transforms import projection_rotation

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
# The values used to draw the figures. Change them and rerun. $v$ is drawn outside the
# angle from $a$ to $b$, so the two triangles don't overlap.

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
# ## The first triangle: $b$ measured against $a$
#
# Step 2 puts $b$ in $a$'s standard position: Step 1's rotation by $-\theta_a$, with
# $\theta_a = \operatorname{atan2}(a_2, a_1)$ the angle of $a$, carries $b$ to $(x, y)$,
# the signed lengths of $b$'s projection onto $a$ and of its rejection.


# %%
def standard_position(onto: Vector, v: Vector) -> Vector:
    """``v`` in ``onto``'s standard position (Step 2): rotated by minus the angle of
    ``onto``."""
    return v.rotate(-sympy.atan2(onto.coefficient(e_2), onto.coefficient(e_1)))


# %% [markdown]
# $b$ in $a$'s standard position:

# %%
measured: Vector = standard_position(a, b).simplified()
measured

# %% [markdown]
# Divided by $|b|$, its coordinates are the cosine and sine of the angle $\theta$ from
# $a$ to $b$, and the angle itself is never computed. The cosine:

# %%
cos: Real = sympy.simplify(sympy.sympify(measured.coefficient(e_1) / b.magnitude()))
cos

# %% [markdown]
# the sine:

# %%
sin: Real = sympy.simplify(sympy.sympify(measured.coefficient(e_2) / b.magnitude()))
sin

# %% [markdown]
# At the plot values, the cosine:

# %%
at_values(cos, values)

# %% [markdown]
# and the sine:

# %%
at_values(sin, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_FOOT: Point = point(coordinates=list(at_values(b.projected_onto(a), values)))
fig_first: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_first:
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
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
    note(at=0.22 * (P_A + P_B), text=r"$\theta$")
fig_first

# %% [markdown]
# ## The second triangle: the same angle on $v$
#
# $v' = \cos(\theta) * v + \sin(\theta) * r(v; \pi/2)$: the cosine part along $v$, the
# sine part across it. This step builds the rotation out of the cosine and sine the
# first triangle measured, without computing $\theta$, so it writes the blend out
# rather than calling `Vector.rotate`, which takes an angle. $b$ has no part in this
# triangle; only the angle carries over. The cosine part:

# %%
cos_part: Vector = Scalar(cos) * v
cos_part

# %% [markdown]
# the sine part:

# %%
sin_part: Vector = Scalar(sin) * v.rotate_90_degrees()
sin_part

# %% [markdown]
# and $v'$, their sum:

# %%
rotated: Vector = (cos_part + sin_part).simplified()
rotated

# %% [markdown]
# At the plot values:

# %%
at_values(rotated, values)

# %%
P_V: Point = point(coordinates=list(at_values(v, values)))
P_COS: Point = point(coordinates=list(at_values(cos_part, values)))
P_ROTATED: Point = point(coordinates=list(at_values(rotated, values)))
fig_second: PendingFigure
with scene_around(points=[P_V, P_ROTATED]) as fig_second:
    arrow(head=P_ROTATED, color=PURPLE)
    note(
        at=0.5 * P_ROTATED,
        text=r"$\vec{v}'$",
        color=PURPLE,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_V, color=BLACK, text=r"$\vec{v}$")
    arrow(head=P_COS, color=GREEN, width=2.4)
    note(
        at=0.5 * P_COS,
        text=r"$\cos(\theta) * \vec{v}$",
        color=GREEN,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    arrow(head=P_ROTATED, tail=P_COS, color=BLUE)
    note(
        at=0.5 * (P_COS + P_ROTATED),
        text=r"$\sin(\theta) * \vec{r}(\vec{v}; \pi/2)$",
        color=BLUE,
        offset=Point(x=-4, y=18),
        align=LabelPos.tl,
    )
    right_angle(corner=P_COS, toward_a=P_V, toward_b=P_ROTATED - P_COS)
    note(at=0.22 * (P_V + P_ROTATED), text=r"$\theta$")
fig_second

# %% [markdown]
# ## Checks, for all vectors
#
# Some checks run the construction on other vectors, so here it is as one function,
# the two triangles above in order.


# %%
def rotation_by_projection(a: Vector, b: Vector, v: Vector) -> Vector:
    """The two triangles: ``b`` measured against ``a`` gives the cosine and sine, and
    the same angle is applied to ``v``."""
    measured: Vector = standard_position(a, b)
    cos: Real = measured.coefficient(e_1) / b.magnitude()
    sin: Real = measured.coefficient(e_2) / b.magnitude()
    return (Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()).simplified()


# %% [markdown]
# ### The cosine and sine in coordinates
#
# The cosine was:

# %%
cos

# %% [markdown]
# The formula $(a_1 * b_1 + a_2 * b_2) / (|a| * |b|)$:

# %%
cos_formula: Real = (a_1 * b_1 + a_2 * b_2) / (a.magnitude() * b.magnitude())
cos_formula

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(cos - cos_formula))

# %% [markdown]
# The sine was:

# %%
sin

# %% [markdown]
# The formula $(a_1 * b_2 - a_2 * b_1) / (|a| * |b|)$:

# %%
sin_formula: Real = (a_1 * b_2 - a_2 * b_1) / (a.magnitude() * b.magnitude())
sin_formula

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(sin - sin_formula))

# %% [markdown]
# ### They are a unit pair
#
# $\cos(\theta)^2 + \sin(\theta)^2$:

# %%
sympy.simplify(sympy.sympify(cos**2 + sin**2))

# %% [markdown]
# Its difference from $1$:

# %%
sympy.simplify(sympy.sympify(cos**2 + sin**2 - 1))

# %% [markdown]
# ### The second triangle's legs are perpendicular
#
# The dot product of the cosine part and the sine part is $0$:

# %%
sympy.simplify(sympy.sympify(cos_part.dot(sin_part).scalar_part()))

# %% [markdown]
# ### It is the composition $(R_b^{e_1})^{-1} \circ R_a^{e_1}$
#
# Into $a$'s standard position, then back out of $b$'s: Step 1's rotation by
# $+\theta_b$, with $\theta_b$ the angle of $b$:

# %%
composed: Vector = standard_position(a, v).rotate(sympy.atan2(b_2, b_1)).simplified()
composed

# %% [markdown]
# $v'$ was:

# %%
rotated

# %% [markdown]
# Their difference:

# %%
(rotated - composed).simplified()

# %% [markdown]
# ### It keeps length
#
# $|v'|^2$:

# %%
sympy.simplify(sympy.sympify(rotated.magnitude_squared()))

# %% [markdown]
# $|v|^2$:

# %%
v.magnitude_squared()

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(rotated.magnitude_squared() - v.magnitude_squared()))

# %% [markdown]
# ### It carries sums to sums
#
# A second vector $w$:

# %%
w_1: sympy.Symbol
w_2: sympy.Symbol
w_1, w_2 = sympy.symbols("w_1 w_2", real=True)
w: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
w

# %% [markdown]
# The sum, rotated:

# %%
rotated_sum: Vector = rotation_by_projection(a, b, v + w)
rotated_sum

# %% [markdown]
# The sum of the rotated vectors:

# %%
sum_of_rotated: Vector = (rotated + rotation_by_projection(a, b, w)).simplified()
sum_of_rotated

# %% [markdown]
# Their difference:

# %%
(rotated_sum - sum_of_rotated).simplified()

# %% [markdown]
# ### and scalar multiples to scalar multiples
#
# $k * v$, rotated:

# %%
k: sympy.Symbol = sympy.Symbol("k", real=True)
rotated_multiple: Vector = rotation_by_projection(a, b, Scalar(k) * v)
rotated_multiple

# %% [markdown]
# $k * v'$:

# %%
(Scalar(k) * rotated).simplified()

# %% [markdown]
# Their difference:

# %%
(rotated_multiple - Scalar(k) * rotated).simplified()

# %% [markdown]
# ### Only directions matter
#
# Rescaling $a$ and $b$ by positive numbers $p$ and $q$:

# %%
p: sympy.Symbol
q: sympy.Symbol
p, q = sympy.symbols("p q", positive=True)
rescaled: Vector = rotation_by_projection(Scalar(p) * a, Scalar(q) * b, v)
rescaled

# %% [markdown]
# Its difference from $v'$:

# %%
(rescaled - rotated).simplified()

# %% [markdown]
# ### It carries $a$'s direction onto $b$'s
#
# $a$'s direction, rotated:

# %%
a_direction_rotated: Vector = rotation_by_projection(a, b, a.normalize())
a_direction_rotated

# %% [markdown]
# $b$'s direction:

# %%
b.normalize().simplified()

# %% [markdown]
# Their difference:

# %%
(a_direction_rotated - b.normalize()).simplified()

# %% [markdown]
# ### gacalc agrees
#
# gacalc's `projection_rotation`, applied to $v$:

# %%
turn: MultiVectorFn = projection_rotation(from_vector=a, to_vector=b)
turn(v).simplified()

# %% [markdown]
# Its difference from $v'$:

# %%
(turn(v) - rotated).simplified()
