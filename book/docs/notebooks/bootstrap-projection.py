# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 2, projection from rotation — worked example
#
# Companion to *Step 2: Projection, from Rotation*. The next cell sets the two vectors.
# Every step after it is computed from them and drawn: rotate $a$ onto the x-axis,
# carrying $b$ along; apply the base cases there (keep the x-coordinate for the
# projection, the y-coordinate for the rejection); rotate back. Change the vectors and
# rerun the notebook to see the same steps for others. The last section repeats the
# checks with every coordinate a symbol, so they hold for all vectors.

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
from gacalc.g2 import Scalar, Vector, e_1, e_2

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


P_A: Point = point(coordinates=list(a))
P_B: Point = point(coordinates=list(b))
fig_given: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_given:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
fig_given

# %% [markdown]
# ## Rotate $a$ onto the x-axis, carrying $b$ along
#
# The cosine and sine of the rotation are read off $a$: $a_1 / |a|$ and $-a_2 / |a|$.
# The rotation sends $a$ to $|a| * e_1$.

# %%
cos: Real = a.coefficient(e_1) / a.magnitude()
sin: Real = -a.coefficient(e_2) / a.magnitude()
a_rotated: Vector = rotate(cos, sin, a).simplified()
a_rotated

# %%
b_rotated: Vector = rotate(cos, sin, b).simplified()
b_rotated

