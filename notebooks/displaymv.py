# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
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
import warnings

import sympy
from IPython.display import Math, display

from gacalc.base import MultiVectorFn
from gacalc.gn import (
    InvertibleFunction,
    MultiVector,
    a_1,
    compose,
    compose_intermediate_fns,
    e_1,
    e_2,
    e_3,
    e_4,
    inverse,
    one,
    scale_non_uniform,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
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
    plot_multivector,
    show_mult,
)

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %% [markdown]
# How multiplication works in G_n
# ===============================
#
# You already know how to multiply things like `(x + 2)(x + 3)`: you multiply
# everything by everything and add up the pieces. Multiplying in geometric algebra
# is the *same* idea, with just a couple of new rules for the "letters".
#
# Our letters are the **basis vectors** `e_1`, `e_2`, `e_3`, ... Think of them as
# the arrows pointing along the x-axis, the y-axis, the z-axis, and so on. A general
# object (a *multivector*) is any sum of these, with numbers out front — for example
# `3*e_1 + 4*e_2`. To multiply two multivectors you "FOIL" them out (multiply every
# term by every term) and then clean up using **three rules**:
#
# **Rule 1 — an arrow times itself is 1.** `e_1*e_1 = 1`, `e_2*e_2 = 1`, and so on.
# (Squaring a unit arrow gives you the plain number 1.)

# %%
e_1 * e_1  # -> 1     (Rule 1)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **Rule 2 — swapping two *different* arrows flips the sign.** `e_1*e_2 = -(e_2*e_1)`.
# So order matters here, unlike with ordinary numbers where `3*5 = 5*3`. The combo
# `e_1*e_2` is a brand-new object (a little piece of the e_1-e_2 *plane*); we cannot
# simplify it to a number, but we can always reorder it at the cost of a minus sign.

# %%
e_1 * e_2  # -> e_12     (a new "plane" object)  # pyright: ignore[reportUnusedExpression]

# %%
e_2 * e_1  # -> -e_12     (same thing, opposite sign — Rule 2)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **Rule 3 — distribute and collect, and numbers slide freely.** Ordinary numbers
# (the coefficients out front) multiply and move around like normal; you just
# distribute the product across every term and add up like terms. For example
# `2*e_1 + 3*e_2 + 5*e_1` collects into `7*e_1 + 3*e_2`, exactly like combining
# `2x + 3y + 5x`.

# %%
(
    2 * e_1 + 3 * e_2 + 5 * e_1
)  # -> 7*e_1 + 3*e_2  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# Putting the rules together
# --------------------------
#
# Any product, no matter how messy, reduces to a tidy standard form by (a) FOILing it
# out, (b) using Rule 2 to sort the arrows into increasing order (`e_2*e_1` becomes
# `-e_1*e_2`), and (c) using Rule 1 to cancel any arrow that meets itself.
#
# Two payoffs worth seeing:
#
# **A vector times itself gives its length squared — that's the Pythagorean theorem.**
# Watch the cross-terms cancel by Rule 2 and the squares collapse by Rule 1:
#
# `(3*e_1 + 4*e_2) * (3*e_1 + 4*e_2)`
# `= 9*(e_1*e_1) + 12*(e_1*e_2) + 12*(e_2*e_1) + 16*(e_2*e_2)`
# `= 9*1 + 12*e_12 - 12*e_12 + 16*1`
# `= 25`   (and 25 = 3^2 + 4^2, the length squared).

# %%
v: MultiVector = 3 * e_1 + 4 * e_2
v * v  # -> 25 = 3^2 + 4^2  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# **The unit plane `e_1*e_2` squares to -1 — just like the imaginary number i.**
# The geometric algebra of the plane secretly *contains* the complex numbers:

