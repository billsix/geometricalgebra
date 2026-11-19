# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Reflection in space: across a vector, and in a plane — calculations
#
# Companion to *Reflection in Space*. In the plane, the reflection of
# $\vec{\mathbf{v}}$ across the line through $\vec{\mathbf{a}}$ kept the part of
# $\vec{\mathbf{v}}$ along $\vec{\mathbf{a}}$ and flipped the part across:
# the projection minus the rejection. The same definition works in space, and it works
# for a plane as well as a line. This notebook reflects
#
# 1. across the line through a vector $\vec{\mathbf{a}}$;
# 2. in the plane $B = \vec{\mathbf{p}} \wedge \vec{\mathbf{q}}$, like a mirror;
# 3. in the same plane again, but working from the plane's normal, its dual
#    $\vec{\mathbf{n}} = B * I^{-1}$ (chapter *The Dual in Space*).
#
# The last two are computed differently and come out equal, once one sign is
# accounted for. Every coordinate is a symbol; numbers appear only to draw the figures.
# The Lean theorems are `reflectVec_eq` and `reflectPlane_eq_neg_reflectVec_dual`
# (`proofs/GacalcProofs/Reflect.lean`).

# %%
# twin: GacalcProofs.G3.reflectVec_eq
# twin: GacalcProofs.G3.reflectPlane_eq_neg_reflectVec_dual
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _frame_scene import (
    BLUE,
    GREEN,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    patch,
    point,
    scene_3d,
)

from gacalc.base import Real
from gacalc.g3 import Bivector, Scalar, Vector, e_1, e_2, e_3
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## The vector to reflect
#
# $\vec{\mathbf{v}}$, every coordinate a symbol:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_3: sympy.Symbol
v_1, v_2, v_3 = sympy.symbols("v_1 v_2 v_3", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2 + Scalar(v_3) * e_3
v

# %% [markdown]
# ## 1. Across the line through a vector
#
# The mirror line runs through $\vec{\mathbf{a}}$:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2 + Scalar(a_3) * e_3
a

# %% [markdown]
# Keep the part along $\vec{\mathbf{a}}$, flip the part across:
# $\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{v}}) -
# \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{v}})$. The projection:

# %%
projection_a: Vector = v.projected_onto(a).simplified()
projection_a

# %% [markdown]
# the rejection:

# %%
rejection_a: Vector = v.rejected_away_from(a).simplified()
rejection_a

# %% [markdown]
# and their difference, the reflection:

# %%
across_a: Vector = (projection_a - rejection_a).simplified()
across_a

# %% [markdown]
# gacalc's `reflected_across(a)` gives the same; their difference:

# %%
(v.reflected_across(a) - across_a).simplified()

# %% [markdown]
# As in the plane, it is also one product,
# $\vec{\mathbf{a}} * \vec{\mathbf{v}} * \vec{\mathbf{a}}^{-1}$. Its difference from the
# reflection:

# %%
(a * v * a.inverse() - across_a).simplified()

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (v_1, 1),
    (v_2, 0),
    (v_3, 2),
    (a_1, 2),
    (a_2, 2),
    (a_3, 0),
]
LOWER_LEFT: Point = Point(x=-3.0, y=-2.4)
UPPER_RIGHT: Point = Point(x=4.0, y=3.0)

# %% [markdown]
# Drawn at the plot values: the projection in green, the rejection in blue, and the
# reflection in purple, on the far side of the line.

# %%
P_V: Point = point(coordinates=list(at_values(v, values)))
P_A: Point = point(coordinates=list(at_values(a, values)))
P_PROJECTION_A: Point = point(coordinates=list(at_values(projection_a, values)))
P_ACROSS_A: Point = point(coordinates=list(at_values(across_a, values)))
fig_line: PendingFigure
with scene_3d(lower_left=LOWER_LEFT, upper_right=UPPER_RIGHT) as fig_line:
    dashed_arrow(tail=-1 * P_A, head=P_A)
    arrow(head=P_PROJECTION_A, color=GREEN, width=2.4)
    arrow(head=P_V, tail=P_PROJECTION_A, color=BLUE)
    arrow(head=P_ACROSS_A, tail=P_PROJECTION_A, color=BLUE)
    arrow(head=P_V, text=r"$\vec{\mathbf{v}}$")
    arrow(head=P_A, text=r"$\vec{\mathbf{a}}$", align=LabelPos.b)
    arrow(head=P_ACROSS_A, color=PURPLE, text=r"reflection")
