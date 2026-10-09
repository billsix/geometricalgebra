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

from gacalc.g2 import Vector, e_1, e_2

a_x: sympy.Symbol
a_y: sympy.Symbol
b_x: sympy.Symbol
b_y: sympy.Symbol
a_x, a_y, b_x, b_y = sympy.symbols("a_x a_y b_x b_y", real=True)
a: Vector = a_x * e_1 + a_y * e_2
b: Vector = b_x * e_1 + b_y * e_2

a + b  # the coordinates add: (a_x + b_x) e_1 + (a_y + b_y) e_2

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