# %%
i: MultiVector = e_1 * e_2
i * i  # -> -1     (so e_1*e_2 behaves like the imaginary unit)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# The same rules, written as math
# -------------------------------
#
# *(A little more formal — the same rules, stated the way a math class would put them.)*
#
# The entire geometric product is pinned down by **two identities about the basis
# vectors**, together with the ordinary algebra you already trust: it distributes over
# `+`, it is associative, and plain numbers factor out freely.
#
# > `e_i e_i = 1`  — each basis vector squares to `1`.  **(R1)**
# >
# > `e_i e_j = - e_j e_i`  (for `i ≠ j`)  — swapping two *different* ones flips the sign.  **(R2)**
#
# Everything else is bookkeeping. Any product of basis vectors `e_{i_1} e_{i_2} ... e_{i_k}`
# is brought to **standard form** — indices in increasing order, with no repeats — using
# just two moves:
#
# 1. **Sort, with a sign.** By (R2), slide a smaller index to the left past a larger
#    neighbor; each swap of two neighbors multiplies the whole term by `-1`. It is
#    ordinary sorting, except every swap costs a factor of `-1`.
# 2. **Cancel repeats.** By (R1), whenever two equal indices end up next to each other,
#    erase the pair.
#
# The worked example above is then just a chain of equalities:
#
# > `e_1 e_3 e_3 e_1`
# > `  = e_1 (e_3 e_3) e_1`   — regroup (associativity)
# > `  = e_1 (1) e_1`         — (R1) on the middle pair
# > `  = e_1 e_1`
# > `  = 1`                   — (R1) again
#
# and one that only sorts, with nothing to cancel:
#
# > `e_2 e_1 e_3 = - e_1 e_2 e_3`   — one swap of `e_2` past `e_1`, by (R2).
#
# (These two moves — sort with a sign, then cancel repeats — are exactly what `Gn`'s
# geometric product carries out: in the code, the recursive `decrease_grade` helper in
# `src/gacalc/gn.py`.)

# %% [markdown]
# Where do the plain numbers go? Scalars first.
# ---------------------------------------------
#
# So far every factor was a bare basis vector like `e_1`. In real life a term also has a
# **number** out front — `3*e_1`, `-2*e_2`, and so on. Where do those numbers go when we
# multiply?
#
# The happy answer: **numbers are ordinary numbers.** They commute with everything
# (`3*e_1 = e_1*3`) and they multiply among themselves the usual way. So the recipe grows
# just one opening step:
#
# 1. **Scalars first.** Sweep every numeric factor to the front and multiply them
#    together into a single number.
# 2. Then reduce the leftover string of basis vectors exactly as before — sort with a
#    sign (R2), cancel repeats (R1).
#
# For instance, gather the four numbers up front, then reuse the very reduction we just
# did (`e_1 e_3 e_3 e_1 = 1`):
#
# > `(2 e_1)(3 e_3)(4 e_3)(5 e_1)`
# > `  = (2·3·4·5) (e_1 e_3 e_3 e_1)`   — scalars to the front
# > `  = 120 · 1`                       — reduce the basis vectors
# > `  = 120`
#
# The scalars ride along untouched by the sign-flipping; only the basis vectors produce
# minus signs. A shorter one where the arrows *do* create a sign:
#
# > `(2 e_2)(3 e_1)`
# > `  = 6 (e_2 e_1)`      — scalars to the front
# > `  = 6 (- e_1 e_2)`    — one swap, by (R2)
# > `  = -6 e_12`

# %%
(2 * e_1) * (3 * e_3) * (4 * e_3) * (
    5 * e_1
)  # -> 120  # pyright: ignore[reportUnusedExpression]

# %%
(2 * e_2) * (3 * e_1)  # -> -6*e_12  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# A longer example — and why grouping is about to matter
# ------------------------------------------------------
#
# Let's do a messier one and reduce it by hand with the three rules:
#
# `(e_1*e_3) * (e_3*e_1)`
#
# Written out, that's the four arrows `e_1 e_3 e_3 e_1` in a row. Nothing here is a
# plain number yet, so we lean on the rules. The trick is to notice the two `e_3`'s
# sitting next to each other in the middle:
#
# `e_1 * (e_3 * e_3) * e_1`   ... group the middle pair
# `= e_1 * 1 * e_1`            ... Rule 1: `e_3*e_3 = 1`
# `= e_1 * e_1`
# `= 1`                        ... Rule 1 again
#
# So the whole four-arrow product collapses all the way down to the number `1`.

# %%
(e_1 * e_3) * (e_3 * e_1)  # -> 1  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# But wait — reducing that by hand, we quietly *re-grouped* the arrows. The original
# was `(e_1*e_3) * (e_3*e_1)`, yet we chose to first multiply the middle `e_3 * e_3`.
# Were we *allowed* to do that? What if we had grouped it a different way — would we
# still get `1`?
#
# Here are three different ways of parenthesizing the very same four arrows
# `e_1 e_3 e_3 e_1`. Every one of them gives `1`:

