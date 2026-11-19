# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Projection in space, one plane at a time — calculations
#
# Companion to the *Proof: Projection in Space, One Plane at a Time* chapter. In the
# plane, projecting $\vec{\mathbf{a}}$ onto $\vec{\mathbf{b}}$ took one rotation: turn
# $\vec{\mathbf{b}}$ onto the x-axis, keep the x-coordinate, turn back. In space one
# rotation is not enough, so the construction turns one plane at a time: first the
# $xy$-shadow of $\vec{\mathbf{b}}$ onto the x-axis, then the $z$-part down. This
# notebook works each step with symbolic coordinates, so every result is a formula for
# every $\vec{\mathbf{a}}$ and every nonzero $\vec{\mathbf{b}}$, and checks that the
# result is the projection and that projection and rejection add back to
# $\vec{\mathbf{a}}$. Numbers appear only to draw the figures. The Lean theorems are
# `projectSP_eq_proj` and `rejectSP_eq_reject` in
# `proofs/GacalcProofs/StandardPosition.lean`.

# %%
import sympy

from gacalc import g2
from gacalc.base import Real
from gacalc.epixscene.frame_scene import (
    BLUE,
    GREEN,
    ORIGIN3,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    note,
    point,
    scene_3d,
)
from gacalc.functions import InvertibleFunction, inverse
from gacalc.g3 import Scalar, Vector, e_1, e_2, e_3
from gacalc.nbdisplay import at_values
from gacalc.standardposition import in_plane, rotation_from_to

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2 + Scalar(a_3) * e_3
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2 + Scalar(b_3) * e_3
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (a_1, 1),
    (a_2, 3),
    (a_3, 3),
    (b_1, 2),
    (b_2, 1),
    (b_3, 2),
]
LOWER_LEFT: Point = Point(x=-2.6, y=-2.2)
UPPER_RIGHT: Point = Point(x=5.4, y=3.6)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_given:
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, text=r"$\vec{\mathbf{b}}$")
fig_given

# %% [markdown]
# ## Step 1: swing $\vec{\mathbf{b}}$'s shadow in the $\mathbf{e}_{12}$ plane onto the x-axis
#
# Each turn is the rotation from one direction to another of *Proof: Rotate from the
# Direction of a to the Direction of b* (`rotation_from_to`), applied in one coordinate
# plane by `in_plane(rotation, first, second, v)`, which leaves the third coordinate
# alone. The first is the rotation from $\vec{\mathbf{b}}$'s shadow
# $b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2$ to $\vec{\mathbf{e}}_1$:

# %%
R_xy: InvertibleFunction[g2.Vector] = rotation_from_to(
    g2.Scalar(b_1) * g2.e_1 + g2.Scalar(b_2) * g2.e_2, g2.e_1
)
R_xy

# %% [markdown]
# It leaves $\vec{\mathbf{b}}$ in the $\mathbf{e}_{13}$ plane, at
# $k * \vec{\mathbf{e}}_1 + b_3 * \vec{\mathbf{e}}_3$ with $k$ the length of the shadow:

# %%
b_step_1: Vector = in_plane(R_xy, e_1, e_2, b).simplified()
b_step_1

# %% [markdown]
# ## Step 2: swing $\vec{\mathbf{b}}$ down onto $\vec{\mathbf{e}}_1$
#
# The rotation, in the $\mathbf{e}_{13}$ plane, from $\vec{\mathbf{b}}$'s new direction
# to $\vec{\mathbf{e}}_1$:

# %%
R_xz: InvertibleFunction[g2.Vector] = rotation_from_to(
    g2.Scalar(b_step_1.coefficient(e_1)) * g2.e_1
    + g2.Scalar(b_step_1.coefficient(e_3)) * g2.e_2,
    g2.e_1,
)
R_xz


# %% [markdown]
# The two turns together, applied to any vector:


# %%
def align(v: Vector) -> Vector:
    """Steps 1 and 2: the two turns that put ``b`` on ``e_1``."""
    return in_plane(R_xz, e_1, e_3, in_plane(R_xy, e_1, e_2, v))


# %% [markdown]
# $\vec{\mathbf{b}}$ lands on $\vec{\mathbf{e}}_1$ at its length $|\vec{\mathbf{b}}|$:

# %%
b_aligned: Vector = align(b).simplified()
b_aligned

# %% [markdown]
# and $\vec{\mathbf{a}}$ rides along to $\vec{\mathbf{a}}'$:

# %%
a_aligned: Vector = align(a).simplified()
a_aligned

# %% [markdown]
# At the plot values, $\vec{\mathbf{b}}$ on $\vec{\mathbf{e}}_1$:

