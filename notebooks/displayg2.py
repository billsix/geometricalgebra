# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: geometricalgebra
#     language: python
#     name: geometricalgebra
# ---

# %%

# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# %% [markdown]
# 𝒢₂ — the geometric algebra of the Euclidean plane
# ==================================================
#
# This notebook demonstrates the **specialized `G2` class** (𝒢₂), the
# fast, named-field representation of the geometric algebra of ℝ². It mirrors
# `displaymv.py` (which uses the general `Gn`), but every value here is a `G2`:
# its closed-form geometric product is code-generated from `Gn`, so it is
# provably consistent with the reference while being much faster.
#
# 𝒢₂ has 2² = 4 basis blades: the scalar `1`, the two vectors `e_1`, `e_2`, and
# the bivector / pseudoscalar `e_12 = e_1 e_2`.

# %%
import math
import warnings

import sympy
from IPython.display import Math, display

from geometricalgebra.g2 import (
    G2,
    e_1,
    e_2,
    e_12,
    one,
    zero,
)
from geometricalgebra.nbplotutils import (
    create_basis,
    create_graphs,
    create_unit_circle,
    create_x_and_y,
    draw_isoceles_triangle,
    draw_right_triangle,
    draw_second_right_triangle,
    plot_multivector,
    show_mult,
)
from geometricalgebra.transforms import (
    InvertibleFunction,
    compose,
    compose_intermediate_fns,
    inverse,
    scale_non_uniform,
    translate,
)

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# Basis blades and the unit bivector
# ----------------------------------
#
# The product of the two basis vectors is the unit bivector `e_12`, the
# pseudoscalar of 𝒢₂. It squares to −1 — so it behaves like the imaginary
# unit *i*, and the even subalgebra {scalar, `e_12`} is isomorphic to ℂ.

# %%
i: G2 = e_1 * e_2
i  # pyright: ignore[reportUnusedExpression]

# %%
i * i  # pyright: ignore[reportUnusedExpression]

# %%
# e_12 is the same value as e_1 * e_2
e_12 == e_1 * e_2

# %% [markdown]
# Linear combinations
# -------------------
#
# `G2` values add and scale like vectors; like terms collect automatically.

# %%
2 * e_1 + 3 * e_2 + 5 * e_1  # pyright: ignore[reportUnusedExpression]

# %%
zero, one  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Symbolic vectors
# ----------------
#
# `G2` works symbolically too. `symbolic_multivector` builds a full multivector
# of `sympy` symbols; `r_vector_part(1)` keeps only the grade-1 (vector) part.

# %%
a = G2.symbolic_multivector(prefix="a")
a  # pyright: ignore[reportUnusedExpression]

# %%
a_vec = G2.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec  # pyright: ignore[reportUnusedExpression]

# %%
b_vec = G2.symbolic_multivector(prefix="b").r_vector_part(1)
b_vec  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The geometric product of two vectors
# ------------------------------------
#
# For vectors *a* and *b*, the geometric product splits into a symmetric scalar
# part (the dot product) and an antisymmetric bivector part (the wedge):
#
# $$ ab = a\cdot b + a\wedge b $$

# %%
a_vec * b_vec  # pyright: ignore[reportUnusedExpression]

# %%
a_vec.dot(b_vec)

# %%
a_vec.wedge(b_vec)

# %%
# `^` is the wedge (outer) product operator
a_vec ^ b_vec  # pyright: ignore[reportUnusedExpression]

# %%
# dot + wedge reconstructs the full geometric product
a_vec.dot(b_vec) + a_vec.wedge(b_vec) == a_vec * b_vec

# %% [markdown]
# Distributing a full product
# ---------------------------
#
# `show_mult` expands the product of two general multivectors term by term.

# %%
g2_1 = G2.symbolic_multivector(prefix="a")
g2_2 = G2.symbolic_multivector(prefix="b")
show_mult(g2_1, g2_2)

# %% [markdown]
# Associativity
# -------------
#
# The geometric product is associative: $(g_1 g_2) g_3 = g_1 (g_2 g_3)$, so
# their difference is zero.

# %%
g2_3 = G2.symbolic_multivector(prefix="c")
((g2_1 * g2_2) * g2_3) - (g2_1 * (g2_2 * g2_3))

