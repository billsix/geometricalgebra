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


# %%
import math
import typing

import sympy

from gacalc.base import Real
from gacalc.gn import (
    InvertibleFunction,
    MultiVector,
    compose,
    compose_intermediate_fns,
    e_1,
    e_2,
    e_3,
    inverse,
    plane_rotation,
    scale_non_uniform,
    translate,
)
from gacalc.nbplotutils import (
    create_basis,
    create_graphs,
    create_unit_circle,
    create_x_and_y,
    draw_isoceles_triangle,
    draw_right_triangle,
    draw_second_right_triangle,
)

# %% [markdown]
# Transforms in G_n
# =================
#
# A function from points to points is a *transform*. You know two from algebra:
# $f(x) = x + b$ slides every point by $b$, and $f(x) = m * x$ stretches it. gacalc
# names them `translate` and `scale_non_uniform`, and adds rotations. Each one is an
# *invertible function*: it carries its own inverse, and it prints as math. The
# pictures after them draw a transform as a sheet of graph paper moved by it.
#
# The names used below: $T$ translates, $S$ scales each axis by its own factor, and $R$
# rotates in the $\vec{\mathbf{e}}_1 \vec{\mathbf{e}}_2$ plane, with a positive angle
# turning $\vec{\mathbf{e}}_1$ toward $\vec{\mathbf{e}}_2$.

# %%
rotate: typing.Callable[[Real], InvertibleFunction[MultiVector]] = plane_rotation(
    e_1, e_2
)
T: typing.Callable[[MultiVector], InvertibleFunction[MultiVector]] = translate
S: typing.Callable[..., InvertibleFunction[typing.Any]] = scale_non_uniform
R: typing.Callable[[float], InvertibleFunction[MultiVector]] = rotate

# %% [markdown]
# A translation by $5 * \vec{\mathbf{e}}_1$:

# %%
T(5 * e_1)

# %% [markdown]
# A scale by $5$ along $\vec{\mathbf{e}}_1$ and $6$ along $\vec{\mathbf{e}}_2$:

# %%
S(5, 6)

# %% [markdown]
# The inverse of a translation is the translation back:

# %%
inverse(T(5 * e_1))

# %% [markdown]
# A translation in two dimensions:

# %%
T(5 * e_1 + 6 * e_2)

# %% [markdown]
# In three dimensions,

# %%
T(5 * e_1 + 6 * e_2 + 7 * e_3)

# %% [markdown]
# and its inverse, the translation back:

# %%
inverse(T(5 * e_1 + 6 * e_2 + 7 * e_3))

# %% [markdown]
# A quarter turn:

# %%
R(sympy.pi / 2)

# %% [markdown]
# Composing two transforms: translate, then turn. The composition prints in the order
# the functions are written, as $f \circ g$; the one on the right is applied first.

# %%
compose([R(sympy.pi / 2), T(5 * e_1 + 6 * e_2)])

# %% [markdown]
# The inverse of a composition undoes the steps in the reverse order:

# %%
inverse(compose([R(sympy.pi / 2), T(5 * e_1 + 6 * e_2)]))

# %% [markdown]
# Draw graph paper
# ----------------
#
# Just draw graph paper, where one unit in the x direction is blue,
# and one unit in the y direction is pink.  The graph paper corresponds
# to the numbers on the left and on the bottom.
#
#

# %%
fn: InvertibleFunction[MultiVector] = R(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=fn)
    create_x_and_y(fn=fn)
    create_unit_circle(fn=fn)
    axes.set_title(fn._repr_latex_())


# %% [markdown]
# Draw relative graph paper
# -------------------------
#
# Draw two relative number lines, making a relative graph paper,
# but keep the original coordinate system on the left and bottom.
# Any point in the plane can be described using two different
# graph papers.

# %%
fn: InvertibleFunction[MultiVector] = R(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=R(0.0))
    create_x_and_y(fn=R(0.0))
    create_basis(
        fn=fn,
        xcolor=(0, 1, 0),
        ycolor=(1, 1, 0),
    )
    create_x_and_y(
        fn=fn,
        xcolor=(0, 1, 0),
        ycolor=(1, 1, 0),
    )
    create_unit_circle(fn=fn)
    axes.set_title(fn._repr_latex_())


# %% [markdown]
# Relative graph paper, with its right triangles
# ----------------------------------------------
#
# The same two graph papers. The rotation is by the angle whose cosine is $3/5$ and sine
# $4/5$ (about 53.13 degrees). Two 3-4-5 right triangles are drawn on the original
# paper: the hypotenuse of the first, to $(3, 4)$, lies along the rotated
# $\vec{\mathbf{e}}_1$ axis, and that of the second, to $(-4, 3)$, along the rotated
# $\vec{\mathbf{e}}_2$ axis.

# %%
fn: InvertibleFunction[MultiVector] = R(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=R(0.0))
    create_x_and_y(fn=R(0.0))
    create_basis(
        fn=fn,
        xcolor=(0, 1, 0),
        ycolor=(1, 1, 0),
    )
    create_x_and_y(
        fn=fn,
        xcolor=(0, 1, 0),
        ycolor=(1, 1, 0),
    )
    create_unit_circle(fn=fn)
    draw_right_triangle()
    draw_second_right_triangle()
    axes.set_title(fn._repr_latex_())


# %% [markdown]
# Draw relative graph paper, defined by composed functions
# --------------------------------------------------------
#
# Draw a translated and rotated graph paper.
# You can read the sequence of composed functions
# in the order that they are applied, or in reverse order.
#
# The angle in this cell and the next two is the float
# `math.pi / 4`, not the exact `sympy.pi / 4`: drawing the unit
# circle through a symbolic rotation takes minutes per frame, so
# the titles show $0.785\ldots$ instead.

# %%
fn: InvertibleFunction[MultiVector] = compose(
    [
        R(math.pi / 4),
        T(2 * e_1),
    ]
)
with create_graphs() as axes:
    create_basis(
        fn=fn,
    )
    create_x_and_y(fn=fn)
    create_unit_circle(fn=fn)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Composed functions, read bottom up
# ----------------------------------
#
# The sequence of functions shown, where the translate
# is applied first, and operations are relative to the
# units on the left and bottom.

# %%
f: InvertibleFunction[MultiVector]
for f in compose_intermediate_fns([R(math.pi / 4), T(2 * e_1)]):
    with create_graphs() as axes:
        create_basis(fn=f)
        create_x_and_y(fn=f)
        create_x_and_y()
        draw_isoceles_triangle(fn=f)
        create_unit_circle(fn=f)
        create_unit_circle()
        axes.set_title(f._repr_latex_())

# %% [markdown]
# Composed functions, read top down
# ---------------------------------
#
# The sequence of functions shown, where we visualize
# the rotate first, and then the translate relative to
# that relative graph paper.

# %%
f: InvertibleFunction[MultiVector]
for f in compose_intermediate_fns(
    [
        R(math.pi / 4),
        T(2 * e_1),
    ],
    relative_basis=True,
):
    with create_graphs() as axes:
        create_basis(fn=f)
        create_x_and_y(fn=f)
        draw_isoceles_triangle(fn=f)
        create_unit_circle(fn=f)
        axes.set_title(f._repr_latex_())
