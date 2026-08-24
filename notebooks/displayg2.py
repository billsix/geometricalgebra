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
# 𝒢₂ — the geometric algebra of the Euclidean plane
# ==================================================
#
# This notebook demonstrates the **specialized `g2.G` class** (𝒢₂), the
# fast, named-field representation of the geometric algebra of ℝ². It mirrors
# `displaymv.py` (which uses the general `Gn`), but every value here is a `g2.G`:
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

from gacalc.base import Coef
from gacalc.g2 import G, Vector
from gacalc.measure import area, signed_area
from gacalc.nbplotutils import (
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
# These are the FULL 𝒢₂ constants (e_1 here is G.e_1) -- not the graded Vector
# that `from gacalc.g2 import e_1` gives; every value in this notebook is a G.
e_1: G = G.e_1
e_2: G = G.e_2
e_12: G = G.e_12

# %% [markdown]
# Basis blades and the unit bivector
# ----------------------------------
#
# The product of the two basis vectors is the unit bivector `e_12`, the
# pseudoscalar of 𝒢₂. It squares to −1 — so it behaves like the imaginary
# unit *i*, and the even subalgebra {scalar, `e_12`} is isomorphic to ℂ.

# %%
i: G = e_1 * e_2
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
# `g2.G` values add and scale like vectors; like terms collect automatically.

# %%
2 * e_1 + 3 * e_2 + 5 * e_1  # pyright: ignore[reportUnusedExpression]

# %%
G.from_scalar(0)  # pyright: ignore[reportUnusedExpression]

# %%
G.from_scalar(1)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Symbolic vectors
# ----------------
#
# `g2.G` works symbolically too. `symbolic_multivector` builds a full multivector
# of `sympy` symbols; `r_vector_part(1)` keeps only the grade-1 (vector) part.

# %%
a: G = G.symbolic_multivector(prefix="a")
a  # pyright: ignore[reportUnusedExpression]

# %%
a_vec: G = G.symbolic_multivector(prefix="a").r_vector_part(1)
a_vec  # pyright: ignore[reportUnusedExpression]

# %%
b_vec: G = G.symbolic_multivector(prefix="b").r_vector_part(1)
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
g2_1: G = G.symbolic_multivector(prefix="a")
g2_2: G = G.symbolic_multivector(prefix="b")
show_mult(g2_1, g2_2)

# %% [markdown]
# Associativity
# -------------
#
# The geometric product is associative: $(g_1 g_2) g_3 = g_1 (g_2 g_3)$, so
# their difference is zero.

# %%
g2_3: G = G.symbolic_multivector(prefix="c")
((g2_1 * g2_2) * g2_3) - (g2_1 * (g2_2 * g2_3))

# %% [markdown]
# Grade projection
# ----------------
#
# `r_vector_part(r)` extracts the grade-*r* part: scalars (0), vectors (1),
# bivectors (2).

# %%
c: G = G.symbolic_multivector(prefix="c")
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
for x in G.bases():
    display(Math(x._repr_latex_()))

# %% [markdown]
# Magnitude, inverse, reverse, dual
# ---------------------------------
#
# A vector squares to its magnitude squared, so its inverse is itself over that
# magnitude. The reverse $\tilde{A}$ flips the order of the basis vectors in
# each blade; the dual multiplies by the inverse pseudoscalar.

# %%
m: G = 3 * e_1 + 4 * e_2
m.magnitude()

# %%
m * m  # pyright: ignore[reportUnusedExpression]

# %%
m.normalize()

# %%
m.inverse()

# %%
m * m.inverse() == G.from_scalar(1)

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
# two units' inverses. Everything stays a `g2.G`.


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> G:
    unit_gram_fe: G = e_1
    unit_mol_fe: G = e_2

    ratio: G = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)

# %% [markdown]
# Transforms
# ----------
#
# The transform layer (`translate`, `scale_non_uniform`, `compose`, ...) is
# **representation preserving**: applied to a `g2.G`, it returns a `g2.G`.  Each
# factory builds an `InvertibleFunction` that renders its own LaTeX.
#
# Rotation in geometric algebra is the rotor sandwich `R v R.inverse()`, and
# `plane_rotation(a, b)` packages it: it wedge-normalizes the two vectors `a`, `b`
# into the unit bivector of their plane once, then returns an
# `angle -> InvertibleFunction` factory (the half-angle rotor is built inside the
# library -- no hand-rolled cos/sin).  So `rotate = plane_rotation(g2.Vector.e_1,
# g2.Vector.e_2)` rotates in the `e_1 e_2` plane (positive `angle` turns `e_1` toward
# `e_2`); each `rotate(angle)` is an `InvertibleFunction` that renders its own LaTeX,
# composes / inverts like the other transforms, and -- via the rotor sandwich --
# preserves the type of whatever it rotates (a `g2.G` stays a `g2.G`).