# %% [markdown]
# Grade projection
# ----------------
#
# `r_vector_part(r)` extracts the grade-*r* part: scalars (0), vectors (1),
# bivectors (2).

# %%
c = G2.symbolic_multivector(prefix="c")
c.r_vector_part(0)

# %%
c.r_vector_part(1)

# %%
c.r_vector_part(2)

# %% [markdown]
# The basis of 𝒢₂
# ---------------
#
# All 2² = 4 basis blades, in grade order.

# %%
for x in G2.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Magnitude, inverse, reverse, dual
# ---------------------------------
#
# A vector squares to its magnitude squared, so its inverse is itself over that
# magnitude. The reverse $\tilde{A}$ flips the order of the basis vectors in
# each blade; the dual multiplies by the inverse pseudoscalar.

# %%
m = 3 * e_1 + 4 * e_2
m.magnitude()

# %%
m * m  # pyright: ignore[reportUnusedExpression]

# %%
m.normalize()

# %%
m.inverse()

# %%
m * m.inverse() == one

# %%
# reverse of the bivector negates it
i.reverse()

# %%
# the dual rotates a vector by the pseudoscalar
m.dual()

# %% [markdown]
# An applied example: unit conversion as a vector
# -----------------------------------------------
#
# Treating "grams of Fe" as the e_1 axis and "moles of Fe" as the e_2 axis, a
# conversion factor is just the geometric product with a ratio built from the
# two units' inverses. Everything stays a `G2`.


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> G2:
    unit_gram_fe: G2 = e_1
    unit_mol_fe: G2 = e_2

    ratio: G2 = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)

# %% [markdown]
# Transforms
# ----------
#
# The transform layer (`translate`, `scale_non_uniform`, `compose`, ...) is
# **representation preserving**: applied to a `G2`, it returns a `G2`.  Each
# factory builds an `InvertibleFunction` that renders its own LaTeX.
#
# Rotation in geometric algebra is the rotor sandwich `R v R.inverse()`.  Here
# `rotate(angle)` takes the unit vector `to` at `angle` from `e_1` and uses
# `rotor_from_vectors` (the half-angle rotor carrying `e_1 -> to`), wrapped as an
# `InvertibleFunction` so it composes / inverts like the other transforms.


# %%
def rotate(angle):
    """Planar rotation by `angle` (positive turns e_1 toward e_2), built the
    geometric-algebra way: take the unit vector `to` at `angle` from e_1, form the
    half-angle rotor carrying e_1 -> to with `rotor_from_vectors`, and sandwich it.
    """
    to = sympy.cos(angle) * e_1 + sympy.sin(angle) * e_2
    R = G2.rotor_from_vectors(from_vector=e_1, to_vector=to)
    return InvertibleFunction(
        lambda v: R * v * R.inverse(),
        lambda v: R.inverse() * v * R,
        f"R_{{{sympy.latex(angle)}}}",
        f"R_{{{sympy.latex(-angle)}}}",
    )


# %%
translate(5 * e_1)

# %%
# `scale_non_uniform` is the n-D scale (pass two factors for the 2D case)
scale_non_uniform(5, 6)

# %%
inverse(translate(5 * e_1))

# %%
translate(5 * e_1 + 6 * e_2)

# %%
rotate(sympy.pi / 2)

# %%
compose([rotate(sympy.pi / 2), translate(5 * e_1 + 6 * e_2)])

# %%
inverse(compose([rotate(sympy.pi / 2), translate(5 * e_1 + 6 * e_2)]))

# %% [markdown]
# Applying transforms to a `G2` vector
# ------------------------------------
#
# This is what the representation-preserving work buys us: feeding a `G2` vector
# through a transform yields a `G2` vector (not a coerced general `Gn`).

# %%
w = 3 * e_1 + 4 * e_2
w  # pyright: ignore[reportUnusedExpression]

# %%
# a 90 degree rotation in the e_1 e_2 plane: 3 e_1 + 4 e_2  ->  -4 e_1 + 3 e_2
rotate(sympy.pi / 2)(w)  # pyright: ignore[reportUnusedExpression]

# %%
# the result is still a G2, not a Gn
type(rotate(sympy.pi / 2)(w)).__name__

