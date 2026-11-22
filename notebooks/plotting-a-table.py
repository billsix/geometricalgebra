# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% tags=["remove-cell"]
# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

# %% [markdown]
# # Plotting a table — calculations
#
# Companion to *Plotting a Table*. As a child you plotted a function by filling in a
# table of inputs and outputs and marking the points. *One Dimension* drew each row of
# that table on one line: the input $x * \vec{\mathbf{e}}_1$ and the output
# $f(x) * \vec{\mathbf{e}}_1$. This notebook takes the next step. Multiplying the output
# by $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ turns it a quarter turn, so it points
# along $\vec{\mathbf{e}}_2$, and the input plus the turned output is the point
# $(x, f(x))$ you used to mark on graph paper. The notebook computes the table, the
# turn and the plot with symbols, then checks why the product turns a vector.
#
# Every formula is computed with symbols; numbers appear only to draw the figures.

# %%
# twin: GacalcProofs.G2.plotted_point_eq
import sympy

from gacalc.base import Real
from gacalc.epixscene.line_scene import (
    BLACK,
    OUTPUT_OFFSET,
    PURPLE,
    PendingFigure,
    Point,
    line_through,
    number_line,
    number_lines_scene,
    plot_row,
    plotted_table_scene,
    step,
    tip,
    turn_picture,
)
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2
from gacalc.nbdisplay import at_values, show_difference
from gacalc.transforms import translate, uniform_scale

# %% [markdown]
# ## The function and its table
#
# The function of *One Dimension*, $f = T_b \circ S_m$: scale by $m$, then translate by
# $b$. This time the vectors live in the plane, because the output is about to be
# turned. The input is $x * \vec{\mathbf{e}}_1$:

# %%
m: sympy.Symbol
b: sympy.Symbol
x: sympy.Symbol
m, b, x = sympy.symbols("m b x", real=True)
x_input: Vector = Scalar(x) * e_1
x_input

# %% [markdown]
# The function:

# %%
f: InvertibleFunction[Vector] = translate(b=Scalar(b) * e_1) @ uniform_scale(m=m)
f

# %% [markdown]
# and the output for the input $x * \vec{\mathbf{e}}_1$:

# %%
f(x_input)

# %% [markdown]
# The values used to fill in the table and draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(m, 1), (b, 2)]
at_values(f(x_input), values)


# %% [markdown]
# The table a child makes, read from $f$ itself: the inputs $x$ on the top row and the
# outputs $f(x)$ below them.


# %%
def output_number(input_number: int) -> sympy.Expr:
    """The number ``f(input_number * e_1)`` along ``e_1``, at the table's values."""
    output: Vector = at_values(f(x_input), [*values, (x, input_number)])
    return sympy.sympify(output.coefficient(e_1))


inputs: list[int] = list(range(-5, 6))
outputs: list[sympy.Expr] = [output_number(k) for k in inputs]
table: sympy.Matrix = sympy.Matrix([inputs, outputs])
table

# %% [markdown]
# ## The same table as vectors, along one direction
#
# *One Dimension* drew each row on one line. Here is the row $x = 2$: the input
# $2 * \vec{\mathbf{e}}_1$ in black on the left, and the output on a number line
# on the right, in purple. Both point the same way.

# %%
low: float = min(0.0, *[float(o) for o in outputs]) - 1
high: float = max(0.0, *[float(o) for o in outputs]) + 1


def draw_row(row: int, k: int, labelled: bool) -> None:
    """Row ``row``: the input ``k * e_1`` on the left, the output on the right."""
    result: float = float(output_number(k))
    number_line(row=row, low=-6, high=6)
    step(row=row, tail=0, head=k, color=BLACK)
    tip(row=row, value=k, color=BLACK, text=f"${k}$" if labelled else "")
    number_line(row=row, low=low, high=high, origin=OUTPUT_OFFSET)
    step(row=row, tail=0, head=result, color=PURPLE, origin=OUTPUT_OFFSET)
    tip(
        row=row,
        value=result,
        color=PURPLE,
        text=f"${sympy.latex(sympy.nsimplify(result))}$" if labelled else "",
        origin=OUTPUT_OFFSET,
    )


