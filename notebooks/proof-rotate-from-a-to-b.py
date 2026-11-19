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
# # Rotate from a to b — calculations
#
# Companion to the *Proof: Rotate from the Direction of a to the Direction of b*
# chapter. In precalculus, rotating by $\theta_1$ and then by $\theta_2$ is rotating by
# $\theta_1 + \theta_2$: the angles add. The chapter builds a rotation from
# $\vec{\mathbf{a}}$'s direction to $\vec{\mathbf{b}}$'s in three turns and uses that
# fact to collapse them into one. This notebook works each step with the coordinates
# left as symbols, so every result is a formula that holds for every vector and every
# angle:
#
# 1. **2D rotations commute**, which lets the three turns collapse to the middle one;
# 2. **the three turns are one rotation**, whose cosine and sine are read off the
#    coordinates of $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$; and
# 3. **that rotation carries $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$'s direction**.
#
# Only the rotation of *Proof: Rotate* is used, no dot product and no geometric product.
# Numbers appear only to draw the figures. Each check shows both sides, then their
# difference.

# %%
import sympy

from gacalc.base import Real
from gacalc.epixscene.bootstrap_live import (
    BLACK,
    BLUE,
    GREEN,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    dashed_arrow,
    point,
    scene_around,
)
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values

# %% [markdown]
# ## 1. Rotations commute (in 2D)
#
# A general vector $\vec{\mathbf{v}}$, every coordinate a symbol, and two angles:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
theta_1: sympy.Symbol
theta_2: sympy.Symbol
v_1, v_2, theta_1, theta_2 = sympy.symbols("v_1 v_2 theta_1 theta_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# The values used to draw the figures in this section. Change them and rerun.

# %%
values_v: list[tuple[sympy.Symbol, Real]] = [
    (v_1, 2),
    (v_2, 1),
    (theta_1, sympy.pi / 6),
    (theta_2, sympy.pi / 3),
]

# %% [markdown]
# The rotation of *Proof: Rotate* is `Vector.rotate`,
# $r(\vec{\mathbf{v}}; \theta) = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * r(\vec{\mathbf{v}}; \pi/2)$.
# Rotate by $\theta_1$, then by $\theta_2$:

# %%
first_then_second: Vector = v.rotate(theta_1).rotate(theta_2).simplified()
first_then_second

# %% [markdown]
# and in the other order:

# %%
second_then_first: Vector = v.rotate(theta_2).rotate(theta_1).simplified()
second_then_first

# %% [markdown]
# Their difference:

# %%
(first_then_second - second_then_first).simplified()

# %% [markdown]
# Each order is the single rotation by $\theta_1 + \theta_2$:

# %%
v.rotate(theta_1 + theta_2).simplified()

# %% [markdown]
# The difference from the first order:

# %%
(first_then_second - v.rotate(theta_1 + theta_2)).simplified()

# %% [markdown]
# Drawn at the plot values: $\vec{\mathbf{v}}$ turned by $\theta_1$ first (green) or by
# $\theta_2$ first (blue), and both orders landing on the same vector (purple).

# %%
P_V: Point = point(coordinates=list(at_values(v, values_v)))
P_AFTER_1: Point = point(coordinates=list(at_values(v.rotate(theta_1), values_v)))
P_AFTER_2: Point = point(coordinates=list(at_values(v.rotate(theta_2), values_v)))
P_BOTH: Point = point(coordinates=list(at_values(first_then_second, values_v)))
fig_commute: PendingFigure
with scene_around(points=[P_V, P_AFTER_1, P_AFTER_2, P_BOTH]) as fig_commute:
    arrow(head=P_V, color=BLACK, text=r"$\vec{\mathbf{v}}$")
    arrow(
        head=P_BOTH,
        color=PURPLE,
        text=r"$r(r(\vec{\mathbf{v}};\theta_1);\theta_2)$",
        align=LabelPos.l,
    )
    dashed_arrow(
        tail=Point(x=0, y=0),
        head=P_AFTER_1,
        color=GREEN,
        text=r"$r(\vec{\mathbf{v}};\theta_1)$",
    )
    dashed_arrow(
        tail=Point(x=0, y=0),
        head=P_AFTER_2,
        color=BLUE,
        text=r"$r(\vec{\mathbf{v}};\theta_2)$",
        align=LabelPos.l,
    )
fig_commute

# %% [markdown]
# The chapter's three turns are given not by angles but by a cosine $c$ and a sine $s$
# read off a vector's coordinates, because the point is never to compute an angle. So
# this notebook needs the rotation written with its cosine and sine, the one place it
# defines a rotation of its own; the chapter's result, `rotation_from_to`, is what is
# being built here, so it cannot be used yet.


# %%
def rotate_cs(v: Vector, cos: Real, sin: Real) -> Vector:
    """*Proof: Rotate*'s rotation, given its cosine and sine, not its angle."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


# %% [markdown]
# Two turns given that way commute too, as polynomials in $c_1, s_1, c_2, s_2$, with no
# need for $c^2 + s^2 = 1$. One order:

# %%
c_1: sympy.Symbol
s_1: sympy.Symbol
c_2: sympy.Symbol
s_2: sympy.Symbol
c_1, s_1, c_2, s_2 = sympy.symbols("c_1 s_1 c_2 s_2", real=True)
turns_1_then_2: Vector = rotate_cs(rotate_cs(v, c_1, s_1), c_2, s_2).simplified()
turns_1_then_2

# %% [markdown]
# the other order:

# %%
turns_2_then_1: Vector = rotate_cs(rotate_cs(v, c_2, s_2), c_1, s_1).simplified()
turns_2_then_1

# %% [markdown]
# Their difference:

# %%
(turns_1_then_2 - turns_2_then_1).simplified()

# %% [markdown]
# ## 2. The three turns are one rotation
#
# Now $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures from here on. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
fig_given: PendingFigure
with scene_around(points=[P_A, P_B]) as fig_given:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$")
fig_given

# %% [markdown]
# ### Turn 1: swing $\vec{\mathbf{a}}$ onto the x-axis
#
# The cosine and sine of $R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}$ are read off
# $\vec{\mathbf{a}}$, with $\beta$ the angle of $\vec{\mathbf{a}}$. The cosine,
# $\cos(-\beta) = a_1 / |\vec{\mathbf{a}}|$:

# %%
cos_1: Real = a_1 / a.magnitude()
cos_1

# %% [markdown]
# and the sine, $\sin(-\beta) = -a_2 / |\vec{\mathbf{a}}|$:

# %%
sin_1: Real = -a_2 / a.magnitude()
sin_1

# %% [markdown]
# $R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{a}})$:

# %%
a_on_axis: Vector = rotate_cs(a, cos_1, sin_1).simplified()
a_on_axis

# %% [markdown]
# is $|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$:

# %%
Scalar(a.magnitude()) * e_1

# %% [markdown]
# Their difference:

# %%
(a_on_axis - Scalar(a.magnitude()) * e_1).simplified()

# %% [markdown]
# $\vec{\mathbf{b}}$ rides along to
# $\vec{\mathbf{b}}' = R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}})$:

# %%
b_prime: Vector = rotate_cs(b, cos_1, sin_1).simplified()
b_prime

# %% [markdown]
# At the plot values, $|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$:

# %%
at_values(a_on_axis, values)

# %% [markdown]
# and $\vec{\mathbf{b}}'$:

# %%
at_values(b_prime, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_ON_AXIS: Point = point(coordinates=list(at_values(a_on_axis, values)))
P_B_PRIME: Point = point(coordinates=list(at_values(b_prime, values)))
fig_turn_1: PendingFigure
with scene_around(points=[P_A, P_B, P_A_ON_AXIS, P_B_PRIME]) as fig_turn_1:
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$"
    )
    dashed_arrow(
        tail=Point(x=0, y=0), head=P_B, color=BLACK, text=r"$\vec{\mathbf{b}}$"
    )
    arrow(
        head=P_A_ON_AXIS,
        color=BLACK,
        text=r"$|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=-6, y=-8),
        align=LabelPos.bl,
    )
    arrow(head=P_B_PRIME, color=BLACK, text=r"$\vec{\mathbf{b}}'$")
fig_turn_1

# %% [markdown]
# ### Turn 2: in standard position, turn $\vec{\mathbf{e}}_1$ onto $\vec{\mathbf{b}}'$
#
# The cosine and sine of $R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'}$ are read off
# $\vec{\mathbf{b}}'$. Rotations keep lengths, so
# $|\vec{\mathbf{b}}'| = |\vec{\mathbf{b}}|$. The cosine:

# %%
cos_2: Real = b_prime.coefficient(e_1) / b.magnitude()
cos_2

# %% [markdown]
# and the sine:

# %%
sin_2: Real = b_prime.coefficient(e_2) / b.magnitude()
sin_2

# %% [markdown]
# Turn 2 carries $|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$ onto $\vec{\mathbf{b}}'$'s
# direction:

# %%
a_turned: Vector = rotate_cs(a_on_axis, cos_2, sin_2).simplified()
a_turned

# %% [markdown]
# At the plot values:

# %%
at_values(a_turned, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_TURNED: Point = point(coordinates=list(at_values(a_turned, values)))
fig_turn_2: PendingFigure
with scene_around(points=[P_A_ON_AXIS, P_B_PRIME, P_A_TURNED]) as fig_turn_2:
    arrow(
        head=P_A_ON_AXIS,
        color=BLACK,
        text=r"$|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1$",
        offset=Point(x=-6, y=-8),
        align=LabelPos.bl,
    )
    arrow(
        head=P_A_TURNED,
        color=PURPLE,
        text=r"$R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'}(|\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1)$",
        align=LabelPos.l,
    )
    arrow(
        head=P_B_PRIME,
        color=BLACK,
        text=r"$\vec{\mathbf{b}}'$",
        offset=Point(x=8, y=-6),
        align=LabelPos.br,
    )
fig_turn_2

# %% [markdown]
# ### Turn 3: undo turn 1
#
# $(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1})^{-1}$ has the same cosine and the sine
# negated. The three turns, applied to the general $\vec{\mathbf{v}}$:

# %%
three_turns: Vector = rotate_cs(
    rotate_cs(rotate_cs(v, cos_1, sin_1), cos_2, sin_2), cos_1, -sin_1
).simplified()
three_turns

# %% [markdown]
# Applied to $\vec{\mathbf{a}}$, they land on $\vec{\mathbf{b}}$'s direction (purple):

# %%
a_image: Vector = rotate_cs(a_turned, cos_1, -sin_1).simplified()
a_image

# %% [markdown]
# At the plot values:

# %%
at_values(a_image, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A_IMAGE: Point = point(coordinates=list(at_values(a_image, values)))
fig_turn_3: PendingFigure
with scene_around(points=[P_A, P_B, P_A_IMAGE]) as fig_turn_3:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(
        head=P_A_IMAGE,
        color=PURPLE,
        text=r"$R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
        align=LabelPos.l,
    )
    arrow(
        head=P_B,
        color=BLACK,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=8, y=-6),
        align=LabelPos.br,
    )
fig_turn_3

# %% [markdown]
# ### The collapse
#
# The chapter's single rotation has its cosine and sine written in the coordinates of
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$. The cosine,
# $(a_1 * b_1 + a_2 * b_2) / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$:

# %%
cos_ab: Real = (a_1 * b_1 + a_2 * b_2) / (a.magnitude() * b.magnitude())
cos_ab

# %% [markdown]
# and the sine, $(a_1 * b_2 - a_2 * b_1) / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)$:

# %%
sin_ab: Real = (a_1 * b_2 - a_2 * b_1) / (a.magnitude() * b.magnitude())
sin_ab

# %% [markdown]
# That one rotation, applied to $\vec{\mathbf{v}}$:

# %%
one_turn: Vector = rotate_cs(v, cos_ab, sin_ab).simplified()
one_turn

# %% [markdown]
# The three turns were:

# %%
three_turns

# %% [markdown]
# Their difference:

# %%
(three_turns - one_turn).simplified()

# %% [markdown]
# ## 3. The rotation carries $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$'s direction
#
# Applied to $\vec{\mathbf{a}}$ itself, the single rotation gives:

# %%
a_rotated: Vector = rotate_cs(a, cos_ab, sin_ab).simplified()
a_rotated

# %% [markdown]
# $\vec{\mathbf{b}}$'s direction with $\vec{\mathbf{a}}$'s own length is
# $(|\vec{\mathbf{a}}| / |\vec{\mathbf{b}}|) * \vec{\mathbf{b}}$:

# %%
a_length_along_b: Vector = (Scalar(a.magnitude() / b.magnitude()) * b).simplified()
a_length_along_b

# %% [markdown]
# Their difference:

# %%
(a_rotated - a_length_along_b).simplified()
