# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Frames and QR in two dimensions — calculations
#
# Companion to the *Frames and QR* chapter. On graph paper the two axes are
# perpendicular, and a point's coordinates are read straight off them. A frame is a
# pair of slanted axes $v_1, v_2$; this notebook builds perpendicular axes $w_1, w_2$
# from them, then uses those to read a point's coordinates in the slanted frame.
#
# Each section computes with gacalc's `Frame` (`gacalc.frame`) on symbolic
# coordinates, so every result is a formula for every frame, then draws it with ePiX,
# live, at the plot values. The colours are the same throughout: the frame $v_i$ is
# blue, the orthogonal $w_i$ green, the unit $u_i$ purple, and the target $y$ and its
# remainders red. The axes are drawn light and unlabelled: here $x$ and $y$ are
# vectors, the coordinates and the target of the frame's map. Each check shows both
# sides, then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _frame_scene import (
    BLUE,
    GRAY_FILL,
    GREEN,
    ORIGIN2,
    PURPLE,
    PURPLE_FILL,
    RED,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    patch,
    point,
    right_angle,
    scene_2d,
)

from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame
from gacalc.functions import InvertibleFunction, MatrixBackend, inverse
from gacalc.g2 import G, Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## A frame and its orthogonal set
#
# Two vectors, every coordinate a symbol. `Frame` keeps them as they are:

# %%
p: sympy.Symbol
q: sympy.Symbol
r: sympy.Symbol
t: sympy.Symbol
p, q, r, t = sympy.symbols("p q r t", real=True)
v_1: Vector = Scalar(p) * e_1 + Scalar(q) * e_2
v_1

# %%
v_2: Vector = Scalar(r) * e_1 + Scalar(t) * e_2
v_2

# %% [markdown]
# The values used to draw the figures in the first part of the notebook; the figures'
# frames are sized for these values. They are neither perpendicular nor of unit length.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(p, 2), (q, 1), (r, 1), (t, 2)]