# %%
((e_1 * e_3) * e_3) * e_1  # left-to-right  # pyright: ignore[reportUnusedExpression]

# %%
e_1 * (e_3 * (e_3 * e_1))  # right-to-left  # pyright: ignore[reportUnusedExpression]

# %%
e_1 * (
    (e_3 * e_3) * e_1
)  # middle-pair first (what we did by hand)  # pyright: ignore[reportUnusedExpression]

# %% [markdown]
# They all agree. That is **associativity**: for a product of several things, *how you
# parenthesize does not change the answer*, so we can safely write `e_1*e_3*e_3*e_1`
# with no parentheses at all. We relied on it the moment we chose to reduce the middle
# pair first — and we'll rely on it constantly from here on.
#
# It is worth pausing on *why* this is not obvious. Remember Rule 2: order is **not**
# free here (`e_1*e_3` is the *negative* of `e_3*e_1`). When even the order of two
# things flips the sign, it is a fair question whether the *grouping* of many things
# might change the answer too. It turns out it doesn't — but that is something we
# should *prove* from the three rules, not just take on faith. (That proof is its own
# story; see the associativity section / task.)

# %%
sym_vec2_1  # pyright: ignore[reportUnusedExpression]

# %%
sym_vec2_2  # pyright: ignore[reportUnusedExpression]

# %%
sym_vec2_1 * sym_vec2_2  # pyright: ignore[reportUnusedExpression]

# %%
sym_vec2_1.dot(sym_vec2_2)

# %%
sym_vec2_1.wedge(sym_vec2_2)

# %%
e1e2plane: MultiVectorFn = MultiVector.project(onto=e_1 * e_2)
e1e2plane(sym_vec3_1) ^ e1e2plane(sym_vec3_2)  # pyright: ignore[reportUnusedExpression]

# %%
e2e3plane: MultiVectorFn = MultiVector.project(onto=e_2 * e_3)
e2e3plane(sym_vec3_1) ^ e2e3plane(sym_vec3_2)  # pyright: ignore[reportUnusedExpression]

# %%
e1e3plane: MultiVectorFn = MultiVector.project(onto=e_1 * e_3)
e1e3plane(sym_vec3_1) ^ e1e3plane(sym_vec3_2)  # pyright: ignore[reportUnusedExpression]

# %%
# ordering of the plane doesn't matter
e3e1plane: MultiVectorFn = MultiVector.project(onto=e_3 * e_1)
e3e1plane(sym_vec3_1) ^ e1e3plane(sym_vec3_2)  # pyright: ignore[reportUnusedExpression]

# %%
sym_vec3_1 * sym_vec3_2  # pyright: ignore[reportUnusedExpression]

# %%
sym_vec3_1.wedge(sym_vec3_2)

# %%
(sym_vec3_1.wedge(sym_vec3_2)).inverse()

# %%
show_mult((sym_vec3_1.wedge(sym_vec3_2)).inverse(), sym_vec3_1.wedge(sym_vec3_2))


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> MultiVector:
    # let gram_fe be e_1
    # let mol_fe be e_2
    unit_gram_fe: MultiVector = e_1
    unit_mol_fe: MultiVector = e_2

    ratio: MultiVector = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)

# %%
for x in MultiVector.bases(1):
    display(Math(x._repr_latex_()))

# %%
MultiVector.symbolic_multivector(n=1, prefix="a")

# %%
for x in MultiVector.bases(2):
    display(Math(x._repr_latex_()))

# %%
MultiVector.symbolic_multivector(n=2, prefix="b")

# %%
MultiVector.symbolic_multivector(n=2, prefix="b") * MultiVector.symbolic_multivector(
    n=2, prefix="d"
)  # pyright: ignore[reportUnusedExpression]

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(0)

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(1)

# %%
MultiVector.symbolic_multivector(n=2, prefix="c").r_vector_part(2)

# %%
for x in MultiVector.bases(3):
    display(Math(x._repr_latex_()))


# %%
g2_1 = MultiVector.symbolic_multivector(n=2, prefix="a")
g2_1


# %%
g2_2 = MultiVector.symbolic_multivector(n=2, prefix="b")
g2_2


# %%
g2_3 = MultiVector.symbolic_multivector(n=2, prefix="c")
g2_3


# %%
show_mult(g2_1, g2_2)


# %%
show_mult(g2_1 * g2_2, g2_3)


# %%
show_mult(g2_2, g2_3)