# %%
# non-uniform scale: stretch e_1 by 2, e_2 by 3
scale_non_uniform(2, 3)(w)  # pyright: ignore[reportUnusedExpression]

# %%
# compose: translate first, then rotate (read right-to-left)
compose([rotate(sympy.pi / 2), translate(5 * e_1)])(w)  # pyright: ignore[reportUnusedExpression]

# %%
# a transform and its inverse round-trip back to the original vector
inverse(rotate(sympy.pi / 2))(rotate(sympy.pi / 2)(w)) == w

# %% [markdown]
# Plotting a multivector
# ----------------------
#
# `plot_multivector` draws each blade's coefficient on its own number line. It
# accepts any representation — here, `G2` values.

# %%
plot_multivector(2 * one + 3 * e_1 - 1.5 * e_2 + 0.7 * (e_1 * e_2))

# %%
u = 3 * e_1 - 1.5 * e_2
plot_multivector(u)

# %%
v = 1.5 * e_1 + 5 * e_2
plot_multivector(v)

# %%
plot_multivector(u * v)

# %% [markdown]
# Graph paper: visualizing transforms in 𝒢₂
# -----------------------------------------
#
# The graph-paper helpers draw a transformed coordinate system. Passing
# `cls=G2` makes them sample entirely in `G2` (rather than the general `Gn`):
# the grid, axes, and unit circle are built from `G2` basis vectors and pushed
# through a `G2`-valued transform.

# %% [markdown]
# Draw graph paper
# ----------------
#
# One unit in the x direction is blue, one unit in the y direction is pink. The
# graph paper corresponds to the numbers on the left and on the bottom.

# %%
fn = rotate(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=fn, cls=G2)
    create_x_and_y(fn=fn, cls=G2)
    create_unit_circle(fn=fn, cls=G2)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Draw relative graph paper
# -------------------------
#
# Draw a rotated graph paper (green/yellow) on top of the original coordinate
# system (blue/pink). Any point can be described in either graph paper.

# %%
fn = rotate(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=rotate(0.0), cls=G2)
    create_x_and_y(fn=rotate(0.0), cls=G2)
    create_basis(fn=fn, xcolor=(0, 1, 0), ycolor=(1, 1, 0), cls=G2)
    create_x_and_y(fn=fn, xcolor=(0, 1, 0), ycolor=(1, 1, 0), cls=G2)
    create_unit_circle(fn=fn, cls=G2)
    draw_right_triangle(cls=G2)
    draw_second_right_triangle(cls=G2)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Relative graph paper, defined by composed functions
# ---------------------------------------------------
#
# A translated and rotated graph paper. Read the composed functions in the
# order applied, or in reverse.

# %%
fn = compose(
    [
        rotate(sympy.pi / 4),
        translate(2 * e_1),
    ]
)
with create_graphs() as axes:
    create_basis(fn=fn, cls=G2)
    create_x_and_y(fn=fn, cls=G2)
    create_unit_circle(fn=fn, cls=G2)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Composed functions, read bottom up
# ----------------------------------
#
# The sequence of functions, where the translate is applied first, relative to
# the units on the left and bottom.

# %%
for f in compose_intermediate_fns([rotate(sympy.pi / 4), translate(2 * e_1)]):
    with create_graphs() as axes:
        create_basis(fn=f, cls=G2)
        create_x_and_y(fn=f, cls=G2)
        create_x_and_y(cls=G2)
        draw_isoceles_triangle(fn=f, cls=G2)
        create_unit_circle(fn=f, cls=G2)
        create_unit_circle(cls=G2)
        axes.set_title(f._repr_latex_())

# %% [markdown]
# Composed functions, read top down
# ---------------------------------
#
# The rotate is visualized first, then the translate relative to that relative
# graph paper.

# %%
for f in compose_intermediate_fns(
    [
        rotate(sympy.pi / 4),
        translate(2 * e_1),
    ],
    relative_basis=True,
):
    with create_graphs() as axes:
        create_basis(fn=f, cls=G2)
        create_x_and_y(fn=f, cls=G2)
        draw_isoceles_triangle(fn=f, cls=G2)
        create_unit_circle(fn=f, cls=G2)
        axes.set_title(f._repr_latex_())

# %%