def tex(value: Real) -> str:
    """``value`` at the plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, values))


# %% [markdown]
# `orthogonal_vectors()` computes the orthogonal set: $w_1 = v_1$, and $w_2$ is $v_2$
# with its part along $v_1$ rejected. $w_1$:

# %%
frame: Frame = Frame((v_1, v_2))
w_1: MultiVectorBase
w_2: MultiVectorBase
w_1, w_2 = frame.orthogonal_vectors()
w_1

# %% [markdown]
# $w_2$:

# %%
w_2 = w_2.simplified()
w_2

# %% [markdown]
# They are perpendicular, $w_1 \cdot w_2 = 0$:

# %%
sympy.simplify(sympy.sympify(w_1.dot(w_2).scalar_part()))

# %% [markdown]
# The unit vectors $u_i = w_i / |w_i|$ (purple, short) are the orthonormal set. $u_1$:

# %%
u_1: MultiVectorBase
u_2: MultiVectorBase
u_1, u_2 = frame.orthonormal_vectors()
u_1 = u_1.simplified()
u_1

# %% [markdown]
# $u_2$:

# %%
u_2 = u_2.simplified()
u_2

# %%
P_V1: Point = point(coordinates=list(at_values(v_1, values)))
P_V2: Point = point(coordinates=list(at_values(v_2, values)))
P_W2: Point = point(coordinates=list(at_values(w_2, values)))
P_U1: Point = point(coordinates=list(at_values(u_1, values)))
P_U2: Point = point(coordinates=list(at_values(u_2, values)))
fig: PendingFigure
with scene_2d(lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.0, y=2.6)) as fig:
    arrow(head=P_V1, color=BLUE, text="$v_1 = w_1$")
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=6, y=2))
    arrow(
        head=P_W2,
        color=GREEN,
        text="$w_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    right_angle(corner=ORIGIN2, toward_a=P_V1, toward_b=P_W2)
    # w_2 is v_2 minus its shadow on v_1: the dashed drop from v_2 to the v_1 line
    dashed_arrow(tail=P_V2, head=P_V2 - P_W2, color=GREEN)
    # the unit vectors last, so they sit on top of the longer w's they point along
    arrow(head=P_U1, color=PURPLE, width=3.0, text="$u_1$", offset=Point(x=4, y=-10))
    arrow(head=P_U2, color=PURPLE, width=3.0, text="$u_2$", offset=Point(x=8, y=0))
fig

# %% [markdown]
# ## The coefficients are shadows
#
# `coefficients()` is the table $(w_j \cdot v_i) / |w_j|^2$: row $i$ says how much of
# each $w_j$ it takes to rebuild $v_i$. It is triangular, because $v_1 = w_1$ uses no
# $w_2$, and its diagonal is all ones, because each $v_i$ is $w_i$ plus a part in the
# earlier directions.

# %%
table: sympy.Matrix = sympy.Matrix(frame.coefficients()).applyfunc(sympy.simplify)
table

# %% [markdown]
# The entry below the diagonal is the length of $v_2$'s shadow on $w_1$, in units of
# $|w_1|$:

# %%
c_21: Real = table[1, 0]
c_21

# %% [markdown]
# Rebuilding $v_2$ from the table, $c_{21} * w_1 + 1 * w_2$:

# %%
rebuilt_v_2: MultiVectorBase = (Scalar(c_21) * w_1 + 1 * w_2).simplified()
rebuilt_v_2

# %% [markdown]
# Its difference from $v_2$:

# %%
(v_2 - rebuilt_v_2).simplified()

# %% [markdown]
# At the plot values, $c_{21}$:

# %%
at_values(c_21, values)

# %%
P_SHADOW: Point = point(coordinates=list(at_values(Scalar(c_21) * w_1, values)))
fig_shadow: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.0, y=2.6)
) as fig_shadow:
    arrow(head=P_V1, color=BLUE, text="$w_1$", offset=Point(x=6, y=-4))
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=0, y=6))
    arrow(
        head=P_SHADOW,
        color=GREEN,
        text=rf"${tex(c_21)} * w_1$",
        offset=Point(x=4, y=-10),
    )
    dashed_arrow(tail=P_SHADOW, head=P_V2, color=GREEN)
    note(
        at=0.5 * (P_SHADOW + P_V2),
        text="$w_2$",
        color=GREEN,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    right_angle(corner=P_SHADOW, toward_a=P_V1, toward_b=P_W2)
fig_shadow

# %% [markdown]
# ## Area is base times height
#
# The parallelogram of $v_1$ and $v_2$ has base $|w_1|$ along $v_1$ and height $|w_2|$,
# the part of $v_2$ that sticks out of $v_1$'s line. Their product is the area, the
# magnitude of $v_1 \wedge v_2$. The base:

# %%
base: Real = w_1.magnitude()
base

# %% [markdown]
# the height:

# %%
height: Real = sympy.simplify(sympy.sympify(w_2.magnitude()))
height

# %% [markdown]
# base times height:

# %%
base_times_height: Real = sympy.simplify(sympy.sympify(base * height))
base_times_height

# %% [markdown]
# The area $|v_1 \wedge v_2|$:

# %%
area: Real = (v_1 ^ v_2).magnitude()
area

# %% [markdown]
# Their difference:

# %%
sympy.simplify(sympy.sympify(base_times_height - area))

# %%
fig_area: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.4, y=3.4)
) as fig_area:
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    arrow(
        head=P_V1, color=BLUE, text=rf"$|w_1| = {tex(base)}$", offset=Point(x=6, y=-6)
    )
    arrow(
        head=P_V2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-6, y=4),
        align=LabelPos.l,
    )
    dashed_arrow(tail=P_SHADOW, head=P_V2, color=GREEN)
    note(
        at=0.5 * (P_SHADOW + P_V2),
        text=rf"$|w_2| = {tex(height)}$",
        color=GREEN,
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    right_angle(corner=P_SHADOW, toward_a=P_V1, toward_b=P_W2)
    note(at=Point(x=2.1, y=2.0), text=rf"area $= |w_1| * |w_2| = {tex(area)}$")
fig_area

# %% [markdown]
# ## The forward map sends $e_i$ to $v_i$
#
# `to_invertible_function()` is the linear map $f(x) = x_1 * v_1 + x_2 * v_2$: it sends
# $e_1$ to $v_1$ and $e_2$ to $v_2$, so the unit square (gray) lands on the frame's
# parallelogram (purple). Its matrix has the $v_i$ as columns:

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
F: sympy.Matrix = sympy.Matrix(f.to_matrix(G, n=2, backend=MatrixBackend.SYMPY))[:2, :2]
F

# %% [markdown]
# $f(e_1)$:

# %%
f(1 * e_1 + 0 * e_2)

# %% [markdown]
# minus $v_1$:

# %%
(f(1 * e_1 + 0 * e_2) - v_1).simplified()

# %% [markdown]
# $f(e_2)$:

# %%
f(0 * e_1 + 1 * e_2)

# %% [markdown]
# minus $v_2$:

# %%
(f(0 * e_1 + 1 * e_2) - v_2).simplified()

# %%
P_E1: Point = Point(x=1, y=0)
P_E2: Point = Point(x=0, y=1)
fig_forward: PendingFigure
with scene_2d(
    lower_left=Point(x=-0.6, y=-0.6), upper_right=Point(x=3.4, y=3.4)
) as fig_forward:
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    patch(corners=[ORIGIN2, P_E1, P_E1 + P_E2, P_E2], color=GRAY_FILL)
    arrow(head=P_E1, text="$e_1$", offset=Point(x=0, y=-8), align=LabelPos.b)
    arrow(head=P_E2, text="$e_2$", offset=Point(x=-6, y=0), align=LabelPos.l)
    arrow(head=P_V1, color=BLUE, text="$f(e_1) = v_1$")
    arrow(
        head=P_V2,
        color=BLUE,
        text="$f(e_2) = v_2$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_forward

# %% [markdown]
# ## $f = Q \circ R$
#
# QR splits $f$ into two steps. $R$ writes each $v_i$ in the orthonormal coordinates
# $u_j \cdot v_i$: it keeps $e_1$'s line, and its matrix is upper triangular because
# $v_1$ has no $u_2$ part. $Q$ then turns the plane so the $e_j$ land on the $u_j$:
# a rotation. $Q$ is itself a frame's function, the frame of the $u_j$, and
# $R = Q^{-1} \circ f$. $R$'s matrix:

# %%
Q: InvertibleFunction[MultiVectorBase] = Frame((u_1, u_2)).to_invertible_function()
R: InvertibleFunction[MultiVectorBase] = inverse(Q) @ f
R_matrix: sympy.Matrix = sympy.Matrix(R.to_matrix(G, n=2, backend=MatrixBackend.SYMPY))[
    :2, :2
].applyfunc(sympy.simplify)
R_matrix

# %% [markdown]
# $Q$'s matrix:

# %%
Q_matrix: sympy.Matrix = sympy.Matrix(Q.to_matrix(G, n=2, backend=MatrixBackend.SYMPY))[
    :2, :2
].applyfunc(sympy.simplify)
Q_matrix

# %% [markdown]
# Their product $Q * R$:

# %%
QR_product: sympy.Matrix = (Q_matrix * R_matrix).applyfunc(sympy.simplify)
QR_product

# %% [markdown]
# minus $f$'s matrix:

# %%
(QR_product - F).applyfunc(sympy.simplify)

# %%
P_R1: Point = point(coordinates=list(at_values(R(1 * e_1 + 0 * e_2), values)))
P_R2: Point = point(coordinates=list(at_values(R(0 * e_1 + 1 * e_2), values)))
fig_r: PendingFigure
with scene_2d(
    lower_left=Point(x=-0.6, y=-0.6), upper_right=Point(x=4.6, y=2.2)
) as fig_r:
    patch(corners=[ORIGIN2, P_R1, P_R1 + P_R2, P_R2], color=PURPLE_FILL)
    patch(corners=[ORIGIN2, P_E1, P_E1 + P_E2, P_E2], color=GRAY_FILL)
    arrow(
        head=P_R1,
        color=BLUE,
        text="$R(e_1)$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_R2,
        color=BLUE,
        text="$R(e_2)$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_r

# %%
fig_qr: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=4.6, y=3.4)
) as fig_qr:
    patch(corners=[ORIGIN2, P_R1, P_R1 + P_R2, P_R2], color=GRAY_FILL)
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    arrow(
        head=P_U1,
        color=PURPLE,
        width=2.6,
        text="$u_1$",
        offset=Point(x=4, y=-8),
    )
    arrow(
        head=P_U2,
        color=PURPLE,
        width=2.6,
        text="$u_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_V1, color=BLUE, text="$Q(R(e_1)) = v_1$")
    arrow(
        head=P_V2,
        color=BLUE,
        text="$Q(R(e_2)) = v_2$",
        offset=Point(x=0, y=8),
        align=LabelPos.t,
    )
fig_qr

# %% [markdown]
# ## The inverse, one peel at a time
#
# `f.inverse` recovers the coordinates $x$ from $y = f(x)$ by peeling the frame from its
# last vector. The steps below use a second frame $v_1, v_2$ and a target $y$, every
# coordinate a symbol:

# %%
m_1: sympy.Symbol
m_2: sympy.Symbol
n_1: sympy.Symbol
n_2: sympy.Symbol
y_1: sympy.Symbol
y_2: sympy.Symbol
m_1, m_2, n_1, n_2, y_1, y_2 = sympy.symbols("m_1 m_2 n_1 n_2 y_1 y_2", real=True)
a_1: Vector = Scalar(m_1) * e_1 + Scalar(m_2) * e_2
a_1

# %%
a_2: Vector = Scalar(n_1) * e_1 + Scalar(n_2) * e_2
a_2

# %%
y: Vector = Scalar(y_1) * e_1 + Scalar(y_2) * e_2
y

# %% [markdown]
# The plot values for this part are the frame from the reference text,
# $v_1 = 2 * e_1$ and $v_2 = 1 * e_1 + 3 * e_2$, with $y = 3 * e_1 + 3 * e_2$, so every
# number in the figures is small and exact; the figures' frames are sized for them.

# %%
peel_values: list[tuple[sympy.Symbol, Real]] = [
    (m_1, 2),
    (m_2, 0),
    (n_1, 1),
    (n_2, 3),
    (y_1, 3),
    (y_2, 3),
]


def peel_tex(value: Real) -> str:
    """``value`` at the peel's plot values, as LaTeX for a figure label."""
    return sympy.latex(at_values(value, peel_values))


