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
# # Projection by standard position — calculations
#
# Companion to the *Proof: Projection by Rotating to Standard Position* chapter.
# Projecting onto the x-axis is easy: keep the x-coordinate. The chapter projects onto
# any nonzero $b$ by making $b$ the x-axis for a moment: rotate so that $b$ lies on the
# x-axis, keep the x-coordinate (the projection) and the y-coordinate (the rejection),
# then rotate back.
#
# Every step here is computed with symbolic coordinates $a_1, a_2, b_1, b_2$, so each
# result is a formula that holds for every $a$ and $b$. Numbers appear only to draw the
# figures: one cell sets them, and each step also shows its formula with those numbers
# substituted. The Lean theorem is `projectSP_eq_proj` in
# `proofs/GacalcProofs/StandardPosition.lean`.

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
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# ## The vectors
#
# $a$ and $b$ have symbolic coordinates:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
a

# %%
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun; the formulas do not
# change, only the pictures and the substituted results.

# %%
values: list[tuple[sympy.Symbol, int]] = [(a_1, 1), (a_2, 4), (b_1, 2), (b_2, 1)]


def number_at_values(r: Real) -> Real:
    """``r`` with the plot values substituted for the symbols."""
    return sympy.nsimplify(sympy.sympify(r).subs(values))


def vector_at_values(v: Vector) -> Vector:
    """``v`` with the plot values substituted for the symbols."""
    return (
        Scalar(number_at_values(v.coefficient(e_1))) * e_1
        + Scalar(number_at_values(v.coefficient(e_2))) * e_2
    ).simplified()


def plot_point(v: Vector) -> Point:
    """Where ``v`` lands in the figures, at the plot values."""
    return point(coordinates=list(vector_at_values(v)))


# %%
P_A: Point = plot_point(a)
P_B: Point = plot_point(b)
fig_given: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_given:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$")
fig_given

# %% [markdown]
# ## Step 1: rotate $b$ onto the x-axis, carrying $a$ along
#
# The rotation is the one built in *Proof: Rotate from the Direction of a to the
# Direction of b*: the rotation $R_{\vec{b}}^{e_1}$ from $b$'s direction to $e_1$'s. In
# gacalc it is `rotation_from_to`:

# %%
R: InvertibleFunction[Vector] = rotation_from_to(b, e_1)
R

# %% [markdown]
# Its cosine and sine are read straight off $b$'s coordinates, with no angle computed:
# $R_{\vec{b}}^{e_1}$ sends $e_1$ to $\cos(-\theta) * e_1 + \sin(-\theta) * e_2$, with
# $\theta$ the angle of $b$:

# %%
R(1 * e_1).simplified()

# %% [markdown]
# $b$ lands on the x-axis at its length $|b|$:

# %%
b_aligned: Vector = R(b).simplified()
b_aligned

# %% [markdown]
# At the plot values:

# %%
vector_at_values(b_aligned)

# %% [markdown]
# $a$ rides along. Its x-coordinate there is $a \cdot b / |b|$, how far $a$ reaches
# along $b$, and its y-coordinate is $(a_2 * b_1 - a_1 * b_2) / |b|$, how far across:

# %%
a_aligned: Vector = R(a).simplified()
a_aligned

# %% [markdown]
# At the plot values:

# %%
vector_at_values(a_aligned)

# %%
P_A_ALIGNED: Point = plot_point(a_aligned)
P_B_ALIGNED: Point = plot_point(b_aligned)
fig_rotated: PendingFigure
with scene_around(points=[P_A, P_B, P_A_ALIGNED, P_B_ALIGNED]) as fig_rotated:
    dashed_arrow(tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{a}$")
    dashed_arrow(tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{b}$")
    arrow(head=P_A_ALIGNED, color=BLACK, text=r"$\vec{a}'$")
    arrow(head=P_B_ALIGNED, color=BLACK, text=r"$\vec{b}'$", align=LabelPos.b)
fig_rotated

# %% [markdown]
# ## Step 2: on the x-axis, keep each coordinate
#
# $\operatorname{proj}_{e_1}(a') = x * e_1$ keeps $a'$'s x-coordinate and
# $\operatorname{rej}_{e_1}(a') = y * e_2$ keeps its y-coordinate:

# %%
x: Real = a_aligned.coefficient(e_1)
y: Real = a_aligned.coefficient(e_2)
x

# %%
y

# %% [markdown]
# At the plot values:

# %%
number_at_values(x)

# %%
number_at_values(y)

# %%
P_X: Point = plot_point(Scalar(x) * e_1)
fig_base: PendingFigure
with scene_around(points=[P_A_ALIGNED, P_B_ALIGNED]) as fig_base:
    arrow(head=P_A_ALIGNED, color=BLACK, text=r"$\vec{a}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    arrow(head=P_B_ALIGNED, color=BLACK, text=r"$\vec{b}'$", align=LabelPos.t)
    note(
        at=0.5 * P_X,
        text=r"$x * e_1$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_ALIGNED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_A_ALIGNED),
        text=r"$y * e_2$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_X, toward_a=P_B_ALIGNED, toward_b=P_A_ALIGNED - P_X)
fig_base

# %% [markdown]
# ## Step 3: rotate back
#
# The rotation back is the inverse,
# $(R_{\vec{b}}^{e_1})^{-1} = R_{e_1}^{\vec{b}}$, from $e_1$'s direction to $b$'s:

# %%
inverse(R)

# %% [markdown]
# It carries $x * e_1$ to the projection of $a$ onto $b$:

# %%
projection: Vector = inverse(R)(Scalar(x) * e_1).simplified()
projection

# %% [markdown]
# At the plot values:

# %%
vector_at_values(projection)

# %% [markdown]
# and $y * e_2$ to the rejection:

# %%
rejection: Vector = inverse(R)(Scalar(y) * e_2).simplified()
rejection

# %% [markdown]
# At the plot values:

# %%
vector_at_values(rejection)

# %%
P_PROJECTION: Point = plot_point(projection)
fig_back: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_back:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    arrow(head=P_B, color=BLACK, text=r"$\vec{b}$", align=LabelPos.t)
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{b}}(\vec{a})$",
        color=GREEN,
        offset=Point(x=6, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_A, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_A),
        text=r"$\operatorname{rej}_{\vec{b}}(\vec{a})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_B, toward_b=P_A - P_PROJECTION)
fig_back

# %% [markdown]
# ## Checks, for every $a$ and $b$
#
# Each check shows both formulas, then their difference. The coordinates are symbols,
# so a difference of $0$ holds for every $a$ and every nonzero $b$.
#
# ### The construction is gacalc's projection
#
# The construction gave:

# %%
projection

# %% [markdown]
# gacalc's projection, $(a \cdot b) * b^{-1}$, gives:

# %%
a.projected_onto(b).simplified()

# %% [markdown]
# Their difference:

# %%
(projection - a.projected_onto(b)).simplified()

# %% [markdown]
# ### The projection plus the rejection is $a$
#
# The sum of the two parts:

# %%
(projection + rejection).simplified()

# %% [markdown]
# and $a$:

# %%
a

# %% [markdown]
# Their difference:

# %%
(projection + rejection - a).simplified()
