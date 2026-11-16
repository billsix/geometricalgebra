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
# The projection chapters made a hard problem easy by turning the picture until one
# vector lay on an axis. The cross product works the same way. Three elementary plane
# rotations turn the pair so that $a$ lies on $e_1$ and $b$ in the $e_1 e_2$ plane;
# there the cross product is a multiple of $e_3$ you can read off; turning back gives
# the cross product of the original pair. This notebook checks that the result is
# gacalc's cross product, `gacalc.vectorcalc.cross`.
#
# This is the runnable, symbolic twin of the Lean capstone `cross_via_reduction`
# (and its explicit-angle form `cross_via_reduction_of_vectors`) in
# `proofs/GacalcProofs/CrossStandardPosition.lean`, whose engine is the three
# elementary cross-equivariances assembled by `cross_reduceToPlane_equivariant`.

# %%
import sympy

from gacalc import g2
from gacalc.base import MultiVectorBase, Real
from gacalc.g3 import Scalar, Vector, e_1, e_2, e_3
from gacalc.vectorcalc import cross

# %% [markdown]
# ## The construction
#
# Three elementary plane rotations put the pair in standard position. The first two,
# read off $a$'s coordinates, swing $a$ onto the $e_1$ axis: its $xy$-shadow onto the
# x-axis, then its $z$-part down, as in the projection chapter. The third, about the
# fixed $e_1$ axis and read off where $b$ has moved to, swings $b$ into the $e_1 e_2$
# plane. Both vectors ride along. In that position $a = (|a|, 0, 0)$ and
# $b = (b'_1, b'_2, 0)$, so $a \times b = (0, 0, |a| * b'_2)$, a multiple of $e_3$.
# Rotating it back gives the cross product of the original $a$ and $b$.


# %%
def cross_via_standard_position(a: Vector, b: Vector) -> Vector:
    """Cross product of `a` and `b` by reduction to standard position (3-D).

    Reduce both vectors to the `e_1 e_2` plane with three elementary plane rotations,
    cross there (a pure `e_3` vector), and rotate back. Uses only 2-D rotations — no
    geometric product, no versor, no matrix. Equal to `gacalc.vectorcalc.cross`.
    """

    def rotate_2d(cos: Real, sin: Real, v: g2.Vector) -> g2.Vector:
        """The 2-D rotation as a blend of v and its quarter turn (eq-rotate-formula)."""
        return g2.Scalar(cos) * v + g2.Scalar(sin) * v.rotate_90_degrees()

    def rotate_xy(cos: Real, sin: Real, v: Vector) -> Vector:
        """Rotate the (e_1, e_2) pair in 2-D; the e_3 part rides along."""
        rotated: g2.Vector = rotate_2d(
            cos,
            sin,
            g2.Scalar(v.coefficient(e_1)) * g2.e_1
            + g2.Scalar(v.coefficient(e_2)) * g2.e_2,
        )
        return (
            Scalar(rotated.coefficient(g2.e_1)) * e_1
            + Scalar(rotated.coefficient(g2.e_2)) * e_2
            + Scalar(v.coefficient(e_3)) * e_3
        )

    def rotate_xz(cos: Real, sin: Real, v: Vector) -> Vector:
        """Rotate the (e_1, e_3) pair in 2-D; the e_2 part rides along."""
        rotated: g2.Vector = rotate_2d(
            cos,
            sin,
            g2.Scalar(v.coefficient(e_1)) * g2.e_1
            + g2.Scalar(v.coefficient(e_3)) * g2.e_2,
        )
        return (
            Scalar(rotated.coefficient(g2.e_1)) * e_1
            + Scalar(v.coefficient(e_2)) * e_2
            + Scalar(rotated.coefficient(g2.e_2)) * e_3
        )

    def rotate_yz(cos: Real, sin: Real, v: Vector) -> Vector:
        """Rotate the (e_2, e_3) pair in 2-D; the e_1 part rides along."""
        rotated: g2.Vector = rotate_2d(
            cos,
            sin,
            g2.Scalar(v.coefficient(e_2)) * g2.e_1
            + g2.Scalar(v.coefficient(e_3)) * g2.e_2,
        )
        return (
            Scalar(v.coefficient(e_1)) * e_1
            + Scalar(rotated.coefficient(g2.e_1)) * e_2
            + Scalar(rotated.coefficient(g2.e_2)) * e_3
        )

    # (cos, sin) to swing a onto e_1, read straight off a's coordinates.
    a_1: Real = a.coefficient(e_1)
    a_2: Real = a.coefficient(e_2)
    a_3: Real = a.coefficient(e_3)
    a_xy_magnitude: Real = (Scalar(a_1) * e_1 + Scalar(a_2) * e_2).magnitude()
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
    yz_magnitude: Real = (
        Scalar(b_aligned_2) * e_2 + Scalar(b_aligned_3) * e_3
    ).magnitude()
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
    b_reduced: Vector = reduce_to_plane(b)  # (b'_1, b'_2, 0)
    # In the reduced frame the cross product is the pure e_3 vector (0, 0, |a| * b'_2).
    reduced_x: Real = a_reduced.coefficient(e_1)
    reduced_y: Real = b_reduced.coefficient(e_2)
    cross_in_frame: Vector = (Scalar(reduced_x * reduced_y)) * e_3
    return rotate_back(cross_in_frame)


# %% [markdown]
# ## The vectors
#
# $a = 3 * e_1 + 4 * e_2 + 12 * e_3$ has an exact length: its $xy$-shadow has length
# $5$ and $|a| = 13$, so the two rotations that align $a$ have rational cosines and
# sines. $b$ is fully symbolic, so the check holds for every $b$.

# %%
a_exact: Vector = 3 * e_1 + 4 * e_2 + 12 * e_3
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
b_symbolic: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2 + Scalar(b_3) * e_3

# %% [markdown]
# The construction's result:

# %%
by_standard_position: MultiVectorBase = cross_via_standard_position(
    a_exact, b_symbolic
).simplified()
by_standard_position

# %% [markdown]
# ## Check
#
# The third rotation brings in $\sqrt{b_2'^2 + b_3'^2}$, which cancels on the way
# back. The difference from gacalc's cross product is $0$, so the construction gives
# $a \times b$ for every $b$:

# %%
(by_standard_position - cross(a_exact, b_symbolic)).simplified()
