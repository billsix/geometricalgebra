# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Vectors as relative number lines — calculations
#
# Companion to *Vectors as Relative Number Lines*. In *One Dimension* the input
# $x * \vec{\mathbf{e}}_1$ was a number on a number line: $\vec{\mathbf{e}}_1$ gave the
# direction and the size of one step, and $x$ counted steps. Any arrow in the plane can
# play the part of $\vec{\mathbf{e}}_1$. Each one lays down its own number line, and a
# point's number depends on which line you read it from: a vector is a **relative**
# number line.
#
# Every formula is computed with symbols; numbers appear only to draw the figures.

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
    PendingFigure,
    Point,
    arrow,
    point,
    scene_around,
)
from _line_scene import slanted_number_line

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.transforms import coordinate_along

# %% [markdown]
# ## An arrow makes a number line
#
# Take any arrow $\vec{\mathbf{v}}$ that is not zero, with symbolic coordinates:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# Its number line is every multiple $t * \vec{\mathbf{v}}$: the number $t$ counts steps
# of $\vec{\mathbf{v}}$ from the origin, forward for positive $t$ and backward for
# negative $t$.

# %%
t: sympy.Symbol = sympy.Symbol("t", real=True)
on_line: Vector = Scalar(t) * v
on_line

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(v_1, 2), (v_2, 1)]

# %% [markdown]
# Drawn at the plot values: $\vec{\mathbf{v}}$ in black, and its number line in green,
# with a tick at every whole step. Before running the cell, predict where the tick
# labelled $-1$ falls.

# %%
P_V: Point = point(coordinates=list(at_values(v, values)))
fig_line: PendingFigure
with scene_around(points=[-2 * P_V, 3 * P_V]) as fig_line:
    slanted_number_line(unit=P_V, low=-2, high=3, color=GREEN, labels=(-2, -1, 2, 3))
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
fig_line

# %% [markdown]
# ## Reading a point's number
#
# gacalc's `coordinate_along(p, along=v)` reads the number of a point $\vec{\mathbf{p}}$
# on $\vec{\mathbf{v}}$'s number line: the $t$ with $\vec{\mathbf{p}} =
# t * \vec{\mathbf{v}}$. For the point $t * \vec{\mathbf{v}}$ it gives back $t$:

# %%
sympy.simplify(sympy.sympify(coordinate_along(on_line, along=v)))

# %% [markdown]
# On $\vec{\mathbf{e}}_1$'s number line, the one from *One Dimension*, the point
# $x * \vec{\mathbf{e}}_1$ reads $x$, as it did there:

# %%
x: sympy.Symbol = sympy.Symbol("x", real=True)
coordinate_along(Scalar(x) * e_1, along=1 * e_1)

# %% [markdown]
# ## The same point, read from different lines
#
# Here is where "relative" comes in. Take the point $\vec{\mathbf{p}} = 3 *
# \vec{\mathbf{v}}$. On $\vec{\mathbf{v}}$'s line it reads $3$:

# %%
p: Vector = 3 * v
sympy.simplify(sympy.sympify(coordinate_along(p, along=v)))

# %% [markdown]
# Now read it from the number line of $2 * \vec{\mathbf{v}}$, whose steps are twice as
# long. Predict the number, then run:

# %%
sympy.simplify(sympy.sympify(coordinate_along(p, along=2 * v)))

# %% [markdown]
# Half as many steps. And from the line of $-\vec{\mathbf{v}}$, which counts the other
# way:

# %%
sympy.simplify(sympy.sympify(coordinate_along(p, along=-1 * v)))

# %% [markdown]
# In general, read from the line of $s * \vec{\mathbf{v}}$ (for $s \neq 0$), the point
# $t * \vec{\mathbf{v}}$ reads $t / s$:

# %%
s: sympy.Symbol = sympy.Symbol("s", real=True, nonzero=True)
sympy.simplify(sympy.sympify(coordinate_along(on_line, along=Scalar(s) * v)))

# %% [markdown]
# Drawn at the plot values: the point $3 * \vec{\mathbf{v}}$ in purple, with
# $\vec{\mathbf{v}}$'s number line (green, just above) and the number line of
# $2 * \vec{\mathbf{v}}$ (blue, just below), both along the same direction. The purple
# tip sits at $3$ on one and at $1.5$, halfway between $1$ and $2$, on the other.

# %%
P_P: Point = point(coordinates=list(at_values(p, values)))
# a unit step across the line, to set the two number lines either side of it
ACROSS: Point = (1 / P_V.norm()) * Point(x=-P_V.x2(), y=P_V.x1())
fig_two: PendingFigure
with scene_around(points=[-1 * P_V, 4 * P_V]) as fig_two:
    slanted_number_line(
        unit=P_V,
        low=-1,
        high=4,
        color=GREEN,
        labels=(1, 2, 3),
        side=1,
        offset=0.3 * ACROSS,
    )
    slanted_number_line(
        unit=2 * P_V,
        low=0,
        high=2,
        color=BLUE,
        labels=(1, 2),
        side=-1,
        offset=-0.3 * ACROSS,
    )
    arrow(head=P_P, color=PURPLE, text=r"$3 * \vec{\mathbf{v}}$")
fig_two

# %% [markdown]
# A point has no number of its own. It has a number *relative to a vector*: which
# direction is forward, and how long one step is. A ruler is the same: a length of "3"
# means nothing until you say what the ruler is laid against.
#
# ## Two arrows, two number lines
#
# $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$ each make a number line, one across and
# one up:

# %%
P_E1: Point = point(coordinates=list(e_1))
P_E2: Point = point(coordinates=list(e_2))
fig_axes: PendingFigure
with scene_around(points=[-3 * P_E1, 3 * P_E1, -3 * P_E2, 3 * P_E2]) as fig_axes:
    slanted_number_line(unit=P_E1, low=-3, high=3, color=GREEN, labels=(-2, 2), side=-1)
    slanted_number_line(unit=P_E2, low=-3, high=3, color=BLUE, labels=(-2, 2), side=1)
    arrow(head=P_E1, color=GREEN, text=r"$\vec{\mathbf{e}}_1$")
    arrow(head=P_E2, color=BLUE, text=r"$\vec{\mathbf{e}}_2$")
fig_axes

# %% [markdown]
# Two number lines together make graph paper: a point is so many steps along the first
# and so many along the second. That is the next chapter, *Relative Graph Paper*.