fig_row: PendingFigure
with number_lines_scene(rows=1, low=low, high=high) as fig_row:
    draw_row(row=0, k=2, labelled=True)
fig_row

# %% [markdown]
# ## Turn the output
#
# The output is an arrow along $\vec{\mathbf{e}}_1$. Multiply it on the right by
# $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$, the product that turns a vector a
# quarter turn (*The Geometric Product*). The unit plane:

# %%
i: Versor = e_1 * e_2
i

# %% [markdown]
# The output, multiplied by it:

# %%
turned: Vector = f(x_input) * i
turned

# %% [markdown]
# The same number, $m * x + b$, now sits on $\vec{\mathbf{e}}_2$. Why: the output
# is $(m * x + b) * \vec{\mathbf{e}}_1$, and
# $\vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)$ has two equal unit
# vectors side by side, which multiply to $1$, leaving $\vec{\mathbf{e}}_2$. The product
# of the two factors, computed:

# %%
e_1 * i

# %% [markdown]
# The length did not change. The square of the output's length:

# %%
f(x_input).magnitude_squared()

# %% [markdown]
# and of the turned output:

# %%
turned.magnitude_squared()

# %% [markdown]
# They are equal. At the row $x = 2$, drawn: the output, dashed green along
# $\vec{\mathbf{e}}_1$, and the output after the product, purple along
# $\vec{\mathbf{e}}_2$, a quarter turn counterclockwise.

# %%
length: float = float(output_number(2))
fig_turn: PendingFigure
with plotted_table_scene(
    points=[Point(x=length, y=0), Point(x=0, y=length)]
) as fig_turn:
    turn_picture(
        length=length,
        before=rf"${sympy.latex(output_number(2))} * \vec{{\mathbf{{e}}}}_1$",
        after=rf"${sympy.latex(output_number(2))} * \vec{{\mathbf{{e}}}}_2$",
    )
fig_turn

# %% [markdown]
# ## Plot the table
#
# Put the turned output at the tip of its input, with vector addition. The point for
# the input $x$:

# %%
plotted: Vector = x_input + f(x_input) * i
plotted

# %% [markdown]
# It is the pair $(x, m * x + b)$ on graph paper: $x$ steps along
# $\vec{\mathbf{e}}_1$, $m * x + b$ steps along $\vec{\mathbf{e}}_2$. The check, against
# the point written out directly:

# %%
graph_paper_point: Vector = x_input + Scalar(m * x + b) * e_2
graph_paper_point

# %% [markdown]
# Their difference:

# %%
show_difference(plotted, graph_paper_point)

# %% [markdown]
# At the row $x = 2$:

# %%
at_values(plotted, [*values, (x, 2)])

# %% [markdown]
# Drawn for that one row: the input in black along $\vec{\mathbf{e}}_1$, the turned
# output in purple from its tip, and the purple dot at the point.

# %%
fig_point: PendingFigure
with plotted_table_scene(
    points=[Point(x=2, y=0), Point(x=2, y=float(output_number(2)))]
) as fig_point:
    plot_row(
        input_value=2,
        output_value=float(output_number(2)),
        turn=1.0,
        text=f"$({2}, {sympy.latex(output_number(2))})$",
    )
fig_point

# %% [markdown]
# Now every row of the table, $x = -5$ to $x = 5$. The purple dots are the graph of
# $y = m * x + b$ that you plotted by hand, drawn here as inputs plus turned outputs.
# No head-tilting is needed: the product did the turn.

# %%
dots: list[Point] = [
    Point(x=k, y=float(o)) for k, o in zip(inputs, outputs, strict=True)
]
fig_graph: PendingFigure
with plotted_table_scene(points=dots) as fig_graph:
    line_through(start=dots[0], end=dots[-1])
    k: int
    o: sympy.Expr
    for k, o in zip(inputs, outputs, strict=True):
        plot_row(input_value=k, output_value=float(o), turn=1.0, text="")
