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
# Companion to the *Frames and QR* chapter. Each section computes with gacalc's
# `Frame` (`gacalc.frame`), then draws the result with ePiX, live: every figure is
# built in its cell from the numbers gacalc has just computed. The colours are the
# same throughout: the frame $v_i$ is blue, the orthogonal $w_i$ green, the unit
# $u_i$ purple, and the target $y$ and its remainders red.
# The axes are drawn light and unlabelled: here $x$ and $y$ are vectors, the
# coordinates and the target of the frame's map.

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
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g2 import G, Vector, e_1, e_2

# %% [markdown]
# ## A frame and its orthogonal set
#
# Two vectors that are neither perpendicular nor of unit length. `Frame` keeps them
# as they are, and `orthogonal_vectors()` computes the orthogonal set from them:
# $w_1 = v_1$, and $w_2$ is $v_2$ with its part along $v_1$ rejected. The unit
# vectors $u_i = w_i / |w_i|$ (purple, short) are the orthonormal set.

# %%
v_1: Vector = 2 * e_1 + 1 * e_2
v_2: Vector = 1 * e_1 + 2 * e_2
frame: Frame = Frame((v_1, v_2))
w_1: MultiVectorBase
w_2: MultiVectorBase
w_1, w_2 = frame.orthogonal_vectors()
u_1: MultiVectorBase
u_2: MultiVectorBase
u_1, u_2 = frame.orthonormal_vectors()
(w_1, w_2), (u_1, u_2), w_1.dot(w_2).scalar_part()

# %%
P_V1: Point = point(coordinates=list(v_1))
P_V2: Point = point(coordinates=list(v_2))
P_W2: Point = point(coordinates=list(w_2))
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
    P_U1: Point = point(coordinates=list(u_1))
    P_U2: Point = point(coordinates=list(u_2))
    arrow(head=P_U1, color=PURPLE, width=3.0, text="$u_1$", offset=Point(x=4, y=-10))
    arrow(head=P_U2, color=PURPLE, width=3.0, text="$u_2$", offset=Point(x=8, y=0))
fig

# %% [markdown]
# ## The coefficients are shadows
#
# `coefficients()` is the table $(w_j \cdot v_i) / |w_j|^2$: row $i$ says how much of
# each $w_j$ it takes to rebuild $v_i$. It is triangular, because $v_1 = w_1$ uses no
# $w_2$, and its diagonal is all ones, because each $v_i$ is $w_i$ plus a part in the
# earlier directions. The entry below the diagonal is the length of $v_2$'s shadow on
# $w_1$, in units of $|w_1|$.

# %%
table: tuple[tuple[Real, ...], ...] = frame.coefficients()
c_21: Real = table[1][0]
table, v_2 == c_21 * w_1 + 1 * w_2

# %%
P_SHADOW: Point = point(coordinates=list(c_21 * w_1))
fig_shadow: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.0, y=2.6)
) as fig_shadow:
    arrow(head=P_V1, color=BLUE, text="$w_1$", offset=Point(x=6, y=-4))
    arrow(head=P_V2, color=BLUE, text="$v_2$", offset=Point(x=0, y=6))
    arrow(
        head=P_SHADOW,
        color=GREEN,
        text=r"$\frac{4}{5} * w_1$",
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
# magnitude of $v_1 \wedge v_2$.

# %%
base: Real = w_1.magnitude()
height: Real = w_2.magnitude()
area: Real = (v_1 ^ v_2).magnitude()
base, height, sympy.simplify(sympy.sympify(base * height - area)) == 0

# %%
fig_area: PendingFigure
with scene_2d(
    lower_left=Point(x=-1.2, y=-0.6), upper_right=Point(x=3.4, y=3.4)
) as fig_area:
    patch(corners=[ORIGIN2, P_V1, P_V1 + P_V2, P_V2], color=PURPLE_FILL)
    arrow(head=P_V1, color=BLUE, text=r"$|w_1| = \sqrt{5}$", offset=Point(x=6, y=-6))
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
        text=r"$|w_2| = \frac{3}{\sqrt{5}}$",
        color=GREEN,
        offset=Point(x=-6, y=0),
        align=LabelPos.l,
    )
    right_angle(corner=P_SHADOW, toward_a=P_V1, toward_b=P_W2)
    note(at=Point(x=2.1, y=2.0), text=r"area $= |w_1| * |w_2| = 3$")
