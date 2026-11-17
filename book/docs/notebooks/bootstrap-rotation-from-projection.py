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
# Companion to *Step 3: Rotation from One Vector to Another, from Projection*. The
# next cell sets three vectors: $a$, $b$, and a $v$ to rotate. One right triangle is
# drawn twice. The first measures $b$ against $a$ (Step 2) and gives the cosine and sine
# of the angle from $a$ to $b$. The second is the same triangle on $v$, and its
# hypotenuse is the rotated $v'$. Change the vectors and rerun the notebook to see the
# same steps for others. The last section repeats the checks with every coordinate a
# symbol, so they hold for all vectors.

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
from gacalc.transforms import projection_rotation

# %% [markdown]
# ## The vectors
#
# Change these and rerun. $v$ is drawn outside the angle from $a$ to $b$, so the two
# triangles don't overlap.

# %%
a: Vector = 2 * e_1 + 1 * e_2
b: Vector = 1 * e_1 + 2 * e_2
v: Vector = -1 * e_1 + 2 * e_2


# %%
def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def standard_position(onto: Vector, v: Vector) -> Vector:
    """``v`` in ``onto``'s standard position (Step 2): its coordinates are the signed
    lengths of ``v``'s projection onto ``onto`` and of its rejection."""
    return rotate(
        onto.coefficient(e_1) / onto.magnitude(),
        -onto.coefficient(e_2) / onto.magnitude(),
        v,
    )


def rotation_from_to(a: Vector, b: Vector, v: Vector) -> Vector:
    """The two triangles: ``b`` measured against ``a`` gives the cosine and sine, and
    the same angle is applied to ``v``."""
    measured: Vector = standard_position(a, b)
    return rotate(
        measured.coefficient(e_1) / b.magnitude(),
        measured.coefficient(e_2) / b.magnitude(),
        v,
    )


# %% [markdown]
# ## The first triangle: $b$ measured against $a$
#
# Step 2 gives $x$ and $y$, the signed lengths of $b$'s projection onto $a$ and of its
# rejection. Divided by $|b|$ they are the cosine and sine of the angle $\theta$ from
# $a$ to $b$, and the angle itself is never computed.

# %%
measured: Vector = standard_position(a, b).simplified()
x: Real = measured.coefficient(e_1)
y: Real = measured.coefficient(e_2)
cos: Real = sympy.simplify(sympy.sympify(x / b.magnitude()))
sin: Real = sympy.simplify(sympy.sympify(y / b.magnitude()))
(cos, sin)

# %%
P_A: Point = point(coordinates=list(a))
P_B: Point = point(coordinates=list(b))
P_FOOT: Point = point(coordinates=list(b.projected_onto(a)))
fig_first: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_first:
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
    note(at=0.22 * (P_A + P_B), text=r"$\theta$")
fig_first

# %% [markdown]
# ## The second triangle: the same angle on $v$
#
# $v' = \cos(\theta) * v + \sin(\theta) * r(v; \pi/2)$: the cosine part along $v$, the
# sine part across it. $b$ has no part in this triangle; only the angle carries over.

# %%
cos_part: Vector = Scalar(cos) * v
sin_part: Vector = Scalar(sin) * v.rotate_90_degrees()
rotated: Vector = (cos_part + sin_part).simplified()
rotated

