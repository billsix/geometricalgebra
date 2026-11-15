# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Step 3, rotation from projection — calculations
#
# Companion to *Step 3: Rotation from One Vector to Another, from Projection*. One
# triangle, drawn twice. The first measures `b` against `a` (Step 2) and gives the
# cosine and sine of the angle from `a` to `b`. The second is the same triangle on any
# `v`: `v' = cos(θ) * v + sin(θ) * r(v; π/2)`. Each check prints zeros when it holds.

# %%
import sympy

from gacalc.base import MultiVectorBase, MultiVectorFn, Real
from gacalc.g2 import Scalar, Vector, e_1, e_2
from gacalc.transforms import projection_rotation


def rotate(cos: Real, sin: Real, v: Vector) -> Vector:
    """Rotate ``v`` by the angle with cosine ``cos`` and sine ``sin`` (Step 1)."""
    return Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()


def standard_position(a: Vector, v: Vector) -> Vector:
    """``v`` in ``a``'s standard position (Step 2): its coordinates are the signed
    lengths of ``v``'s projection and rejection on ``a``."""
    return rotate(
        a.coefficient(e_1) / a.magnitude(), -a.coefficient(e_2) / a.magnitude(), v
    )


def cos_sin_from_to(a: Vector, b: Vector) -> tuple[Real, Real]:
    """The first triangle: ``b`` measured against ``a``, divided by ``|b|``."""
    measured: Vector = standard_position(a, b)
    return (
        measured.coefficient(e_1) / b.magnitude(),
        measured.coefficient(e_2) / b.magnitude(),
    )


def rotation_from_to(a: Vector, b: Vector, v: Vector) -> Vector:
    """The second triangle: the same angle applied to ``v``."""
    cos: Real
    sin: Real
    cos, sin = cos_sin_from_to(a, b)
    return rotate(cos, sin, v)


def zeros(value: MultiVectorBase) -> list[sympy.Expr]:
    """Each coefficient of ``value``, simplified -- all zeros when it is zero."""
    return [sympy.simplify(sympy.sympify(coefficient)) for coefficient in value]


# %%
a_1: sympy.Symbol
a_2: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
v_1: sympy.Symbol
v_2: sympy.Symbol
a_1, a_2, b_1, b_2, v_1, v_2 = sympy.symbols("a_1 a_2 b_1 b_2 v_1 v_2", real=True)
a: Vector = Scalar(a_1) * e_1 + Scalar(a_2) * e_2
b: Vector = Scalar(b_1) * e_1 + Scalar(b_2) * e_2
v: Vector = Scalar(v_1) * e_1 + Scalar(v_2) * e_2
cos: Real
sin: Real
cos, sin = cos_sin_from_to(a, b)
rotated: Vector = rotation_from_to(a, b, v)

# %% [markdown]
# ## The first triangle: the cosine and sine of the angle from `a` to `b`
#
# `(a_1 * b_1 + a_2 * b_2) / (|a| * |b|)` and `(a_1 * b_2 - a_2 * b_1) / (|a| * |b|)`,
# a unit pair.

# %%
[
    sympy.simplify(
        sympy.sympify(cos - (a_1 * b_1 + a_2 * b_2) / (a.magnitude() * b.magnitude()))
    ),
    sympy.simplify(
        sympy.sympify(sin - (a_1 * b_2 - a_2 * b_1) / (a.magnitude() * b.magnitude()))
    ),
    sympy.simplify(sympy.sympify(cos**2 + sin**2 - 1)),
]  # -> [0, 0, 0]

# %% [markdown]
# ## The second triangle is the same triangle on `v`
#
# Its legs, `cos(θ) * v` and `sin(θ) * r(v; π/2)`, are perpendicular, and their lengths
# are the first triangle's legs times `|v| / |b|`.

# %%
along: Vector = Scalar(cos) * v
across: Vector = Scalar(sin) * v.rotate_90_degrees()
measured_b: Vector = standard_position(a, b)
scale: Real = v.magnitude() / b.magnitude()
[
    sympy.simplify(sympy.sympify(along.dot(across).scalar_part())),
    sympy.simplify(
        sympy.sympify(
            along.magnitude_squared() - (scale * measured_b.coefficient(e_1)) ** 2
        )
    ),
    sympy.simplify(
        sympy.sympify(
            across.magnitude_squared() - (scale * measured_b.coefficient(e_2)) ** 2
        )
    ),
]  # -> [0, 0, 0]

# %% [markdown]
# ## The same map as two rotations: `(R_b^{e_1})⁻¹ ∘ R_a^{e_1}`
#
# The rotation back from `b`'s standard position negates the sine.

# %%
back: Vector = rotate(
    b.coefficient(e_1) / b.magnitude(),
    b.coefficient(e_2) / b.magnitude(),
    standard_position(a, v),
)
zeros(rotated - back)  # -> [0, 0]

# %% [markdown]
# ## It keeps length, and it is linear

# %%
sympy.simplify(
    sympy.sympify(rotated.magnitude_squared() - v.magnitude_squared())
)  # -> 0

# %%
w_1: sympy.Symbol
w_2: sympy.Symbol
k: sympy.Symbol
w_1, w_2, k = sympy.symbols("w_1 w_2 k", real=True)
w: Vector = Scalar(w_1) * e_1 + Scalar(w_2) * e_2
[
    zeros(
        rotation_from_to(a, b, v + w)
        - (rotation_from_to(a, b, v) + rotation_from_to(a, b, w))
    ),
    zeros(rotation_from_to(a, b, Scalar(k) * v) - Scalar(k) * rotated),
]  # -> [[0, 0], [0, 0]]

# %% [markdown]
# ## Only directions matter
#
# Rescaling `a` and `b` by positive numbers `p`, `q` gives the same rotation.

# %%
p: sympy.Symbol
q: sympy.Symbol
p, q = sympy.symbols("p q", positive=True)
zeros(rotation_from_to(Scalar(p) * a, Scalar(q) * b, v) - rotated)  # -> [0, 0]

# %% [markdown]
# ## It carries `a`'s direction onto `b`'s

# %%
zeros(rotation_from_to(a, b, a.normalize()) - b.normalize())  # -> [0, 0]

# %% [markdown]
# ## The library's `projection_rotation` agrees
#
# Exact vectors keep the square roots rational (`|a| = 5`, `|b| = 13`); `v` stays
# symbolic.

# %%
a_exact: Vector = 3 * e_1 + 4 * e_2
b_exact: Vector = 5 * e_1 + 12 * e_2
turn: MultiVectorFn = projection_rotation(from_vector=a_exact, to_vector=b_exact)
zeros(rotation_from_to(a_exact, b_exact, v) - turn(v))  # -> [0, 0]