# %%
P_A_ROTATED: Point = point(coordinates=list(a_rotated))
P_B_ROTATED: Point = point(coordinates=list(b_rotated))
fig_rotated: PendingFigure
with scene_around(points=[P_A, P_B, P_A_ROTATED, P_B_ROTATED]) as fig_rotated:
    dashed_arrow(tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{a}$")
    dashed_arrow(tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_A_ROTATED, color=BLACK, text=r"$\vec{a}'$", align=LabelPos.b)
    arrow(head=P_B_ROTATED, color=BLACK, text=r"$\vec{b}'$")
fig_rotated

# %% [markdown]
# ## The base cases, on the x-axis
#
# $\operatorname{proj}_{e_1}(b') = x * e_1$ keeps $b'$'s x-coordinate and
# $\operatorname{rej}_{e_1}(b') = y * e_2$ keeps its y-coordinate. $x$ and $y$ are the
# signed lengths of $b$'s projection onto $a$ and of its rejection.

# %%
x: Real = b_rotated.coefficient(e_1)
y: Real = b_rotated.coefficient(e_2)
(x, y)

# %%
P_X: Point = point(coordinates=list(Scalar(x) * e_1))
fig_base: PendingFigure
with scene_around(points=[P_A_ROTATED, P_B_ROTATED]) as fig_base:
    arrow(head=P_A_ROTATED, color=BLACK, text=r"$\vec{a}'$", align=LabelPos.b)
    arrow(head=P_B_ROTATED, color=BLACK, text=r"$\vec{b}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    note(
        at=0.5 * P_X,
        text=r"$x * e_1$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_B_ROTATED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_B_ROTATED),
        text=r"$y * e_2$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_X, toward_a=P_A_ROTATED, toward_b=P_B_ROTATED - P_X)
fig_base

# %% [markdown]
# ## Rotate back
#
# The rotation back negates the sine. It carries $x * e_1$ to the projection of $b$
# onto $a$, and $y * e_2$ to the rejection.

# %%
projection: Vector = rotate(cos, -sin, Scalar(x) * e_1).simplified()
projection

# %%
rejection: Vector = rotate(cos, -sin, Scalar(y) * e_2).simplified()
rejection

# %%
P_PROJECTION: Point = point(coordinates=list(projection))
fig_back: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_back:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{a}}(\vec{b})$",
        color=GREEN,
        offset=Point(x=4, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_B),
        text=r"$\operatorname{rej}_{\vec{a}}(\vec{b})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_A, toward_b=P_B - P_PROJECTION)
fig_back

# %% [markdown]
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, $0$ when they agree.
#
# The projection matches the formula
# $(a_1 * b_1 + a_2 * b_2) / (a_1^2 + a_2^2) * a$:

# %%
a_1: Real = a.coefficient(e_1)
a_2: Real = a.coefficient(e_2)
b_1: Real = b.coefficient(e_1)
b_2: Real = b.coefficient(e_2)
(projection - Scalar((a_1 * b_1 + a_2 * b_2) / (a_1**2 + a_2**2)) * a).simplified()

# %% [markdown]
# The rejection matches the formula
# $(a_1 * b_2 - a_2 * b_1) / (a_1^2 + a_2^2) * r(a; \pi/2)$:

# %%
(
    rejection
    - Scalar((a_1 * b_2 - a_2 * b_1) / (a_1**2 + a_2**2)) * a.rotate_90_degrees()
).simplified()

# %% [markdown]
# The two parts add back to $b$:

# %%
(projection + rejection - b).simplified()

# %% [markdown]
# gacalc's projection, $(b \cdot a) * a^{-1}$ (Step 5's formula), agrees:

# %%
(projection - b.projected_onto(a)).simplified()

# %% [markdown]
# ## For all vectors
#
# The same construction with every coordinate a symbol. Each cell checks one fact.


# %%
def project_and_reject(onto: Vector, v: Vector) -> tuple[Vector, Vector]:
    """Step 2's construction: rotate ``onto`` to the x-axis, apply the base cases,
    rotate back."""
    cos_onto: Real = onto.coefficient(e_1) / onto.magnitude()
    sin_onto: Real = -onto.coefficient(e_2) / onto.magnitude()
    v_rotated: Vector = rotate(cos_onto, sin_onto, v)
    return (
        rotate(cos_onto, -sin_onto, Scalar(v_rotated.coefficient(e_1)) * e_1),
        rotate(cos_onto, -sin_onto, Scalar(v_rotated.coefficient(e_2)) * e_2),
    )


s_1: sympy.Symbol
s_2: sympy.Symbol
t_1: sympy.Symbol
t_2: sympy.Symbol
s_1, s_2, t_1, t_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a_symbolic: Vector = Scalar(s_1) * e_1 + Scalar(s_2) * e_2
b_symbolic: Vector = Scalar(t_1) * e_1 + Scalar(t_2) * e_2
projection_symbolic: Vector
rejection_symbolic: Vector
projection_symbolic, rejection_symbolic = project_and_reject(a_symbolic, b_symbolic)

# %% [markdown]
# On the x-axis the construction gives back the base case
# $\operatorname{proj}_{e_1}(b) = b_1 * e_1$:

# %%
(project_and_reject(1 * e_1, b_symbolic)[0] - Scalar(t_1) * e_1).simplified()

# %% [markdown]
# and the base case $\operatorname{rej}_{e_1}(b) = b_2 * e_2$:

# %%
(project_and_reject(1 * e_1, b_symbolic)[1] - Scalar(t_2) * e_2).simplified()

# %% [markdown]
# The projection formula:

# %%
(
    projection_symbolic
    - Scalar((s_1 * t_1 + s_2 * t_2) / (s_1**2 + s_2**2)) * a_symbolic
).simplified()

# %% [markdown]
# The rejection formula:

# %%
(
    rejection_symbolic
    - Scalar((s_1 * t_2 - s_2 * t_1) / (s_1**2 + s_2**2))
    * a_symbolic.rotate_90_degrees()
).simplified()

# %% [markdown]
# The two parts add back to $b$:

# %%
(projection_symbolic + rejection_symbolic - b_symbolic).simplified()

# %% [markdown]
# Projecting twice changes nothing:

# %%
(
    project_and_reject(a_symbolic, projection_symbolic)[0] - projection_symbolic
).simplified()

# %% [markdown]
# The rejection has no part along $a$:

# %%
project_and_reject(a_symbolic, rejection_symbolic)[0].simplified()

# %% [markdown]
# gacalc's projection agrees:

# %%
(projection_symbolic - b_symbolic.projected_onto(a_symbolic)).simplified()

# %% [markdown]
# and gacalc's rejection:

# %%
(rejection_symbolic - b_symbolic.rejected_away_from(a_symbolic)).simplified()
