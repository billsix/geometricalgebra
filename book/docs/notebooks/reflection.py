# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Reflection across a vector — calculations
#
# Companion to *Reflection*. Reflecting across the x-axis is easy: keep the
# x-coordinate and flip the sign of the y-coordinate. To reflect across the line
# through any nonzero $\vec{\mathbf{b}}$, do what *Proof: Projection by Rotating to
# Standard Position* did: rotate so that $\vec{\mathbf{b}}$ lies on the x-axis, do the
# easy reflection there, and rotate back.
#
# Then the same reflection two more ways: as the projection minus the rejection, and
# as one product, $\vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1}$. All
# three agree for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$.
#
# Every step is computed with symbolic coordinates; numbers appear only to draw the
# figures.

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
    dashed_arrow,
    note,
    point,
    scene_around,
)

from gacalc.base import Real
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values, show_mult
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ is the vector to reflect, and the mirror is the line through
# $\vec{\mathbf{b}}$. Both have symbolic coordinates:

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
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 1), (a_2, 3), (b_1, 3), (b_2, 1)]

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_around(points=[P_A, P_B, -1 * P_B]) as fig_given:
    dashed_arrow(tail=-1 * P_B, head=P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$", align=LabelPos.b)
fig_given

# %% [markdown]
# ## The easy case: reflecting across the x-axis
#
# Across the x-axis, a vector keeps its x-coordinate and its y-coordinate changes
# sign. For a vector $x * \vec{\mathbf{e}}_1 + y * \vec{\mathbf{e}}_2$ the reflection is
# $x * \vec{\mathbf{e}}_1 - y * \vec{\mathbf{e}}_2$. Before reading on, predict: what is
# the reflection of $\vec{\mathbf{e}}_2$? Of $\vec{\mathbf{e}}_1$?

# %% [markdown]
# ## Step 1: rotate $\vec{\mathbf{b}}$ onto the x-axis, carrying $\vec{\mathbf{a}}$ along
#
# The rotation from $\vec{\mathbf{b}}$'s direction to $\vec{\mathbf{e}}_1$'s,
# $R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}$, from *Proof: Rotate from the Direction of
# a to the Direction of b*:

# %%
R: InvertibleFunction[Vector] = rotation_from_to(b, e_1)
a_aligned: Vector = R(a).simplified()
a_aligned

# %% [markdown]
# $\vec{\mathbf{b}}$ itself lands on the x-axis:

# %%
R(b).simplified()

# %% [markdown]
# ## Step 2: on the x-axis, keep $x$ and flip $y$
#
# $\vec{\mathbf{a}}'$'s coordinates there:

# %%
x: Real = a_aligned.coefficient(e_1)
y: Real = a_aligned.coefficient(e_2)
x

# %% [markdown]
# and

# %%
y

# %% [markdown]
# The reflection across the x-axis, $x * \vec{\mathbf{e}}_1 - y * \vec{\mathbf{e}}_2$:

# %%
flipped: Vector = Scalar(x) * e_1 - Scalar(y) * e_2
flipped

# %% [markdown]
# Drawn at the plot values, with the reflected vector in purple:

# %%
P_A_ALIGNED: Point = point(coordinates=list(at_values(a_aligned, values)))
P_B_ALIGNED: Point = point(coordinates=list(at_values(R(b), values)))
P_FLIPPED: Point = point(coordinates=list(at_values(flipped, values)))
fig_flip: PendingFigure
with scene_around(points=[P_A_ALIGNED, P_B_ALIGNED, P_FLIPPED]) as fig_flip:
    arrow(head=P_A_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{a}}'$")
    arrow(head=P_B_ALIGNED, color=BLACK, text=r"$\vec{\mathbf{b}}'$", align=LabelPos.b)
    arrow(
        head=P_FLIPPED,
        color=PURPLE,
        text=r"$x * \vec{\mathbf{e}}_1 - y * \vec{\mathbf{e}}_2$",
    )
fig_flip

# %% [markdown]
# ## Step 3: rotate back
#
# The inverse rotation carries the flipped vector back, giving the reflection of
# $\vec{\mathbf{a}}$ across the line through $\vec{\mathbf{b}}$:

# %%
reflection: Vector = inverse(R)(flipped).simplified()
reflection

# %% [markdown]
# At the plot values:

# %%
at_values(reflection, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_REFLECTION: Point = point(coordinates=list(at_values(reflection, values)))
fig_back: PendingFigure
with scene_around(points=[P_A, P_B, -1 * P_B, P_REFLECTION]) as fig_back:
    dashed_arrow(tail=-1 * P_B, head=P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$", align=LabelPos.b)
    arrow(head=P_REFLECTION, color=PURPLE, text=r"reflection")
fig_back

# %% [markdown]
# ## The same reflection: projection minus rejection
#
# On the x-axis, $x * \vec{\mathbf{e}}_1$ was the projection and
# $y * \vec{\mathbf{e}}_2$ the rejection, so "keep $x$, flip $y$" is the projection
# minus the rejection. Rotating back keeps that true, so the reflection across
# $\vec{\mathbf{b}}$ should be
#
# $$
# \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
#   - \operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}).
# $$
#
# The projection:

# %%
projection: Vector = a.projected_onto(b).simplified()
projection

# %% [markdown]
# the rejection:

# %%
rejection: Vector = a.rejected_away_from(b).simplified()
rejection

# %% [markdown]
# Drawn at the plot values: the projection in green, the rejection in blue, and the
# reflection is the projection plus the rejection turned around.

# %%
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_parts: PendingFigure
with scene_around(points=[P_A, P_B, -1 * P_B, P_REFLECTION]) as fig_parts:
    dashed_arrow(tail=-1 * P_B, head=P_B, color=BLACK)
    arrow(head=P_PROJECTION, color=GREEN, width=2.4)
    note(
        at=0.5 * P_PROJECTION,
        text=r"$\operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        color=GREEN,
        offset=Point(x=-2, y=8),
        align=LabelPos.tl,
    )
    arrow(head=P_A, tail=P_PROJECTION, color=BLUE)
    arrow(head=P_REFLECTION, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_A),
        text=r"$\operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_REFLECTION, color=PURPLE, text=r"reflection")
fig_parts

# %% [markdown]
# The projection minus the rejection:

# %%
(projection - rejection).simplified()

# %% [markdown]
# Its difference from the reflection built by rotating:

# %%
(projection - rejection - reflection).simplified()

# %% [markdown]
# gacalc's `reflected_across` is defined as the projection minus the rejection. Its
# difference from the reflection built by rotating:

# %%
(a.reflected_across(b) - reflection).simplified()

# %% [markdown]
# ## The same reflection: one product
#
# The geometric product gives a third way, with no rotation and no projection:
#
# $$
# \vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1}.
# $$
#
# Why it works: write $\vec{\mathbf{a}}$ as its part along $\vec{\mathbf{b}}$ plus its
# part across. The part along commutes with $\vec{\mathbf{b}}$, so the outer factors
# cancel and it stays. The part across anticommutes with $\vec{\mathbf{b}}$ (swapping
# perpendicular vectors flips the sign), so it comes out negated. Along kept, across
# flipped: a reflection.
#
# The base case first: across $\vec{\mathbf{e}}_1$, whose inverse is itself, the
# product is $\vec{\mathbf{e}}_1 * \vec{\mathbf{a}} * \vec{\mathbf{e}}_1$. First
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{a}}$, term by term, at the plot values:

# %%
show_mult(1 * e_1, at_values(a, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(1 * e_1, a)

# %% [markdown]
# and that times $\vec{\mathbf{e}}_1$: keep $x$, flip $y$.

# %%
show_mult(e_1 * a, 1 * e_1)

# %% [markdown]
# For the general $\vec{\mathbf{b}}$:

# %%
sandwich: Vector = (b * a * b.inverse()).simplified()
sandwich

# %% [markdown]
# Its difference from the reflection built by rotating:

# %%
(sandwich - reflection).simplified()

# %% [markdown]
# ## Checks, for every $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$
#
# ### A reflection keeps the length
#
# The squared length of the reflection:

# %%
sympy.simplify(sympy.sympify(reflection.magnitude_squared()))

# %% [markdown]
# and of $\vec{\mathbf{a}}$:

# %%
a.magnitude_squared()

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(reflection.magnitude_squared() - a.magnitude_squared()))

# %% [markdown]
# ### Reflecting twice gives back $\vec{\mathbf{a}}$
#
# Reflect the reflection across the same line:

# %%
twice: Vector = reflection.reflected_across(b).simplified()
twice

# %% [markdown]
# Its difference from $\vec{\mathbf{a}}$:

# %%
(twice - a).simplified()

# %% [markdown]
# Reflection in space, across a vector and across a plane, is *Reflection in Space*.
