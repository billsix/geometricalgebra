# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Relative graph paper — calculations
#
# Companion to *Relative Graph Paper*. Two arrows, $\vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{e}}_2$, make a sheet of graph paper: a point's coordinates say how many
# steps of each arrow to take from the origin. A function of the plane carries the whole
# sheet somewhere else, and the carried sheet is graph paper too, with its own origin
# and its own arrows. Coordinates only mean something relative to a sheet.
#
# When two functions are composed, there are two ways to watch them act, and they
# describe the same result:
#
# - read **right to left** (the inner function first), every step is measured on the
#   **standard** graph paper;
# - read **left to right** (the outer function first), every step is measured on the
#   **relative** graph paper the earlier steps left behind.
#
# This is the way the book *Model View Projection*
# (github.com/billsix/modelviewprojection) reads its sequences of transformations. Here
# the functions are a translate and a uniform scale; rotation joins them in *Rotation Is
# Turning the Graph Paper*.

# %%
import sympy
from IPython.display import display

from gacalc.base import Real
from gacalc.epixscene.frame_scene import point
from gacalc.epixscene.paper_scene import (
    Mapping,
    PendingFigure,
    Point,
    carried_paper,
    paper_scene,
)
from gacalc.functions import InvertibleFunction, identity
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.transforms import compose_intermediate_fns, translate, uniform_scale

# %% [markdown]
# ## Coordinates are relative to a sheet
#
# A point with coordinates $x$ and $y$ on the standard sheet is
# $x * \vec{\mathbf{e}}_1 + y * \vec{\mathbf{e}}_2$:

# %%
x: sympy.Symbol
y: sympy.Symbol
x, y = sympy.symbols("x y", real=True)
p: Vector = Scalar(x) * e_1 + Scalar(y) * e_2
p

# %% [markdown]
# Now slide the whole sheet by a vector $\vec{\mathbf{b}}$, with the translate $T_b$:

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
T: InvertibleFunction[Vector] = translate(b=b)
T(p)

# %% [markdown]
# The spot that had coordinates $(x, y)$ is carried to
# $(x + b_1) * \vec{\mathbf{e}}_1 + (y + b_2) * \vec{\mathbf{e}}_2$. Measured on the
# standard sheet its coordinates changed; measured on the slid sheet they are still
# $(x, y)$: still $x$ steps of the sheet's first arrow and $y$ of its second, from the
# sheet's own origin, which is now at $\vec{\mathbf{b}}$:

# %%
T(0 * e_1)

# %% [markdown]
# A ruler works the same way: a length of "3" means nothing until you say what the
# ruler is laid against.

# %% [markdown]
# ## The composition
#
# Scale the sheet by $m$ about the origin, then slide it by $\vec{\mathbf{b}}$:

# %%
m: sympy.Symbol = sympy.Symbol("m", positive=True)
S: InvertibleFunction[Vector] = uniform_scale(m=m)
f: InvertibleFunction[Vector] = T @ S
f

# %% [markdown]
# It carries the spot $(x, y)$ to

# %%
f(p)

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(b_1, 3), (b_2, 1), (m, 2)]


# %% [markdown]
# Each figure needs to know where each spot of the sheet goes. This helper turns a
# function into that mapping, at the plot values:


# %%
def mapping(function: InvertibleFunction[Vector]) -> Mapping:
    """Where ``function`` carries the spot ``(x, y)`` of the standard sheet."""

    def carried(x_coordinate: float, y_coordinate: float) -> Point:
        """The carried spot, as an ePiX point."""
        spot: Vector = function(x_coordinate * e_1 + y_coordinate * e_2)
        return point(coordinates=list(at_values(spot, values)))

    return carried


def draw(function: InvertibleFunction[Vector]) -> PendingFigure:
    """The standard sheet faintly, and the sheet ``function`` carries, captioned with
    the function."""
    fig: PendingFigure
    with paper_scene(
        lower_left=Point(x=-4, y=-4),
        upper_right=Point(x=10, y=8),
        caption=function._repr_latex_(),
    ) as fig:
        carried_paper(mapped=mapping(function))
    return fig


