# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # One dimension: m * x + b — calculations
#
# Companion to *One Dimension: m·x + b*. You have graphed $y = m * x + b$ many times:
# $x$ across, $y$ up, a straight line. This notebook builds the same function from two
# simpler ones, a **uniform scale** by $m$ and a **translate** by $b$, and then draws it
# a second way, with the input and the output on number lines that point the same way.
# The second picture is the one the rest of the book uses.
#
# Every formula is computed with symbols; numbers appear only to draw the figures.

# %%
import sympy
from IPython.display import display

from gacalc.base import Real
from gacalc.epixscene.line_scene import (
    BLACK,
    BLUE,
    GREEN,
    OUTPUT_OFFSET,
    PURPLE,
    Color,
    PendingFigure,
    Point,
    graph_line,
    graph_paper_scene,
    number_line,
    number_lines_scene,
    step,
    tip,
)
from gacalc.functions import InvertibleFunction
from gacalc.g1 import Scalar, Vector, e_1
from gacalc.nbdisplay import at_values
from gacalc.transforms import translate, uniform_scale

# %% [markdown]
# ## The function, from two pieces
#
# The input is a number $x$ on a number line. We write it as $x * \vec{\mathbf{e}}_1$:
# $x$ steps along the number line's direction, $\vec{\mathbf{e}}_1$. (The chapter
# *Vectors as Number Lines* says more about that arrow; for now it just means "this
# way along the line".)

# %%
m: sympy.Symbol
b: sympy.Symbol
x: sympy.Symbol
m, b, x = sympy.symbols("m b x", real=True)
x_input: Vector = Scalar(x) * e_1
x_input

# %% [markdown]
# **Uniform scale by $m$** stretches the input by the factor $m$ (and flips it if $m$ is
# negative):

# %%
uniform_scale(m=m)(x_input)

# %% [markdown]
# **Translate by $b$** slides it $b$ steps along the line:

# %%
translate(b=Scalar(b) * e_1)(x_input)

# %% [markdown]
# Scale first, then translate: the composition $f = T_{b} \circ S_{m}$, read right to
# left like $\sin(\cos(x))$, the inner function first.

# %%
f: InvertibleFunction[Vector] = translate(b=Scalar(b) * e_1) @ uniform_scale(m=m)
f

# %% [markdown]
# Applied to $x * \vec{\mathbf{e}}_1$, it gives $(m * x + b) * \vec{\mathbf{e}}_1$:
# the familiar $m * x + b$, pointing along the same line.

# %%
f(x_input)

# %% [markdown]
# The output's number, its coordinate along $\vec{\mathbf{e}}_1$:

# %%
f(x_input).coefficient(e_1)

# %% [markdown]
# ## The familiar picture: graph paper
#
# To draw the graph you know, put each input $x$ across and its output up, and join the
# points. A line is fixed by two points, so the inputs $-6$ and $6$ are enough. The
# helper below reads the output number from $f$ itself, at chosen values of $m$ and
# $b$:


# %%
def output_at(m_value: Real, b_value: Real, x_value: Real) -> float:
    """The number ``f(x * e_1)`` with ``m``, ``b`` and ``x`` set to the given values."""
    output: Vector = at_values(f(x_input), [(m, m_value), (b, b_value), (x, x_value)])
    return float(output.coefficient(e_1))


def label(m_value: Real, b_value: Real) -> str:
    """The equation ``y = m * x + b`` at the given values, as LaTeX."""
    expression: sympy.Expr = sympy.sympify(f(x_input).coefficient(e_1)).subs(
        {m: m_value, b: b_value}
    )
    return f"$y = {sympy.latex(expression, mul_symbol='*')}$"


# %% [markdown]
# ### Changing the slope: $b = 0$
#
# With $b = 0$ only the scale acts, and every line passes through the origin. Before
# running the cell, predict which line is steepest, and which one falls.

# %%
slopes: list[Real] = [2, 1, sympy.Rational(1, 2), -1]
fig_slopes: PendingFigure
with graph_paper_scene(
    lower_left=Point(x=-7, y=-13), upper_right=Point(x=11, y=13)
) as fig_slopes:
    slope: Real
    color: Color
    for slope, color in zip(slopes, [PURPLE, GREEN, BLUE, BLACK], strict=True):
        graph_line(
            start=Point(x=-6, y=output_at(slope, 0, -6)),
            end=Point(x=6, y=output_at(slope, 0, 6)),
            color=color,
            text=label(slope, 0),
        )
fig_slopes

# %% [markdown]
# ### Changing the intercept: $m = 1$
#
# With $m = 1$ the scale does nothing, and only the translate acts: each line is the
# line $y = x$ slid up or down by $b$.

