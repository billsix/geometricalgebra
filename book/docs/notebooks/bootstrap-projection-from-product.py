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
# Companion to *Step 5: Projection, through the Product*. The next cell sets two
# vectors. Every step after it is computed from them and drawn: the inverse of `a`,
# then the projection `(b · a) * a⁻¹` and the rejection `(b ∧ a) * a⁻¹`, which match
# Step 2's construction by rotation. Change the vectors and rerun the notebook to see
# the same steps for others. The last section repeats the checks with every coordinate
# a symbol, so they hold for all vectors.

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
from gacalc.nbdisplay import show_mult

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


def project_and_reject_by_rotation(onto: Vector, v: Vector) -> tuple[Vector, Vector]:
    """Step 2's construction: rotate ``onto`` to the x-axis, apply the base cases,
    rotate back."""
    cos: Real = onto.coefficient(e_1) / onto.magnitude()
    sin: Real = -onto.coefficient(e_2) / onto.magnitude()
    v_rotated: Vector = rotate(cos, sin, v)
    return (
        rotate(cos, -sin, Scalar(v_rotated.coefficient(e_1)) * e_1),
        rotate(cos, -sin, Scalar(v_rotated.coefficient(e_2)) * e_2),
    )


# %% [markdown]
# ## The inverse of a vector
#
# `a * a = |a|^2` is a plain number, so `a⁻¹ = a / |a|^2`: along `a`, at length
# `1 / |a|`.

# %%
a_inverse: Vector = a.inverse()
a_inverse

# %% [markdown]
# ## The projection through the product
#
# `proj_a(b) = (b · a) * a⁻¹`, where `b · a` is the plain-number part of `b * a`.

# %% [markdown]
# `b * a` term by term. Its plain-number part, the sum of the `e_1 * e_1` and
# `e_2 * e_2` rows, is `b · a`:

# %%
show_mult(b, a)

# %%
b_dot_a: Real = (b * a).scalar_part()
projection: Vector = (Scalar(b_dot_a) * a_inverse).simplified()
projection

# %% [markdown]
# ## The rejection, the same way
#
# `rej_a(b) = (b ∧ a) * a⁻¹`.

# %% [markdown]
# `(b ∧ a) * a⁻¹` term by term: `e_12` times each term of `a⁻¹` is a quarter turn of
# that term, so the result is a vector again:

# %%
show_mult(b.wedge(a), a_inverse)

# %%
rejection: MultiVectorBase = (b.wedge(a) * a_inverse).simplified()
rejection

# %%
P_A: Point = point(coordinates=list(a))
P_B: Point = point(coordinates=list(b))
P_INVERSE: Point = point(coordinates=list(a_inverse))
P_PROJECTION: Point = point(coordinates=list(projection))
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
# ## Checks on these vectors
#
# Each cell subtracts two things and shows the difference, `0` when they agree.
#
# `a * a⁻¹ = 1`:

# %%
(a * a_inverse - Scalar(1)).simplified()

# %% [markdown]
# The projection through the product is Step 2's projection, built by rotating:

# %%
by_rotation_projection: Vector
by_rotation_rejection: Vector
by_rotation_projection, by_rotation_rejection = project_and_reject_by_rotation(a, b)
(projection - by_rotation_projection).simplified()

# %% [markdown]
# The rejection through the product is Step 2's rejection:

# %%
(rejection - by_rotation_rejection).simplified()

# %% [markdown]
# Together they give back `b`, since `b * a * a⁻¹ = b`:

# %%
(projection + rejection - b).simplified()

# %% [markdown]
# gacalc's projection agrees:

# %%
(projection - b.projected_onto(a)).simplified()

# %% [markdown]
# and gacalc's rejection:

# %%
(rejection - b.rejected_away_from(a)).simplified()

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
projection_symbolic: Vector = (
    Scalar((b_symbolic * a_symbolic).scalar_part()) * a_symbolic.inverse()
)
rejection_symbolic: MultiVectorBase = (
    b_symbolic.wedge(a_symbolic) * a_symbolic.inverse()
)
by_rotation_projection_symbolic: Vector
by_rotation_rejection_symbolic: Vector
by_rotation_projection_symbolic, by_rotation_rejection_symbolic = (
    project_and_reject_by_rotation(a_symbolic, b_symbolic)
)

# %% [markdown]
# `b * a` term by term, for every `a` and `b`; its plain-number part is
# `a_1 * b_1 + a_2 * b_2`:

# %%
show_mult(b_symbolic, a_symbolic)

# %% [markdown]
# `a⁻¹ = a / |a|^2`:

# %%
(a_symbolic.inverse() - Scalar(1 / (a_1**2 + a_2**2)) * a_symbolic).simplified()

# %% [markdown]
# `a * a⁻¹ = 1`:

# %%
(a_symbolic * a_symbolic.inverse() - Scalar(1)).simplified()

# %% [markdown]
# The projection through the product is Step 2's projection:

# %%
(projection_symbolic - by_rotation_projection_symbolic).simplified()

# %% [markdown]
# The rejection through the product is Step 2's rejection:

# %%
(rejection_symbolic - by_rotation_rejection_symbolic).simplified()

# %% [markdown]
# Together they give back `b`:

# %%
(projection_symbolic + rejection_symbolic - b_symbolic).simplified()