# %% [markdown]
# Before anything happens, the sheet is the standard one, with a purple triangle drawn
# on it so its motion is easy to follow:

# %%
draw(identity())

# %% [markdown]
# ## Reading right to left: every step on the standard sheet
#
# Read $T_b \circ S_m$ the way you evaluate $\sin(\cos(x))$: the inner function first.
# First the scale stretches the sheet away from the standard origin, by $m$ in standard
# units; then the translate slides the stretched sheet by $\vec{\mathbf{b}}$, again
# measured on the standard sheet. After each step, the next one is measured against the
# standard sheet, as if nothing had moved.

# %%
standard_steps: list[InvertibleFunction[Vector]] = list(
    compose_intermediate_fns([T, S])
)
step: InvertibleFunction[Vector]
for step in standard_steps:
    display(draw(step))

# %% [markdown]
# ## Reading left to right: every step on the relative sheet
#
# Now read the same $T_b \circ S_m$ from the left. First the translate slides the sheet
# by $\vec{\mathbf{b}}$. Then the scale stretches by $m$, but **relative to the slid
# sheet**: about its own origin, at $\vec{\mathbf{b}}$, and in its own units. Each step
# is measured against the sheet the previous steps left behind.

# %%
relative_steps: list[InvertibleFunction[Vector]] = list(
    compose_intermediate_fns([T, S], relative_basis=True)
)
for step in relative_steps:
    display(draw(step))

# %% [markdown]
# Same last picture. Before reading on, ask yourself why: the middle pictures disagree,
# so why do the ends agree?
#
# They agree because both sequences end with the same function, $T_b \circ S_m$; only
# the stories in between differ. Measured on the standard sheet, the scale happened
# first. Measured on the slid sheet, the slide happened first and the scale was about
# the slid origin, which is the same thing said from a different sheet.
#
# The check, at every spot: the last function of each sequence, applied to
# $x * \vec{\mathbf{e}}_1 + y * \vec{\mathbf{e}}_2$, minus $f$ applied to it. Reading
# right to left:

# %%
standard_last: InvertibleFunction[Vector] = standard_steps[-1]
(standard_last(p) - f(p)).simplified()

# %% [markdown]
# reading left to right:

# %%
relative_last: InvertibleFunction[Vector] = relative_steps[-1]
(relative_last(p) - f(p)).simplified()

# %% [markdown]
# The middle steps differ. Right to left, the middle picture is $S_m$ alone, which
# carries the origin nowhere:

# %%
standard_steps[1](0 * e_1)

# %% [markdown]
# Left to right, the middle picture is $T_b$ alone, which carries the origin to
# $\vec{\mathbf{b}}$:

# %%
relative_steps[1](0 * e_1)

# %% [markdown]
# ## The order of the functions does matter
#
# Reading direction is a choice of story; the order of the functions is not. Slide
# first and scale after, $S_m \circ T_b$, and the slide gets scaled too:

# %%
f_swapped: InvertibleFunction[Vector] = S @ T
f_swapped(p)

# %% [markdown]
# Its difference from $T_b \circ S_m$ is the slide scaled by $m - 1$:

# %%
(f_swapped(p) - f(p)).simplified()

# %% [markdown]
# Drawn at the plot values: the sheet lands somewhere else.

# %%
draw(f_swapped)

# %% [markdown]
# ## The coordinates, relative to each sheet
#
# Finally, the coordinates. The spot of the carried sheet with coordinates $(x, y)$ on
# that sheet has standard coordinates

# %%
(f(p).coefficient(e_1), f(p).coefficient(e_2))

# %% [markdown]
# and the inverse function reads them back: given a spot in standard coordinates, it
# says where that spot is on the carried sheet. Applied to the carried spot, it returns
# $(x, y)$; the difference:

# %%
(f.inverse(f(p)) - p).simplified()