# %%
rotate = plane_rotation(Vector.e_1, Vector.e_2)


# %%
translate(b=5 * e_1)

# %%
# `scale_non_uniform` is the n-D scale (pass two factors for the 2D case)
scale_non_uniform(5, 6)

# %%
inverse(translate(b=5 * e_1))

# %%
translate(b=5 * e_1 + 6 * e_2)

# %%
rotate(sympy.pi / 2)

# %%
compose([rotate(sympy.pi / 2), translate(b=5 * e_1 + 6 * e_2)])

# %%
inverse(compose([rotate(sympy.pi / 2), translate(b=5 * e_1 + 6 * e_2)]))

# %% [markdown]
# Applying transforms to a `g2.G` vector
# ------------------------------------
#
# This is what the representation-preserving work buys us: feeding a `g2.G` vector
# through a transform yields a `g2.G` vector (not a coerced general `Gn`).

# %%
w: G = 3 * e_1 + 4 * e_2
w  # pyright: ignore[reportUnusedExpression]

# %%
# a 90 degree rotation in the e_1 e_2 plane: 3 e_1 + 4 e_2  ->  -4 e_1 + 3 e_2
rotate(sympy.pi / 2)(w)  # pyright: ignore[reportUnusedExpression]

# %%
# the result is still a g2.G, not a Gn
type(rotate(sympy.pi / 2)(w)).__name__

# %%
# non-uniform scale: stretch e_1 by 2, e_2 by 3
scale_non_uniform(2, 3)(w)  # pyright: ignore[reportUnusedExpression]

# %%
# compose: translate first, then rotate (read right-to-left)
compose([rotate(sympy.pi / 2), translate(b=5 * e_1)])(w)  # pyright: ignore[reportUnusedExpression]

# %%
# a transform and its inverse round-trip back to the original vector
inverse(rotate(sympy.pi / 2))(rotate(sympy.pi / 2)(w)) == w

# %% [markdown]
# Plotting a multivector
# ----------------------
#
# `plot_multivector` draws each blade's coefficient on its own number line. It
# accepts any representation — here, `g2.G` values.

# %%
plot_multivector(2 * G.from_scalar(1) + 3 * e_1 - 1.5 * e_2 + 0.7 * (e_1 * e_2))

# %%
u: G = 3 * e_1 - 1.5 * e_2
plot_multivector(u)

# %%
v: G = 1.5 * e_1 + 5 * e_2
plot_multivector(v)

# %%
plot_multivector(u * v)

# %% [markdown]
# Graph paper: visualizing transforms in 𝒢₂
# -----------------------------------------
#
# The graph-paper helpers draw a transformed coordinate system. Passing
# `cls=g2.G` makes them sample entirely in `g2.G` (rather than the general `Gn`):
# the grid, axes, and unit circle are built from `g2.G` basis vectors and pushed
# through a `g2.G`-valued transform.

# %% [markdown]
# Draw graph paper
# ----------------
#
# One unit in the x direction is blue, one unit in the y direction is pink. The
# graph paper corresponds to the numbers on the left and on the bottom.

# %%
fn: InvertibleFunction = rotate(math.radians(53.130102))
with create_graphs(graph_bounds=(5, 5)) as axes:
    create_basis(fn=fn, cls=G)
    create_x_and_y(fn=fn, cls=G)
    create_unit_circle(fn=fn, cls=G)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Draw relative graph paper
# -------------------------
#
# Draw a rotated graph paper (green/yellow) on top of the original coordinate
# system (blue/pink). Any point can be described in either graph paper.

# %%
fn: InvertibleFunction = rotate(math.radians(53.130102))
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
# Relative graph paper, defined by composed functions
# ---------------------------------------------------
#
# A translated and rotated graph paper. Read the composed functions in the
# order applied, or in reverse.

# %%
fn: InvertibleFunction = compose(
    [
        rotate(sympy.pi / 4),
        translate(b=2 * e_1),
    ]
)
with create_graphs() as axes:
    create_basis(fn=fn, cls=G)
    create_x_and_y(fn=fn, cls=G)
    create_unit_circle(fn=fn, cls=G)
    axes.set_title(fn._repr_latex_())

