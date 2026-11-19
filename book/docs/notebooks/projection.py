# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection and rejection, and what they do to the product — calculations
#
# Companion to *Projection*. The projection of $\vec{\mathbf{b}}$ onto
# $\vec{\mathbf{a}}$ is the part of $\vec{\mathbf{b}}$ along $\vec{\mathbf{a}}$; the
# rejection is the part across. (*Proof: Projection by Rotating to Standard Position*
# derives how to compute them.) This notebook draws the two parts, checks that they add
# back to $\vec{\mathbf{b}}$, and then multiplies each part by $\vec{\mathbf{a}}$: the
# part along gives a plain number and the part across gives a piece of plane. Those two
# products split $\vec{\mathbf{a}} * \vec{\mathbf{b}}$ in two, and the next chapter,
# *The Product from Projection*, gives the two halves their names.
#
# Every step is computed with symbolic coordinates; numbers appear only to draw the
# figures and in the first product tables. The Lean theorems are `mul_proj_eq_dot` and
# `mul_reject_eq_wedge` (`proofs/GacalcProofs/Bootstrap2D.lean`).

# %%
# twin: GacalcProofs.G2.mul_proj_eq_dot
# twin: GacalcProofs.G2.mul_reject_eq_wedge
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
    note,
    point,
    right_angle,
    scene_around,
)

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# ## The two parts
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
# and

# %%
b

# %% [markdown]
# The projection of $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$,
# $\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$, is a multiple of
# $\vec{\mathbf{a}}$:

# %%
projection: Vector = b.projected_onto(a).simplified()
projection

# %% [markdown]
# and the rejection, $\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$, is what
# is left:

# %%
rejection: Vector = b.rejected_away_from(a).simplified()
rejection

# %% [markdown]
# They add back to $\vec{\mathbf{b}}$; the difference:

# %%
(projection + rejection - b).simplified()

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 1), (b_1, 1), (b_2, 3)]

# %% [markdown]
# Drawn at the plot values: the projection in green along $\vec{\mathbf{a}}$, the
# rejection in blue across it.

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_parts: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_parts:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$", align=LabelPos.b)
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$",
        color=GREEN,
        offset=Point(x=12, y=-12),
        align=LabelPos.br,
    )
    arrow(head=P_B, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_B),
        text=r"$\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_PROJECTION, toward_a=P_A, toward_b=P_B - P_PROJECTION)
fig_parts

# %% [markdown]
# ## Multiply each part by $\vec{\mathbf{a}}$
#
# $\vec{\mathbf{b}}$ is the sum of its two parts, and the product distributes, so
#
# $$
# \vec{\mathbf{a}} * \vec{\mathbf{b}}
#   = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
#   + \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}).
# $$
#
# What does each piece look like? Predict before running: the projection points the same
# way as $\vec{\mathbf{a}}$, and the rejection is perpendicular to it.
#
# ### The part along: a plain number
#
# The projection is a number $\lambda$ times $\vec{\mathbf{a}}$, so its product with
# $\vec{\mathbf{a}}$ is $\lambda * \vec{\mathbf{a}} * \vec{\mathbf{a}} = \lambda *
# |\vec{\mathbf{a}}|^2$: a vector times itself is its squared length. Term by term, first
# at the plot values:

# %%
show_mult(at_values(a, values), at_values(projection, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, projection)

# %% [markdown]
# Simplified, it is a plain number with no $\mathbf{e}_{12}$ part:

# %%
along: Versor = (a * projection).simplified()
along

# %% [markdown]
# ### The part across: a piece of plane
#
# The rejection is perpendicular to $\vec{\mathbf{a}}$. The product of two perpendicular
# vectors has no plain-number part: the cross terms are all that is left, and they make
# a multiple of $\mathbf{e}_{12}$. First at the plot values:

# %%
show_mult(at_values(a, values), at_values(rejection, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, rejection)

# %% [markdown]
# Simplified, it is a multiple of $\mathbf{e}_{12}$ and nothing else:

# %%
across: Versor = (a * rejection).simplified()
across

# %% [markdown]
# Its size is the area of the parallelogram that $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$ span: $|\vec{\mathbf{a}}|$ times the height of $\vec{\mathbf{b}}$
# above $\vec{\mathbf{a}}$, which is the length of the rejection.

# %% [markdown]
# ### Together they are the whole product
#
# The product $\vec{\mathbf{a}} * \vec{\mathbf{b}}$:

# %%
(a * b).simplified()

# %% [markdown]
# minus the two pieces:

# %%
(a * b - along - across).simplified()

# %% [markdown]
# So the product of two vectors carries two facts at once: a plain number from the part
# of $\vec{\mathbf{b}}$ along $\vec{\mathbf{a}}$, and a piece of plane from the part
# across. *The Product from Projection* names them the **dot product**
# $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}$ and the **wedge**
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$.

# %% [markdown]
# ## Swapping the roles
#
# Project $\vec{\mathbf{a}}$ onto $\vec{\mathbf{b}}$ instead, and multiply by
# $\vec{\mathbf{b}}$. The plain number is the same:

# %%
(b * a.projected_onto(b) - along).simplified()

# %% [markdown]
# but the piece of plane changes sign, because the turn from $\vec{\mathbf{b}}$ to
# $\vec{\mathbf{a}}$ goes the other way. The sum of the two:

# %%
(b * a.rejected_away_from(b) + across).simplified()
