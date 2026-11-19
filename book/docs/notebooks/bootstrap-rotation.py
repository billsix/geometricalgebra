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
# Companion to *Step 1: Rotation, from Precalculus*. Every step is computed with a
# symbolic vector and angle, so each result is a formula for every vector and angle:
# the quarter turn (the base case), then the rotation by the angle as a blend of the
# vector and its quarter turn. Numbers appear only to draw the figures; change them and
# rerun. Each check shows both sides, then their difference.

# %%
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
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
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## The vector and the angle
#
# $\vec{\mathbf{v}}$, every coordinate a symbol, and the angle $\theta$:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
theta: sympy.Symbol
v_1, v_2, theta = sympy.symbols("v_1 v_2 theta", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(v_1, 2), (v_2, 1), (theta, sympy.pi / 3)]

# %% [markdown]
# ## The base case: the quarter turn
#
# $r(\vec{\mathbf{v}}; \pi/2) = (-v_2, v_1)$: swap the coordinates and change the sign
# of the new first one.

# %%
quarter_turn: Vector = v.rotate_90_degrees()
quarter_turn

# %% [markdown]
# At the plot values:

# %%
at_values(quarter_turn, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_V: Point = point(coordinates=list(at_values(v, values)))
P_QUARTER: Point = point(coordinates=list(at_values(quarter_turn, values)))
fig_quarter: PendingFigure
with scene_around(points=[P_V, P_QUARTER]) as fig_quarter:
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$",
        align=LabelPos.l,
        offset=Point(x=-6, y=4),
    )
    right_angle(corner=Point(x=0, y=0), toward_a=P_V, toward_b=P_QUARTER)
fig_quarter

# %% [markdown]
# ## The rotation by the angle
#
# $r(\vec{\mathbf{v}}; \theta) = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * r(\vec{\mathbf{v}}; \pi/2)$:
# the cosine part along $\vec{\mathbf{v}}$:

# %%
cos_part: Vector = Scalar(sympy.cos(theta)) * v
cos_part

# %% [markdown]
# the sine part along its quarter turn:

# %%
sin_part: Vector = Scalar(sympy.sin(theta)) * quarter_turn
sin_part

# %% [markdown]
# and their sum, the rotated vector:

# %%
rotated: Vector = (cos_part + sin_part).simplified()
rotated

# %% [markdown]
# At the plot values, the cosine part:

# %%
at_values(cos_part, values)

# %% [markdown]
# and the rotated vector:

