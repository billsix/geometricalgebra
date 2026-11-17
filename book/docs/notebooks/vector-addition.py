# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Vector Addition — calculations
#
# You already know that $3 + 5 = 5 + 3$. The chapter's pictures say that $a + b$ and
# $b + a$ land on the same corner of the parallelogram. Here is the same fact in
# coordinates: adding two vectors adds their coordinates, and each coordinate is a sum
# of two ordinary numbers, which gives the same answer in either order. The coordinates
# are left as symbols, so every result holds for every $a$ and $b$. Numbers appear only
# to draw the figures. Each check shows both sides, then their difference.

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
    point,
    scene_around,
)
from _frame_scene import GRAY_EDGE, line

from gacalc.base import Real
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.transforms import translate

# %% [markdown]
# ## The vectors
#
# $a$ and $b$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 2), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# ## $a + b = b + a$
#
# Before running the next two cells, predict each coordinate of $a + b$ and of
# $b + a$. $a + b$:

# %%
a + b

# %% [markdown]
# $b + a$:

# %%
b + a

# %% [markdown]
# Each coordinate is the same two numbers added in the other order. Their difference:

# %%
(a + b) - (b + a)

# %% [markdown]
# At the plot values, $a + b$:

# %%
at_values(a + b, values)

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_SUM: Point = point(coordinates=list(at_values(a + b, values)))
fig_sum: PendingFigure
with scene_around(points=[P_A, P_B, P_SUM]) as fig_sum:
    arrow(head=P_SUM, color=PURPLE, text=r"$\vec{a} + \vec{b}$")
    arrow(head=P_A, color=GREEN, text=r"$\vec{a}$")
    arrow(head=P_SUM, tail=P_A, color=BLUE)
    arrow(head=P_B, color=BLUE, text=r"$\vec{b}$", align=LabelPos.l)
    arrow(head=P_SUM, tail=P_B, color=GREEN)
fig_sum

# %% [markdown]
# ## Subtraction
#
# The chapter's second pair of pictures: $a - b$ is what you add to $b$ to get back
# $a$. $a - b$:

# %%
a - b

# %% [markdown]
# $(a - b) + b$:

# %%
(a - b) + b

# %% [markdown]
# Its difference from $a$:

# %%
((a - b) + b) - a

# %% [markdown]
# It is the same as adding the opposite. $a + (-b)$:

# %%
a + (-b)

# %% [markdown]
# Its difference from $a - b$:

# %%
(a - b) - (a + (-b))

# %% [markdown]
# At the plot values, $a - b$:

# %%
at_values(a - b, values)

# %%
P_DIFFERENCE: Point = point(coordinates=list(at_values(a - b, values)))
fig_difference: PendingFigure
with scene_around(points=[P_A, P_B, P_DIFFERENCE]) as fig_difference:
    arrow(head=P_A, color=BLACK, text=r"$\vec{a}$")
    arrow(head=P_B, color=BLUE, text=r"$\vec{b}$", align=LabelPos.l)
    arrow(head=P_DIFFERENCE, color=PURPLE, text=r"$\vec{a} - \vec{b}$")
    dashed_arrow(tail=P_B, head=P_A, color=PURPLE)
fig_difference

# %% [markdown]
# ## Translate: adding the same vector to everything
#
# Fix $b$ and let the other input vary, and $+$ becomes a one-input machine,
# `translate(b=b)`: feed it any point $v$, get $v + b$. This is **partial binding**:
# one of the two blanks of $+$ filled in. It moves every point the same way, so
# applying it to the whole plane slides the graph paper by $b$.

# %%
t: InvertibleFunction[Vector] = translate(b=b)
t

# %% [markdown]
# Applied to $a$, it gives the one-off sum:

# %%
t(a)

# %% [markdown]
# Its difference from $a + b$:

# %%
t(a) - (a + b)

# %% [markdown]
# It moves every point by the same $b$. $e_1$ goes to:

# %%
t(1 * e_1)

# %% [markdown]
# and $e_2$ to:

# %%
t(1 * e_2)

# %% [markdown]
# A whole sheet of graph paper, a 3 by 3 lattice of points, each slid by $b$ at the
# plot values. (No separate check is needed: $a$ above is symbolic, so $t(a) = a + b$
# already covers every point.)

# %%
P_SHIFT: Point = point(coordinates=list(at_values(b, values)))

fig_lattice: PendingFigure
with scene_around(
    points=[Point(x=2, y=2), Point(x=2, y=2) + P_SHIFT, P_SHIFT]
) as fig_lattice:
    k: int
    for k in range(3):
        line(tail=Point(x=k, y=0), head=Point(x=k, y=2), color=GRAY_EDGE)
        line(tail=Point(x=0, y=k), head=Point(x=2, y=k), color=GRAY_EDGE)
        line(tail=Point(x=k, y=0) + P_SHIFT, head=Point(x=k, y=2) + P_SHIFT, color=BLUE)
        line(tail=Point(x=0, y=k) + P_SHIFT, head=Point(x=2, y=k) + P_SHIFT, color=BLUE)
    arrow(head=P_SHIFT, color=PURPLE, text=r"$\vec{b}$", align=LabelPos.l)
fig_lattice

# %% [markdown]
# Its **inverse** is `translate(b=-b)`: sliding the paper back undoes the slide.
# $t^{-1}(t(a))$:

# %%
t.inverse(t(a))

# %% [markdown]
# Its difference from $a$:

# %%
t.inverse(t(a)) - a

# %% [markdown]
# `t.at(0.5)` is the paper slid half way. $t_{0.5}(a)$:

# %%
t.at(0.5)(a)

# %% [markdown]
# $a + 0.5 * b$:

# %%
a + b * 0.5

# %% [markdown]
# Their difference:

# %%
t.at(0.5)(a) - (a + b * 0.5)
