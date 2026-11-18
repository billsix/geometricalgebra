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
# any nonzero $\vec{\mathbf{b}}$ by making $\vec{\mathbf{b}}$ the x-axis for a moment:
# rotate so that $\vec{\mathbf{b}}$ lies on the x-axis, keep the x-coordinate (the
# projection) and the y-coordinate (the rejection), then rotate back.
#
# Every step here is computed with symbolic coordinates $a_1, a_2, b_1, b_2$, so each
# result is a formula that holds for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$.
# Numbers appear only to draw the figures: one cell sets them, and each step also shows
# its formula with those numbers substituted. The Lean theorem is `projectSP_eq_proj` in
# `proofs/GacalcProofs/StandardPosition.lean`.

# %%
# twin: GacalcProofs.G3.projectSP_eq_proj
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
from gacalc.nbdisplay import at_values
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$ have symbolic coordinates:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun; the formulas do not
# change, only the pictures and the substituted results.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 1), (a_2, 4), (b_1, 2), (b_2, 1)]

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_given:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
fig_given

# %% [markdown]
# ## Step 1: rotate $\vec{\mathbf{b}}$ onto the x-axis, carrying $\vec{\mathbf{a}}$ along
#
# The rotation is the one built in *Proof: Rotate from the Direction of a to the
# Direction of b*: the rotation $R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}$ from
# $\vec{\mathbf{b}}$'s direction to $\vec{\mathbf{e}}_1$'s. In gacalc it is
# `rotation_from_to`:

# %%
R: InvertibleFunction[Vector] = rotation_from_to(b, e_1)
R

# %% [markdown]
# Its cosine and sine are read straight off $\vec{\mathbf{b}}$'s coordinates, with no
# angle computed: $R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}$ sends $\vec{\mathbf{e}}_1$
# to $\cos(-\theta) * \vec{\mathbf{e}}_1 + \sin(-\theta) * \vec{\mathbf{e}}_2$, with
# $\theta$ the angle of $\vec{\mathbf{b}}$:

# %%
R(1 * e_1).simplified()

# %% [markdown]
# $\vec{\mathbf{b}}$ lands on the x-axis at its length $|\vec{\mathbf{b}}|$:

# %%
b_aligned: Vector = R(b).simplified()
b_aligned

# %% [markdown]
# At the plot values:

# %%
at_values(b_aligned, values)

# %% [markdown]
# $\vec{\mathbf{a}}$ rides along. Its x-coordinate there is
# $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}} / |\vec{\mathbf{b}}|$, how far
# $\vec{\mathbf{a}}$ reaches along $\vec{\mathbf{b}}$, and its y-coordinate is
# $(a_2 * b_1 - a_1 * b_2) / |\vec{\mathbf{b}}|$, how far across:

# %%
a_aligned: Vector = R(a).simplified()
a_aligned

# %% [markdown]
# At the plot values:

# %%
at_values(a_aligned, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_ALIGNED: Point = point(coordinates=list(at_values(a_aligned, values)))
P_B_ALIGNED: Point = point(coordinates=list(at_values(b_aligned, values)))
fig_rotated: PendingFigure
with scene_around(points=[P_A, P_B, P_A_ALIGNED, P_B_ALIGNED]) as fig_rotated:
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$"
    )
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$"
    )
    arrow(head=P_A_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{a}}'$")
    arrow(head=P_B_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{b}}'$", align=LabelPos.b)
fig_rotated

# %% [markdown]
# ## Step 2: on the x-axis, keep each coordinate
#
# $\operatorname{proj}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{a}}') = x * \vec{\mathbf{e}}_1$
# keeps $\vec{\mathbf{a}}'$'s x-coordinate and
# $\operatorname{rej}_{\vec{\mathbf{e}}_1}(\vec{\mathbf{a}}') = y * \vec{\mathbf{e}}_2$
# keeps its y-coordinate:

# %%
x: Real = a_aligned.coefficient(e_1)
y: Real = a_aligned.coefficient(e_2)
x

# %% [markdown]
# and its $y$-coordinate:

# %%
y

# %% [markdown]
# At the plot values:

# %%
at_values(x, values)

# %% [markdown]
# and $y$ at the plot values:

# %%
at_values(y, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_X: Point = point(coordinates=list(at_values(Scalar(x) * e_1, values)))
fig_base: PendingFigure
with scene_around(points=[P_A_ALIGNED, P_B_ALIGNED]) as fig_base:
    arrow(head=P_A_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{a}}'$")
    arrow(head=P_X, color=GREEN, width=2.4)
    arrow(head=P_B_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{b}}'$", align=LabelPos.t)
    note(
        at=0.5 * P_X,
        text=r"$x * \vec{\mathbf{e}}_1$",
        color=GREEN,
        offset=Point(x=0, y=-10),
        align=LabelPos.b,
    )
    arrow(head=P_A_ALIGNED, tail=P_X, color=BLUE)
    note(
        at=0.5 * (P_X + P_A_ALIGNED),
        text=r"$y * \vec{\mathbf{e}}_2$",
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
# $(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1})^{-1} = R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}}$,
# from $\vec{\mathbf{e}}_1$'s direction to $\vec{\mathbf{b}}$'s:

# %%
inverse(R)

# %% [markdown]
# It carries $x * \vec{\mathbf{e}}_1$ to the projection of $\vec{\mathbf{a}}$ onto
# $\vec{\mathbf{b}}$:

# %%
projection: Vector = inverse(R)(Scalar(x) * e_1).simplified()
projection

# %% [markdown]
# At the plot values:

# %%
at_values(projection, values)

# %% [markdown]
# and $y * \vec{\mathbf{e}}_2$ to the rejection:

# %%
rejection: Vector = inverse(R)(Scalar(y) * e_2).simplified()
rejection

# %% [markdown]
# At the plot values:

# %%
at_values(rejection, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_back: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_back:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$", align=LabelPos.t)
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        color=GREEN,
        offset=Point(x=6, y=-6),
        align=LabelPos.br,
    )
    arrow(head=P_A, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_A),
        text=r"$\operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_B, toward_b=P_A - P_PROJECTION)
fig_back

# %% [markdown]
# ## Checks, for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$
#
# Each check shows both formulas, then their difference. The coordinates are symbols, so
# a difference of $0$ holds for every $\vec{\mathbf{a}}$ and every nonzero
# $\vec{\mathbf{b}}$.
#
# ### The construction is gacalc's projection
#
# The construction gave:

# %%
projection

# %% [markdown]
# gacalc's projection,
# $(\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}) * \vec{\mathbf{b}}^{-1}$, gives:

# %%
a.projected_onto(b).simplified()

# %% [markdown]
# Their difference:

# %%
(projection - a.projected_onto(b)).simplified()

# %% [markdown]
# ### The projection plus the rejection is $\vec{\mathbf{a}}$
#
# The sum of the two parts:

# %%
(projection + rejection).simplified()

# %% [markdown]
# and $\vec{\mathbf{a}}$:

# %%
a

# %% [markdown]
# Their difference:

# %%
(projection + rejection - a).simplified()
