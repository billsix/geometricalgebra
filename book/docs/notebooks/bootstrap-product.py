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
# # Step 4, the geometric product — worked example
#
# Companion to *Step 4: The Geometric Product, from Projection*. Every step is computed
# with symbolic coordinates, so each result is a formula for every $\vec{\mathbf{a}}$
# and $\vec{\mathbf{b}}$: $\vec{\mathbf{b}}$ measured against $\vec{\mathbf{a}}$ (Step
# 2) gives $x$ and $y$, and the product is
# $|\vec{\mathbf{a}}| * (x + y * \mathbf{e}_{12})$. Then the quarter turn as a product,
# and the dot and wedge as $\vec{\mathbf{a}}$ times the projection and the rejection.
# Numbers appear only to draw the figures; change them and rerun. Each check shows both
# sides, then their difference.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.epixscene.bootstrap_live import (
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
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2, e_12
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# ## The product from projection
#
# Step 2 puts $\vec{\mathbf{b}}$ in $\vec{\mathbf{a}}$'s standard position: Step 1's
# rotation by minus the angle of $\vec{\mathbf{a}}$ carries $\vec{\mathbf{b}}$ to
# $(x, y)$. $x$ is the signed length of $\vec{\mathbf{b}}$'s shadow on
# $\vec{\mathbf{a}}$ and $y$ its height above $\vec{\mathbf{a}}$.

# %%
measured: Vector = b.rotate(-sympy.atan2(a_2, a_1)).simplified()
measured

# %% [markdown]
# The product keeps both, times $|\vec{\mathbf{a}}|$:
# $|\vec{\mathbf{a}}| * (x + y * \mathbf{e}_{12})$. The plain-number part is the dot
# product and the $\mathbf{e}_{12}$ part, the signed area of the parallelogram, is the
# wedge.

# %%
product: Versor = (
    Scalar(a.magnitude())
    * (Scalar(measured.coefficient(e_1)) + Scalar(measured.coefficient(e_2)) * e_12)
).simplified()
product

# %% [markdown]
# At the plot values:

