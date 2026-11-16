# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 1, rotation — worked example
#
# Companion to *Step 1: Rotation, from Precalculus*. The next cell sets a vector and an
# angle. Every step after it is computed from them and drawn: the quarter turn (the base
# case), then the rotation by the angle as a blend of the vector and its quarter turn.
# Change the vector or the angle and rerun the notebook to see the same steps for
# others. The last section repeats the checks with every coordinate and angle a symbol,
# so they hold for all vectors and angles.

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

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2

# %% [markdown]
# ## The vector and the angle
#
# Change these and rerun.

# %%
v: Vector = 2 * e_1 + 1 * e_2
theta: sympy.Expr = sympy.pi / 3


# %%
def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin``: the blend of
    ``v`` and its quarter turn."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


# %% [markdown]
# ## The base case: the quarter turn
#
# $r(v; \pi/2) = (-v_2, v_1)$: swap the coordinates and change the sign of the new first
# one.

# %%
quarter_turn: Vector = v.rotate_90_degrees()
quarter_turn

# %%
P_V: Point = point(coordinates=list(v))
P_QUARTER: Point = point(coordinates=list(quarter_turn))
fig_quarter: PendingFigure
with scene_around(points=[P_V, P_QUARTER]) as fig_quarter:
    arrow(head=P_V, color=BLACK, text=r"$\vec{v}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{r}(\vec{v}; \pi/2)$",
        align=LabelPos.l,
        offset=Point(x=-6, y=4),
    )
    right_angle(corner=Point(x=0, y=0), toward_a=P_V, toward_b=P_QUARTER)
fig_quarter

# %% [markdown]
# ## The rotation by the angle
#
# $r(v; \theta) = \cos(\theta) * v + \sin(\theta) * r(v; \pi/2)$: the cosine part along
# $v$, the sine part along its quarter turn.

# %%
cos_part: Vector = Scalar(sympy.cos(theta)) * v
sin_part: Vector = Scalar(sympy.sin(theta)) * quarter_turn
rotated: Vector = (cos_part + sin_part).simplified()
rotated

# %%
P_COS: Point = point(coordinates=list(cos_part))
P_ROTATED: Point = point(coordinates=list(rotated))
fig_rotated: PendingFigure
with scene_around(points=[P_V, P_QUARTER, P_ROTATED]) as fig_rotated:
    arrow(head=P_V, color=BLACK, text=r"$\vec{v}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{r}(\vec{v}; \pi/2)$",
        align=LabelPos.l,
        offset=Point(x=-6, y=4),
    )
    arrow(head=P_COS, color=GREEN, width=2.4)
    note(
        at=0.5 * P_COS,
        text=r"$\cos(\theta) * \vec{v}$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_ROTATED, tail=P_COS, color=BLUE)
    note(
        at=0.5 * (P_COS + P_ROTATED),
        text=r"$\sin(\theta) * \vec{r}(\vec{v}; \pi/2)$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    arrow(head=P_ROTATED, color=PURPLE, text=r"$\vec{r}(\vec{v}; \theta)$")
fig_rotated

# %% [markdown]
# ## Checks on this vector and angle
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The rotation keeps length:

# %%
sympy.simplify(sympy.sympify(rotated.magnitude_squared() - v.magnitude_squared()))

# %% [markdown]
# Rotating back by $-\theta$ (the sine negated) gives $v$ again:

# %%
(rotate(sympy.cos(theta), -sympy.sin(theta), rotated) - v).simplified()

# %% [markdown]
# gacalc's `Vector.rotate(θ)` is the same blend:

# %%
(v.rotate(theta) - rotated).simplified()

# %% [markdown]
# ## For all vectors and angles
#
# The same steps with every coordinate and angle a symbol. Each cell checks one fact.

# %%
r: sympy.Symbol
beta: sympy.Symbol
phi: sympy.Symbol
k: sympy.Symbol
theta_symbolic: sympy.Symbol
r, beta, phi, k, theta_symbolic = sympy.symbols("r beta phi k theta", real=True)
v_1: sympy.Symbol
v_2: sympy.Symbol
w_1: sympy.Symbol
w_2: sympy.Symbol
v_1, v_2, w_1, w_2 = sympy.symbols("v_1 v_2 w_1 w_2", real=True)
v_symbolic: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
w_symbolic: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
polar: Vector = Scalar(r * sympy.cos(beta)) * e_1 + Scalar(r * sympy.sin(beta)) * e_2
c: sympy.Expr = sympy.cos(theta_symbolic)
s: sympy.Expr = sympy.sin(theta_symbolic)
rotated_symbolic: Vector = rotate(c, s, v_symbolic)

# %% [markdown]
# The base case: a vector of length $r$ at angle $\beta$, turned a quarter turn, lands
# at angle $\beta + \pi/2$:

# %%
(
    polar.rotate_90_degrees()
    - (
        Scalar(r * sympy.cos(beta + sympy.pi / 2)) * e_1
        + Scalar(r * sympy.sin(beta + sympy.pi / 2)) * e_2
    )
).simplified()

# %% [markdown]
# The formula: rotated by $\theta$, it lands at angle $\beta + \theta$:

# %%
(
    rotate(c, s, polar)
    - (
        Scalar(r * sympy.cos(beta + theta_symbolic)) * e_1
        + Scalar(r * sympy.sin(beta + theta_symbolic)) * e_2
    )
).simplified()

# %% [markdown]
# A rotation keeps length:

# %%
sympy.simplify(
    sympy.sympify(rotated_symbolic.magnitude_squared() - v_symbolic.magnitude_squared())
)

# %% [markdown]
# Rotations add their angles:

# %%
(
    rotate(sympy.cos(phi), sympy.sin(phi), rotated_symbolic)
    - rotate(
        sympy.cos(theta_symbolic + phi), sympy.sin(theta_symbolic + phi), v_symbolic
    )
).simplified()

# %% [markdown]
# The negated sine undoes a rotation:

# %%
(rotate(c, -s, rotated_symbolic) - v_symbolic).simplified()

# %% [markdown]
# A rotation carries sums to sums:

# %%
(
    rotate(c, s, v_symbolic + w_symbolic)
    - (rotate(c, s, v_symbolic) + rotate(c, s, w_symbolic))
).simplified()

# %% [markdown]
# and scalar multiples to scalar multiples:

# %%
(rotate(c, s, Scalar(k) * v_symbolic) - Scalar(k) * rotated_symbolic).simplified()

# %% [markdown]
# gacalc's `Vector.rotate(θ)` agrees:

# %%
(v_symbolic.rotate(theta_symbolic) - rotated_symbolic).simplified()
