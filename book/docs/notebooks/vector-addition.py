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
# The chapter's pictures say that `a + b` and `b + a` land on the same corner of the
# parallelogram. Here is the same fact in coordinates, with the coordinates left as
# symbols so it holds for *every* `a` and `b`: adding two vectors adds their
# coordinates, and adding two ordinary numbers gives the same answer in either order.

# %%
import sympy

from gacalc.functions import InvertibleFunction
from gacalc.g2 import Vector, e_1, e_2
from gacalc.transforms import translate

a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = a_1 * e_1 + a_2 * e_2
b: Vector = b_1 * e_1 + b_2 * e_2

a + b  # the coordinates add: (a_1 + b_1) * e_1 + (a_2 + b_2) * e_2

# %%
b + a  # the same two coordinates — each a sum of two numbers, in the other order

# %%
a + b == b + a  # -> True

# %% [markdown]
# The chapter's second pair of pictures: `a - b` is what you add to `b` to get back `a`,
# and it is the same as adding the opposite, `a + (-b)`. Both hold coordinate by
# coordinate.

# %%
(a - b) + b == a  # -> True

# %%
a - b == a + (-b)  # -> True

# %% [markdown]
# ## Translate: adding the same vector to everything
#
# Fix `b` and let the other input vary, and `+` becomes a one-input machine
# `translate(b)`: feed it any point `v`, get `v + b`. This is **partial binding** --
# one of the two blanks of `+` filled in. It moves *every* point the same way, so
# applying it to the whole plane slides the graph paper by `b`.

# %%
t: InvertibleFunction[Vector] = translate(b=b)

# applied to a: the one-off a + b, now produced by the machine
t(a) == a + b  # -> True

# %%
# it moves every point by the same b -- here the two basis vectors
[t(e_1), t(e_2)]  # -> [e_1 + b, e_2 + b]

# %%
# the whole sheet of graph paper: a lattice of points, each slid by b
grid_points: list[Vector] = [i * e_1 + j * e_2 for i in range(3) for j in range(3)]
translated: list[Vector] = [t(point) for point in grid_points]
all(moved == point + b for moved, point in zip(translated, grid_points))  # -> True

# %% [markdown]
# Its **inverse** is `translate(-b)`: sliding the paper back undoes the slide. And
# `.at(0.5)` is the paper slid half way (the interpolation `translate(b * t)`).

# %%
# `inverse` is the inverse function itself (a callable), so apply it directly.
t.inverse(t(a)) == a  # -> True

# %%
halfway: Vector = t.at(0.5)(a)
halfway == a + b * 0.5  # -> True
