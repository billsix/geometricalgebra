# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Vector Addition — calculations
#
# You already know that $3 + 5 = 5 + 3$. The chapter's pictures say that $a + b$ and
# $b + a$ land on the same corner of the parallelogram. Here is the same fact in
# coordinates: adding two vectors adds their coordinates, and each coordinate is a sum
# of two ordinary numbers, which gives the same answer in either order. The coordinates
# are left as symbols, so it holds for every $a$ and $b$. Each check cell subtracts two
# things and shows the difference, $0$ when they agree.

# %%
import sympy

from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.transforms import translate

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2

# %% [markdown]
# ## $a + b = b + a$
#
# Before running the next two cells, predict each coordinate of $a + b$ and of
# $b + a$.

# %%
a + b

# %%
b + a

# %% [markdown]
# Each coordinate is the same two numbers added in the other order:

# %%
(a + b) - (b + a)

# %% [markdown]
# ## Subtraction
#
# The chapter's second pair of pictures: $a - b$ is what you add to $b$ to get back
# $a$,

# %%
((a - b) + b) - a

# %% [markdown]
# and it is the same as adding the opposite, $a + (-b)$:

# %%
(a - b) - (a + (-b))

# %% [markdown]
# ## Translate: adding the same vector to everything
#
# Fix $b$ and let the other input vary, and $+$ becomes a one-input machine,
# `translate(b=b)`: feed it any point $v$, get $v + b$. This is **partial binding**:
# one of the two blanks of $+$ filled in. It moves every point the same way, so
# applying it to the whole plane slides the graph paper by $b$.

# %%
t: InvertibleFunction[Vector] = translate(b=b)
t

# %% [markdown]
# Applied to $a$, it gives the one-off sum $a + b$:

# %%
t(a) - (a + b)

# %% [markdown]
# It moves every point by the same $b$. The two basis vectors:

# %%
[t(1 * e_1), t(1 * e_2)]

# %% [markdown]
# A whole sheet of graph paper, a 3 by 3 lattice of points, each slid by $b$. (No
# separate check is needed: $a$ above is symbolic, so $t(a) = a + b$ already covers
# every point.)

# %%
grid_points: list[Vector] = [i * e_1 + j * e_2 for i in range(3) for j in range(3)]
[t(point) for point in grid_points]

# %% [markdown]
# Its **inverse** is `translate(b=-b)`: sliding the paper back undoes the slide.

# %%
t.inverse(t(a)) - a

# %% [markdown]
# `t.at(0.5)` is the paper slid half way, $a + 0.5 * b$:

# %%
t.at(0.5)(a) - (a + b * 0.5)
