# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 6, rotation through the product — calculations
#
# Companion to *Step 6: Rotation, through the Product*. The rotation from `a` to `b`,
# applied to any `v`, three ways: Step 3's `cos(θ) * v + sin(θ) * r(v; π/2)` (the
# cosine and sine from `b` measured against `a`), the one-sided product
# `v * (a_hat * b_hat)`, and the sandwich `R * v * R⁻¹` with `R = b * a + |a| * |b|`.
# Each check prints zeros when it holds.

# %%
import sympy

from gacalc.base import MultiVectorBase, Real
from gacalc.g2 import Scalar, Vector, Versor, e_1, e_2, e_12
from gacalc.transforms import versor_rotation


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def rotation_from_to(a: Vector, b: Vector, v: Vector) -> Vector:
    """Step 3: ``b`` measured against ``a`` gives the cosine and sine of the angle from
    ``a`` to ``b``; the same angle applied to ``v``."""
    b_measured: Vector = rotate(
        a.coefficient(e_1) / a.magnitude(), -a.coefficient(e_2) / a.magnitude(), b
    )
    return rotate(
        b_measured.coefficient(e_1) / b.magnitude(),
        b_measured.coefficient(e_2) / b.magnitude(),
        v,
    )


def zeros(value: MultiVectorBase) -> list[sympy.Expr]:
    """Each coefficient of ``value``, simplified -- all zeros when it is zero."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in value]


# %%
v_1: sympy.Symbol
v_2: sympy.Symbol
v_1, v_2 = sympy.symbols("v_1 v_2", real=True)
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2

# %% [markdown]
# ## The quarter turn is a product: `v * e_12 = r(v; π/2)`

# %%
zeros(v * e_12 - v.rotate_90_degrees())  # -> [0, 0]

# %% [markdown]
# ## The one-sided form is Step 3's rotation
#
# For any `a` and `b` (all coordinates symbolic), right-multiplying `v` by the product
# of the unit vectors is Step 3's rotation of `v`, built from projection.

# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
one_sided: MultiVectorBase = v * (a.normalize() * b.normalize())
zeros(one_sided - rotation_from_to(a, b, v))  # -> [0, 0]

# %% [markdown]
# ## The other order turns the other way: it is the rotation from `b` to `a`

# %%
zeros((a.normalize() * b.normalize()) * v - rotation_from_to(b, a, v))  # -> [0, 0]

# %% [markdown]
# ## The sandwich
#
# `R = b * a + |a| * |b|` turns `a` halfway, onto the bisector
# `h = |b| * a + |a| * b` (scaled by `|a|`), and `R * v * R⁻¹` is the whole rotation.
# Exact vectors keep the square roots rational (`|a| = 5`, `|b| = 13`); `v` stays
# symbolic.

# %%
a_exact: Vector = 3 * e_1 + 4 * e_2
b_exact: Vector = 5 * e_1 + 12 * e_2
R: Versor = b_exact * a_exact + Scalar(a_exact.magnitude() * b_exact.magnitude())
h: Vector = (
    Scalar(b_exact.magnitude()) * a_exact + Scalar(a_exact.magnitude()) * b_exact
)
zeros(R * a_exact - Scalar(a_exact.magnitude()) * h)  # -> [0, 0]

# %%
sandwich: MultiVectorBase = R * v * R.inverse()
zeros(sandwich - v * (a_exact.normalize() * b_exact.normalize()))  # -> [0, 0]

# %% [markdown]
# ## All three agree with the library's `versor_rotation`

# %%
library: Vector = versor_rotation(from_vector=a_exact, to_vector=b_exact)(v)
[
    zeros(library - rotation_from_to(a_exact, b_exact, v)),
    zeros(library - sandwich),
]  # -> [[0, 0], [0, 0]]

# %% [markdown]
# ## The reverse-over-inverse identity, for any `a` and `b`
#
# The step that makes the forms agree: `R̃ * R⁻¹ = a_hat * b_hat`, checked with unit
# vectors at symbolic angles `α`, `β`.

# %%
alpha: sympy.Symbol
beta: sympy.Symbol
alpha, beta = sympy.symbols("alpha beta", real=True)
a_hat: Vector = Scalar(sympy.cos(alpha)) * e_1 + Scalar(sympy.sin(alpha)) * e_2
b_hat: Vector = Scalar(sympy.cos(beta)) * e_1 + Scalar(sympy.sin(beta)) * e_2
R_unit: Versor = b_hat * a_hat + Scalar(1)
zeros(R_unit.reverse() * R_unit.inverse() - a_hat * b_hat)  # -> [0, 0]
