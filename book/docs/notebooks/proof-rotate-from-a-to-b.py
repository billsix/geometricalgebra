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
# chapter. In precalculus, rotating by $\theta_1$ and then by $\theta_2$ is rotating by
# $\theta_1 + \theta_2$: the angles add. The chapter builds a rotation from $a$'s
# direction to $b$'s in three turns and uses that fact to collapse them into one. This
# notebook checks each step with the coordinates left as symbols, so it holds for every
# vector and every angle:
#
# 1. **2D rotations commute**, which lets the three turns collapse to the middle one;
# 2. **the three turns are one rotation**, whose cosine and sine are read off the
#    coordinates of $a$ and $b$; and
# 3. **that rotation carries $a$ to $b$'s direction**.
#
# Only the plain 2D rotation of *Proof: Rotate* is used, no dot product and no
# geometric product. Each check cell subtracts two things and shows the difference,
# $0$ when they agree.

# %%
import sympy

from gacalc.base import Real
from gacalc.g2 import Scalar, Vector, e_1, e_2

# %% [markdown]
# A general vector $v$ to rotate, every coordinate a symbol:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2

# %% [markdown]
# The rotation of *Proof: Rotate*:
#
# $$r(v; \theta) = \cos(\theta) * v + \sin(\theta) * r(v; \pi/2)$$


# %%
def rotate(v: Vector, theta: Real) -> Vector:
    """``r(v; theta) = cos(theta) * v + sin(theta) * r(v; pi/2)``."""
    return v.rotate(theta)


# %% [markdown]
# ## 1. Rotations commute (in 2D)
#
# Rotate by $\theta_1$ then by $\theta_2$, and in the other order. The chapter expands
# both by hand with the angle-addition identities; here sympy does the expanding.

# %%
theta_1: sympy.Symbol
theta_2: sympy.Symbol
theta_1, theta_2 = sympy.symbols("theta_1 theta_2", real=True)
first_then_second: Vector = rotate(rotate(v, theta_1), theta_2)
second_then_first: Vector = rotate(rotate(v, theta_2), theta_1)
(first_then_second - second_then_first).simplified()

# %% [markdown]
# Each order is the single rotation by $\theta_1 + \theta_2$:

# %%
(first_then_second - rotate(v, theta_1 + theta_2)).simplified()

# %% [markdown]
# The chapter's three turns are given not by angles but by a cosine $c$ and a sine $s$
# read off a vector. The same fact holds in that form, and the two sides are equal as
# polynomials in $c_1, s_1, c_2, s_2$, with no need for $c^2 + s^2 = 1$.

# %%
c_1: sympy.Symbol
s_1: sympy.Symbol
c_2: sympy.Symbol
s_2: sympy.Symbol
c_1, s_1, c_2, s_2 = sympy.symbols("c_1 s_1 c_2 s_2", real=True)


def rotate_cs(v: Vector, cos: Real, sin: Real) -> Vector:
    """The same rotation, given its cosine and sine instead of its angle."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


(
    rotate_cs(rotate_cs(v, c_1, s_1), c_2, s_2)
    - rotate_cs(rotate_cs(v, c_2, s_2), c_1, s_1)
).simplified()

# %% [markdown]
# ## 2. The three turns are one rotation
#
# Now a general $a$, and a $b$ with an exact length, $b = 3 * e_1 + 4 * e_2$ with
# $|b| = 5$, so the square roots stay short. $|a|$ stays symbolic.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
a_1, a_2 = sympy.symbols("a_1 a_2", real=True, positive=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = 3 * e_1 + 4 * e_2
magnitude_a: Real = a.magnitude()
magnitude_b: Real = b.magnitude()

# %% [markdown]
# **Turn 1** swings $a$ onto the x-axis, with $\cos(-\beta) = a_1 / |a|$ and
# $\sin(-\beta) = -a_2 / |a|$, $\beta$ the angle of $a$. It lands on $|a| * e_1$:

# %%
cos_1: Real = a_1 / magnitude_a
sin_1: Real = -a_2 / magnitude_a
(rotate_cs(a, cos_1, sin_1) - Scalar(magnitude_a) * e_1).simplified()

# %% [markdown]
# **Turn 2.** $b$ rides along to $b'$, and the middle turn reads its cosine and sine
# off $b'$. Rotations keep lengths, so $|b'| = |b|$.

# %%
b_prime: Vector = rotate_cs(b, cos_1, sin_1)
cos_2: Real = b_prime.coefficient(e_1) / magnitude_b
sin_2: Real = b_prime.coefficient(e_2) / magnitude_b
b_prime.simplified()

# %% [markdown]
# **Turn 3** undoes turn 1: the same cosine, the sine negated. The three turns, applied
# to the general $v$:

# %%
three_turns: Vector = rotate_cs(
    rotate_cs(rotate_cs(v, cos_1, sin_1), cos_2, sin_2), cos_1, -sin_1
)

# %% [markdown]
# The chapter's single rotation has its cosine and sine written in the coordinates of
# $a$ and $b$:
#
# $$\cos(\theta) = \frac{3 * a_1 + 4 * a_2}{|a| * |b|}, \qquad
# \sin(\theta) = \frac{4 * a_1 - 3 * a_2}{|a| * |b|}.$$

# %%
cos_ab: Real = (a_1 * 3 + a_2 * 4) / (magnitude_a * magnitude_b)
sin_ab: Real = (a_1 * 4 - a_2 * 3) / (magnitude_a * magnitude_b)
one_turn: Vector = rotate_cs(v, cos_ab, sin_ab)

# %% [markdown]
# The three turns are that one rotation:

# %%
(three_turns - one_turn).simplified()

# %% [markdown]
# ## 3. The rotation carries $a$ to $b$'s direction
#
# Applied to $a$ itself, the single rotation lands on $b$'s direction with $a$'s own
# length, $(|a| / |b|) * b$:

# %%
(rotate_cs(a, cos_ab, sin_ab) - Scalar(magnitude_a / magnitude_b) * b).simplified()
