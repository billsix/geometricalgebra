# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The cross product by standard position — calculations
#
# Companion to the *Proof: The Cross Product by Rotating to Standard Position* chapter.
# We check that the standard-position construction — reduce **both** vectors to the
# `e_1 e_2` plane with three elementary plane rotations (so `a` lands on `e_1` and `b`
# lands in the plane), take the cross product there (where it is a pure `e_3` vector),
# then rotate back — lands on the same answer as gacalc's cross product
# `gacalc.vectorcalc.cross`.
#
# This is the runnable, symbolic twin of the Lean capstone `cross_via_reduction`
# (and its explicit-angle form `cross_via_reduction_of_vectors`) in
# `proofs/GacalcProofs/CrossStandardPosition.lean`, whose engine is the three
# elementary cross-equivariances assembled by `cross_reduceToPlane_equivariant`.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.g3 import Vector, e_1, e_2, e_3
from gacalc.vectorcalc import cross

# %% [markdown]
# ## The construction
#
# Three elementary plane rotations put the frame in standard position. The first two
# (read off `a`'s coordinates) swing `a` onto the `e_1` axis — its `xy` shadow onto the
# x-axis, then its `z` part down — as in the projection chapter. A third rotation
# about the fixed `e_1` axis (read off `b`'s image) swings `b` into the `e_1 e_2` plane.
# Both vectors ride along with the graph paper. In that frame `a = (|a|, 0, 0)` and
# `b = (b_1', b_2', 0)`, so `a x b = (0, 0, |a| * b_2')` is a pure `e_3` vector — the
# easy value. Rotating it back recovers the true cross product.


# %%
def cross_via_standard_position(a: Vector, b: Vector) -> Vector:
    """Cross product of `a` and `b` by reduction to standard position (3-D).

    Reduce both vectors to the `e_1 e_2` plane with three elementary plane rotations,
    cross there (a pure `e_3` vector), and rotate back. Uses only 2-D rotations — no
    geometric product, no versor, no matrix. Equal to `gacalc.vectorcalc.cross`.
    """

    def rotate_xy(cos: Real, sin: Real, v: Vector) -> Vector:
        """2-D rotation on the (e_1, e_2) components; the e_3 part rides along."""
        x: Real = v.coefficient(e_1)
        y: Real = v.coefficient(e_2)
        z: Real = v.coefficient(e_3)
        return (cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2 + z * e_3

    def rotate_xz(cos: Real, sin: Real, v: Vector) -> Vector:
        """2-D rotation on the (e_1, e_3) components; the e_2 part rides along."""
        x: Real = v.coefficient(e_1)
        y: Real = v.coefficient(e_2)
        z: Real = v.coefficient(e_3)
        return (cos * x - sin * z) * e_1 + y * e_2 + (sin * x + cos * z) * e_3

    def rotate_yz(cos: Real, sin: Real, v: Vector) -> Vector:
        """2-D rotation on the (e_2, e_3) components; the e_1 part rides along."""
        x: Real = v.coefficient(e_1)
        y: Real = v.coefficient(e_2)
        z: Real = v.coefficient(e_3)
        return x * e_1 + (cos * y - sin * z) * e_2 + (sin * y + cos * z) * e_3

    # (cos, sin) to swing a onto e_1, read straight off a's coordinates.
    a_1: Real = a.coefficient(e_1)
    a_2: Real = a.coefficient(e_2)
    a_3: Real = a.coefficient(e_3)
    a_xy_magnitude: Real = (a_1 * e_1 + a_2 * e_2).magnitude()
    a_magnitude: Real = a.magnitude()
    cos_xy: Real = a_1 / a_xy_magnitude
    sin_xy: Real = -a_2 / a_xy_magnitude
    cos_xz: Real = a_xy_magnitude / a_magnitude
    sin_xz: Real = -a_3 / a_magnitude

    def align_a(v: Vector) -> Vector:
        """The two rotations that put a on e_1, applied to any vector."""
        return rotate_xz(cos_xz, sin_xz, rotate_xy(cos_xy, sin_xy, v))

    # (cos, sin) to swing b into the e_1 e_2 plane, read off b after the a-alignment.
    b_aligned: Vector = align_a(b)
    b_aligned_2: Real = b_aligned.coefficient(e_2)
    b_aligned_3: Real = b_aligned.coefficient(e_3)
    yz_magnitude: Real = (b_aligned_2 * e_2 + b_aligned_3 * e_3).magnitude()
    cos_yz: Real = b_aligned_2 / yz_magnitude
    sin_yz: Real = -b_aligned_3 / yz_magnitude

    def reduce_to_plane(v: Vector) -> Vector:
        """All three rotations: a lands on e_1, b lands in the e_1 e_2 plane."""
        return rotate_yz(cos_yz, sin_yz, align_a(v))

    def rotate_back(v: Vector) -> Vector:
        """Undo the reduction: negate each sine, apply the inverses in reverse order."""
        return rotate_xy(
            cos_xy, -sin_xy, rotate_xz(cos_xz, -sin_xz, rotate_yz(cos_yz, -sin_yz, v))
        )

    a_reduced: Vector = reduce_to_plane(a)  # (|a|, 0, 0)
    b_reduced: Vector = reduce_to_plane(b)  # (b_1', b_2', 0)
    # In the reduced frame the cross product is the pure e_3 vector (0, 0, |a| * b_2').
    reduced_x: Real = a_reduced.coefficient(e_1)
    reduced_y: Real = b_reduced.coefficient(e_2)
    cross_in_frame: Vector = (reduced_x * reduced_y) * e_3
    return rotate_back(cross_in_frame)


# %% [markdown]
# ## Symbolic check: standard position equals the canonical cross
#
# We take an **exact-magnitude** `a` (the Pythagorean quadruple `3, 4, 12`, with
# `|a_xy| = 5` and `|a| = 13`, so the alignment rotations stay rational) and a fully
# **symbolic** `b`. The swing's `sqrt(b_2'^2 + b_3'^2)` cancels in the round trip, so
# difference simplifies to zero — the standard-position cross product equals the
# geometric-algebra cross product `a x b`.

# %%
a_exact: Vector = 3 * e_1 + 4 * e_2 + 12 * e_3
b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
b_symbolic: Vector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

difference: MultiVectorBase = cross_via_standard_position(a_exact, b_symbolic) - cross(
    a_exact, b_symbolic
)
[
    sympy.simplify(sympy.sympify(coefficient)) for coefficient in difference
]  # -> [0, 0, 0]
