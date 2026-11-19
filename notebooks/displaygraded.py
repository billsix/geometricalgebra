# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
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
# Graded types — the operation decides the type
# ==============================================
#
# Mathematicians rarely carry a full multivector; they work with *vectors*,
# *bivectors*, *versors*, and so on. This library has those as first-class types
# (`g2.Vector`, `g2.Bivector`, `g2.Versor`, `g2.Scalar`, ...), and **the product
# decides the return type**: two vectors multiply to a *versor* (scalar +
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
from gacalc.nbplotutils import (
    create_graphs,
    create_graphs_3d,
    draw_angle,
    draw_bivector,
    draw_vectors,
)
from gacalc.transforms import (
    ComposableFunction,
    InvertibleFunction,
    compose,
    inverse,
    projection_rotation,
    translate,
)


def kind(x: MultiVectorBase) -> str:
    """The runtime type name -- this is the star of the notebook."""
    return type(x).__name__


def show(*values: MultiVectorBase) -> None:
    """Display each value as 'Type:  <latex>' -- the type is the point here."""
    x: MultiVectorBase
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
# Drawn as an arrow from the origin:

# %%
with create_graphs(graph_bounds=(5, 5)):
    draw_vectors([(a, r"\vec{\mathbf{a}}", "tab:blue")])

# %% [markdown]
# A scalar times a vector stretches it along its own line: `2 * b` is twice as
# long, and `-1 * b` points the other way.

# %%
show(2 * b, -1 * b)
with create_graphs(graph_bounds=(5, 5)):
    draw_vectors(
        [
            (2 * b, r"2 * \vec{\mathbf{b}}", "tab:orange"),
            (b, r"\vec{\mathbf{b}}", "tab:blue"),
            (-1 * b, r"-1 * \vec{\mathbf{b}}", "tab:red"),
        ]
    )

# %% [markdown]
# The geometric product of two vectors
# ------------------------------------
#
# $$ \vec{\mathbf{a}} * \vec{\mathbf{b}} = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} $$
#
# The scalar part is the dot product, the bivector part is the wedge — together
# an element of the even subalgebra, i.e. a **versor**.

# %%
show(a * b)

# %% [markdown]
# Asked for separately, the wedge alone is a `g2.Bivector` and the dot alone a
# `g2.Scalar`:

# %%
show(a ^ b, a.inner_product(b))

# %% [markdown]
# The wedge `a ^ b` is the parallelogram the two vectors span: its area is
# `|a ^ b|`, and the arc from `a` toward `b` is its orientation (counterclockwise
# here, so the `e_12` coefficient is positive).

# %%
with create_graphs(graph_bounds=(5, 5)):
    draw_bivector(a, b, label=r"\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}")
    draw_vectors(
        [(a, r"\vec{\mathbf{a}}", "tab:blue"), (b, r"\vec{\mathbf{b}}", "tab:orange")]
    )

# %% [markdown]
# Type follows the operation, not the value
# -----------------------------------------
#
# Orthogonal vectors have a zero dot product, but `e_1 * e_2` is still a `g2.Versor`
# (its scalar field just happens to be 0) — we never narrow by looking at a value.
# Want the pure bivector? Use `^`.

# %%
show(e_1 * e_2)

# %% [markdown]
# The wedge of the same two vectors is the pure bivector:

# %%
show(e_1 ^ e_2)

# %% [markdown]
# Bivectors and the g2.Scalar type
# -----------------------------
#
# In 𝒢₂ a bivector squares to a scalar — so `g2.Bivector * g2.Bivector` lands in the
# dedicated `g2.Scalar` type.

# %%
I2: g2.Bivector = e_1 ^ e_2  # the unit bivector
show(I2 * I2)

# %% [markdown]
# Versors are the complex numbers
# ------------------------------
#
# The even subalgebra of 𝒢₂ is ℂ. Build a versor as `scalar + bivector` (the `+`
# narrows to `g2.Versor`), and the unit bivector squares to −1.

# %%
R0: g2.Versor = 2 + 3 * I2
show(R0)

# %% [markdown]
# Predict the square of the unit bivector before running the cell:

# %%
show(I2 * I2)

# %% [markdown]
# A versor rotates a vector. The one that turns $\vec{\mathbf{e}}_1$ to
# $\vec{\mathbf{e}}_2$ is a quarter turn, built from the two vectors, with no
# cosines or sines written by hand:

# %%
quarter: g2.Versor = g2.Vector.versor_from_vectors(from_vector=e_1, to_vector=e_2)
rotated: g2.Vector = quarter * e_1 * quarter.inverse()
show(rotated)

# %% [markdown]
# The quarter turn carries $\vec{\mathbf{e}}_1$ to $\vec{\mathbf{e}}_2$; the arc is
# the turn:

# %%
with create_graphs(graph_bounds=(3, 3)):
    draw_angle(from_vector=e_1, to_vector=rotated, radius=0.6)
    draw_vectors(
        [
            (e_1, r"\vec{\mathbf{e}}_1", "tab:blue"),
            (rotated, r"\mathrm{rotated}", "tab:orange"),
        ]
    )

