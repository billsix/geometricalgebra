# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Into Three Dimensions — calculations
#
# Part II starts again from the geometric product, now with three basis directions.
# In the plane, the product of two vectors split into a plain-number part, the dot
# product, and a bivector part, the wedge. The first thing to check is that it still
# splits that way in space. The code for the dot and the wedge is the same code as in
# 𝒢₂: nothing in `inner_product` or `outer_product` mentions the dimension. Every
# coordinate is a symbol, and numbers appear only to draw the figure. Each check shows
# both sides, then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _frame_scene import (
    ORIGIN3,
    PLANE_FILL,
    PendingFigure,
    Point,
    arrow,
    patch,
    point,
    scene_3d,
)

import gacalc.g3 as g3
from gacalc.base import Real
from gacalc.nbdisplay import at_values, show_mult

# %% [markdown]
# Two vectors in space, every coordinate a symbol:

# %%
p_1: sympy.Symbol
p_2: sympy.Symbol
p_3: sympy.Symbol
q_1: sympy.Symbol
q_2: sympy.Symbol
q_3: sympy.Symbol
p_1, p_2, p_3, q_1, q_2, q_3 = sympy.symbols("p_1 p_2 p_3 q_1 q_2 q_3", real=True)
p: g3.Vector = (
    g3.Scalar(p_1) * g3.Vector.e_1
    + g3.Scalar(p_2) * g3.Vector.e_2
    + g3.Scalar(p_3) * g3.Vector.e_3
)
p

# %% [markdown]
# and $\vec{\mathbf{q}}$:

# %%
q: g3.Vector = (
    g3.Scalar(q_1) * g3.Vector.e_1
    + g3.Scalar(q_2) * g3.Vector.e_2
    + g3.Scalar(q_3) * g3.Vector.e_3
)
q

# %% [markdown]
# The values used to draw the figure. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [
    (p_1, 2),
    (p_2, 0),
    (p_3, 1),
    (q_1, 0),
    (q_2, 2),
    (q_3, 1),
]

# %% [markdown]
# Drawn at the plot values: $\vec{\mathbf{p}}$, $\vec{\mathbf{q}}$, and the
# parallelogram they span, which the wedge measures.

# %%
P_P: Point = point(coordinates=list(at_values(p, values)))
P_Q: Point = point(coordinates=list(at_values(q, values)))
fig_pair: PendingFigure
with scene_3d(
    lower_left=Point(x=-2.6, y=-2.2), upper_right=Point(x=5.4, y=3.6)
) as fig_pair:
    patch(corners=[ORIGIN3, P_P, P_P + P_Q, P_Q], color=PLANE_FILL)
    arrow(head=P_P, text=r"$\vec{\mathbf{p}}$")
    arrow(head=P_Q, text=r"$\vec{\mathbf{q}}$")
fig_pair

# %% [markdown]
# ## The product
#
# The product term by term: nine pairs now, three of them a direction times itself.
# Those three rows add to the dot; the other six pair up,
# $\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j$ with
# $\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i$, into the three bivector parts of the wedge.
# First at the plot values:

# %%
show_mult(at_values(p, values), at_values(q, values))

# %% [markdown]
# Then with every coordinate a symbol:

# %%
show_mult(p, q)

# %% [markdown]
# The sum: a plain number plus three bivector parts, one for each coordinate plane.

# %%
product_3d: g3.Versor = p * q
product_3d

# %% [markdown]
# ## The two parts
#
# The grade-0 part, $\langle \vec{\mathbf{p}} * \vec{\mathbf{q}} \rangle_0$:

# %%
product_3d.r_vector_part(0)

# %% [markdown]
# The dot product, `p.inner_product(q)`:

# %%
p.inner_product(q)

# %% [markdown]
# Their difference:

# %%
product_3d.r_vector_part(0) - p.inner_product(q)

# %% [markdown]
# The grade-2 part, $\langle \vec{\mathbf{p}} * \vec{\mathbf{q}} \rangle_2$:

# %%
product_3d.r_vector_part(2)

# %% [markdown]
# The wedge, `p.outer_product(q)`:

# %%
p.outer_product(q)

# %% [markdown]
# Their difference:

# %%
product_3d.r_vector_part(2) - p.outer_product(q)
