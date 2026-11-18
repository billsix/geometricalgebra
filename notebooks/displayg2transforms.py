# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: gacalc
#     language: python
#     name: gacalc
# ---

# %%

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
# 𝒢₂: moving the plane
# ====================
#
# `displaytransforms.py` introduced transforms with the general class `Gn`: translate,
# scale, rotate, and compositions of them. This notebook applies the same transforms
# to the plane's own class, `g2.G`, and draws what they do to graph paper. The point to
# watch: a transform fed a `g2.G` hands back a `g2.G`. The transform takes its basis
# vectors from whatever value it is given, so nothing gets converted to the slower
# general class along the way.

# %%
import math
import warnings
from collections.abc import Callable

import sympy

from gacalc.base import Real
from gacalc.g2 import G
from gacalc.nbplotutils import (
    create_basis,
    create_graphs,
    create_unit_circle,
    create_x_and_y,
    draw_isoceles_triangle,
    draw_right_triangle,
    draw_second_right_triangle,
    plot_multivector,
)
from gacalc.transforms import (
    InvertibleFunction,
    compose,
    compose_intermediate_fns,
    inverse,
    plane_rotation,
    scale_non_uniform,
    translate,
)

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# Bare names for the full-G basis constants, so the code reads like the math.
e_1: G = G.e_1
e_2: G = G.e_2

# %% [markdown]
# The transforms, written as math
# -------------------------------
#
# Each transform shows itself as a formula. A translation by
# $5 * \vec{\mathbf{e}}_1$:

# %%
translate(b=5 * e_1)

# %% [markdown]
# A scale by $5$ along $\vec{\mathbf{e}}_1$ and $6$ along $\vec{\mathbf{e}}_2$:

# %%
scale_non_uniform(5, 6)

# %% [markdown]
# The inverse of a translation is the translation back:

# %%
inverse(translate(b=5 * e_1))

# %% [markdown]
# A rotation needs a plane and an angle. `plane_rotation(e_1, e_2)` fixes the plane of
# $\vec{\mathbf{e}}_1$ and $\vec{\mathbf{e}}_2$ once and hands back a function of the
# angle; a positive angle turns $\vec{\mathbf{e}}_1$ toward $\vec{\mathbf{e}}_2$.
# Inside, it is the versor sandwich from `displayg2.py`, built from the two vectors,
# with no cosines or sines written by hand.

# %%
rotate: Callable[[Real], InvertibleFunction[G]] = plane_rotation(e_1, e_2)
rotate(sympy.pi / 2)

# %% [markdown]
# Composing two transforms: translate by $5 * \vec{\mathbf{e}}_1 + 6 *
# \vec{\mathbf{e}}_2$, then turn a quarter turn. The formula reads right to left,
# like $f(g(x))$:

# %%
compose([rotate(sympy.pi / 2), translate(b=5 * e_1 + 6 * e_2)])

# %% [markdown]
# Undoing a composition undoes the steps in the reverse order:

# %%
inverse(compose([rotate(sympy.pi / 2), translate(b=5 * e_1 + 6 * e_2)]))

# %% [markdown]
# Does a transform keep the plane's class?
# ----------------------------------------
#
# Take $\vec{\mathbf{w}} = 3 * \vec{\mathbf{e}}_1 + 4 * \vec{\mathbf{e}}_2$:

# %%
w: G = 3 * e_1 + 4 * e_2
w

# %% [markdown]
# A quarter turn sends $(3, 4)$ to $(-4, 3)$. Predict it, then run:

# %%
rotate(sympy.pi / 2)(w)

# %% [markdown]
# The answer is still a `g2.G`, not the general `Gn`:

# %%
type(rotate(sympy.pi / 2)(w)).__name__

# %% [markdown]
# A scale by $2$ along $\vec{\mathbf{e}}_1$ and $3$ along $\vec{\mathbf{e}}_2$:

# %%
scale_non_uniform(2, 3)(w)

# %% [markdown]
# Translate first, then turn:

# %%
compose([rotate(sympy.pi / 2), translate(b=5 * e_1)])(w)

