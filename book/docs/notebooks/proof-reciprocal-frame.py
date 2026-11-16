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
# Companion to the *Proof: The Reciprocal Frame* chapter. On graph paper, the
# coordinates of a point are read off the two axes. The reciprocal frame does the same
# for slanted axes $a_1, a_2$: one dot product per coordinate, $x_k = a^k \cdot y$.
# Each section below checks one of the chapter's eight theorems, first in the plane for
# a fully general frame (every coordinate its own symbol), then in space for one slanted
# frame and a fully general vector. Each check cell subtracts the two sides and shows
# the difference, $0$ when they agree.

# %%
import sympy

import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, Real
from gacalc.frame import Frame, InverseMethod, reciprocal_frame
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, e_1, e_2

# %% [markdown]
# ## A general frame in the plane
#
# Two vectors $a_1$ and $a_2$, every coordinate a symbol, and a general vector $y$
# with coordinates $x_1, x_2$ in that frame: $y = x_1 * a_1 + x_2 * a_2$. The only
# assumption is that the frame is a frame: its signed area $a_1 \wedge a_2$ is not
# $0$.

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
a_1 ^ a_2

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
(upper_1 - reciprocal[0]).simplified()

# %%
(upper_2 - reciprocal[1]).simplified()

# %% [markdown]
# ## Theorem 2: each reciprocal vector is a vector
#
# A vector times a bivector could have a grade-3 part. In the plane it cannot, and in
# general the face lies inside the frame's space, so only grade 1 is left. The grades
# present in $a^1$ and in $a^2$:

# %%
[upper.grades() for upper in reciprocal]

# %% [markdown]
# ## Theorem 3: eq 3.5, the Kronecker delta
#
# $a^k \cdot a_j$ is $1$ when $j = k$ and $0$ otherwise. The table of all four dot
# products, row $k$ and column $j$:

# %%
sympy.Matrix(
    [
        [
            sympy.simplify(sympy.sympify(upper.dot(lower).scalar_part()))
            for lower in frame
        ]
        for upper in reciprocal
    ]
)

# %% [markdown]
# ## Theorem 4: eq 3.4, reconstruction
#
# Each coordinate is one dot product, $x_k = a^k \cdot y$:

# %%
(Scalar(reciprocal[0].dot(y).scalar_part()) - Scalar(x_1)).simplified()

# %%
(Scalar(reciprocal[1].dot(y).scalar_part()) - Scalar(x_2)).simplified()

# %% [markdown]
# and the vector is the sum of its coordinates times the frame,
# $y = \sum_k (a^k \cdot y) * a_k$:

# %%
rebuilt: MultiVectorBase = sum(
    [
        Scalar(upper.dot(y).scalar_part()) * lower
        for upper, lower in zip(reciprocal, frame)
    ],
    start=0 * e_1,
)
(rebuilt - y).simplified()

# %% [markdown]
# ## Theorem 5: similar right triangles
#
# Take any vector $m$ perpendicular to $a_2$. Every term of $y$ but $x_1 * a_1$ adds
# no height along $m$, so $x_1 = (m \cdot y) / (m \cdot a_1)$: the height of $y$
# above $a_2$'s line over the height of $a_1$. In the plane the quarter turn of $a_2$
# is such an $m$. It is perpendicular to $a_2$:

# %%
m: MultiVectorBase = a_2.rotate_90_degrees()
m.dot(a_2).simplified()

# %% [markdown]
# The ratio of the two heights is $x_1$:

# %%
height_of_y: Real = m.dot(y).scalar_part()
height_of_a_1: Real = m.dot(a_1).scalar_part()
(Scalar(height_of_y / height_of_a_1) - Scalar(x_1)).simplified()

# %% [markdown]
# Folding that division into the vector gives the reciprocal vector,
# $a^1 = m / (m \cdot a_1)$, whatever the length of $m$:

# %%
(Scalar(1 / height_of_a_1) * m - reciprocal[0]).simplified()

# %% [markdown]
# ## Theorem 6: the last reciprocal vector is the last rejection over its length squared
#
# $w_2$ is $a_2$ with its part along $a_1$ rejected, so it is perpendicular to $a_1$:

# %%
w_2: MultiVectorBase = Frame(tuple(frame)).orthogonal_vectors()[-1]
w_2.dot(a_1).simplified()

