# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # The reciprocal frame — calculations
#
# Companion to the *Proof: The Reciprocal Frame* chapter. Each section checks one of
# its eight theorems with gacalc and sympy: in the plane for a fully general frame
# (every coordinate its own symbol), and in space for one oblique frame with a fully
# general vector. A result is checked by subtracting the two sides and simplifying
# every coordinate of the difference to zero.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame, InverseMethod, reciprocal_frame
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, e_1, e_2


# %%
def simplified(value: MultiVectorBase) -> list[sympy.Expr]:
    """Every coordinate of ``value``, simplified."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in value]


def simplified_scalar(value: Real) -> sympy.Expr:
    """A number or expression, simplified."""
    return sympy.simplify(sympy.sympify(value))


# %% [markdown]
# ## A general frame in the plane
#
# Two vectors $a_1$ and $a_2$, every coordinate a symbol, and a general vector $y$
# with coordinates $x_1, x_2$ in that frame: $y = x_1 * a_1 + x_2 * a_2$. The only
# assumption is that the frame is a frame: $a_1 \wedge a_2 \neq 0$.

# %%
p: sympy.Symbol
q: sympy.Symbol
r: sympy.Symbol
t: sympy.Symbol
x_1: sympy.Symbol
x_2: sympy.Symbol
p, q, r, t, x_1, x_2 = sympy.symbols("p q r t x_1 x_2", real=True)
a_1: MultiVectorBase = Scalar(p) * e_1 + Scalar(q) * e_2
a_2: MultiVectorBase = Scalar(r) * e_1 + Scalar(t) * e_2
frame: list[MultiVectorBase] = [a_1, a_2]
y: MultiVectorBase = Scalar(x_1) * a_1 + Scalar(x_2) * a_2
a_1 ^ a_2  # the signed area, nonzero for a frame

# %% [markdown]
# ## Theorem 1: eq 3.7, the definition
#
# $a^1 = a_2 * (a_1 \wedge a_2)^{-1}$ and $a^2 = -1 * a_1 * (a_1 \wedge a_2)^{-1}$:
# each frame vector's face (the wedge of the others) divided by the area.
# `reciprocal_frame` builds the same two vectors.

# %%
A_2: MultiVectorBase = a_1 ^ a_2
upper_1: MultiVectorBase = a_2 * A_2.inverse()
upper_2: MultiVectorBase = -1 * (a_1 * A_2.inverse())
reciprocal: list[MultiVectorBase] = reciprocal_frame(frame)
[simplified(upper_1 - reciprocal[0]), simplified(upper_2 - reciprocal[1])]

# %% [markdown]
# ## Theorem 2: each reciprocal vector is a vector
#
# The product of a vector and a bivector could have had a grade-3 part; in the plane
# it cannot, and in general the face lies inside the frame's space, so only grade 1
# survives.

# %%
[upper.grades() for upper in reciprocal]  # -> [[1], [1]]

# %% [markdown]
# ## Theorem 3: eq 3.5, the Kronecker delta
#
# $a^k \cdot a_j$ is $1$ when $j = k$ and $0$ otherwise: the table is the identity.

# %%
[
    [simplified_scalar(upper.dot(lower).scalar_part()) for lower in frame]
    for upper in reciprocal
]  # -> [[1, 0], [0, 1]]

# %% [markdown]
# ## Theorem 4: eq 3.4, reconstruction
#
# Each coordinate is one dot product, $x_k = a^k \cdot y$, and the vector is the sum
# of its coordinates times the frame: $y = \sum_k (a^k \cdot y) * a_k$.

# %%
[simplified_scalar(upper.dot(y).scalar_part()) for upper in reciprocal]  # -> [x_1, x_2]

# %%
rebuilt: MultiVectorBase = sum(
    [
        Scalar(upper.dot(y).scalar_part()) * lower
        for upper, lower in zip(reciprocal, frame)
    ],
    start=0 * e_1,
)
simplified(rebuilt - y)  # -> [0, 0]

# %% [markdown]
# ## Theorem 5: similar right triangles
#
# Take any vector $m$ perpendicular to $a_2$. Every term of $y$ but $x_1 * a_1$ adds
# no height along $m$, so $x_1 = (m \cdot y) / (m \cdot a_1)$: the height of $y$
# above $a_2$'s line over the height of $a_1$. In the plane the quarter turn of
# $a_2$ is such an $m$.

# %%
m: MultiVectorBase = a_2.rotate_90_degrees()
simplified_scalar(m.dot(a_2).scalar_part())  # -> 0: m is perpendicular to a_2

# %%
height_of_y: Real = m.dot(y).scalar_part()
height_of_a_1: Real = m.dot(a_1).scalar_part()
simplified_scalar(height_of_y / height_of_a_1)  # -> x_1

# %% [markdown]
# Folding that division into the vector gives the reciprocal vector:
# $a^1 = m / (m \cdot a_1)$, whatever the length of $m$.

# %%
simplified(Scalar(1 / height_of_a_1) * m - reciprocal[0])  # -> [0, 0]

# %% [markdown]
# ## Theorem 6: the last reciprocal vector is the last rejection over its length squared
#
# $w_2$ is $a_2$ with its part along $a_1$ rejected, so it is perpendicular to $a_1$,
# and $a^2 = w_2 / |w_2|^2$.

# %%
w_2: MultiVectorBase = Frame(tuple(frame)).orthogonal_vectors()[-1]
simplified_scalar(w_2.dot(a_1).scalar_part())  # -> 0

# %%
simplified(Scalar(1 / w_2.magnitude_squared()) * w_2 - reciprocal[1])  # -> [0, 0]

# %% [markdown]
# ## Theorems 7 and 8: both inverses undo the frame's map, and they agree
#
# `Frame.to_invertible_function` sends $e_i \mapsto a_i$. Its inverse reads the
# coordinates either with the reciprocal frame or by peeling the frame from its last
# vector. Both round trips are the identity, and the two inverses give the same
# answer on a general vector.

# %%
by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
x: MultiVectorBase = Scalar(x_1) * e_1 + Scalar(x_2) * e_2
[
    simplified(by_reciprocal.inverse(by_reciprocal(x)) - x),
    simplified(by_peel.inverse(by_peel(x)) - x),
    simplified(by_reciprocal(by_reciprocal.inverse(y)) - y),
    simplified(by_peel(by_peel.inverse(y)) - y),
]  # -> four [0, 0]

# %%
simplified(by_reciprocal.inverse(y) - by_peel.inverse(y))  # -> [0, 0]

# %% [markdown]
# ## In space
#
# The same checks for the oblique frame $b_1 = 2 * e_1$, $b_2 = 1 * e_1 + 3 * e_2$,
# $b_3 = 1 * e_1 + 1 * e_2 + 2 * e_3$ and a fully general vector $z$. Now the face
# of each frame vector is a plane, eq 3.7 divides it by the volume
# $b_1 \wedge b_2 \wedge b_3$, and the last rejection $w_3$ is $b_3$'s height above
# the plane of $b_1$ and $b_2$.

# %%
z_1: sympy.Symbol
z_2: sympy.Symbol
z_3: sympy.Symbol
z_1, z_2, z_3 = sympy.symbols("z_1 z_2 z_3", real=True)
b_1: MultiVectorBase = 2 * g3.e_1
b_2: MultiVectorBase = 1 * g3.e_1 + 3 * g3.e_2
b_3: MultiVectorBase = 1 * g3.e_1 + 1 * g3.e_2 + 2 * g3.e_3
space_frame: list[MultiVectorBase] = [b_1, b_2, b_3]
z: MultiVectorBase = (
    g3.Scalar(z_1) * g3.e_1 + g3.Scalar(z_2) * g3.e_2 + g3.Scalar(z_3) * g3.e_3
)
space_reciprocal: list[MultiVectorBase] = reciprocal_frame(space_frame)
space_reciprocal  # theorem 1, eq 3.7

# %%
[upper.grades() for upper in space_reciprocal]  # theorem 2 -> [[1], [1], [1]]

# %%
[
    [simplified_scalar(upper.dot(lower).scalar_part()) for lower in space_frame]
    for upper in space_reciprocal
]  # theorem 3 -> the 3 by 3 identity

# %%
space_rebuilt: MultiVectorBase = sum(
    [
        g3.Scalar(upper.dot(z).scalar_part()) * lower
        for upper, lower in zip(space_reciprocal, space_frame)
    ],
    start=0 * g3.e_1,
)
simplified(space_rebuilt - z)  # theorem 4 -> [0, 0, 0]

# %%
n: MultiVectorBase = (b_2 ^ b_3).dual()  # theorem 5: a normal to b_1's face
simplified(
    g3.Scalar(sympy.Integer(1) / n.dot(b_1).scalar_part()) * n - space_reciprocal[0]
)  # -> [0, 0, 0]

# %%
w_3: MultiVectorBase = Frame(tuple(space_frame)).orthogonal_vectors()[-1]
simplified(
    g3.Scalar(sympy.Integer(1) / w_3.magnitude_squared()) * w_3 - space_reciprocal[2]
)  # theorem 6 -> [0, 0, 0]

# %%
space_by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
space_by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
[
    simplified(space_by_reciprocal.inverse(space_by_reciprocal(z)) - z),
    simplified(space_by_peel.inverse(space_by_peel(z)) - z),
    simplified(space_by_reciprocal(space_by_reciprocal.inverse(z)) - z),
    simplified(space_by_peel(space_by_peel.inverse(z)) - z),
    simplified(space_by_reciprocal.inverse(z) - space_by_peel.inverse(z)),
]  # theorems 7 and 8 -> five [0, 0, 0]
