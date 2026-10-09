# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Rotate from a to b — calculations
#
# Companion to the *Proof: Rotate from the Direction of a to the Direction of b*
# chapter. The coordinate checks that chapter leans on, run with the coordinates left
# as symbols so each holds for *every* vector and *every* angle, not just the ones we
# happened to draw:
#
# 1. **2D rotations commute** — the fact that lets the three-turn sandwich collapse to
#    its middle turn;
# 2. **the sandwich really does collapse** — align `a` to the x-axis, rotate, un-align,
#    and compare with the single rotation the chapter ends with; and
# 3. **that single rotation carries `a` to `b`'s direction**, with its cosine and sine
#    read off the coordinates of `a` and `b` — no angle ever named.
#
# Only the plain 2D rotation of *Proof: Rotate* is used — no dot product, no geometric
# product.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Vector, e_1, e_2

v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = v_1 * e_1 + v_2 * e_2


def rotate(v: Vector, theta: Real) -> Vector:
    """The rotation of *Proof: Rotate* on the (e_1, e_2) components: r(v; theta)."""
    x: Real = v.coefficient(e_1)
    y: Real = v.coefficient(e_2)
    return (sympy.cos(theta) * x - sympy.sin(theta) * y) * e_1 + (
        sympy.sin(theta) * x + sympy.cos(theta) * y
    ) * e_2


# %% [markdown]
# ## 1. Rotations commute (in 2D)
#
# Rotate by `theta_1` then by `theta_2`, and by `theta_2` then by `theta_1`. The chapter
# expands both by hand with the angle-addition identities; here sympy does the
# expanding. Each order is the single rotation by `theta_1 + theta_2`, so the two agree.

# %%
theta_1: sympy.Symbol
theta_2: sympy.Symbol
theta_1, theta_2 = sympy.symbols("theta_1 theta_2", real=True)

first_then_second: Vector = rotate(rotate(v, theta_1), theta_2)
second_then_first: Vector = rotate(rotate(v, theta_2), theta_1)
first_then_second.symbolically_equal(second_then_first)  # -> True

# %%
# ...and each is the single rotation by the angle sum.
first_then_second.symbolically_equal(rotate(v, theta_1 + theta_2))  # -> True

# %% [markdown]
# The chapter's three turns are not written with angles but with a cosine and a sine
# read off a vector. Here is the same fact in that form. The two sides are equal *as
# polynomials* in the four numbers — no unit constraint needed.

# %%
c_1: sympy.Symbol
s_1: sympy.Symbol
c_2: sympy.Symbol
s_2: sympy.Symbol
c_1, s_1, c_2, s_2 = sympy.symbols("c_1 s_1 c_2 s_2", real=True)


def rotate_cs(v: Vector, cos: Real, sin: Real) -> Vector:
    """The same rotation, given its cosine and sine instead of its angle."""
    x: Real = v.coefficient(e_1)
    y: Real = v.coefficient(e_2)
    return (cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2


rotate_cs(rotate_cs(v, c_1, s_1), c_2, s_2) == rotate_cs(
    rotate_cs(v, c_2, s_2), c_1, s_1
)

# %% [markdown]
# ## 2. The sandwich collapses
#
# Build the chapter's three turns for a general `a` and compare the composite with the
# single rotation the chapter ends with. We keep `a` fully symbolic and pick a `b` with
# an exact length (`3 * e_1 + 4 * e_2`, `|b| = 5`) so the square roots stay clean; `|a|`
# stays symbolic.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2", real=True, positive=True)
a: Vector = a_1 * e_1 + a_2 * e_2
b: Vector = 3 * e_1 + 4 * e_2
magnitude_a: Real = a.magnitude()
magnitude_b: Real = b.magnitude()

# Step 1: swing a onto the x-axis (cos(-β) = a_1/|a|, sin(-β) = -a_2/|a|). It lands on
# |a| * e_1.
cos_1: Real = a_1 / magnitude_a
sin_1: Real = -a_2 / magnitude_a
rotate_cs(a, cos_1, sin_1).symbolically_equal(magnitude_a * e_1)  # -> True

# %%
# b rides along to b'. Step 2 reads its cosine and sine off b' (|b'| = |b|: rotations
# keep lengths).
b_prime: Vector = rotate_cs(b, cos_1, sin_1)
cos_2: Real = b_prime.coefficient(e_1) / magnitude_b
sin_2: Real = b_prime.coefficient(e_2) / magnitude_b

# Step 3 undoes step 1 (same cosine, sine negated). Apply all three to a general v.
three_turns: Vector = rotate_cs(
    rotate_cs(rotate_cs(v, cos_1, sin_1), cos_2, sin_2), cos_1, -sin_1
)

# The chapter's single rotation, with cos and sin written in the coordinates of a and b.
cos_ab: Real = (a_1 * 3 + a_2 * 4) / (magnitude_a * magnitude_b)
sin_ab: Real = (a_1 * 4 - a_2 * 3) / (magnitude_a * magnitude_b)
one_turn: Vector = rotate_cs(v, cos_ab, sin_ab)

three_turns.symbolically_equal(
    one_turn
)  # -> True: the sandwich collapses to its middle

# %% [markdown]
# ## 3. The collapsed rotation carries `a` to `b`'s direction
#
# Applied to `a` itself, the single rotation should land on `b`'s direction with `a`'s
# own length: `(|a| / |b|) b`.

# %%
carried: Vector = rotate_cs(a, cos_ab, sin_ab)
carried.symbolically_equal((magnitude_a / magnitude_b) * b)  # -> True
