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
# Graded types — the operation decides the type
# ==============================================
#
# Mathematicians rarely carry a full multivector; they work with *vectors*,
# *bivectors*, *rotors*, and so on. This library has those as first-class types
# (`g2.Vector`, `g2.Bivector`, `g2.Rotor`, `g2.Scalar`, ...), and **the product
# decides the return type**: two vectors multiply to a *rotor* (scalar +
# bivector), their wedge is a *bivector*, and so on.
#
# The return type is decided by the *operation*, derived symbolically
# when the classes are generated — never by inspecting (possibly float-fuzzy)
# coefficients. So if you want a pure blade you *ask* for it (with `^`), and a
# product that happens to come out with a zero component still has the type its
# operation dictates.

# %%
import sympy
from IPython.display import Markdown, Math, display

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.g2 import e_1, e_2
from gacalc.transforms import (
    ComposableFunction,
    InvertibleFunction,
    inverse,
    projection_rotation,
    translate,
)


def kind(x: MultiVectorBase) -> str:
    """The runtime type name -- this is the star of the notebook."""
    return type(x).__name__


def show(*values: MultiVectorBase) -> None:
    """Display each value as 'Type:  <latex>' -- the type is the point here."""
    for x in values:
        display(Math(f"{kind(x)}:\\quad " + x._repr_latex_().strip("$")))


# %% [markdown]
# A vector basis
# --------------
#
# Build a vector basis and combine it linearly: `3*e_1 + 4*e_2` is a `g2.Vector`,
# so the code reads like the printed math. Each `g2`/`g3` module exports its basis
# blades at **module scope, already graded** — `from gacalc.g2 import e_1, e_2`
# yields `g2.Vector` constants — so the vectors are written unqualified below. (The
# same blades are also class constants, `g2.Vector.e_1 == g2.Vector.basis_vector(1)`,
# and reading a coefficient back out is `v.coefficient(g2.Vector.e_1)`, a thin reader
# over `to_blade_dict()`.)

# %%
a: g2.Vector = 3 * e_1 + 4 * e_2
b: g2.Vector = 1 * e_1 + 2 * e_2
show(a)

# %% [markdown]
# The geometric product of two vectors
# ------------------------------------
#
# $$ ab = a\cdot b + a\wedge b $$
#
# The scalar part is the dot product, the bivector part is the wedge — together
# an element of the even subalgebra, i.e. a **rotor**.

# %%
show(a * b)

# %%
# the wedge alone is a g2.Bivector; the dot alone is a g2.Scalar
show(a ^ b, a.inner_product(b))

# %% [markdown]
# Type follows the operation, not the value
# -----------------------------------------
#
# Orthogonal vectors have a zero dot product, but `e_1 * e_2` is still a `g2.Rotor`
# (its scalar field just happens to be 0) — we never narrow by looking at a value.
# Want the pure bivector? Use `^`.

# %%
show(e_1 * e_2)

# %%
show(e_1 ^ e_2)

# %% [markdown]
# Bivectors and the g2.Scalar type
# -----------------------------
#
# In 𝒢₂ a bivector squares to a scalar — so `g2.Bivector * g2.Bivector` lands in the
# dedicated `g2.Scalar` type.

# %%
i2: g2.Bivector = e_1 ^ e_2  # the unit bivector
show(i2 * i2)

# %% [markdown]
# Rotors are the complex numbers
# ------------------------------
#
# The even subalgebra of 𝒢₂ is ℂ. Build a rotor as `scalar + bivector` (the `+`
# narrows to `g2.Rotor`), and the unit bivector squares to −1.

# %%
r: g2.Rotor = 2 + 3 * i2  # scalar + bivector  -> g2.Rotor
show(r)

# %%
show(i2 * i2)  # == -1

# %%
# a rotor rotates a vector: the normalized rotor that turns e_1 -> e_2 is a
# quarter turn, built from the two vectors (no hand-rolled cos/sin needed)
quarter: g2.Rotor = g2.Vector.rotor_from_vectors(from_vector=e_1, to_vector=e_2)
rotated: g2.Vector = quarter * e_1 * quarter.inverse()
show(rotated)

# %% [markdown]
# A rotor's plane of rotation
# ---------------------------
#
# `plane_of_rotation()` returns the unit bivector (a 2-blade) the rotor turns in
# — the normalized bivector part. In 2D that 2-blade is also the pseudoscalar.

# %%
show(quarter.plane_of_rotation())