# %%
at_values(b_aligned, values)

# %% [markdown]
# and $\vec{\mathbf{a}}'$:

# %%
at_values(a_aligned, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_ALIGNED: Point = point(coordinates=list(at_values(a_aligned, values)))
P_B_ALIGNED: Point = point(coordinates=list(at_values(b_aligned, values)))
fig_aligned: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_aligned:
    dashed_arrow(tail=ORIGIN3, head=P_A, text=r"$\vec{\mathbf{a}}$")
    dashed_arrow(tail=ORIGIN3, head=P_B, text=r"$\vec{\mathbf{b}}$")
    arrow(head=P_A_ALIGNED, text=r"$\vec{\mathbf{a}}'$")
    arrow(
        head=P_B_ALIGNED,
        text=r"$|\vec{\mathbf{b}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
    )
fig_aligned

# %% [markdown]
# ## Step 3: on the x-axis, keep the x-coordinate
#
# Projecting onto $\vec{\mathbf{e}}_1$ keeps $\vec{\mathbf{a}}'$'s x-coordinate,
# $x * \vec{\mathbf{e}}_1$; the rest, the $\vec{\mathbf{e}}_2$ and $\vec{\mathbf{e}}_3$
# parts, is the rejection there:

# %%
x_part: Vector = (Scalar(a_aligned.coefficient(e_1)) * e_1).simplified()
x_part

# %% [markdown]
# and the part across it:

# %%
across_part: Vector = (
    Scalar(a_aligned.coefficient(e_2)) * e_2 + Scalar(a_aligned.coefficient(e_3)) * e_3
)
across_part

# %% [markdown]
# At the plot values, $x * \vec{\mathbf{e}}_1$:

# %%
at_values(x_part, values)

# %% [markdown]
# and the rest:

# %%
at_values(across_part, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_X: Point = point(coordinates=list(at_values(x_part, values)))
fig_keep_x: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_keep_x:
    arrow(head=P_A_ALIGNED, text=r"$\vec{\mathbf{a}}'$")
    arrow(
        head=P_X,
        color=GREEN,
        width=2.4,
        text=r"$x * \vec{\mathbf{e}}_1$",
        offset=Point(x=-4, y=-10),
        align=LabelPos.bl,
    )
    arrow(head=P_A_ALIGNED, tail=P_X, color=BLUE)
fig_keep_x

# %% [markdown]
# ## Step 4: rotate back
#
# Undo the two turns in reverse order, each by its inverse:


# %%
def rotate_back(v: Vector) -> Vector:
    """Undo steps 2 and 1, in that order."""
    return in_plane(inverse(R_xy), e_1, e_2, in_plane(inverse(R_xz), e_1, e_3, v))


# %% [markdown]
# The kept x-coordinate goes back to the projection of $\vec{\mathbf{a}}$ onto
# $\vec{\mathbf{b}}$:

# %%
projection: Vector = rotate_back(x_part).simplified()
projection

# %% [markdown]
# and the rest to the rejection:

# %%
rejection: Vector = rotate_back(across_part).simplified()
rejection

# %% [markdown]
# At the plot values, the projection:

# %%
at_values(projection, values)

# %% [markdown]
# and the rejection:

# %%
at_values(rejection, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_PROJECTION: Point = point(coordinates=list(at_values(projection, values)))
fig_back: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_back:
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$")
    arrow(
        head=P_PROJECTION,
        color=GREEN,
        width=2.4,
        text=r"$\operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
    )
    arrow(head=P_B, text=r"$\vec{\mathbf{b}}$", align=LabelPos.b)
    arrow(head=P_A, tail=P_PROJECTION, color=BLUE)
    note(
        at=0.5 * (P_PROJECTION + P_A),
        text=r"$\operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        color=BLUE,
        offset=Point(x=6, y=0),
        align=LabelPos.r,
    )
fig_back

# %% [markdown]
# ## Checks, for every $\vec{\mathbf{a}}$ and every nonzero $\vec{\mathbf{b}}$
#
# ### The construction is the projection
#
# The construction gave:

# %%
projection

# %% [markdown]
# The projection
# $\operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) = (\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}) * \vec{\mathbf{b}}^{-1}$
# is:

# %%
a.projected_onto(b).simplified()

# %% [markdown]
# Their difference:

# %%
(projection - a.projected_onto(b)).simplified()

# %% [markdown]
# ### The projection plus the rejection is $\vec{\mathbf{a}}$
#
# The sum:

# %%
(projection + rejection).simplified()

# %% [markdown]
# and $\vec{\mathbf{a}}$:

# %%
a

# %% [markdown]
# Their difference:

# %%
(projection + rejection - a).simplified()