# %%
show_mult(g2_1, g2_2 * g2_3)


# %%
((g2_1 * g2_2) * g2_3) - (g2_1 * (g2_2 * g2_3))


# %%
MultiVector.symbolic_multivector(n=3, prefix="c")


# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(0)


# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(1)


# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(2)


# %%
MultiVector.symbolic_multivector(n=3, prefix="c").r_vector_part(3)


# %%
a_1 * e_1 * e_2 * e_4  # pyright: ignore[reportUnusedExpression]

# %%
asdf = MultiVector.symbolic_multivector(n=3, prefix="e").r_vector_part(1)
asdf2 = MultiVector.symbolic_multivector(n=3, prefix="f").r_vector_part(1)
asdf3 = asdf ^ asdf2
asdf3  # pyright: ignore[reportUnusedExpression]


# %%
asdf3 * asdf3

# %%
asdf3.dual(3)


# %%


# %%
asdf3.dot(asdf3.dual(3))

# %%
show_mult(asdf3, asdf3.dual(3))

# %%
show_mult(asdf3, asdf3.dual(3).inverse())

# %%
asdf3 * (asdf3.dual(3))  # pyright: ignore[reportUnusedExpression]

# %%
show_mult(sym_vec2_1, sym_vec2_2)


# %%
show_mult(sym_vec3_1, sym_vec3_2)


# %%
show_mult(
    MultiVector.symbolic_multivector(n=8, prefix="a").r_vector_part(1),
    MultiVector.symbolic_multivector(n=9, prefix="b").r_vector_part(1),
)

# %%


# %%


def rotate(angle):
    """Planar rotation by `angle` (positive turns e_1 toward e_2), built the
    geometric-algebra way: take the unit vector `to` at `angle` from e_1, form the
    half-angle rotor carrying e_1 -> to with `rotor_from_vectors`, and sandwich it.
    """
    to = sympy.cos(angle) * e_1 + sympy.sin(angle) * e_2
    R = MultiVector.rotor_from_vectors(from_vector=e_1, to_vector=to)
    return InvertibleFunction(
        lambda v: R * v * R.inverse(),
        lambda v: R.inverse() * v * R,
        f"R_{{{sympy.latex(angle)}}}",
        f"R_{{{sympy.latex(-angle)}}}",
    )


T: typing.Callable[[MultiVector], MultiVectorFn] = translate
S: typing.Callable[[float, float], InvertibleFunction] = scale_non_uniform
R: typing.Callable[[float], InvertibleFunction] = rotate
# %%
T(5 * e_1)

# %%
S(5, 6)

# %%
inverse(T(5 * e_1))

# %%
T(5 * e_1 + 6 * e_2)

# %%
T(5 * e_1 + 6 * e_2 + 7 * e_3)

# %%
inverse(T(5 * e_1 + 6 * e_2 + 7 * e_3))

# %%
R(sympy.pi / 2)

# %%
compose([R(sympy.pi / 2), T(5 * e_1 + 6 * e_2)])

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
fn = R(math.radians(53.130102))
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
fn = R(math.radians(53.130102))
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
# Draw relative graph paper
# -------------------------
#
# Draw two relative number lines, making a relative graph paper,
# but keep the original coordinate system on the left and bottom.
# Any point in the plane can be described using two different
# graph papers.

# %%
fn = R(math.radians(53.130102))
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
# in the order that they are applied, or in reverse order

# %%
fn = compose(
    [
        R(sympy.pi / 4),
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
for f in compose_intermediate_fns([R(sympy.pi / 4), T(2 * e_1)]):
    # TODO - figure out if I can render the latex as part of one markdown command,
    # if I were to uncomment out this line and other markdown lines,
    # the build of HTML would fail

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
#

# %%
for f in compose_intermediate_fns(
    [
        R(sympy.pi / 4),
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
# %%
plot_multivector(MultiVector.symbolic_multivector(n=8, prefix="a").r_vector_part(1))
plot_multivector(2 * one + 3 * e_1 - 1.5 * e_2 + 4 * e_3 + 0.7 * (e_1 * e_2))
5

# %%
aoeu = 3 * e_1 - 1.5 * e_2

# %%
plot_multivector(aoeu)
5

# %%
aoeu2 = 1.5 * e_1 + 5 * e_2

# %%
plot_multivector(aoeu2)
5

# %%
plot_multivector(aoeu * aoeu2)
5

# %%