# %% [markdown]
# Two ways to rotate are the same thing
# -------------------------------------
#
# `projection_rotation(from, to)` rotates a vector by `project`/`reject` +
# the geometric product. The *rotor* way builds `R = rotor_from_vectors(from, to)`
# = `|from||to| + to·from` and sandwiches: `R v R⁻¹`. They give the **same**
# rotation — provably, even symbolically (see `tests/test_graded.py`).

# %%
frm, to = 1 * e_1, 1 * e_2  # rotate by the e_1 -> e_2 angle (a quarter turn)
R: g2.Rotor = g2.Vector.rotor_from_vectors(from_vector=frm, to_vector=to)
show(R)  # an (un-normalized) g2.Rotor

# %% [markdown]
# Because `R` is not normalized, the bare sandwich `R v R̃` *scales* as well as
# rotates — by `R.magnitude_squared()` (= `R R̃`). Using `R.inverse()` (which is
# `R̃ / |R|²`) divides that out, leaving a pure rotation equal to `projection_rotation`.

# %%
w: g2.Vector = e_1
for label, value in [
    (r"R\,\tilde R", R * R.reverse()),
    (r"R\,w\,\tilde R", R * w * R.reverse()),
    (r"R\,w\,R^{-1}", R * w * R.inverse()),
    (
        r"\mathrm{projection\_rotation}(w)",
        projection_rotation(from_vector=frm, to_vector=to)(w),
    ),
]:
    display(Math(label + " = " + value._repr_latex_().strip("$")))

# %%
# the rotor sandwich and projection_rotation agree exactly
R * w * R.inverse() == projection_rotation(from_vector=frm, to_vector=to)(w)

# %% [markdown]
# The grade product table, made visible
# -------------------------------------
#
# Because the return type is the dispatch, we can just print it. This *is* the
# 𝒢₂ grade product table.

# %%
named = [
    ("g2.Scalar", g2.Scalar.from_scalar(5)),
    ("g2.Vector", a),
    ("g2.Bivector", i2),
    ("g2.Rotor", r),
]
# the 𝒢₂ grade product table: (row) * (column) -> result type
header = "| `*` | " + " | ".join(na for na, _ in named) + " |"
sep = "| --- " * (len(named) + 1) + "|"
rows = [
    f"| **{na}** | " + " | ".join(kind(x * y) for _, y in named) + " |"
    for na, x in named
]
display(Markdown("\n".join([header, sep, *rows])))

# %% [markdown]
# Three dimensions
# ----------------
#
# The same story in 𝒢₃: vectors multiply to rotors (quaternions), wedge to
# bivectors, and the **dual of a bivector is a vector** — the geometric-algebra
# form of the cross product.
#
# The 𝒢₃ basis is written qualified as `g3.Vector.e_1` … here: this file already
# imported the bare `e_1`/`e_2` from `gacalc.g2`, and a name binds to one algebra
# at a time. In a 𝒢₃-only notebook you would `from gacalc.g3 import e_1, e_2, e_3`
# and write them unqualified just the same.

# %%
u: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3
v: g3.Vector = 4 * g3.Vector.e_1 + 5 * g3.Vector.e_2 + 6 * g3.Vector.e_3
show(u * v, u ^ v)

# %%
# dual of a bivector (a plane) is the orthogonal vector -- like u x v
biv: g3.Bivector = u ^ v
show(biv, biv.dual())

# %%
biv.dual()  # the components of u x v

# %%
# each unit bivector of g3.G squares to -1 (the even subalgebra is the quaternions)
show((g3.Vector.e_1 ^ g3.Vector.e_2) * (g3.Vector.e_1 ^ g3.Vector.e_2))

# %% [markdown]
# A bivector times its **own dual** collapses to the pseudoscalar scaled by
# `|B|²`:  `B (B*) = |B|² I`.  For a *unit* bivector that is just the pseudoscalar
# `I = e₁e₂e₃`.  The lazy `g3.Bivector` stores the raw `cos²t + sin²t` coefficient;
# only the **display** simplifies it — so the cancellation shows.

# %%
t = sympy.symbols("t")
B: g3.Bivector = (g3.Vector.e_1 ^ g3.Vector.e_2) * sympy.cos(t) + (
    g3.Vector.e_1 ^ g3.Vector.e_3
) * sympy.sin(t)
# B * B.dual() stores (cos^2 t + sin^2 t)·e_123 but displays as the trivector e_123
show(B, B.dual(), B * B.dual())