# %% [markdown]
# The orthogonal set of this frame: $w_1$,

# %%
peel_frame: Frame = Frame((a_1, a_2))
b_1: MultiVectorBase
b_2: MultiVectorBase
b_1, b_2 = peel_frame.orthogonal_vectors()
b_1

# %% [markdown]
# and $w_2$:

# %%
b_2 = b_2.simplified()
b_2

# %% [markdown]
# $w_2$ is perpendicular to *every other* frame vector, $w_2 \cdot v_1 = 0$, so it can
# read off $x_2$ alone:

# %%
sympy.simplify(sympy.sympify(b_2.dot(a_1).scalar_part()))

# %% [markdown]
# $w_1$ is not perpendicular to $v_2$, so $w_1 \cdot y$ mixes both coordinates: the peel
# cannot start with $x_1$. $w_1 \cdot v_2$:

# %%
w_1_dot_v_2: Real = b_1.dot(a_2).scalar_part()
w_1_dot_v_2

# %% [markdown]
# **Step 0, the setup.** The frame (blue) and its parallelogram, the target $y$ (red),
# and the orthogonal set (green): $w_1 = v_1$, and $w_2$ at a right angle to $v_1$'s
# line.

# %%
P_A1: Point = point(coordinates=list(at_values(a_1, peel_values)))
P_A2: Point = point(coordinates=list(at_values(a_2, peel_values)))
P_B2: Point = point(coordinates=list(at_values(b_2, peel_values)))
P_Y: Point = point(coordinates=list(at_values(y, peel_values)))
PEEL_LOWER_LEFT: Point = Point(x=-0.6, y=-0.6)
PEEL_UPPER_RIGHT: Point = Point(x=4.0, y=3.8)
fig_step_0: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_0:
    patch(corners=[ORIGIN2, P_A1, P_A1 + P_A2, P_A2], color=PURPLE_FILL)
    arrow(
        head=P_A1,
        color=BLUE,
        text="$v_1 = w_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(
        head=P_B2,
        color=GREEN,
        text="$w_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
        width=2.2,
    )
    right_angle(corner=ORIGIN2, toward_a=P_A1, toward_b=P_B2)
    arrow(head=P_Y, color=RED, text="$y$")
    note(
        at=Point(x=2.0, y=3.5),
        text=rf"$w_2 \cdot v_1 = 0$, but $w_1 \cdot v_2 = {peel_tex(w_1_dot_v_2)}$",
    )