fig_area

# %% [markdown]
# ## The forward map sends $e_i$ to $v_i$
#
# `to_invertible_function()` is the linear map $f(x) = x_1 * v_1 + x_2 * v_2$: it sends
# $e_1$ to $v_1$ and $e_2$ to $v_2$, so the unit square (gray) lands on the frame's
# parallelogram (purple). Its matrix has the $v_i$ as columns.

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
F: sympy.Matrix = sympy.Matrix(f.to_matrix(G, n=2, backend="sympy"))[:2, :2]
f(1 * e_1 + 0 * e_2) == v_1, f(0 * e_1 + 1 * e_2) == v_2, F

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
# $R = Q^{-1} \circ f$.

# %%
Q: InvertibleFunction[MultiVectorBase] = Frame((u_1, u_2)).to_invertible_function()
R: InvertibleFunction[MultiVectorBase] = inverse(Q) @ f
Q_matrix: sympy.Matrix = sympy.Matrix(Q.to_matrix(G, n=2, backend="sympy"))[:2, :2]
R_matrix: sympy.Matrix = sympy.Matrix(R.to_matrix(G, n=2, backend="sympy"))[
    :2, :2
].applyfunc(sympy.simplify)
R_matrix, Q_matrix, (Q_matrix * R_matrix - F).applyfunc(sympy.simplify).is_zero_matrix

# %%
P_R1: Point = point(coordinates=list(R(1 * e_1 + 0 * e_2)))
P_R2: Point = point(coordinates=list(R(0 * e_1 + 1 * e_2)))
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
        head=point(coordinates=list(u_1)),
        color=PURPLE,
        width=2.6,
        text="$u_1$",
        offset=Point(x=4, y=-8),
    )
    arrow(
        head=point(coordinates=list(u_2)),
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
# last vector. The steps below use the frame from the reference text,
# $v_1 = 2 * e_1$ and $v_2 = 1 * e_1 + 3 * e_2$, with $y = 3 * e_1 + 3 * e_2$, so
# every number is small and exact.

# %%
a_1: Vector = 2 * e_1 + 0 * e_2
a_2: Vector = 1 * e_1 + 3 * e_2
peel_frame: Frame = Frame((a_1, a_2))
b_1: MultiVectorBase
b_2: MultiVectorBase
b_1, b_2 = peel_frame.orthogonal_vectors()
y: Vector = 3 * e_1 + 3 * e_2
g: InvertibleFunction[MultiVectorBase] = peel_frame.to_invertible_function()
(b_1, b_2), b_1.dot(a_2).scalar_part()

# %% [markdown]
# **Step 0, the setup.** The frame (blue) and its parallelogram, the target $y$ (red),
# and the orthogonal set (green): $w_1 = v_1$, and $w_2 = 3 * e_2$ at a right angle to
# $v_1$'s line. $w_2$ is perpendicular to *every other* frame vector, so it can read
# off $x_2$ alone. $w_1$ is not perpendicular to $v_2$ ($w_1 \cdot v_2 = 2$), so
# $w_1 \cdot y$ mixes both coordinates: the peel cannot start with $x_1$.

# %%
P_A1: Point = point(coordinates=list(a_1))
P_A2: Point = point(coordinates=list(a_2))
P_B2: Point = point(coordinates=list(b_2))
P_Y: Point = point(coordinates=list(y))
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
        text=r"$w_2 \cdot v_1 = 0$, but $w_1 \cdot v_2 = 2 \neq 0$",
    )
fig_step_0

# %% [markdown]
# **Step 1, read $x_2$.** Project $y$ onto $w_2$. Every earlier frame vector is
# perpendicular to $w_2$ and drops out, so the projection is $x_2$ copies of $w_2$:
# dividing it by $w_2$ reads $x_2$. The projection's length is $y$'s height above
# $v_1$'s line, and $|w_2|$ is $v_2$'s own height, so $x_2$ is two heights, one
# divided by the other.

