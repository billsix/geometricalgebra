# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Graded subtype suite.

The graded types (Vector_n, Bivector_n, Trivector3, Rotor_n, Scalar) dispatch a
product by the operand types and return the *grade-correct* type, decided
symbolically at generation time (so it never depends on runtime float values).
Each case asserts both the **return type** and that the **value** equals the same
operation done through the general reference ``Gn`` (widen both operands, run the
reference op, compare via the simplify-aware ``==``).

Instances are built through ``from_blade_dict`` (whose dict argument is
unchecked) so the literals don't trip the ``numbers.Real`` field annotation.
"""

import sympy

from geometricalgebra.g1 import G1, Vector1
from geometricalgebra.g2 import G2, Bivector2, Rotor2, Vector2
from geometricalgebra.g3 import G3, Bivector3, Rotor3, Trivector3, Vector3
from geometricalgebra.gn import Gn
from geometricalgebra.scalar import Scalar


# typed constructor helpers (keep the literals out of the numbers.Real fields)
def gn(d) -> Gn:
    return Gn.from_blade_dict(d)


def S(x) -> Scalar:
    return Scalar.from_blade_dict({(): x})


def V1(x) -> Vector1:
    return Vector1.from_blade_dict({(1,): x})


def V2(x, y) -> Vector2:
    return Vector2.from_blade_dict({(1,): x, (2,): y})


def B2(x) -> Bivector2:
    return Bivector2.from_blade_dict({(1, 2): x})


def R2(s, b) -> Rotor2:
    return Rotor2.from_blade_dict({(): s, (1, 2): b})


def V3(x, y, z) -> Vector3:
    return Vector3.from_blade_dict({(1,): x, (2,): y, (3,): z})


def B3(a, b, c) -> Bivector3:
    return Bivector3.from_blade_dict({(1, 2): a, (1, 3): b, (2, 3): c})


def T3(x) -> Trivector3:
    return Trivector3.from_blade_dict({(1, 2, 3): x})


def R3(s, a, b, c) -> Rotor3:
    return Rotor3.from_blade_dict({(): s, (1, 2): a, (1, 3): b, (2, 3): c})


def widen(x) -> Gn:
    return Gn.from_blade_dict(x.to_blade_dict())


# typed op, and the matching reference op on Gn
OPS = {
    "*": (lambda a, b: a * b, lambda a, b: a * b),
    "^": (lambda a, b: a ^ b, lambda a, b: a.outer_product(b)),
    ".": (lambda a, b: a.inner_product(b), lambda a, b: a.inner_product(b)),
}

# (lhs, op, rhs, expected return type) -- this table *is* the grade product table.
PRODUCT_TABLE = [
    # 1D
    (V1(3), "*", V1(2), Scalar),
    # 2D
    (V2(3, 4), "*", V2(1, 2), Rotor2),
    (V2(3, 4), "^", V2(1, 2), Bivector2),
    (V2(3, 4), ".", V2(1, 2), Scalar),
    (V2(3, 4), "*", B2(5), Vector2),
    (B2(5), "*", V2(3, 4), Vector2),
    (B2(2), "*", B2(3), Scalar),
    (R2(2, 3), "*", R2(1, 1), Rotor2),
    (R2(2, 3), "*", V2(3, 4), Vector2),
    (V2(3, 4), "*", R2(2, 3), Vector2),
    (B2(2), "*", R2(1, 1), Rotor2),
    # 3D
    (V3(1, 2, 3), "*", V3(4, 5, 6), Rotor3),
    (V3(1, 2, 3), "^", V3(4, 5, 6), Bivector3),
    (V3(1, 2, 3), ".", V3(4, 5, 6), Scalar),
    (B3(1, 2, 3), "*", B3(4, 5, 6), Rotor3),
    (V3(1, 2, 3), "*", T3(2), Bivector3),
    (T3(2), "*", T3(3), Scalar),
    (R3(1, 2, 3, 4), "*", R3(2, 1, 1, 1), Rotor3),
    (V3(1, 2, 3), "*", B3(4, 5, 6), G3),  # mixed grade -> widen
]


def test_product_table():
    for a, opname, b, expected in PRODUCT_TABLE:
        typed_op, gn_op = OPS[opname]
        result = typed_op(a, b)
        label = f"{type(a).__name__} {opname} {type(b).__name__}"
        assert type(result) is expected, (
            f"{label}: expected {expected.__name__}, got {type(result).__name__}"
        )
        assert result == gn_op(widen(a), widen(b)), f"value mismatch for {label}"


def test_type_is_operation_driven_not_value_driven():
    # orthogonal vectors: the scalar (dot) part is exactly 0, but the type stays
    # Rotor2 -- we never narrow by inspecting a (possibly float-fuzzy) value.
    r = V2(1, 0) * V2(0, 1)
    assert type(r) is Rotor2
    assert r == gn({(1, 2): 1})
    # a pure blade is got by *asking* for it (wedge), never by luck of the values
    assert type(V2(1, 0) ^ V2(0, 1)) is Bivector2


def test_dual_narrows():
    cases = [
        (V2(3, 4), Vector2),  # 2D: vectors are the self-dual grade
        (B2(5), Scalar),  # 2D: grade 2 -> grade 0
        (V3(1, 2, 3), Bivector3),  # 3D: vector -> bivector
        (V3(1, 2, 3) ^ V3(4, 5, 6), Vector3),  # 3D: bivector -> vector
    ]
    for val, expected in cases:
        d = val.dual()
        got, want = type(d).__name__, expected.__name__
        assert type(d) is expected, f"dual({type(val).__name__}) -> {got}, want {want}"
        assert d == widen(val).dual(val.DIMENSION)


def test_grade_projection_narrows():
    r = R3(1, 2, 3, 4)
    assert type(r.r_vector_part(0)) is Scalar
    assert type(r.r_vector_part(2)) is Bivector3
    assert type(r.even_part()) is Rotor3
    assert r.r_vector_part(2) == widen(r).r_vector_part(2)
    # a grade absent from the type projects to the zero scalar
    assert type(V3(1, 2, 3).r_vector_part(0)) is Scalar
    assert type(V3(1, 2, 3).even_part()) is Scalar


def test_scalar_type():
    v = V2(3, 4)
    assert type(S(5) * v) is Vector2
    assert S(5) * v == gn({(1,): 15, (2,): 20})
    assert type(3 * v) is Vector2 and 3 * v == gn({(1,): 9, (2,): 12})
    assert type(v * 2) is Vector2
    # a pure-scalar product result really lands in Scalar
    assert type(B2(2) * B2(3)) is Scalar


def test_widen_fallback():
    # cross-grade addition widens to the dimension's full type
    s = V2(3, 4) + B2(7)
    assert type(s) is G2 and s == gn({(1,): 3, (2,): 4, (1, 2): 7})
    # multiplying by the full type widens too
    assert type(V2(3, 4) * G2.from_blade_dict({(1,): 1})) is G2


def test_cross_type_equality():
    assert V2(3, 4) == gn({(1,): 3, (2,): 4})
    assert V2(3, 4) == G2.from_blade_dict({(1,): 3, (2,): 4})
    assert B3(1, 0, 0) == gn({(1, 2): 1})


def test_rotor_is_complex_2d():
    # the even subalgebra of G2 is the complex numbers: e_12^2 == -1
    assert R2(0, 1) * R2(0, 1) == gn({(): -1})


def test_rotor_is_quaternion_3d():
    # each unit bivector squares to -1 (the even subalgebra of G3 is the quaternions)
    for e in (R3(0, 1, 0, 0), R3(0, 0, 1, 0), R3(0, 0, 0, 1)):
        sq = e * e
        assert type(sq) is Rotor3
        assert sq == gn({(): -1})


def test_inherited_abc_methods():
    v = V2(3, 4)
    assert v.magnitude() == 5
    assert v.normalize() == gn({(1,): sympy.Rational(3, 5), (2,): sympy.Rational(4, 5)})
    assert B2(5).reverse() == gn({(1, 2): -5})
    assert V3(1, 2, 2).magnitude() == 3


def test_symbolic_product_matches_gn():
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    got = V2(a1, a2) * V2(b1, b2)
    want = gn({(): a1 * b1 + a2 * b2, (1, 2): a1 * b2 - a2 * b1})
    assert got == want
    assert type(got) is Rotor2


def test_constructors_and_iter():
    # graded types interoperate via the blade-dict interchange protocol
    assert Vector2.from_blade_dict({(1,): 3, (2,): 4, (1, 2): 9}) == V2(3, 4)
    assert V3(1, 0, 2).to_blade_dict() == {(1,): 1, (3,): 2}
    assert G1.DIMENSION == 1 and V1(0).to_blade_dict() == {}