fig_line

# %% [markdown]
# ## 2. In a plane, like a mirror
#
# The plane is $B = \vec{\mathbf{p}} \wedge \vec{\mathbf{q}}$:

# %%
p_1: sympy.Symbol
p_2: sympy.Symbol
p_3: sympy.Symbol
q_1: sympy.Symbol
q_2: sympy.Symbol
q_3: sympy.Symbol
p_1, p_2, p_3, q_1, q_2, q_3 = sympy.symbols("p_1 p_2 p_3 q_1 q_2 q_3", real=True)
p: Vector = Scalar(p_1) * e_1 + Scalar(p_2) * e_2 + Scalar(p_3) * e_3
q: Vector = Scalar(q_1) * e_1 + Scalar(q_2) * e_2 + Scalar(q_3) * e_3
B: Bivector = (p ^ q).simplified()
B

# %% [markdown]
# A mirror keeps the part of $\vec{\mathbf{v}}$ in the plane and flips the part
# sticking out of it. That is the same recipe as before, projection minus rejection,
# with the plane in place of the line. The projection onto the plane:

# %%
projection_plane: Vector = v.projected_onto(B).simplified()
projection_plane

# %% [markdown]
# the rejection from the plane:

# %%
rejection_plane: Vector = v.rejected_away_from(B).simplified()
rejection_plane

# %% [markdown]
# and the mirror image:

# %%
mirror: Vector = (projection_plane - rejection_plane).simplified()
mirror

# %% [markdown]
# gacalc's `reflected_across(B)` gives the same; their difference:

# %%
(v.reflected_across(B) - mirror).simplified()

# %% [markdown]
# Values for $\vec{\mathbf{p}}$ and $\vec{\mathbf{q}}$, so the plane can be drawn: here
# the floor, the $\mathbf{e}_{12}$ plane, so the mirror image of $\vec{\mathbf{v}}$
# points down.

# %%
plane_values: list[tuple[sympy.Symbol, Real]] = [
    *values,
    (p_1, 2),
    (p_2, 0),
    (p_3, 0),
    (q_1, 0),
    (q_2, 2),
    (q_3, 0),
]

# %% [markdown]
# Drawn at the plot values:

# %%
P_P: Point = point(coordinates=list(at_values(p, plane_values)))
P_Q: Point = point(coordinates=list(at_values(q, plane_values)))
P_PROJECTION_B: Point = point(
    coordinates=list(at_values(projection_plane, plane_values))
)
P_IN_B: Point = point(coordinates=list(at_values(mirror, plane_values)))
fig_plane: PendingFigure
with scene_3d(
    lower_left=Point(x=-3.0, y=-3.0), upper_right=Point(x=4.0, y=3.0)
) as fig_plane:
    patch(corners=[-1 * P_P - P_Q, P_P - P_Q, P_P + P_Q, P_Q - P_P])
    arrow(head=P_PROJECTION_B, color=GREEN, width=2.4)
    arrow(head=P_V, tail=P_PROJECTION_B, color=BLUE)
    arrow(head=P_IN_B, tail=P_PROJECTION_B, color=BLUE)
    arrow(head=P_V, text=r"$\vec{\mathbf{v}}$")
    arrow(head=P_IN_B, color=PURPLE, text=r"mirror image")
fig_plane

# %% [markdown]
# ## 3. The same mirror, worked from the normal
#
# The plane's dual is its normal, the vector standing straight out of it:

# %%
n: Vector = B.dual(3).simplified()
n

# %% [markdown]
# Here is the observation that connects the two. The part of $\vec{\mathbf{v}}$
# *sticking out of the plane* is the part *along the normal*, and the part *in the
# plane* is the part *across the normal*:
#
# $$
# \operatorname{rej}_{B}(\vec{\mathbf{v}}) =
# \operatorname{proj}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}}), \qquad
# \operatorname{proj}_{B}(\vec{\mathbf{v}}) =
# \operatorname{rej}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}}).
# $$
#
# The first: the rejection from the plane minus the projection onto the normal is