# %%
at_values(product, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_FOOT: Point = point(coordinates=list(at_values(b.projected_onto(a), values)))
fig_product: PendingFigure
with scene_around(points=[P_A, P_B, P_A + P_B]) as fig_product:
    dashed_arrow(tail=P_A, head=P_A + P_B, color=BLACK)
    dashed_arrow(tail=P_B, head=P_A + P_B, color=BLACK)
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
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
fig_product

# %% [markdown]
# ## The same product, term by term
#
# The multiplication rules give $\vec{\mathbf{a}} * \vec{\mathbf{b}}$ the way you
# multiply $(x + 2) * (x + 3)$: every term of $\vec{\mathbf{a}}$ times every term of
# $\vec{\mathbf{b}}$, then add. Each row of the table is one pair of terms.
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2$ are $1$, and
# $\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 = -\mathbf{e}_{12}$. First at the plot
# values:

# %%
show_mult(at_values(a, values), at_values(b, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(a, b)

# %% [markdown]
# ## The quarter turn is a product
#
# Multiplying by $\mathbf{e}_{12}$ on the right turns a vector a quarter turn:
# $\vec{\mathbf{b}} * \mathbf{e}_{12}$ is Step 1's $r(\vec{\mathbf{b}}; \pi/2)$.

# %%
quarter_turn: MultiVectorBase = b * e_12
quarter_turn

# %% [markdown]
# At the plot values:

# %%
at_values(quarter_turn, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_QUARTER: Point = point(coordinates=list(at_values(b.rotate_90_degrees(), values)))
fig_quarter: PendingFigure
with scene_around(points=[P_B, P_QUARTER]) as fig_quarter:
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
    arrow(
        head=P_QUARTER,
        color=BLACK,
        text=r"$\vec{\mathbf{b}} * \mathbf{e}_{12}$",
        align=LabelPos.l,
        offset=Point(x=-6, y=0),
    )
    right_angle(corner=Point(x=0, y=0), toward_a=P_B, toward_b=P_QUARTER)
fig_quarter

# %% [markdown]
# ## Dot and wedge through projection and rejection
#
# $\vec{\mathbf{a}}$ times the projection of $\vec{\mathbf{b}}$ onto $\vec{\mathbf{a}}$
# is a plain number, the dot product:

# %%
along: MultiVectorBase = (a * b.projected_onto(a)).simplified()
along

# %% [markdown]
# $\vec{\mathbf{a}}$ times the rejection is pure area, the wedge:

# %%
across: MultiVectorBase = (a * b.rejected_away_from(a)).simplified()
across

# %% [markdown]
# ## Checks, for all vectors
#
# ### The product from projection is the product of the multiplication rules
#
# The product from projection was:

# %%
product

# %% [markdown]
# The rules give:

# %%
(a * b).simplified()

# %% [markdown]
# Their difference:

# %%
(product - a * b).simplified()

# %% [markdown]
# ### Its parts are the dot product and the wedge
#
# $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$:

# %%
(a.dot(b) + a.wedge(b)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} * \vec{\mathbf{b}}$:

# %%
(a * b - (a.dot(b) + a.wedge(b))).simplified()

# %% [markdown]
# ### A vector times itself is its length squared
#
# $\vec{\mathbf{b}} * \vec{\mathbf{b}}$:

# %%
(b * b).simplified()

# %% [markdown]
# $|\vec{\mathbf{b}}|^2$:

# %%
b.magnitude_squared()

# %% [markdown]
# Their difference:

# %%
(b * b - Scalar(b.magnitude_squared())).simplified()

# %% [markdown]
# ### The quarter turn as a product matches Step 1's
#
# $\vec{\mathbf{b}} * \mathbf{e}_{12}$ was:

# %%
quarter_turn

# %% [markdown]
# Step 1's $r(\vec{\mathbf{b}}; \pi/2)$:

# %%
b.rotate_90_degrees()

# %% [markdown]
# Their difference:

# %%
(quarter_turn - b.rotate_90_degrees()).simplified()

# %% [markdown]
# ### $\vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$ is the dot product
#
# $\vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$ was:

# %%
along

# %% [markdown]
# $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}$:

# %%
a.dot(b).simplified()

# %% [markdown]
# Their difference:

# %%
(along - a.dot(b)).simplified()

# %% [markdown]
# ### $\vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$ is the wedge
#
# $\vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})$ was:

# %%
across

# %% [markdown]
# $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$:

# %%
a.wedge(b).simplified()

# %% [markdown]
# Their difference:

# %%
(across - a.wedge(b)).simplified()

# %% [markdown]
# ### Measured the other way, the dot keeps its value and the wedge changes sign
#
# $\vec{\mathbf{b}} * \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$:

# %%
(b * a.projected_onto(b)).simplified()

# %% [markdown]
# Its difference from $\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}$:

# %%
(b * a.projected_onto(b) - a.dot(b)).simplified()

# %% [markdown]
# $\vec{\mathbf{b}} * \operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$:

# %%
(b * a.rejected_away_from(b)).simplified()

# %% [markdown]
# Its sum with $\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}$:

# %%
(b * a.rejected_away_from(b) + a.wedge(b)).simplified()

# %% [markdown]
# ### Two unit vectors multiply to the cosine and sine of the angle between them
#
# Two unit vectors at angles $\alpha$ and $\beta$:

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
(a_hat * b_hat).simplified()

# %% [markdown]
# The cosine and sine of the angle $\theta = \beta - \alpha$ from the first to the
# second, $\cos(\theta) + \sin(\theta) * \mathbf{e}_{12}$:

# %%
angle_form: Versor = (
    Scalar(sympy.cos(beta - alpha)) + Scalar(sympy.sin(beta - alpha)) * e_12
)
angle_form

# %% [markdown]
# Their difference:

# %%
(a_hat * b_hat - angle_form).simplified()