# %% [markdown]
# and $a^2 = w_2 / |w_2|^2$:

# %%
(Scalar(1 / w_2.magnitude_squared()) * w_2 - reciprocal[1]).simplified()

# %% [markdown]
# ## Theorems 7 and 8: both inverses undo the frame's map, and they agree
#
# `Frame.to_invertible_function` sends $e_i \mapsto a_i$. Its inverse reads the
# coordinates either with the reciprocal frame or by peeling the frame from its last
# vector. Each round trip is the identity, and the two inverses agree on a general
# vector.

# %%
by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
x: MultiVectorBase = Scalar(x_1) * e_1 + Scalar(x_2) * e_2

# %% [markdown]
# The map, then the reciprocal-frame inverse, gives $x$ back:

# %%
(by_reciprocal.inverse(by_reciprocal(x)) - x).simplified()

# %% [markdown]
# and so does the peeling inverse:

# %%
(by_peel.inverse(by_peel(x)) - x).simplified()

# %% [markdown]
# The other order, inverse then map, gives $y$ back, for both inverses:

# %%
(by_reciprocal(by_reciprocal.inverse(y)) - y).simplified()

# %%
(by_peel(by_peel.inverse(y)) - y).simplified()

# %% [markdown]
# The two inverses agree:

# %%
(by_reciprocal.inverse(y) - by_peel.inverse(y)).simplified()

# %% [markdown]
# ## In space
#
# The same checks for the slanted frame $b_1 = 2 * e_1$, $b_2 = 1 * e_1 + 3 * e_2$,
# $b_3 = 1 * e_1 + 1 * e_2 + 2 * e_3$ and a fully general vector $z$. Now the face of
# each frame vector is a plane, eq 3.7 divides it by the volume
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

# %% [markdown]
# Theorem 1, eq 3.7: the reciprocal frame.

# %%
space_reciprocal: list[MultiVectorBase] = reciprocal_frame(space_frame)
space_reciprocal

# %% [markdown]
# Theorem 2: each is a vector. The grades present in each:

# %%
[upper.grades() for upper in space_reciprocal]

# %% [markdown]
# Theorem 3: the table of dot products $b^k \cdot b_j$ is the identity:

# %%
sympy.Matrix(
    [
        [
            sympy.simplify(sympy.sympify(upper.dot(lower).scalar_part()))
            for lower in space_frame
        ]
        for upper in space_reciprocal
    ]
)

# %% [markdown]
# Theorem 4: the coordinates times the frame rebuild $z$:

# %%
space_rebuilt: MultiVectorBase = sum(
    [
        g3.Scalar(upper.dot(z).scalar_part()) * lower
        for upper, lower in zip(space_reciprocal, space_frame)
    ],
    start=0 * g3.e_1,
)
(space_rebuilt - z).simplified()

# %% [markdown]
# Theorem 5: with $n$ a normal to $b_1$'s face (the dual of $b_2 \wedge b_3$),
# $b^1 = n / (n \cdot b_1)$:

# %%
n: MultiVectorBase = (b_2 ^ b_3).dual()
(
    g3.Scalar(sympy.Integer(1) / n.dot(b_1).scalar_part()) * n - space_reciprocal[0]
).simplified()

# %% [markdown]
# Theorem 6: $b^3 = w_3 / |w_3|^2$:

# %%
w_3: MultiVectorBase = Frame(tuple(space_frame)).orthogonal_vectors()[-1]
(
    g3.Scalar(sympy.Integer(1) / w_3.magnitude_squared()) * w_3 - space_reciprocal[2]
).simplified()

# %% [markdown]
# Theorems 7 and 8: both inverses undo the map, in both orders, and they agree.

# %%
space_by_reciprocal: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)
space_by_peel: InvertibleFunction[MultiVectorBase] = Frame(
    tuple(space_frame)
).to_invertible_function(inverse_method=InverseMethod.PEEL)
(space_by_reciprocal.inverse(space_by_reciprocal(z)) - z).simplified()

# %%
(space_by_peel.inverse(space_by_peel(z)) - z).simplified()

# %%
(space_by_reciprocal(space_by_reciprocal.inverse(z)) - z).simplified()

# %%
(space_by_peel(space_by_peel.inverse(z)) - z).simplified()

# %%
(space_by_reciprocal.inverse(z) - space_by_peel.inverse(z)).simplified()