# %%
at_values(rotated, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_COS: Point = point(coordinates=list(at_values(cos_part, values)))
P_ROTATED: Point = point(coordinates=list(at_values(rotated, values)))
fig_rotated: PendingFigure
with scene_around(points=[P_V, P_QUARTER, P_ROTATED]) as fig_rotated:
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$",
        align=LabelPos.l,
        offset=Point(x=-6, y=4),
    )
    arrow(
        head=P_ROTATED,
        color=PURPLE,
        text=r"$\vec{\mathbf{r}}(\vec{\mathbf{v}}; \theta)$",
    )
    arrow(head=P_COS, color=GREEN, width=2.4)
    note(
        at=0.5 * P_COS,
        text=r"$\cos(\theta) * \vec{\mathbf{v}}$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_ROTATED, tail=P_COS, color=BLUE)
    note(
        at=0.5 * (P_COS + P_ROTATED),
        text=r"$\sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
fig_rotated

# %% [markdown]
# ## gacalc's rotation is this blend
#
# `Vector.rotate(θ)` gives:

# %%
v.rotate(theta).simplified()

# %% [markdown]
# The blend gave:

# %%
rotated

# %% [markdown]
# Their difference:

# %%
(v.rotate(theta) - rotated).simplified()

# %% [markdown]
# So from here on the checks use `Vector.rotate`.
#
# ## Checks, for all vectors and angles
#
# ### The base case lands a quarter turn further round
#
# A vector of length $r$ at angle $\beta$:

# %%
r: sympy.Symbol
beta: sympy.Symbol
r, beta = sympy.symbols("r beta", real=True)
polar: Vector = Scalar(r * sympy.cos(beta)) * e_1 + Scalar(r * sympy.sin(beta)) * e_2
polar

# %% [markdown]
# turned a quarter turn:

# %%
polar.rotate_90_degrees()

# %% [markdown]
# The vector of length $r$ at angle $\beta + \pi/2$:

# %%
at_quarter_further: Vector = (
    Scalar(r * sympy.cos(beta + sympy.pi / 2)) * e_1
    + Scalar(r * sympy.sin(beta + sympy.pi / 2)) * e_2
)
at_quarter_further

# %% [markdown]
# Their difference:

# %%
(polar.rotate_90_degrees() - at_quarter_further).simplified()

# %% [markdown]
# ### The formula lands $\theta$ further round
#
# The polar vector rotated by $\theta$:

# %%
polar.rotate(theta).simplified()

# %% [markdown]
# The vector of length $r$ at angle $\beta + \theta$:

# %%
at_theta_further: Vector = (
    Scalar(r * sympy.cos(beta + theta)) * e_1
    + Scalar(r * sympy.sin(beta + theta)) * e_2
)
at_theta_further

# %% [markdown]
# Their difference:

# %%
(polar.rotate(theta) - at_theta_further).simplified()

# %% [markdown]
# ### A rotation keeps length
#
# The rotated vector's length squared:

# %%
rotated_length_squared: Real = sympy.simplify(
    sympy.sympify(v.rotate(theta).magnitude_squared())
)
rotated_length_squared

# %% [markdown]
# $\vec{\mathbf{v}}$'s length squared:

# %%
v.magnitude_squared()

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(rotated_length_squared - v.magnitude_squared()))

# %% [markdown]
# ### Rotations add their angles
#
# Rotating by $\theta$ and then by $\phi$:

# %%
phi: sympy.Symbol
phi = sympy.Symbol("phi", real=True)
theta_then_phi: Vector = v.rotate(theta).rotate(phi).simplified()
theta_then_phi

# %% [markdown]
# Rotating by $\theta + \phi$:

# %%
v.rotate(theta + phi).simplified()

# %% [markdown]
# Their difference:

# %%
(theta_then_phi - v.rotate(theta + phi)).simplified()

# %% [markdown]
# ### Rotating by $-\theta$ undoes a rotation
#
# The rotated vector, rotated back by $-\theta$ (the sine negated):

# %%
v.rotate(theta).rotate(-theta).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{v}}$:

# %%
(v.rotate(theta).rotate(-theta) - v).simplified()

# %% [markdown]
# ### A rotation carries sums to sums
#
# A second vector $\vec{\mathbf{w}}$:

# %%
w_1: sympy.Symbol
w_2: sympy.Symbol
w_1, w_2 = sympy.symbols("w_1 w_2", real=True)
w: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
w

# %% [markdown]
# The sum, rotated:

# %%
(v + w).rotate(theta).simplified()

# %% [markdown]
# The sum of the rotated vectors:

# %%
(v.rotate(theta) + w.rotate(theta)).simplified()

# %% [markdown]
# Their difference:

# %%
((v + w).rotate(theta) - (v.rotate(theta) + w.rotate(theta))).simplified()

# %% [markdown]
# ### and scalar multiples to scalar multiples
#
# $k * \vec{\mathbf{v}}$, rotated:

# %%
k: sympy.Symbol
k = sympy.Symbol("k", real=True)
(Scalar(k) * v).rotate(theta).simplified()

# %% [markdown]
# $k$ times the rotated $\vec{\mathbf{v}}$:

# %%
(Scalar(k) * v.rotate(theta)).simplified()

# %% [markdown]
# Their difference:

# %%
((Scalar(k) * v).rotate(theta) - Scalar(k) * v.rotate(theta)).simplified()
