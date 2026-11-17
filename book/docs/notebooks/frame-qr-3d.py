# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Frames and QR in three dimensions — calculations
#
# The two-dimensional notebook, one dimension up. Each section computes with gacalc's
# `Frame`, then draws the result with ePiX, live, from one fixed camera so a reader can
# follow a vector from figure to figure. The colours match the 2D notebook: the frame
# $v_i$ is blue, the orthogonal $w_i$ green, and the target $y$ and its remainders red.
# The axes are drawn light and unlabelled: here $x$ and $y$ are vectors, the
# coordinates and the target of the frame's map.
#
# The frame here has numbers, not symbols: with all nine frame coordinates symbolic,
# each check takes minutes (`tasks/reference/frames-qr-and-reciprocal-frames.md`). The
# target $y$ of the peel is symbolic, so the peel's steps are formulas for every $y$,
# and numbers for $y$ appear only to draw the figures. Each check shows both sides,
# then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _frame_scene import (
    BLUE,
    GRAY_EDGE,
    GREEN,
    ORIGIN3,
    PLANE_FILL,
    RED,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    box_edges,
    dashed_arrow,
    note,
    patch,
    point,
    right_angle,
    scene_3d,
)

from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame
from gacalc.functions import InvertibleFunction, MatrixBackend, inverse
from gacalc.g3 import G, Scalar, Vector, e_1, e_2, e_3
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## A frame and its orthogonal set
#
# $v_1$ lies along $e_1$, $v_2$ leans over it in the $e_1 e_2$ plane, and $v_3$ leans
# over that plane. Orthogonalizing in frame order rejects from each vector its part in
# the span of the earlier ones: $w_2$ is $v_2$ with its $v_1$ part removed, and $w_3$ is
# $v_3$ with its part in the plane of $v_1, v_2$ removed, so $w_3$ is normal to that
# plane.

# %%
v_1: Vector = 2 * e_1 + 0 * e_2 + 0 * e_3
v_2: Vector = 1 * e_1 + 2 * e_2 + 0 * e_3
v_3: Vector = 1 * e_1 + 1 * e_2 + 2 * e_3
frame: Frame = Frame((v_1, v_2, v_3))
w_1: MultiVectorBase
w_2: MultiVectorBase
w_3: MultiVectorBase
w_1, w_2, w_3 = frame.orthogonal_vectors()
w_1

# %% [markdown]
# $w_2$:

# %%
w_2

# %% [markdown]
# $w_3$:

# %%
w_3

# %% [markdown]
# The coefficient table $(w_j \cdot v_i) / |w_j|^2$, triangular with ones on the
# diagonal:

# %%
sympy.Matrix(frame.coefficients())