# %% [markdown]
# A versor's plane of rotation
# ---------------------------
#
# `plane_of_rotation()` returns the unit bivector (a 2-blade) the versor turns in
# — the normalized bivector part. In 2D that 2-blade is also the pseudoscalar.

# %%
show(quarter.plane_of_rotation())

# %% [markdown]
# The plane of rotation is the unit square $\vec{\mathbf{e}}_1$ and
# $\vec{\mathbf{e}}_2$ span, oriented from $\vec{\mathbf{e}}_1$ toward
# $\vec{\mathbf{e}}_2$:

# %%
with create_graphs(graph_bounds=(3, 3)):
    draw_bivector(e_1, e_2, label=r"\mathbf{e}_{12}")
    draw_vectors(
        [(e_1, r"\vec{\mathbf{e}}_1", "black"), (e_2, r"\vec{\mathbf{e}}_2", "black")]
    )

# %% [markdown]
# Two ways to rotate are the same thing
# -------------------------------------
#
# `projection_rotation(from, to)` rotates a vector by `project`/`reject` +
# the geometric product. The *versor* way builds `R = versor_from_vectors(from, to)`
# = `|from| * |to| + to * from` and sandwiches: `R * v * R⁻¹`. They give the **same**
# rotation — provably, even symbolically (see `tests/test_graded.py`).

# %%
frm: g2.Vector
to: g2.Vector
frm, to = 1 * e_1, 1 * e_2  # rotate by the e_1 -> e_2 angle (a quarter turn)
R: g2.Versor = g2.Vector.versor_from_vectors(from_vector=frm, to_vector=to)
show(R)

# %% [markdown]
# Because `R` is not normalized, the bare sandwich `R * v * R̃` *scales* as well as
# rotates — by `R.magnitude_squared()` (= `R R̃`). Using `R.inverse()` (which is
# `R̃ / |R|²`) divides that out, leaving a pure rotation equal to `projection_rotation`.

# %%
w: g2.Vector = e_1
label: str
value: MultiVectorBase
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

# %% [markdown]
# The versor sandwich minus `projection_rotation`'s answer is $0$:

# %%
R * w * R.inverse() - projection_rotation(from_vector=frm, to_vector=to)(w)

# %% [markdown]
# The picture of that cell: the bare sandwich `R * w * R̃` turns `w` and also
# stretches it by `|R|² = 2`, while `R * w * R⁻¹` only turns it, and lands on
# exactly the arrow `projection_rotation` draws (the `==` above).

# %%
with create_graphs(graph_bounds=(3, 3)):
    draw_angle(from_vector=w, to_vector=R * w * R.inverse(), radius=0.6)
    draw_vectors(
        [
            (w, r"\vec{\mathbf{w}}", "tab:blue"),
            (R * w * R.reverse(), r"R * \vec{\mathbf{w}} * \tilde{R}", "tab:red"),
            (
                R * w * R.inverse(),
                r"R * \vec{\mathbf{w}} * R^{-1}",
                "tab:green",
            ),
        ]
    )

# %% [markdown]
# The grade product table, made visible
# -------------------------------------
#
# Because the return type is the dispatch, we can just print it. This *is* the
# 𝒢₂ grade product table.

# %%
named: list[tuple[str, MultiVectorBase]] = [
    ("g2.Scalar", g2.Scalar.from_real(5)),
    ("g2.Vector", a),
    ("g2.Bivector", I2),
    ("g2.Versor", R0),
]
# the 𝒢₂ grade product table: (row) * (column) -> result type
header: str = "| `*` | " + " | ".join(na for na, _ in named) + " |"
sep: str = "| --- " * (len(named) + 1) + "|"
rows: list[str] = [
    f"| **{na}** | " + " | ".join(kind(x * y) for _, y in named) + " |"
    for na, x in named
]
display(Markdown("\n".join([header, sep, *rows])))

# %% [markdown]
# Three dimensions
# ----------------
#
# The same story in 𝒢₃: vectors multiply to versors (quaternions), wedge to
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

# %% [markdown]
# The dual of a bivector (a plane) is the vector perpendicular to it, like
# $\vec{\mathbf{u}} \times \vec{\mathbf{v}}$:

# %%
B: g3.Bivector = u ^ v
show(B, B.dual())

# %% [markdown]
# In a picture: `u ^ v` is the parallelogram in the plane of `u` and `v`, and its
# dual is the arrow perpendicular to that plane, the cross product `u × v`.

# %%
# a camera that sees the plane at a slant and its normal side-on
with create_graphs_3d(bound=9, elevation=20, azimuth=0):
    draw_bivector(u, v, label=r"\vec{\mathbf{u}} \wedge \vec{\mathbf{v}}")
    draw_vectors(
        [
            (u, r"\vec{\mathbf{u}}", "tab:blue"),
            (v, r"\vec{\mathbf{v}}", "tab:orange"),
            (B.dual(), r"(\vec{\mathbf{u}} \wedge \vec{\mathbf{v}})^*", "tab:red"),
        ]
    )

