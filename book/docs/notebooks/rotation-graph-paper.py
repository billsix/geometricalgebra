# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Rotating and sliding the graph paper — calculations
#
# Companion to *Rotation Is Turning the Graph Paper*. *Relative Graph Paper* composed a
# translate with a uniform scale and read the composition two ways: right to left, every
# step measured on the standard sheet; left to right, every step measured on the sheet
# the earlier steps left behind. Now that rotation is built, the same two readings work
# for a rotation followed by a translate. This is the case *Model View Projection*
# (github.com/billsix/modelviewprojection) uses to place a paddle: turn it about its own
# center, then move it into place.
#
# The translate is symbolic; numbers appear only to draw the figures.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _frame_scene import point
from _paper_scene import Mapping, PendingFigure, Point, carried_paper, paper_scene
from IPython.display import display

from gacalc.base import Real
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.standardposition import rotation_from_to
from gacalc.transforms import compose_intermediate_fns, translate

# %% [markdown]
# ## The two functions
#
# The rotation is the one from $\vec{\mathbf{e}}_1$'s direction to the direction of
# $\vec{\mathbf{e}}_1 + \vec{\mathbf{e}}_2$, a turn of $45°$, built in *Proof: Rotate
# from the Direction of a to the Direction of b*:

# %%
R: InvertibleFunction[Vector] = rotation_from_to(1 * e_1, 1 * e_1 + 1 * e_2)
R

# %% [markdown]
# It turns $\vec{\mathbf{e}}_1$ onto that diagonal:

# %%
R(1 * e_1)

# %% [markdown]
# The translate slides by $\vec{\mathbf{b}}$:

# %%
b_1: sympy.Symbol
b_2: sympy.Symbol
b_1, b_2 = sympy.symbols("b_1 b_2", real=True)
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
T: InvertibleFunction[Vector] = translate(b=b)
T

# %% [markdown]
# Turn, then slide: $f = T_b \circ R$. It carries the spot $(x, y)$ of the standard
# sheet to

# %%
x: sympy.Symbol
y: sympy.Symbol
x, y = sympy.symbols("x y", real=True)
p: Vector = Scalar(x) * e_1 + Scalar(y) * e_2
f: InvertibleFunction[Vector] = T @ R
f(p).simplified()

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(b_1, 4), (b_2, 1)]


# %% [markdown]
# As in *Relative Graph Paper*, a helper turns a function into a picture of the sheet it
# carries, at the plot values:


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
        upper_right=Point(x=9, y=7),
        caption=function._repr_latex_(),
    ) as fig:
        carried_paper(mapped=mapping(function))
    return fig


# %% [markdown]
# ## Reading right to left: every step on the standard sheet
#
# The inner function first. The sheet turns $45°$ about the standard origin; then the
# turned sheet slides by $\vec{\mathbf{b}}$, measured with the standard arrows.

# %%
standard_steps: list[InvertibleFunction[Vector]] = list(
    compose_intermediate_fns([T, R])
)
step: InvertibleFunction[Vector]
for step in standard_steps:
    display(draw(step))

# %% [markdown]
# ## Reading left to right: every step on the relative sheet
#
# The outer function first. The sheet slides by $\vec{\mathbf{b}}$; then it turns
# $45°$, but about its **own** origin, now at $\vec{\mathbf{b}}$. Read this way, the
# triangle turns in place, about the corner of its own sheet. That is the reading that
# makes "turn the paddle about its center, then move it" easy to see.

# %%
relative_steps: list[InvertibleFunction[Vector]] = list(
    compose_intermediate_fns([T, R], relative_basis=True)
)
for step in relative_steps:
    display(draw(step))

# %% [markdown]
# Both sequences end with $T_b \circ R$. The check at every spot, reading right to left:

# %%
(standard_steps[-1](p) - f(p)).simplified()

# %% [markdown]
# and left to right:

# %%
(relative_steps[-1](p) - f(p)).simplified()

# %% [markdown]
# ## Swapping the functions moves the sheet
#
# Slide first and turn after, $R \circ T_b$, and the slide itself gets turned: the
# sheet's origin lands at $R(\vec{\mathbf{b}})$ instead of $\vec{\mathbf{b}}$. Where
# each composition carries the origin, first $T_b \circ R$:

# %%
f(0 * e_1).simplified()

# %% [markdown]
# then $R \circ T_b$:

# %%
f_swapped: InvertibleFunction[Vector] = R @ T
f_swapped(0 * e_1).simplified()

# %% [markdown]
# Drawn at the plot values:

# %%
draw(f_swapped)

# %% [markdown]
# Read left to right, $R \circ T_b$ says: turn the sheet about the standard origin
# first, then slide along the *turned* sheet's arrows. Read right to left it says: slide
# along the standard arrows, then turn everything, slide included, about the standard
# origin. Same picture either way, and a different picture from $T_b \circ R$.