# %%
P_V1: Point = point(coordinates=list(v_1))
P_V2: Point = point(coordinates=list(v_2))
P_V3: Point = point(coordinates=list(v_3))
P_W2: Point = point(coordinates=list(w_2))
P_W3: Point = point(coordinates=list(w_3))
# the projected extent of the parallelepiped and axes from CAMERA, plus room for labels
LOWER_LEFT: Point = Point(x=-0.8, y=-1.9)
UPPER_RIGHT: Point = Point(x=6.0, y=3.6)
# where a step's equation goes: high on the z axis, the text running to the right
EQUATION_AT: Point = Point(x=0, y=0, z=3.4)
fig: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(head=P_V1, color=BLUE, text="$v_1 = w_1$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text="$v_3$", offset=Point(x=4, y=4))
    arrow(
        head=P_W2,
        color=GREEN,
        text="$w_2$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(
        head=P_W3,
        color=GREEN,
        text="$w_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN3, toward_a=P_V1, toward_b=P_W2)
    right_angle(corner=ORIGIN3, toward_a=P_W2, toward_b=P_W3)
    # w_3 is v_3 minus its shadow in the plane: the dashed drop from v_3 to the plane
    dashed_arrow(tail=P_V3, head=P_V3 + (-1) * P_W3, color=GREEN)
fig

# %% [markdown]
# ## Volume is base times height times height
#
# The parallelepiped of $v_1, v_2, v_3$ has a parallelogram base of area
# $|w_1| * |w_2|$ (the 2D result) and height $|w_3|$ above it. The product is the
# volume, the magnitude of $v_1 \wedge v_2 \wedge v_3$.

# %%
base_area: Real = w_1.magnitude() * w_2.magnitude()
base_area

# %% [markdown]
# The height $|w_3|$:

# %%
height: Real = w_3.magnitude()
height

# %% [markdown]
# Base times height:

# %%
base_area * height

# %% [markdown]
# The volume $|v_1 \wedge v_2 \wedge v_3|$:

# %%
volume: Real = (v_1 ^ v_2 ^ v_3).magnitude()
volume

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(base_area * height - volume))

# %%
fig_volume: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_volume:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    box_edges(a=P_V1, b=P_V2, c=P_V3, color=BLUE, width=0.8)
    dashed_arrow(
        tail=P_V3 + (-1) * P_W3,
        head=P_V3,
        color=GREEN,
        text=rf"$|w_3| = {sympy.latex(height)}$",
        offset=Point(x=-6, y=-10),
        align=LabelPos.l,
    )
    note(
        at=Point(x=2.2, y=0.5, z=0), text=rf"$|w_1| * |w_2| = {sympy.latex(base_area)}$"
    )
fig_volume

# %% [markdown]
# ## The forward map sends the unit cube to the parallelepiped
#
# $f(x) = x_1 * v_1 + x_2 * v_2 + x_3 * v_3$ sends each $e_i$ to $v_i$, so the unit
# cube (gray) lands on the frame's parallelepiped (blue). Its matrix has the $v_i$ as
# columns.

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
sympy.Matrix(f.to_matrix(G, n=3, backend=MatrixBackend.SYMPY))[:3, :3]

# %%
fig_forward: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_forward:
    box_edges(
        a=Point(x=1, y=0, z=0),
        b=Point(x=0, y=1, z=0),
        c=Point(x=0, y=0, z=1),
        color=GRAY_EDGE,
        width=1.2,
    )
    box_edges(a=P_V1, b=P_V2, c=P_V3, color=BLUE, width=0.8)
    arrow(head=P_V1, color=BLUE, text="$f(e_1)$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text="$f(e_2)$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text="$f(e_3)$", offset=Point(x=4, y=4))
fig_forward


# %% [markdown]
# ## The inverse, one peel at a time
#
# Recover $x$ from $y = f(x)$ by peeling the frame from its last vector. The target $y$,
# every coordinate a symbol:

# %%
y_1: sympy.Symbol
y_2: sympy.Symbol
y_3: sympy.Symbol
y_1, y_2, y_3 = sympy.symbols("y_1 y_2 y_3", real=True)
y: Vector = Scalar(y_1) * e_1 + Scalar(y_2) * e_2 + Scalar(y_3) * e_3
y

# %% [markdown]
# The plot values make $y = v_1 + v_2 + v_3$, so every coordinate comes out 1 in the
# figures. Change them and rerun; the figures' scenes are sized for these values.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(y_1, 4), (y_2, 3), (y_3, 2)]


def tex(value: Real) -> str:
    """``value`` at the plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, values))


P_Y: Point = point(coordinates=list(at_values(y, values)))

# %% [markdown]
# $w_3$ is normal to the plane of $v_1, v_2$, so it is perpendicular to every frame
# vector but $v_3$: it reads $x_3$ alone. $w_1$ and $w_2$ are not perpendicular to
# $v_3$, so the peel cannot start with them. $w_1 \cdot v_3$:

# %%
w_1.dot(v_3).scalar_part()

# %% [markdown]
# $w_2 \cdot v_3$:

# %%
w_2.dot(v_3).scalar_part()

# %% [markdown]
# **Step 0, the setup.** The plane of $v_1, v_2$ (shaded), $v_3$ leaning over it, and
# the target $y$.

# %%
fig_step_0: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_0:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(head=P_V1, color=BLUE, text="$v_1$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text="$v_3$", offset=Point(x=4, y=4))
    arrow(
        head=P_W3,
        color=GREEN,
        text="$w_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN3, toward_a=P_V1, toward_b=P_W3)
    arrow(head=P_Y, color=RED, text="$y$")
fig_step_0

# %% [markdown]
# **Step 1, read $x_3$.** Project $y$ onto $w_3$: $v_1$ and $v_2$ drop out, and the
# projection is $x_3$ copies of $w_3$. Its length is $y$'s height above the plane and
# $|w_3|$ is $v_3$'s height, so $x_3$ is two heights, one divided by the other. The
# projection:

# %%
y_onto_w_3: MultiVectorBase = y.projected_onto(onto=w_3).simplified()
y_onto_w_3

# %% [markdown]
# $x_3$:

# %%
x_3: Real = sympy.simplify(sympy.sympify((y_onto_w_3 / w_3).scalar_part()))
x_3

# %% [markdown]
# At the plot values:

# %%
at_values(x_3, values)

# %%
w_3_dot_y: Real = w_3.dot(y).scalar_part()
fig_step_1: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_1:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V3,
        color=BLUE,
        text="$v_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text="$y$")
    dashed_arrow(
        tail=P_V3,
        head=P_V3 + (-1) * P_W3,
        color=BLUE,
        text=rf"$|w_3| = {sympy.latex(height)}$",
        offset=Point(x=-6, y=-14),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=P_Y.x2(), z=0),
        color=RED,
        text=rf"$\frac{{w_3 \cdot y}}{{|w_3|}} = {tex(w_3_dot_y / height)}$",
        offset=Point(x=6, y=-14),
    )
    note(
        at=EQUATION_AT,
        text=(
            r"$x_3 = \frac{w_3 \cdot y}{|w_3|^2} = "
            rf"\frac{{{tex(w_3_dot_y)}}}{{{sympy.latex(height**2)}}} = {tex(x_3)}$"
        ),
        align=LabelPos.r,
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_3 * v_3$.** $y$ slides back along $v_3$ (dashed) into the plane of
# $v_1, v_2$. What is left, $r_1$, is a 2D problem in that plane:

# %%
r_1: Vector = (y - Scalar(x_3) * v_3).simplified()
r_1

# %% [markdown]
# At the plot values:

# %%
at_values(r_1, values)

# %%
P_R1: Point = point(coordinates=list(at_values(r_1, values)))
fig_step_2: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_2:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V3,
        color=BLUE,
        text="$v_3$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text="$y$")
    dashed_arrow(
        tail=P_Y, head=P_R1, color=BLUE, text="$-x_3 * v_3$", offset=Point(x=8, y=10)
    )
    arrow(head=P_R1, color=RED, text="$r_1$", offset=Point(x=6, y=-10), width=2.2)
fig_step_2

# %% [markdown]
# **Steps 3 and 4, the 2D peel inside the plane.** The camera stays put. $w_2$ is the
# normal to $v_1$'s line within the plane, so projecting $r_1$ onto it reads $x_2$:

# %%
x_2: Real = sympy.simplify(
    sympy.sympify((r_1.projected_onto(onto=w_2) / w_2).scalar_part())
)
x_2

# %% [markdown]
# Removing $x_2 * v_2$ leaves $r_2$ on $v_1$'s line:

# %%
r_2: Vector = (r_1 - Scalar(x_2) * v_2).simplified()
r_2

# %% [markdown]
# and projecting $r_2$ onto $w_1$ reads $x_1$:

# %%
x_1: Real = sympy.simplify(
    sympy.sympify((r_2.projected_onto(onto=w_1) / w_1).scalar_part())
)
x_1

# %% [markdown]
# At the plot values, $r_2$:

# %%
at_values(r_2, values)

# %%
P_R2: Point = point(coordinates=list(at_values(r_2, values)))
w_2_dot_r_1: Real = w_2.dot(r_1).scalar_part()
fig_step_3: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_step_3:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(
        head=P_V2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
    )
    arrow(head=P_R1, color=RED, text="$r_1$", offset=Point(x=6, y=4))
    P_DROP: Point = Point(x=P_R1.x1(), y=0, z=0)
    dashed_arrow(tail=P_R1, head=P_DROP, color=RED)
    note(
        at=0.5 * (P_R1 + P_DROP),
        text=(
            r"$\frac{w_2 \cdot r_1}{|w_2|} = "
            rf"{tex(w_2_dot_r_1 / w_2.magnitude())}$"
        ),
        color=RED,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    dashed_arrow(tail=P_R1, head=P_R2, color=BLUE)
    note(
        at=0.5 * (P_R1 + P_R2),
        text="$-x_2 * v_2$",
        color=BLUE,
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_R2,
        color=RED,
        text="$r_2 = x_1 * v_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
        width=2.2,
    )
    note(
        at=EQUATION_AT,
        text=(
            rf"$x_2 = \frac{{{tex(w_2_dot_r_1)}}}"
            rf"{{{sympy.latex(w_2.magnitude_squared())}}} = {tex(x_2)}, \quad"
            r" x_1 = \frac{w_1 \cdot r_2}{|w_1|^2} = "
            rf"\frac{{{tex(w_1.dot(r_2).scalar_part())}}}"
            rf"{{{sympy.latex(w_1.magnitude_squared())}}} = {tex(x_1)}$"
        ),
        align=LabelPos.r,
    )
fig_step_3

# %% [markdown]
# **The result.** The recovered coordinates $x$:

# %%
x: Vector = Scalar(x_1) * e_1 + Scalar(x_2) * e_2 + Scalar(x_3) * e_3
x

# %% [markdown]
# gacalc's inverse of the frame's map, applied to $y$:

# %%
f.inverse(y).simplified()

# %% [markdown]
# Its difference from the peeled $x$:

# %%
(f.inverse(y) - x).simplified()

# %% [markdown]
# The map sends $x$ back to:

# %%
f(x).simplified()

# %% [markdown]
# Its difference from $y$:

# %%
(f(x) - y).simplified()

# %% [markdown]
# At the plot values, $x$ (black); $x_1 * v_1 + x_2 * v_2 + x_3 * v_3$, tip to tail
# (blue), ends on $y$:

# %%
at_values(x, values)

# %%
P_X: Point = point(coordinates=list(at_values(x, values)))
P_X1_V1: Point = point(coordinates=list(at_values(Scalar(x_1) * v_1, values)))
P_X2_V2: Point = point(coordinates=list(at_values(Scalar(x_2) * v_2, values)))
fig_result: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_result:
    arrow(head=P_Y, color=RED, text="$y = f(x)$")
    arrow(head=P_X1_V1, color=BLUE, text="$x_1 * v_1$", offset=Point(x=4, y=-8))
    dashed_arrow(tail=P_X1_V1, head=P_X1_V1 + P_X2_V2, color=BLUE)
    dashed_arrow(tail=P_X1_V1 + P_X2_V2, head=P_Y, color=BLUE)
    arrow(head=P_X, text="$x$", offset=Point(x=-4, y=4), align=LabelPos.l, width=2.2)
fig_result

# %% [markdown]
# ## The round trip, for every input
#
# For a symbolic $x$, `inverse(f) @ f` gives $x$ back unchanged, and `f @ inverse(f)`
# does the same for a symbolic $y$. A general $x$:

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_3: sympy.Symbol
s_1, s_2, s_3 = sympy.symbols("x_1 x_2 x_3", real=True)
general: Vector = Scalar(s_1) * e_1 + Scalar(s_2) * e_2 + Scalar(s_3) * e_3
general

# %% [markdown]
# $f^{-1}(f(x))$:

# %%
(inverse(f) @ f)(general).simplified()

# %% [markdown]
# minus $x$:

# %%
((inverse(f) @ f)(general) - general).simplified()

# %% [markdown]
# $f(f^{-1}(y))$, for a general $y$:

# %%
(f @ inverse(f))(general).simplified()

# %% [markdown]
# minus $y$:

# %%
((f @ inverse(f))(general) - general).simplified()

# %% [markdown]
# ## The last reciprocal vector
#
# $v^3 = w_3 / |w_3|^2$ dots to 0 with $v_1$ and $v_2$ and to 1 with $v_3$: step 1 as a
# single dot product. $v^3$:

# %%
reciprocal_3: MultiVectorBase = w_3 / w_3.magnitude_squared()
reciprocal_3

# %% [markdown]
# $v^3 \cdot v_1$:

# %%
reciprocal_3.dot(v_1).scalar_part()

# %% [markdown]
# $v^3 \cdot v_2$:

# %%
reciprocal_3.dot(v_2).scalar_part()

# %% [markdown]
# $v^3 \cdot v_3$:

# %%
reciprocal_3.dot(v_3).scalar_part()

# %%
fig_reciprocal: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_reciprocal:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    arrow(head=P_V1, color=BLUE, text="$v_1$", offset=Point(x=4, y=-8))
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=4, y=4))
    arrow(head=P_V3, color=BLUE, text="$v_3$", offset=Point(x=4, y=4))
    arrow(
        head=point(coordinates=list(reciprocal_3)),
        color=GREEN,
        text=r"$v^3 = \frac{w_3}{|w_3|^2}$",
        offset=Point(x=-4, y=4),
        align=LabelPos.l,
        width=2.4,
    )
fig_reciprocal