# %%
(rejection_plane - v.projected_onto(n)).simplified()

# %% [markdown]
# The second: the projection onto the plane minus the rejection from the normal is

# %%
(projection_plane - v.rejected_away_from(n)).simplified()

# %% [markdown]
# So the two roles swap. Reflecting across the normal keeps the part along
# $\vec{\mathbf{n}}$ and flips the part across, which is exactly backwards from the
# mirror. Before reading on, predict: how are the two reflections related?
#
# $$
# \begin{aligned} \text{mirror in } B &= \operatorname{proj}_{B}(\vec{\mathbf{v}}) -
# \operatorname{rej}_{B}(\vec{\mathbf{v}}) && \text{— keep in-plane, flip out-of-plane}
# \\ &= \operatorname{rej}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})
#      - \operatorname{proj}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})
#     && \text{— the roles swap} \\
#   &= -\left(\operatorname{proj}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})
#      - \operatorname{rej}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})\right)
#     && \text{— factor out } -1 \\
#   &= -(\text{reflection across } \vec{\mathbf{n}})
# \end{aligned}
# $$
#
# The reflection across the normal, computed directly:

# %%
across_n: Vector = v.reflected_across(n).simplified()
across_n

# %% [markdown]
# The mirror image plus the reflection across the normal:

# %%
(mirror + across_n).simplified()

# %% [markdown]
# They differ only in sign: the two routes give the same mirror, once the $-1$ is put
# in. Reflecting across a line in space is a half turn about that line, not a mirror,
# and a half turn about the normal followed by turning every vector around (the $-1$)
# is the mirror in the plane.
#
# Drawn at the plot values: the mirror image in purple and the reflection across the
# normal in green, pointing opposite ways.

# %%
P_N: Point = point(coordinates=list(at_values(n, plane_values)))
P_ACROSS_N: Point = point(coordinates=list(at_values(across_n, plane_values)))
fig_normal: PendingFigure
with scene_3d(
    lower_left=Point(x=-3.0, y=-3.0), upper_right=Point(x=4.0, y=4.6)
) as fig_normal:
    patch(corners=[-1 * P_P - P_Q, P_P - P_Q, P_P + P_Q, P_Q - P_P])
    arrow(head=P_N, color=BLUE, text=r"$\vec{\mathbf{n}}$", align=LabelPos.l)
    arrow(head=P_V, text=r"$\vec{\mathbf{v}}$")
    arrow(head=P_IN_B, color=PURPLE, text=r"mirror in $B$")
    arrow(head=P_ACROSS_N, color=GREEN, text=r"across $\vec{\mathbf{n}}$")
fig_normal

# %% [markdown]
# ### With the product
#
# The product form says the same thing. The sandwich by the plane,
# $B * \vec{\mathbf{v}} * B^{-1}$, equals the sandwich by its normal,
# $\vec{\mathbf{n}} * \vec{\mathbf{v}} * \vec{\mathbf{n}}^{-1}$, because
# $B = \vec{\mathbf{n}} * I$ and $I$ commutes with every vector, so the two $I$s
# cancel. Their difference:

# %%
(B * v * B.inverse() - n * v * n.inverse()).simplified()

# %% [markdown]
# Both are the reflection across the normal, and the mirror in the plane is minus
# either one. The mirror image plus $B * \vec{\mathbf{v}} * B^{-1}$:

# %%
(mirror + B * v * B.inverse()).simplified()

# %% [markdown]
# ## Checks, for every $\vec{\mathbf{v}}$ and every plane
#
# ### The mirror keeps the length
#
# The squared length of the mirror image minus that of $\vec{\mathbf{v}}$:

# %%
sympy.simplify(sympy.sympify(mirror.magnitude_squared() - v.magnitude_squared()))

# %% [markdown]
# ### Mirroring twice gives back $\vec{\mathbf{v}}$
#
# The mirror image of the mirror image, minus $\vec{\mathbf{v}}$:

# %%
(mirror.reflected_across(B) - v).simplified()