# %% [markdown]
# Composed functions, read bottom up
# ----------------------------------
#
# The sequence of functions, where the translate is applied first, relative to
# the units on the left and bottom.

# %%
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
# Composed functions, read top down
# ---------------------------------
#
# The rotate is visualized first, then the translate relative to that relative
# graph paper.

# %%
for f in compose_intermediate_fns(
    [
        rotate(sympy.pi / 4),
        translate(b=2 * e_1),
    ],
    relative_basis=True,
):
    with create_graphs() as axes:
        create_basis(fn=f, cls=G)
        create_x_and_y(fn=f, cls=G)
        draw_isoceles_triangle(fn=f, cls=G)
        create_unit_circle(fn=f, cls=G)
        axes.set_title(f._repr_latex_())

# %% [markdown]
# The wedge magnitude: $|a \wedge b| = |a|\,|b|\,\sin\theta$
# =========================================================
#
# For two general vectors $a = a_1 e_1 + a_2 e_2$ and $b = b_1 e_1 + b_2 e_2$ in
# 𝒢₂, the magnitude of the wedge is $|a||b|\sin\theta$. We derive it from the
# identity
#
# $$|a|^2|b|^2 = |a|^2|b|^2\,(\cos^2\theta + \sin^2\theta)$$
#
# together with the definition of the dot product $a\cdot b = |a||b|\cos\theta$.
# (Symbols are declared **real** so that $\sqrt{x^2}=|x|$ behaves.)

# %%
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = a_1 * Vector.e_1 + a_2 * Vector.e_2
b: Vector = b_1 * Vector.e_1 + b_2 * Vector.e_2

# %% [markdown]
# The dot product is a scalar, the wedge is a bivector:

# %%
a.inner_product(b)

# %%
a ^ b

# %% [markdown]
# **The Lagrange step.** Distributing $|a|^2|b|^2(\cos^2\theta + \sin^2\theta)$
# into $(a\cdot b)^2 + |a\wedge b|^2$ gives
#
# $$|a|^2|b|^2 - (a\cdot b)^2 = |a\wedge b|^2 .$$
#
# Symbolically the residual collapses to $0$:

# %%
dot: Coef = a.inner_product(b).scalar_part()
lagrange_residual: Coef = sympy.simplify(
    a.magnitude_squared() * b.magnitude_squared() - dot**2 - (a ^ b).magnitude_squared()
)
lagrange_residual

# %%
assert lagrange_residual == 0

# %% [markdown]
# **From the squared form to the magnitude.** With
# $\cos\theta = a\cdot b / (|a||b|)$ and $\sin\theta = \sqrt{1-\cos^2\theta}\ge 0$
# (taking $\theta\in[0,\pi]$),
#
# $$|a||b|\sin\theta = \sqrt{|a|^2|b|^2 - (a\cdot b)^2}.$$
#
# sympy leaves this as the square root of a *sum*; **factoring the radicand**
# exposes the perfect square $(a_1 b_2 - a_2 b_1)^2$, whose root is $|a\wedge b|$.

# %%
cos: Coef = a.cosine(b)
sin: Coef = sympy.sqrt(1 - cos**2)  # sinθ ≥ 0 for θ in [0, π]
wedge_magnitude_from_sin: Coef = sympy.sqrt(
    sympy.factor(sympy.simplify((a.magnitude() * b.magnitude() * sin) ** 2))
)
wedge_magnitude_from_sin

# %%
(a ^ b).magnitude()

# %%
assert sympy.simplify(wedge_magnitude_from_sin - (a ^ b).magnitude()) == 0

# %% [markdown]
# **Why this matters for rotors.** The geometric product
# $a b = a\cdot b + a\wedge b$ splits into orthogonal grades, so
#
# $$|ab|^2 = (a\cdot b)^2 + |a\wedge b|^2
#          = |a|^2|b|^2(\cos^2\theta + \sin^2\theta) = |a|^2|b|^2 ,$$
#
# i.e. $|ab| = |a||b|$. A rotor built from $a$ and $b$ can therefore take the
# magnitude of the *product* directly instead of multiplying the two magnitudes:

# %%
a * b

# %%
assert (
    sympy.simplify(
        (a * b).magnitude_squared() - a.magnitude_squared() * b.magnitude_squared()
    )
    == 0
)

# %% [markdown]
# The wedge magnitude *is* an area — `area(a, b)`
# -----------------------------------------------
#
# $|a \wedge b| = |a||b|\sin\theta$ is exactly the **area of the parallelogram**
# spanned by `a` and `b` — the high-school area, generalized by geometric algebra
# (Williamson & Trotter call the k-dimensional version the *content*).
# `gacalc.measure.area(a, b)` names it:

# %%
area(a, b)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **`area` is unsigned, so the order of the two sides does not matter** — it is a
# magnitude, $|a \wedge b| = |b \wedge a|$. Swapping `a` and `b` leaves it
# unchanged:

# %%
area(b, a)  # pyright: ignore[reportUnusedExpression]

# %%
area(a, b) == area(b, a)

# %% [markdown]
# **`signed_area` keeps the orientation — it is the 2-D determinant**
# $a_1 b_2 - a_2 b_1$, and **swapping the two vectors flips its sign** (a
# right-handed pair reads positive, a left-handed one negative). The unsigned
# `area` above is exactly its absolute value.

# %%
signed_area(a, b)  # pyright: ignore[reportUnusedExpression]

# %%
signed_area(b, a)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# So switching the order of the first two arguments **negates `signed_area` but
# leaves `area` unchanged** — that swap is precisely how you tell the signed
# measure from the unsigned one:

# %%
signed_area(b, a) == -signed_area(a, b)

# %%
area(a, b) == abs(signed_area(a, b))

# %% [markdown]
# Dot and wedge are the parallel and perpendicular parts of the product
# =====================================================================
#
# Split `a` **relative to `b`** into the part lying **along** `b` (its
# projection $a_\parallel = \operatorname{proj}_b(a)$) and the part
# **perpendicular** to `b` (its rejection $a_\perp = \operatorname{rej}_b(a)$),
# so that $a = a_\parallel + a_\perp$. Multiplying each part by `b` isolates one
# half of the geometric product:
#
# $$ a_\parallel\, b = a\cdot b \qquad\qquad a_\perp\, b = a\wedge b $$
#
# The wedge term drops out of $a_\parallel b$ because $a_\parallel$ is parallel
# to `b` (parallel vectors span no area, so their wedge is zero); the dot term
# drops out of $a_\perp b$ because $a_\perp$ is perpendicular to `b` (their dot
# is zero). Below we pick concrete vectors and **read the coordinates off both
# sides** — they are the same number. The two-line proof (and its symbolic
# verification) is in `tasks/reference/dot-wedge-projection-rejection.md`.

# %%
# Concrete vectors in the plane. b points along the 45° diagonal -- not on an
# axis -- to show the identity does not depend on a convenient choice of b.
a: Vector = 2 * Vector.e_1 + 3 * Vector.e_2
a  # pyright: ignore[reportUnusedExpression]

# %%
b: Vector = Vector.e_1 + Vector.e_2
b  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The projection and the rejection of `a` relative to `b`. Projecting or
# rejecting a vector across a vector stays a `g2.Vector` -- the type reflects that,
# so `a_par` / `a_perp` are `g2.Vector`, not the abstract base. Notice their
# coordinates are *fractions* -- awkward-looking vectors -- yet each one's
# product with `b` collapses to a clean value.

# %%
a_par: Vector = Vector.project(onto=b)(a)
a_par  # pyright: ignore[reportUnusedExpression]

# %%
a_perp: Vector = Vector.reject(away_from=b)(a)
a_perp  # pyright: ignore[reportUnusedExpression]

# %%
# The two parts add back up to a.
a_par + a_perp == a

# %% [markdown]
# **The projection times `b` is the dot product.** Read the coordinate off each
# side: both are the scalar `5`.

# %%
a_par * b  # pyright: ignore[reportUnusedExpression]

# %%
a.dot(b)

# %%
a_par * b == a.dot(b)

# %% [markdown]
# `show_mult` expands the product term by term, so you can watch the two
# `e_12` (bivector) contributions cancel and leave only the scalar:

# %%
show_mult(a_par, b)

# %% [markdown]
# **The rejection times `b` is the wedge product.** Both sides are the bivector
# $-1\,e_{12}$ -- again, the same single coordinate.

# %%
a_perp * b  # pyright: ignore[reportUnusedExpression]

# %%
a.wedge(b)

# %%
a_perp * b == a.wedge(b)

# %% [markdown]
# Here it is the two scalar contributions that cancel, leaving only the
# bivector:

# %%
show_mult(a_perp, b)

# %% [markdown]
# **Putting it back together.** Adding the two products reconstructs the full
# geometric product $ab = a\cdot b + a\wedge b$: the parallel/perpendicular
# split of `a` *is* the scalar/bivector split of `ab`.

# %%
a_par * b + a_perp * b == a * b

# %%
a * b  # pyright: ignore[reportUnusedExpression]

# %%