# %%
y_onto_w_2: MultiVectorBase = y.projected_onto(onto=b_2)
x_2: Real = (y_onto_w_2 / b_2).scalar_part()
y_onto_w_2, x_2

# %%
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
        text="$|w_2| = 3$",
        offset=Point(x=-6, y=24),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=0),
        color=RED,
        text=r"$\frac{w_2 \cdot y}{|w_2|} = 3$",
        offset=Point(x=6, y=24),
    )
    note(
        at=Point(x=2.0, y=3.5),
        text=r"$x_2 = \frac{w_2 \cdot y}{|w_2|^2} = \frac{9}{9} = 1$",
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_2 * v_2$.** Subtract $v_2$'s share: $y$ slides back along $v_2$
# (dashed) and lands on $v_1$'s line. The remainder $r = y - x_2 * v_2$ is built from
# $v_1$ alone.

# %%
r: Vector = y - x_2 * a_2
r

# %%
P_R: Point = point(coordinates=list(r))
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
# same rule reads $x_1$. The recovered $x$ (black) is the point $f$ sends to $y$:
# $x_1 * v_1 + x_2 * v_2$, drawn tip to tail in blue, ends on $y$.

# %%
x_1: Real = (r.projected_onto(onto=b_1) / b_1).scalar_part()
x: Vector = x_1 * e_1 + x_2 * e_2
x_1, x, g.inverse(y) == x, g(x) == y

# %%
P_X: Point = point(coordinates=list(x))
fig_step_3: PendingFigure
with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_3:
    arrow(
        head=P_A1,
        color=BLUE,
        text="$x_1 * v_1$",
        offset=Point(x=0, y=-8),
        align=LabelPos.b,
    )
    dashed_arrow(tail=P_A1, head=P_A1 + P_A2, color=BLUE)
    note(
        at=P_A1 + 0.5 * P_A2,
        text="$x_2 * v_2$",
        color=BLUE,
        offset=Point(x=8, y=0),
        align=LabelPos.r,
    )
    arrow(head=P_Y, color=RED, text="$y = f(x)$")
    # x lies along y here (y = 3 * x), so it is drawn after y, thicker, to stay visible
    arrow(head=P_X, text="$x$", offset=Point(x=-6, y=4), align=LabelPos.l, width=3.0)
    note(
        at=Point(x=2.0, y=3.5),
        text=r"$x_1 = \frac{w_1 \cdot r}{|w_1|^2} = \frac{4}{4} = 1$",
    )
fig_step_3

# %% [markdown]
# ## The round trip, symbolically
#
# For a symbolic $x$, `inverse(f) @ f` gives $x$ back unchanged, and `f @ inverse(f)`
# does the same for a symbolic $y$: the peel is exact, with no rounding.

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_1, s_2 = sympy.symbols("x_1 x_2", real=True)
symbolic: Vector = s_1 * e_1 + s_2 * e_2
(inverse(f) @ f)(symbolic) == symbolic, (f @ inverse(f))(symbolic) == symbolic

# %% [markdown]
# ## The last reciprocal vector
#
# $v^2 = w_2 / |w_2|^2$ dots to 0 with $v_1$ and to 1 with $v_2$: it reads $x_2$ in a
# single dot product, which is exactly step 1. The whole reciprocal frame, one such
# vector per coordinate, comes from Hestenes and is a separate chapter.

# %%
reciprocal_2: MultiVectorBase = b_2 / b_2.magnitude_squared()
reciprocal_2, reciprocal_2.dot(a_1).scalar_part(), reciprocal_2.dot(a_2).scalar_part()

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
        head=point(coordinates=list(reciprocal_2)),
        color=GREEN,
        text=r"$v^2 = \frac{w_2}{|w_2|^2}$",
        offset=Point(x=-6, y=6),
        align=LabelPos.l,
        width=2.4,
    )
    right_angle(corner=ORIGIN2, toward_a=P_A1, toward_b=P_B2, size=0.12)
fig_reciprocal