# %%
P_V: Point = point(coordinates=list(v))
P_COS: Point = point(coordinates=list(cos_part))
P_ROTATED: Point = point(coordinates=list(rotated))
fig_second: PendingFigure
with scene_around(points=[P_V, P_ROTATED]) as fig_second:
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
    arrow(head=P_ROTATED, color=PURPLE)
    note(
        at=0.5 * P_ROTATED,
        text=r"$\vec{v}'$",
        color=PURPLE,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    note(at=0.22 * (P_V + P_ROTATED), text=r"$\theta$")
fig_second

# %% [markdown]
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The cosine and sine are a unit pair:

# %%
sympy.simplify(sympy.sympify(cos**2 + sin**2 - 1))

# %% [markdown]
# The rotation keeps $v$'s length:

# %%
sympy.simplify(sympy.sympify(rotated.magnitude_squared() - v.magnitude_squared()))

# %% [markdown]
# It is the composition $(R_b^{e_1})^{-1} \circ R_a^{e_1}$: into $a$'s standard
# position, then back out of $b$'s (the sine negated):

# %%
(
    rotated
    - rotate(
        b.coefficient(e_1) / b.magnitude(),
        b.coefficient(e_2) / b.magnitude(),
        standard_position(a, v),
    )
).simplified()

# %% [markdown]
# It carries $a$'s direction onto $b$'s:

# %%
(rotate(cos, sin, a.normalize()) - b.normalize()).simplified()

# %% [markdown]
# gacalc's `projection_rotation` agrees:

# %%
turn: MultiVectorFn = projection_rotation(from_vector=a, to_vector=b)
(turn(v) - rotated).simplified()

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
w_1: sympy.Symbol
w_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2, w_1, w_2 = sympy.symbols(
    "a_1 a_2 b_1 b_2 v_1 v_2 w_1 w_2", real=True
)
k: sympy.Symbol = sympy.Symbol("k", real=True)
p: sympy.Symbol
q: sympy.Symbol
p, q = sympy.symbols("p q", positive=True)
a_symbolic: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b_symbolic: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
v_symbolic: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
w_symbolic: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
measured_symbolic: Vector = standard_position(a_symbolic, b_symbolic)
cos_symbolic: Real = measured_symbolic.coefficient(e_1) / b_symbolic.magnitude()
sin_symbolic: Real = measured_symbolic.coefficient(e_2) / b_symbolic.magnitude()
rotated_symbolic: Vector = rotation_from_to(a_symbolic, b_symbolic, v_symbolic)

# %% [markdown]
# The cosine is $(a_1 * b_1 + a_2 * b_2) / (|a| * |b|)$:

# %%
sympy.simplify(
    sympy.sympify(
        cos_symbolic
        - (a_1 * b_1 + a_2 * b_2) / (a_symbolic.magnitude() * b_symbolic.magnitude())
    )
)

# %% [markdown]
# The sine is $(a_1 * b_2 - a_2 * b_1) / (|a| * |b|)$:

# %%
sympy.simplify(
    sympy.sympify(
        sin_symbolic
        - (a_1 * b_2 - a_2 * b_1) / (a_symbolic.magnitude() * b_symbolic.magnitude())
    )
)

# %% [markdown]
# They are a unit pair:

# %%
sympy.simplify(sympy.sympify(cos_symbolic**2 + sin_symbolic**2 - 1))

# %% [markdown]
# The second triangle's legs are perpendicular:

# %%
sympy.simplify(
    sympy.sympify(
        (Scalar(cos_symbolic) * v_symbolic)
        .dot(Scalar(sin_symbolic) * v_symbolic.rotate_90_degrees())
        .scalar_part()
    )
)

# %% [markdown]
# It is the composition $(R_b^{e_1})^{-1} \circ R_a^{e_1}$:

# %%
(
    rotated_symbolic
    - rotate(
        b_symbolic.coefficient(e_1) / b_symbolic.magnitude(),
        b_symbolic.coefficient(e_2) / b_symbolic.magnitude(),
        standard_position(a_symbolic, v_symbolic),
    )
).simplified()

# %% [markdown]
# It keeps length:

# %%
sympy.simplify(
    sympy.sympify(rotated_symbolic.magnitude_squared() - v_symbolic.magnitude_squared())
)

# %% [markdown]
# It carries sums to sums:

# %%
(
    rotation_from_to(a_symbolic, b_symbolic, v_symbolic + w_symbolic)
    - (rotated_symbolic + rotation_from_to(a_symbolic, b_symbolic, w_symbolic))
).simplified()

# %% [markdown]
# and scalar multiples to scalar multiples:

# %%
(
    rotation_from_to(a_symbolic, b_symbolic, Scalar(k) * v_symbolic)
    - Scalar(k) * rotated_symbolic
).simplified()

# %% [markdown]
# Only directions matter: rescaling $a$ and $b$ by positive numbers changes nothing:

# %%
(
    rotation_from_to(Scalar(p) * a_symbolic, Scalar(q) * b_symbolic, v_symbolic)
    - rotated_symbolic
).simplified()

# %% [markdown]
# It carries $a$'s direction onto $b$'s:

# %%
(
    rotation_from_to(a_symbolic, b_symbolic, a_symbolic.normalize())
    - b_symbolic.normalize()
).simplified()