fig_step_0

# %% [markdown]
# **Step 1, read $x_2$.** Project $y$ onto $w_2$. Every earlier frame vector is
# perpendicular to $w_2$ and drops out, so the projection is $x_2$ copies of $w_2$:
# dividing it by $w_2$ reads $x_2$. The projection's length is $y$'s height above
# $v_1$'s line, and $|w_2|$ is $v_2$'s own height, so $x_2$ is two heights, one
# divided by the other. The projection:

# %%
y_onto_w_2: MultiVectorBase = y.projected_onto(onto=b_2).simplified()
y_onto_w_2

# %% [markdown]
# $x_2$:

# %%
x_2: Real = sympy.simplify(sympy.sympify((y_onto_w_2 / b_2).scalar_part()))
x_2

# %% [markdown]
# At the plot values:

# %%
at_values(x_2, peel_values)

# %%
w_2_dot_y: Real = b_2.dot(y).scalar_part()
fig_step_1: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_1:
    arrow(
        head=P_A1,
        color=BLUE,
        text="$v_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text="$y$")
    dashed_arrow(
        tail=P_A2,
        head=Point(x=P_A2.x1(), y=0),
        color=BLUE,
        text=rf"$|w_2| = {peel_tex(b_2.magnitude())}$",
        offset=Point(x=-6, y=24),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=0),
        color=RED,
        text=(
            r"$\frac{w_2 \cdot y}{|w_2|} = "
            rf"{peel_tex(w_2_dot_y / b_2.magnitude())}$"
        ),
        offset=Point(x=6, y=24),
    )
    note(
        at=Point(x=2.0, y=3.5),
        text=(
            r"$x_2 = \frac{w_2 \cdot y}{|w_2|^2} = "
            rf"\frac{{{peel_tex(w_2_dot_y)}}}{{{peel_tex(b_2.magnitude_squared())}}}"
            rf" = {peel_tex(x_2)}$"
        ),
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_2 * v_2$.** Subtract $v_2$'s share: $y$ slides back along $v_2$
# (dashed) and lands on $v_1$'s line. The remainder $r = y - x_2 * v_2$ is built from
# $v_1$ alone:

# %%
remainder: Vector = (y - Scalar(x_2) * a_2).simplified()
remainder

# %% [markdown]
# At the plot values:

# %%
at_values(remainder, peel_values)

# %%
P_R: Point = point(coordinates=list(at_values(remainder, peel_values)))
fig_step_2: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_2:
    arrow(
        head=P_A2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(head=P_Y, color=RED, text="$y$")
    dashed_arrow(tail=P_Y, head=P_R, color=BLUE)
    note(
        at=0.5 * (P_Y + P_R),
        text="$-x_2 * v_2$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    arrow(
        head=P_R,
        color=RED,
        text="$r = y - x_2 * v_2$",
        offset=Point(x=0, y=-20),
        align=LabelPos.b,
        width=2.2,
    )
fig_step_2

# %% [markdown]
# **Step 3, read $x_1$.** The one-vector frame $v_1$ is left, and its last orthogonal
# vector $w_1$ is perpendicular to every *other* vector in it (there are none). The
# same rule reads $x_1$:

# %%
x_1: Real = sympy.simplify(
    sympy.sympify((remainder.projected_onto(onto=b_1) / b_1).scalar_part())
)
x_1

# %% [markdown]
# The recovered coordinates $x$:

# %%
x: Vector = Scalar(x_1) * e_1 + Scalar(x_2) * e_2
x

# %% [markdown]
# At the plot values:

# %%
at_values(x, peel_values)

# %% [markdown]
# gacalc's inverse of the frame's map, applied to $y$:

# %%
g: InvertibleFunction[MultiVectorBase] = peel_frame.to_invertible_function()
g.inverse(y).simplified()

# %% [markdown]
# Its difference from the peeled $x$:

# %%
(g.inverse(y) - x).simplified()

# %% [markdown]
# The map sends $x$ back to:

# %%
g(x).simplified()

# %% [markdown]
# Its difference from $y$:

# %%
(g(x) - y).simplified()

# %% [markdown]
# The recovered $x$ (black) is the point $f$ sends to $y$: $x_1 * v_1 + x_2 * v_2$,
# drawn tip to tail in blue, ends on $y$.

# %%
P_X: Point = point(coordinates=list(at_values(x, peel_values)))
fig_step_3: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_3:
    P_X1_A1: Point = point(coordinates=list(at_values(Scalar(x_1) * a_1, peel_values)))
    P_X2_A2: Point = point(coordinates=list(at_values(Scalar(x_2) * a_2, peel_values)))
    arrow(head=P_Y, color=RED, text="$y = f(x)$")
    arrow(
        head=P_X1_A1,
        color=BLUE,
        text="$x_1 * v_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    dashed_arrow(tail=P_X1_A1, head=P_X1_A1 + P_X2_A2, color=BLUE)
    note(
        at=P_X1_A1 + 0.5 * P_X2_A2,
        text="$x_2 * v_2$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    # x can lie along y, so it is drawn after y, thicker, to stay visible
    arrow(head=P_X, text="$x$", offset=Point(x=-6, y=4), align=LabelPos.l, width=3.0)
    note(
        at=Point(x=2.0, y=3.5),
        text=(
            r"$x_1 = \frac{w_1 \cdot r}{|w_1|^2} = "
            rf"\frac{{{peel_tex(b_1.dot(remainder).scalar_part())}}}"
            rf"{{{peel_tex(b_1.magnitude_squared())}}} = {peel_tex(x_1)}$"
        ),
    )
fig_step_3

# %% [markdown]
# ## The round trip, for every input
#
# For a symbolic $x$, `inverse(f) @ f` gives $x$ back unchanged, and `f @ inverse(f)`
# does the same for a symbolic $y$: the peel is exact, with no rounding. A general $x$:

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_1, s_2 = sympy.symbols("x_1 x_2", real=True)
general: Vector = Scalar(s_1) * e_1 + Scalar(s_2) * e_2
general

# %% [markdown]
# $f^{-1}(f(x))$, for the first frame:

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
# $v^2 = w_2 / |w_2|^2$ dots to 0 with $v_1$ and to 1 with $v_2$: it reads $x_2$ in a
# single dot product, which is exactly step 1. The whole reciprocal frame, one such
# vector per coordinate, comes from Hestenes and is a separate chapter. $v^2$:

# %%
reciprocal_2: MultiVectorBase = (b_2 / b_2.magnitude_squared()).simplified()
reciprocal_2

# %% [markdown]
# $v^2 \cdot v_1$:

# %%
sympy.simplify(sympy.sympify(reciprocal_2.dot(a_1).scalar_part()))

# %% [markdown]
# $v^2 \cdot v_2$:

# %%
sympy.simplify(sympy.sympify(reciprocal_2.dot(a_2).scalar_part()))

# %%
fig_reciprocal: PendingFigure
with scene_2d(
    lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT
) as fig_reciprocal:
    arrow(
        head=P_A1,
        color=BLUE,
        text="$v_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    arrow(
        head=P_A2,
        color=BLUE,
        text="$v_2$",
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    arrow(
        head=point(coordinates=list(at_values(reciprocal_2, peel_values))),
        color=GREEN,
        text=r"$v^2 = \frac{w_2}{|w_2|^2}$",
        offset=Point(x=-6, y=6),
        align=LabelPos.l,
        width=2.4,
    )
    right_angle(corner=ORIGIN2, toward_a=P_A1, toward_b=P_B2, size=0.12)
fig_reciprocal