fig_graph

# %% [markdown]
# ## Why the product turns a vector 90°
#
# Three facts, each computed.
#
# **First,** $\vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) =
# \vec{\mathbf{e}}_2$: the first two factors are the same unit vector and cancel.

# %%
e_1 * (e_1 * e_2)

# %% [markdown]
# **Second,** the same product sends $\vec{\mathbf{e}}_2$ to $-\vec{\mathbf{e}}_1$.
# Swapping $\vec{\mathbf{e}}_2$ past $\vec{\mathbf{e}}_1$ costs one sign, and then the
# two $\vec{\mathbf{e}}_2$ cancel.

# %%
e_2 * (e_1 * e_2)

# %% [markdown]
# So an arrow $\vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2$
# goes to $-v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2$. With symbols for
# $v_1$ and $v_2$:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# and the arrow after the product:

# %%
turned_v: Vector = v * i
turned_v

# %% [markdown]
# Same length (the square of the length of each):

# %%
v.magnitude_squared()

# %%
turned_v.magnitude_squared()

# %% [markdown]
# and perpendicular: the dot product of the two arrows is $0$.

# %%
v.dot(turned_v).scalar_part()

# %% [markdown]
# The turn is counterclockwise: $\vec{\mathbf{e}}_1$ goes to $\vec{\mathbf{e}}_2$.
# This is the quarter turn $r(\vec{\mathbf{v}}; \pi/2)$ of *The Geometric Product*,
# one operation with one name.
#
# **Third,** doing it twice gives $-\vec{\mathbf{v}}$: two quarter turns are a half
# turn.

# %%
turned_v * i

# %% [markdown]
# That is why $(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * (\vec{\mathbf{e}}_1 *
# \vec{\mathbf{e}}_2) = -1$:

# %%
i * i

# %% [markdown]
# ## The other side, and the other sign
#
# The side matters. Multiply the output on the *left* instead:
# $(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * \vec{\mathbf{e}}_1$.

# %%
i * e_1

# %% [markdown]
# The vector is turned the other way, clockwise, so the plotted point lands below the
# axis, and the graph comes out upside down:

# %%
plotted_left: Vector = x_input + i * f(x_input)
plotted_left

# %% [markdown]
# Drawn for the whole table, each turned output pointing down from its input:

# %%
mirror_dots: list[Point] = [
    Point(x=k, y=-float(o)) for k, o in zip(inputs, outputs, strict=True)
]
fig_mirror: PendingFigure
with plotted_table_scene(points=mirror_dots) as fig_mirror:
    line_through(start=mirror_dots[0], end=mirror_dots[-1])
    for k, o in zip(inputs, outputs, strict=True):
        plot_row(input_value=k, output_value=float(o), turn=-1.0, text="")
fig_mirror

# %% [markdown]
# ## A table that is not a line
#
# Nothing above used $m * x + b$. The same four steps for $f(x) = x * x$, the parabola
# you plotted next as a child: the input, the output along $\vec{\mathbf{e}}_1$, the
# turn, the plot.


# %%
def square(vector: Vector) -> Vector:
    """The vector whose number along ``e_1`` is the square of ``vector``'s."""
    number: Real = vector.coefficient(e_1)
    return Scalar(number * number) * e_1


square(x_input)

# %% [markdown]
# Turned by $\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2$ and put at the tip of the input:

# %%
parabola_point: Vector = x_input + square(x_input) * i
parabola_point

# %% [markdown]
# It is $x * \vec{\mathbf{e}}_1 + x * x * \vec{\mathbf{e}}_2$. The table for
# $x = -3$ to $x = 3$, drawn:

# %%
parabola_inputs: list[int] = list(range(-3, 4))
parabola_dots: list[Point] = [Point(x=k, y=k * k) for k in parabola_inputs]
fig_parabola: PendingFigure
with plotted_table_scene(points=parabola_dots) as fig_parabola:
    for k in parabola_inputs:
        plot_row(input_value=k, output_value=k * k, turn=1.0, text="")
fig_parabola