# %%
intercepts: list[Real] = [3, 1, 0, -2]
fig_intercepts: PendingFigure
with graph_paper_scene(
    lower_left=Point(x=-7, y=-9), upper_right=Point(x=11, y=10)
) as fig_intercepts:
    intercept: Real
    color: Color
    for intercept, color in zip(intercepts, [PURPLE, GREEN, BLUE, BLACK], strict=True):
        graph_line(
            start=Point(x=-6, y=output_at(1, intercept, -6)),
            end=Point(x=6, y=output_at(1, intercept, 6)),
            color=color,
            text=label(1, intercept),
        )
fig_intercepts

# %% [markdown]
# ### Both at once
#
# The values used for the rest of the notebook. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(m, 2), (b, 1)]

# %% [markdown]
# The function at those values:

# %%
at_values(f(x_input), values)

# %% [markdown]
# and its graph:

# %%
M: Real = values[0][1]
B: Real = values[1][1]
fig_line: PendingFigure
with graph_paper_scene(
    lower_left=Point(x=-7, y=-12), upper_right=Point(x=11, y=14)
) as fig_line:
    graph_line(
        start=Point(x=-6, y=output_at(M, B, -6)),
        end=Point(x=6, y=output_at(M, B, 6)),
        color=PURPLE,
        text=label(M, B),
    )
fig_line

# %% [markdown]
# ## The same function, along one direction
#
# The graph paper puts the output on a second axis, but nothing in $f$ points up: the
# input points along $\vec{\mathbf{e}}_1$ and so does the output. So draw it that way.
# For each input, a number line on the left shows $x * \vec{\mathbf{e}}_1$ (black), and
# a number line on the right, pointing the same way, shows the output: the scale step
# $m * x * \vec{\mathbf{e}}_1$ in green, then the translate step
# $b * \vec{\mathbf{e}}_1$ in blue, landing on the output (the purple dot).
#
# One input at a time, from $x = -5$ to $x = 5$:

# %%
inputs: list[int] = list(range(-5, 6))
outputs: list[float] = [output_at(M, B, k) for k in inputs]
low: float = min(0.0, *outputs) - 1
high: float = max(0.0, *outputs) + 1


def draw_row(row: int, k: int, labelled: bool) -> None:
    """Row ``row``: the input ``k * e_1`` on the left, and its scale and translate
    steps on the right, landing on the output."""
    scaled: float = output_at(M, 0, k)
    result: float = output_at(M, B, k)
    number_line(row=row, low=-6, high=6)
    step(row=row, tail=0, head=k, color=BLACK)
    tip(row=row, value=k, color=BLACK, text=f"${k}$" if labelled else "")
    number_line(row=row, low=low, high=high, origin=OUTPUT_OFFSET)
    step(row=row, tail=0, head=scaled, color=GREEN, origin=OUTPUT_OFFSET)
    step(row=row, tail=scaled, head=result, color=BLUE, origin=OUTPUT_OFFSET, lift=0.6)
    tip(
        row=row,
        value=result,
        color=PURPLE,
        text=f"${sympy.latex(sympy.nsimplify(result))}$" if labelled else "",
        origin=OUTPUT_OFFSET,
    )


k: int
for k in inputs:
    fig_k: PendingFigure
    with number_lines_scene(rows=1, low=low, high=high) as fig_k:
        draw_row(row=0, k=k, labelled=True)
    display(fig_k)

# %% [markdown]
# ## Turn your head
#
# Now stack all eleven rows in one picture, $x = -5$ at the top and $x = 5$ at the
# bottom. Before running the cell, predict: if you tilt your head to the right, so the
# top of the picture points left, what shape do the purple output dots make?

# %%
fig_stack: PendingFigure
with number_lines_scene(rows=len(inputs), low=low, high=high) as fig_stack:
    row: int
    for row, k in enumerate(inputs):
        draw_row(row=row, k=k, labelled=False)
fig_stack

# %% [markdown]
# Tilted, the rows run left to right from $x = -5$ to $x = 5$, and each output dot sits
# as far "up" as its output is large. The dots fall on a straight line: the graph of
# $y = m * x + b$ from the graph-paper picture. Nothing about the function changed. The
# graph paper spread the outputs out sideways, one column per input, so they could be
# seen all at once; along one direction, each input and its output share a line.
#
# The check, at every input at once: the output number is $m * x + b$, the
# difference is

# %%
sympy.simplify(sympy.sympify(f(x_input).coefficient(e_1) - (m * x + b)))

# %% [markdown]
# This one-direction picture is the one to keep. In the plane, inputs and outputs are
# both arrows in the same plane, and there is no spare direction to plot an output
# "up" into. Functions are drawn as motions of arrows, like the green and blue steps
# here.
