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
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g3 import G, Vector, e_1, e_2, e_3

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
frame: Frame = Frame([v_1, v_2, v_3])
w_1: MultiVectorBase
w_2: MultiVectorBase
w_3: MultiVectorBase
w_1, w_2, w_3 = frame.orthogonal_vectors
(w_1, w_2, w_3), frame.coefficients()

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
lengths: tuple[Real, Real, Real] = (w_1.magnitude(), w_2.magnitude(), w_3.magnitude())
volume: Real = (v_1 ^ v_2 ^ v_3).magnitude()
(
    lengths,
    volume,
    sympy.simplify(sympy.sympify(lengths[0] * lengths[1] * lengths[2] - volume)) == 0,
)

# %%
fig_volume: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_volume:
    patch(corners=[ORIGIN3, P_V1, P_V1 + P_V2, P_V2], color=PLANE_FILL)
    box_edges(a=P_V1, b=P_V2, c=P_V3, color=BLUE, width=0.8)
    dashed_arrow(
        tail=P_V3 + (-1) * P_W3,
        head=P_V3,
        color=GREEN,
        text="$|w_3| = 2$",
        offset=Point(x=-6, y=-10),
        align=LabelPos.l,
    )
    note(at=Point(x=2.2, y=0.5, z=0), text=r"$|w_1| * |w_2| = 4$")
fig_volume

# %% [markdown]
# ## The forward map sends the unit cube to the parallelepiped
#
# $f(x) = x_1 * v_1 + x_2 * v_2 + x_3 * v_3$ sends each $e_i$ to $v_i$, so the unit
# cube (gray) lands on the frame's parallelepiped (blue). Its matrix has the $v_i$ as
# columns.

# %%
f: InvertibleFunction[MultiVectorBase] = frame.to_invertible_function()
sympy.Matrix(f.to_matrix(G, n=3, backend="sympy"))[:3, :3]

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
# Recover $x$ from $y = f(x)$ by peeling the frame from its last vector. This $y$ is
# $v_1 + v_2 + v_3$, so every coordinate should come out 1.

# %%
y: Vector = 4 * e_1 + 3 * e_2 + 2 * e_3
P_Y: Point = point(coordinates=list(y))
y, w_1.dot(v_3).scalar_part(), w_2.dot(v_3).scalar_part()

# %% [markdown]
# **Step 0, the setup.** The plane of $v_1, v_2$ (shaded), $v_3$ leaning over it, and
# the target $y$. $w_3$ is normal to the plane, so it is perpendicular to every frame
# vector but $v_3$: it reads $x_3$ alone. $w_1$ and $w_2$ are not perpendicular to $v_3$
# (the dot products above are 2 and 2), so the peel cannot start with them.

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
# $|w_3|$ is $v_3$'s height, so $x_3$ is two heights, one divided by the other.

# %%
y_onto_w_3: MultiVectorBase = y.projected_onto(onto=w_3)
x_3: Real = (y_onto_w_3 / w_3).scalar_part()
y_onto_w_3, x_3

# %%
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
        text="$|w_3| = 2$",
        offset=Point(x=-6, y=-14),
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=P_Y,
        head=Point(x=P_Y.x1(), y=P_Y.x2(), z=0),
        color=RED,
        text=r"$\frac{w_3 \cdot y}{|w_3|} = 2$",
        offset=Point(x=6, y=-14),
    )
    note(
        at=EQUATION_AT,
        text=r"$x_3 = \frac{w_3 \cdot y}{|w_3|^2} = \frac{4}{4} = 1$",
        align=LabelPos.r,
    )
fig_step_1

# %% [markdown]
# **Step 2, remove $x_3 * v_3$.** $y$ slides back along $v_3$ (dashed) into the plane of
# $v_1, v_2$. What is left is a 2D problem in that plane.

# %%
r_1: Vector = y - x_3 * v_3
P_R1: Point = point(coordinates=list(r_1))
r_1

# %%
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
# normal to $v_1$'s line within the plane, so projecting $r_1$ onto it reads $x_2$;
# removing $x_2 * v_2$ leaves $r_2$ on $v_1$'s line, and projecting $r_2$ onto $w_1$
# reads $x_1$.

# %%
x_2: Real = (r_1.projected_onto(onto=w_2) / w_2).scalar_part()
r_2: Vector = r_1 - x_2 * v_2
x_1: Real = (r_2.projected_onto(onto=w_1) / w_1).scalar_part()
P_R2: Point = point(coordinates=list(r_2))
x_2, r_2, x_1

# %%
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
        text=r"$\frac{w_2 \cdot r_1}{|w_2|} = 2$",
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
            r"$x_2 = \frac{4}{4} = 1, \quad"
            r" x_1 = \frac{w_1 \cdot r_2}{|w_1|^2} = \frac{4}{4} = 1$"
        ),
        align=LabelPos.r,
    )
fig_step_3

# %% [markdown]
# **The result.** The recovered $x$ (black), and the check: $x_1 * v_1 + x_2 * v_2 +
# x_3 * v_3$, tip to tail (blue), ends on $y$.

# %%
x: Vector = x_1 * e_1 + x_2 * e_2 + x_3 * e_3
P_X: Point = point(coordinates=list(x))
x, f.inverse(y) == x, f(x) == y

# %%
fig_result: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_result:
    arrow(head=P_X, text="$x$", offset=Point(x=-4, y=4), align=LabelPos.l, width=2.2)
    arrow(head=P_V1, color=BLUE, text="$x_1 * v_1$", offset=Point(x=4, y=-8))
    dashed_arrow(tail=P_V1, head=P_V1 + P_V2, color=BLUE)
    dashed_arrow(tail=P_V1 + P_V2, head=P_Y, color=BLUE)
    arrow(head=P_Y, color=RED, text="$y = f(x)$")
fig_result

# %% [markdown]
# ## The round trip, symbolically
#
# For a symbolic $x$, `inverse(f) @ f` gives $x$ back unchanged, and `f @ inverse(f)`
# does the same for a symbolic $y$.

# %%
s_1: sympy.Symbol
s_2: sympy.Symbol
s_3: sympy.Symbol
s_1, s_2, s_3 = sympy.symbols("x_1 x_2 x_3", real=True)
symbolic: Vector = s_1 * e_1 + s_2 * e_2 + s_3 * e_3
(inverse(f) @ f)(symbolic) == symbolic, (f @ inverse(f))(symbolic) == symbolic

# %% [markdown]
# ## The last reciprocal vector
#
# $v^3 = w_3 / |w_3|^2$ dots to 0 with $v_1$ and $v_2$ and to 1 with $v_3$: step 1 as a
# single dot product.

# %%
reciprocal_3: MultiVectorBase = w_3 / w_3.magnitude_squared()
(
    reciprocal_3,
    reciprocal_3.dot(v_1).scalar_part(),
    reciprocal_3.dot(v_2).scalar_part(),
    reciprocal_3.dot(v_3).scalar_part(),
)

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
