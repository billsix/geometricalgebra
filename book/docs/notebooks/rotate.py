# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Rotate — a first example
#
# In precalculus a rotation is given by an angle. The chapter gives it instead by two
# directions: rotate from the direction of $\vec{\mathbf{a}}$ to the direction of
# $\vec{\mathbf{b}}$. Its two proofs build both: the rotation by an angle
# (`Vector.rotate`), and from it the rotation from one direction to another
# (`rotation_from_to(a, b)`), with no angle passed in. This notebook applies the second
# to symbolic vectors, so every result holds for every $\vec{\mathbf{a}}$ and
# $\vec{\mathbf{b}}$, then checks it against the first. Numbers appear only to draw the
# figures. Each check shows both sides, then their difference.

# %%
import pathlib
import sys

# The ePiX scene helpers live with the book's other figure sources.
sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))

import sympy
from _bootstrap_live import (
    BLACK,
    PURPLE,
    LabelPos,
    PendingFigure,
    Point,
    arrow,
    point,
    scene_around,
)

from gacalc.base import Real
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.nbdisplay import at_values
from gacalc.standardposition import rotation_from_to

# %% [markdown]
# ## The vectors
#
# $\vec{\mathbf{a}}$ and $\vec{\mathbf{b}}$, every coordinate a symbol:

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
a

# %% [markdown]
# and $\vec{\mathbf{b}}$:

# %%
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
b

# %% [markdown]
# The values used to draw the figures. Change them and rerun.

# %%
values: list[tuple[sympy.Symbol, Real]] = [(a_1, 3), (a_2, 1), (b_1, 1), (b_2, 2)]

# %% [markdown]
# The rotation from $\vec{\mathbf{a}}$'s direction to $\vec{\mathbf{b}}$'s:

# %%
rotate_a_to_b: InvertibleFunction[Vector] = rotation_from_to(a, b)
rotate_a_to_b

# %% [markdown]
# ## Rotating $\vec{\mathbf{a}}$ itself
#
# Applied to $\vec{\mathbf{a}}$, the rotation lands on $\vec{\mathbf{b}}$'s direction
# and keeps $\vec{\mathbf{a}}$'s length:

# %%
rotated: Vector = rotate_a_to_b(a).simplified()
rotated

# %% [markdown]
# At the plot values:

# %%
at_values(rotated, values)

# %% [markdown]
# Drawn at the plot values:

# %%
P_A: Point = point(coordinates=list(at_values(a, values)))
P_B: Point = point(coordinates=list(at_values(b, values)))
P_ROTATED: Point = point(coordinates=list(at_values(rotated, values)))
fig_rotated: PendingFigure
with scene_around(points=[P_A, P_B, P_ROTATED]) as fig_rotated:
    arrow(head=P_A, color=BLACK, text=r"$\vec{\mathbf{a}}$")
    arrow(
        head=P_ROTATED,
        color=PURPLE,
        text=r"$R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{a}})$",
    )
    arrow(
        head=P_B,
        color=BLACK,
        text=r"$\vec{\mathbf{b}}$",
        offset=Point(x=8, y=-6),
        align=LabelPos.br,
    )
fig_rotated

# %% [markdown]
# $\vec{\mathbf{b}}$'s direction at $\vec{\mathbf{a}}$'s length is
# $(|\vec{\mathbf{a}}| / |\vec{\mathbf{b}}|) * \vec{\mathbf{b}}$:

# %%
a_length_along_b: Vector = (Scalar(a.magnitude() / b.magnitude()) * b).simplified()
a_length_along_b

# %% [markdown]
# Its difference from the rotated $\vec{\mathbf{a}}$:

# %%
(rotated - a_length_along_b).simplified()

# %% [markdown]
# ## The lengths don't matter
#
# Rotating from $p * \vec{\mathbf{a}}$ toward $q * \vec{\mathbf{b}}$, for positive
# numbers $p$ and $q$, is the same rotation, so it moves any vector, here
# $\vec{\mathbf{e}}_1$, to the same place. The rotation from $\vec{\mathbf{a}}$ to
# $\vec{\mathbf{b}}$ moves $\vec{\mathbf{e}}_1$ to:

# %%
p: sympy.Symbol
q: sympy.Symbol
p, q = sympy.symbols("p q", positive=True)
rotate_scaled: InvertibleFunction[Vector] = rotation_from_to(
    Scalar(p) * a, Scalar(q) * b
)
rotate_a_to_b(1 * e_1).simplified()

# %% [markdown]
# The rotation from $p * \vec{\mathbf{a}}$ to $q * \vec{\mathbf{b}}$ moves it to:

# %%
rotate_scaled(1 * e_1).simplified()

# %% [markdown]
# Their difference:

# %%
(rotate_a_to_b(1 * e_1) - rotate_scaled(1 * e_1)).simplified()

# %% [markdown]
# ## The angle is still there, as a property
#
# The same rotation, given by the angle $\theta$ from $\vec{\mathbf{a}}$ to
# $\vec{\mathbf{b}}$, agrees. We never needed $\theta$ to build the rotation above; here
# we compute it only to check, as the angle of $\vec{\mathbf{b}}$ minus the angle of
# $\vec{\mathbf{a}}$:

# %%
theta: Real = sympy.atan2(b_2, b_1) - sympy.atan2(a_2, a_1)
theta

# %% [markdown]
# A general vector $\vec{\mathbf{v}}$:

# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
v

# %% [markdown]
# rotated by the angle $\theta$:

# %%
v.rotate(theta).simplified()

# %% [markdown]
# and by the rotation from $\vec{\mathbf{a}}$ to $\vec{\mathbf{b}}$:

# %%
rotate_a_to_b(v).simplified()

# %% [markdown]
# Their difference:

# %%
(v.rotate(theta) - rotate_a_to_b(v)).simplified()
