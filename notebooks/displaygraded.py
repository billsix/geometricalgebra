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
# Graded types — the operation decides the type
# ==============================================
#
# Mathematicians rarely carry a full multivector; they work with *vectors*,
# *bivectors*, *rotors*, and so on. This library has those as first-class types
# (`Vector2`, `Bivector2`, `Rotor2`, `Scalar`, ...), and **the product decides the
# return type**: two vectors multiply to a *rotor* (scalar + bivector), their
# wedge is a *bivector*, and so on.
#
# Crucially the return type is decided by the *operation*, derived symbolically
# when the classes are generated — never by inspecting (possibly float-fuzzy)
# coefficients. So if you want a pure blade you *ask* for it (with `^`), and a
# product that happens to come out with a zero component still has the type its
# operation dictates.

# %%
import sympy
from IPython.display import Markdown, Math, display

from gacalc.g2 import Vector2
from gacalc.g3 import Vector3
from gacalc.scalar import Scalar


def kind(x):
    """The runtime type name -- this is the star of the notebook."""
    return type(x).__name__


def show(*values):
    """Display each value as 'Type:  <latex>' -- the type is the point here."""
    for x in values:
        display(Math(f"{kind(x)}:\\quad " + x._repr_latex_().strip("$")))


# %% [markdown]
# A vector basis
# --------------
#
# Build a vector basis and combine it linearly. `3*e_1 + 4*e_2` is a `Vector2`.

# %%
e_1, e_2 = Vector2.basis_vector(1), Vector2.basis_vector(2)
a = 3 * e_1 + 4 * e_2
b = 1 * e_1 + 2 * e_2
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
# the wedge alone is a Bivector2; the dot alone is a Scalar
show(a ^ b, a.inner_product(b))

# %% [markdown]
# Type follows the operation, not the value
# -----------------------------------------
#
# Orthogonal vectors have a zero dot product, but `e_1 * e_2` is still a `Rotor2`
# (its scalar field just happens to be 0) — we never narrow by looking at a value.
# Want the pure bivector? Use `^`.

# %%
show(e_1 * e_2)

# %%
show(e_1 ^ e_2)

# %% [markdown]
# Bivectors and the Scalar type
# -----------------------------
#
# In 𝒢₂ a bivector squares to a scalar — so `Bivector2 * Bivector2` lands in the
# dedicated `Scalar` type.

# %%
i2 = e_1 ^ e_2  # the unit bivector
show(i2 * i2)

# %% [markdown]
# Rotors are the complex numbers
# ------------------------------
#
# The even subalgebra of 𝒢₂ is ℂ. Build a rotor as `scalar + bivector` (the `+`
# narrows to `Rotor2`), and the unit bivector squares to −1.

# %%
r = 2 + 3 * i2  # scalar + bivector  -> Rotor2
show(r)

# %%
show(i2 * i2)  # == -1

# %%
# a rotor rotates a vector (here, a quarter turn of e_1)
quarter = sympy.cos(sympy.pi / 4) - sympy.sin(sympy.pi / 4) * (e_1 * e_2)
rotated = quarter * e_1 * quarter.reverse()
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
# `AbstractMultiVector.rotate(from, to)` rotates a vector by `project`/`reject` +
# the geometric product. The *rotor* way builds `R = rotor_from_vectors(from, to)`
# = `|from||to| + to·from` and sandwiches: `R v R⁻¹`. They give the **same**
# rotation — provably, even symbolically (see `tests/test_graded.py`).

# %%
frm, to = e_1, e_2  # rotate by the e_1 -> e_2 angle (a quarter turn)
R = Vector2.rotor_from_vectors(from_vector=frm, to_vector=to)
show(R)  # an (un-normalized) Rotor2

# %% [markdown]
# Because `R` is not normalized, the bare sandwich `R v R̃` *scales* as well as
# rotates — by `R.magnitude_squared()` (= `R R̃`). Using `R.inverse()` (which is
# `R̃ / |R|²`) divides that out, leaving a pure rotation equal to `rotate`.

# %%
w = e_1
for label, value in [
    (r"R\,\tilde R", R * R.reverse()),
    (r"R\,w\,\tilde R", R * w * R.reverse()),
    (r"R\,w\,R^{-1}", R * w * R.inverse()),
    (r"\mathrm{rotate}(w)", Vector2.rotate(from_vector=frm, to_vector=to)(w)),
]:
    display(Math(label + " = " + value._repr_latex_().strip("$")))

# %%
# the rotor sandwich and rotate agree exactly
R * w * R.inverse() == Vector2.rotate(from_vector=frm, to_vector=to)(w)

# %% [markdown]
# The grade product table, made visible
# -------------------------------------
#
# Because the return type is the dispatch, we can just print it. This *is* the
# 𝒢₂ grade product table.

# %%
named = [
    ("Scalar", Scalar.from_scalar(5)),
    ("Vector2", a),
    ("Bivector2", i2),
    ("Rotor2", r),
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

# %%
f_1, f_2, f_3 = (Vector3.basis_vector(i) for i in (1, 2, 3))
u = 1 * f_1 + 2 * f_2 + 3 * f_3
v = 4 * f_1 + 5 * f_2 + 6 * f_3
show(u * v, u ^ v)

# %%
# dual of a bivector (a plane) is the orthogonal vector -- like u x v
biv = u ^ v
show(biv, biv.dual())

# %%
biv.dual()  # the components of u x v

# %%
# each unit bivector of G3 squares to -1 (the even subalgebra is the quaternions)
show((f_1 ^ f_2) * (f_1 ^ f_2))

# %% [markdown]
# When a result spans grades no single type covers
# ------------------------------------------------
#
# `vector * bivector` in 𝒢₃ is generally vector + trivector — no graded type
# holds that, so it **widens to the full `G3`**. Nothing is lost; the type is
# just the smallest that fits.

# %%
kind(u * biv)

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

# %%