# %% [markdown]
# Its coefficients are the components of $\vec{\mathbf{u}} \times
# \vec{\mathbf{v}}$:

# %%
B.dual()

# %% [markdown]
# Each unit bivector of 𝒢₃ squares to $-1$, so the even subalgebra is the
# quaternions. Predict before running:

# %%
show((g3.Vector.e_1 ^ g3.Vector.e_2) * (g3.Vector.e_1 ^ g3.Vector.e_2))

# %% [markdown]
# A bivector times its **own dual** collapses to the pseudoscalar scaled by $|B|^2$:
# $B * B^{*} = |B|^2 * I$. For a *unit* bivector that is just the pseudoscalar
# $I = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3$. The lazy
# `g3.Bivector` stores the raw $\cos(t)^2 + \sin(t)^2$ coefficient; only the **display**
# simplifies it — so the cancellation shows.

# %%
t: sympy.Symbol = sympy.symbols("t")
B: g3.Bivector = (g3.Vector.e_1 ^ g3.Vector.e_2) * sympy.cos(t) + (
    g3.Vector.e_1 ^ g3.Vector.e_3
) * sympy.sin(t)
# B * B.dual() stores (cos^2 t + sin^2 t)·e_123 but displays as the trivector e_123
show(B, B.dual(), B * B.dual())

# %% [markdown]
# The odd part {1,3}: `g3.Odd`
# -----------------------------
#
# `vector * bivector` in 𝒢₃ is generally **vector + trivector** — grades {1,3}, the
# **odd part** of 𝒢₃. That is the mirror of the even part {0,2} = `g3.Versor`, and it
# has its own named type, **`g3.Odd`** (before it was registered, this widened to
# the full `g3.G`). It is a graded *subspace*, **not** a subalgebra: odd·odd = even,
# so `Odd * Odd` is a `Versor` — see
# `tasks/reference/graded-subspaces-vs-subalgebras.md`.

# %%
kind(u * B)

# %% [markdown]
# The three geometric cases. For a plane `B = a ^ b`, the product `B * v` is grade 1
# when `v` is **in** the plane, grade 3 when `v` is **perpendicular** to it (the dual
# of the wedge points that way), and both when `v` mixes them — but the *type* is
# always `Odd` (it follows the operation, not the runtime coefficients).

# %%
a3: g3.Vector = 1 * g3.Vector.e_1 + 2 * g3.Vector.e_2
b3: g3.Vector = 3 * g3.Vector.e_1 + 1 * g3.Vector.e_2 + 1 * g3.Vector.e_3
plane: g3.Bivector = a3 ^ b3
perp: g3.Vector = (a3 ^ b3).dual()  # perpendicular to the plane (dual of the wedge)
show(plane * a3, plane * perp, plane * (a3 + perp))

# %% [markdown]
# Query and cast. The **query** is the inherited `grades()` / `is_vector()` /
# `is_trivector()`; the **cast** `to_vector()` / `to_trivector()` narrows an `Odd`
# to the concrete type, raising if the grade it would discard is nonzero.

# %%
in_plane: g3.Odd = plane * a3
kind(in_plane.to_vector())

# %% [markdown]
# and its value, narrowed to a `g3.Vector`:

# %%
show(in_plane.to_vector())

# %% [markdown]
# The perpendicular case narrows to a `g3.Trivector`:

# %%
kind((plane * perp).to_trivector())

# %% [markdown]
# Casting to the wrong type raises, because the grade it would discard is nonzero:

# %%
try:
    in_plane.to_trivector()
except ValueError as error:
    display(Markdown(f"raises `ValueError`: {error}"))

# %% [markdown]
# Interop
# -------
#
# Graded values compare and combine with the full types and the general `Gn`
# transparently (they share the blade-dict interchange protocol).

# %%
a == 3 * e_1 + 4 * e_2

# %% [markdown]
# A few of them, typeset:

# %%
show(a, a * b, a ^ b, R0)

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
B3: g3.Bivector = g3.Vector.e_1 ^ g3.Vector.e_2  # the e_1 * e_2 plane
P: ComposableFunction[g3.Vector] = g3.Vector.project(
    B3
)  # a ComposableFunction, already labelled from B3
display(Math(P.latex_repr))
# projects onto the plane
P(1 * g3.Vector.e_1 + 1 * g3.Vector.e_3)

# %% [markdown]
# Compose the projection with a translation: the pipeline shows itself as one
# formula and applies translate-then-project to a vector. (Wrapping $P$ in a
# `ComposableFunction` gives it a short label for the display.)

# %%
pipe: ComposableFunction[g3.Vector] = compose(
    [ComposableFunction(P, "P_{B}"), translate(b=g3.Vector.e_3)]
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