# %% [markdown]
# The odd part {1,3}: `g3.Odd_3`
# -----------------------------
#
# `vector * bivector` in 𝒢₃ is generally **vector + trivector** — grades {1,3}, the
# **odd part** of 𝒢₃. That is the mirror of the even part {0,2} = `g3.Rotor`, and it
# has its own named type, **`g3.Odd_3`** (before it was registered, this widened to
# the full `g3.G`). It is a graded *subspace*, **not** a subalgebra: odd·odd = even,
# so `Odd_3 * Odd_3` is a `Rotor` — see
# `tasks/reference/graded-subspaces-vs-subalgebras.md`.

# %%
kind(u * biv)  # g3.Odd_3 (was g3.G)

# %% [markdown]
# The three geometric cases. For a plane `B = a ^ b`, the product `B * v` is grade 1
# when `v` is **in** the plane, grade 3 when `v` is **perpendicular** to it (the dual
# of the wedge points that way), and both when `v` mixes them — but the *type* is
# always `Odd_3` (it follows the operation, not the runtime coefficients).

# %%
a3: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2
b3: g3.Vector = 3 * g3.Vector.e_1 + 1 * g3.Vector.e_2 + 1 * g3.Vector.e_3
plane: g3.Bivector = a3 ^ b3
perp: g3.Vector = (a3 ^ b3).dual()  # perpendicular to the plane (dual of the wedge)
show(plane * a3, plane * perp, plane * (a3 + perp))  # all g3.Odd_3: {1}, {3}, {1,3}

# %% [markdown]
# Query and cast. The **query** is the inherited `grades()` / `is_vector()` /
# `is_trivector()`; the **cast** `to_vector()` / `to_trivector()` narrows an `Odd_3`
# to the concrete type, raising if the grade it would discard is nonzero.

# %%
in_plane = plane * a3
kind(in_plane.to_vector())  # -> g3.Vector (its grade-3 part is zero)

# %%
show(in_plane.to_vector())  # the narrowed g3.Vector value

# %%
kind((plane * perp).to_trivector())  # the perpendicular case -> g3.Trivector

# %%
# casting to the wrong type raises (the grade it would discard is nonzero):
try:
    in_plane.to_trivector()
except ValueError as error:
    print(error)

# %% [markdown]
# Interop
# -------
#
# Graded values compare and combine with the full types and the general `Gn`
# transparently (they share the blade-dict interchange protocol).

# %%
a == 3 * e_1 + 4 * e_2

# %%
# display a few as latex
show(a, a * b, a ^ b, r)

# %% [markdown]
# Projections and reflections compose in a pipeline
# -------------------------------------------------
#
# `project` / `reject` / `reflect` return a **labelled, composable** function —
# `project` / `reject` a `ComposableFunction` (no inverse; a projection discards
# information), and `reflect` an `InvertibleFunction` (an involution, its own
# inverse). So they drop straight into a `@` / `compose` display pipeline next to
# the transform factories (`translate`, `uniform_scale`, …).

# %%
B3: g3.Bivector = g3.Vector.e_1 ^ g3.Vector.e_2  # the e_1 e_2 plane
P: ComposableFunction[g3.Vector] = g3.Vector.project(
    B3
)  # a ComposableFunction, already labelled from B3
display(Math(P.latex_repr))
# projects onto the plane
P(1 * g3.Vector.e_1 + 1 * g3.Vector.e_3)  # pyright: ignore[reportUnusedExpression]

# %%
# compose the projection with a translate: the pipeline renders as one LaTeX
# expression, and applies translate-then-project to a vector. (Wrap in a
# ComposableFunction to give it a tidy custom label for the display.)
pipe: ComposableFunction[g3.Vector] = ComposableFunction(P, "P_{B}") @ translate(
    b=g3.Vector.e_3
)
display(Math(pipe.latex_repr))
show(pipe(1 * g3.Vector.e_1 + 1 * g3.Vector.e_2))

# %% [markdown]
# A projection is **not invertible** — inverting a pipeline that contains it
# raises `NotInvertibleError`. A *reflection*, by contrast, is its own inverse (an
# involution): `reflect` returns an `InvertibleFunction`, so it round-trips.

# %%
M: InvertibleFunction[g3.Vector] = g3.Vector.reflect(
    B3
)  # an InvertibleFunction (its own inverse)
w3: g3.Vector = 1 * g3.Vector.e_1 + 1 * g3.Vector.e_3
show(M(w3), inverse(M)(M(w3)))  # reflected, then reflected back == w3

# %%