# %% [markdown]
# A transform followed by its inverse is back where it started, so the round trip
# minus $\vec{\mathbf{w}}$ is $0$:

# %%
inverse(rotate(sympy.pi / 2))(rotate(sympy.pi / 2)(w)) - w

# %% [markdown]
# Each part on its own number line
# --------------------------------
#
# `plot_multivector` draws each building block's coefficient on its own number line: a
# plain number, two arrows and a piece of plane, all at once.

# %%
plot_multivector(2 * G.from_real(1) + 3 * e_1 - 1.5 * e_2 + 0.7 * (e_1 * e_2))

# %% [markdown]
# A vector has only its two arrow parts,

# %%
u: G = 3 * e_1 - 1.5 * e_2
plot_multivector(u)

# %% [markdown]
# and so does a second one,

# %%
v: G = 1.5 * e_1 + 5 * e_2
plot_multivector(v)

# %% [markdown]
# but their product has a plain-number part and a piece-of-plane part instead:

# %%
plot_multivector(u * v)

# %% [markdown]
# What does a rotation do to graph paper?
# ---------------------------------------
#
# The graph-paper helpers draw a whole coordinate system through a transform. Passing
# `cls=G` builds the grid, axes and unit circle from `g2.G` values, so the picture is
# drawn with the plane's class end to end. The unit along $x$ is blue and the unit
# along $y$ pink; the numbers on the left and bottom are the original axes. Turned by
# the angle whose cosine is $3/5$:

# %%
fn: InvertibleFunction[G] = rotate(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=fn, cls=G)
    create_x_and_y(fn=fn, cls=G)
    create_unit_circle(fn=fn, cls=G)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Two graph papers at once
# ------------------------
#
# The turned paper (green and yellow) on top of the original (blue and pink). Any point
# can be named in either one; the two right triangles show how the coordinates in one
# paper are made from the other's.

# %%
fn = rotate(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=rotate(0.0), cls=G)
    create_x_and_y(fn=rotate(0.0), cls=G)
    create_basis(fn=fn, xcolor=(0, 1, 0), ycolor=(1, 1, 0), cls=G)
    create_x_and_y(fn=fn, xcolor=(0, 1, 0), ycolor=(1, 1, 0), cls=G)
    create_unit_circle(fn=fn, cls=G)
    draw_right_triangle(cls=G)
    draw_second_right_triangle(cls=G)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Graph paper from a composition
# ------------------------------
#
# Translate by $2 * \vec{\mathbf{e}}_1$, then turn an eighth of a turn:

# %%
fn = compose([rotate(sympy.pi / 4), translate(b=2 * e_1)])
with create_graphs() as axes:
    create_basis(fn=fn, cls=G)
    create_x_and_y(fn=fn, cls=G)
    create_unit_circle(fn=fn, cls=G)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Two ways to read a composition
# ------------------------------
#
# **Bottom up**, in the order the steps are applied, each measured against the
# original axes: first the translation, then the turn.

# %%
f: InvertibleFunction[G]
for f in compose_intermediate_fns([rotate(sympy.pi / 4), translate(b=2 * e_1)]):
    with create_graphs() as axes:
        create_basis(fn=f, cls=G)
        create_x_and_y(fn=f, cls=G)
        create_x_and_y(cls=G)
        draw_isoceles_triangle(fn=f, cls=G)
        create_unit_circle(fn=f, cls=G)
        create_unit_circle(cls=G)
        axes.set_title(f._repr_latex_())

# %% [markdown]
# **Top down**, each step measured against the paper the step before it made: first
# the turn, then the translation along the turned paper. Both readings end at the same
# picture.

# %%
for f in compose_intermediate_fns(
    [rotate(sympy.pi / 4), translate(b=2 * e_1)], relative_basis=True
):
    with create_graphs() as axes:
        create_basis(fn=f, cls=G)
        create_x_and_y(fn=f, cls=G)
        draw_isoceles_triangle(fn=f, cls=G)
        create_unit_circle(fn=f, cls=G)
        axes.set_title(f._repr_latex_())
