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
operation done through the general reference ``Gn``.

Values are built the geometric-algebra way -- linear combinations of a vector
basis, wedges for blades, ``scalar + bivector`` for rotors -- which exercises the
narrowing ``+``/``*``/``^`` and stays clear of the ``numbers.Real`` field
annotation (scaling goes through ``__rmul__``, which casts internally).
"""

import sympy

from geometricalgebra.g1 import Vector1
from geometricalgebra.g2 import G2, Bivector2, Rotor2, Vector2
from geometricalgebra.g3 import G3, Bivector3, Rotor3, Trivector3, Vector3
from geometricalgebra.gn import Gn
from geometricalgebra.scalar import Scalar

# --- a vector basis per dimension; everything else is built from it -----------
U1 = Vector1.basis_vector(1)
E1, E2 = Vector2.basis_vector(1), Vector2.basis_vector(2)
I2 = E1 ^ E2  # the unit bivector of G2 (also its pseudoscalar)
F1, F2, F3 = (Vector3.basis_vector(i) for i in (1, 2, 3))
B12, B13, B23 = F1 ^ F2, F1 ^ F3, F2 ^ F3  # the three bivector planes of G3
I3 = (F1 ^ F2) ^ F3  # the unit trivector / pseudoscalar of G3


def gn(d) -> Gn:
    return Gn.from_blade_dict(d)


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
    (3 * U1, "*", 2 * U1, Scalar),
    # 2D -- vectors, bivector (5 I2), rotor (2 + 3 I2)
    (3 * E1 + 4 * E2, "*", E1 + 2 * E2, Rotor2),
    (3 * E1 + 4 * E2, "^", E1 + 2 * E2, Bivector2),
    (3 * E1 + 4 * E2, ".", E1 + 2 * E2, Scalar),
    (3 * E1 + 4 * E2, "*", 5 * I2, Vector2),
    (5 * I2, "*", 3 * E1 + 4 * E2, Vector2),
    (2 * I2, "*", 3 * I2, Scalar),
    (2 + 3 * I2, "*", 1 + I2, Rotor2),
    (2 + 3 * I2, "*", 3 * E1 + 4 * E2, Vector2),
    (3 * E1 + 4 * E2, "*", 2 + 3 * I2, Vector2),
    (2 * I2, "*", 1 + I2, Rotor2),
    # 3D
    (F1 + 2 * F2 + 3 * F3, "*", 4 * F1 + 5 * F2 + 6 * F3, Rotor3),
    (F1 + 2 * F2 + 3 * F3, "^", 4 * F1 + 5 * F2 + 6 * F3, Bivector3),
    (F1 + 2 * F2 + 3 * F3, ".", 4 * F1 + 5 * F2 + 6 * F3, Scalar),
    (B12 + 2 * B13 + 3 * B23, "*", 4 * B12 + 5 * B13 + 6 * B23, Rotor3),
    (F1 + 2 * F2 + 3 * F3, "*", 2 * I3, Bivector3),
    (2 * I3, "*", 3 * I3, Scalar),
    (1 + B12 + B13 + B23, "*", 2 + B12, Rotor3),
    (F1 + 2 * F2 + 3 * F3, "*", 4 * B12 + 5 * B13 + 6 * B23, G3),  # mixed -> widen
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


def test_linear_combination_construction():
    # the basis builds each graded type by linear combination / wedge
    assert type(3 * E1 + 4 * E2) is Vector2
    assert (3 * E1 + 4 * E2) == gn({(1,): 3, (2,): 4})
    assert type(E1 ^ E2) is Bivector2
    assert type(2 + 3 * I2) is Rotor2 and (2 + 3 * I2) == gn({(): 2, (1, 2): 3})
    assert type(2 + B12) is Rotor3  # scalar + bivector narrows to the rotor type
    assert type((F1 ^ F2) ^ F3) is Trivector3
    # reflected ops work too
    assert (5 - I2) == gn({(): 5, (1, 2): -1}) and type(5 - I2) is Rotor2


def test_type_is_operation_driven_not_value_driven():
    # orthogonal vectors: the scalar (dot) part is exactly 0, but the type stays
    # Rotor2 -- we never narrow by inspecting a (possibly float-fuzzy) value.
    r = E1 * E2
    assert type(r) is Rotor2 and r == gn({(1, 2): 1})
    # a pure blade is got by *asking* for it (wedge), never by luck of the values
    assert type(E1 ^ E2) is Bivector2


def test_dual_narrows():
    cases = [
        (3 * E1 + 4 * E2, Vector2),  # 2D: vectors are the self-dual grade
        (5 * I2, Scalar),  # 2D: grade 2 -> grade 0
        (F1 + 2 * F2 + 3 * F3, Bivector3),  # 3D: vector -> bivector
        ((F1 + 2 * F2) ^ (3 * F1 + F3), Vector3),  # 3D: bivector -> vector
    ]
    for val, expected in cases:
        d = val.dual()
        got, want = type(d).__name__, expected.__name__
        assert type(d) is expected, f"dual({type(val).__name__}) -> {got}, want {want}"
        assert d == widen(val).dual(val.DIMENSION)


def test_grade_projection_narrows():
    r = 1 + B12 + 2 * B13 + 3 * B23  # a Rotor3
    assert type(r.r_vector_part(0)) is Scalar
    assert type(r.r_vector_part(2)) is Bivector3
    assert type(r.even_part()) is Rotor3
    assert r.r_vector_part(2) == widen(r).r_vector_part(2)
    # a grade absent from the type projects to the zero scalar
    assert type((F1 + F2).r_vector_part(0)) is Scalar
    assert type((F1 + F2).even_part()) is Scalar


def test_plane_of_rotation():
    # a rotor by angle t in the e1-e2 plane: R = cos(t/2) - sin(t/2) * (e1 e2)
    half = sympy.pi / 4
    r2 = sympy.cos(half) - sympy.sin(half) * (E1 * E2)
    assert type(r2) is Rotor2
    assert r2.plane_of_rotation() == gn({(1, 2): -1})  # the (oriented) unit plane
    r3 = sympy.cos(half) - sympy.sin(half) * (F1 * F2)
    assert type(r3) is Rotor3
    plane = r3.plane_of_rotation()
    assert type(plane) is Bivector3 and plane == gn({(1, 2): -1})


def test_scalar_type():
    s5 = Scalar.from_scalar(5)
    v = 3 * E1 + 4 * E2
    assert type(s5 * v) is Vector2 and s5 * v == gn({(1,): 15, (2,): 20})
    assert type(3 * v) is Vector2 and 3 * v == gn({(1,): 9, (2,): 12})
    assert type(v * 2) is Vector2
    assert type(I2 * I2) is Scalar  # a pure-scalar product result lands in Scalar


def test_widen_fallback():
    # a sum with no covering graded type widens to the dimension's full type
    s = (3 * E1 + 4 * E2) + 7 * I2
    assert type(s) is G2 and s == gn({(1,): 3, (2,): 4, (1, 2): 7})
    assert type((3 * E1 + 4 * E2) * G2.from_blade_dict({(1,): 1})) is G2


def test_cross_type_equality():
    assert (3 * E1 + 4 * E2) == gn({(1,): 3, (2,): 4})
    assert (3 * E1 + 4 * E2) == G2.from_blade_dict({(1,): 3, (2,): 4})
    assert B12 == gn({(1, 2): 1})


def test_rotor_is_complex_2d():
    # the even subalgebra of G2 is the complex numbers: e_12^2 == -1
    assert I2 * I2 == gn({(): -1})


def test_rotor_is_quaternion_3d():
    # each unit bivector squares to -1 (the even subalgebra of G3 is the quaternions).
    # bivector*bivector is *typed* Rotor3 (generally scalar+bivector) -- here the
    # value is a pure scalar, but the type follows the operation, not the value.
    for plane in (B12, B13, B23):
        sq = plane * plane
        assert type(sq) is Rotor3 and sq == gn({(): -1})


def test_inherited_abc_methods():
    v = 3 * E1 + 4 * E2
    assert v.magnitude() == 5
    assert v.normalize() == gn({(1,): sympy.Rational(3, 5), (2,): sympy.Rational(4, 5)})
    assert (5 * I2).reverse() == gn({(1, 2): -5})
    assert (F1 + 2 * F2 + 2 * F3).magnitude() == 3


def test_symbolic_product_matches_gn():
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    got = (a1 * E1 + a2 * E2) * (b1 * E1 + b2 * E2)
    want = gn({(): a1 * b1 + a2 * b2, (1, 2): a1 * b2 - a2 * b1})
    assert got == want and type(got) is Rotor2


# --- the rotor sandwich equals the rotate(from, to) method --------------------
# R = rotor_from_vectors(from, to) = |from||to| + to*from ; for any vector v,
#   R v R.inverse()  ==  rotate(from, to)(v)
# (R.inverse() = R.reverse()/|R|^2 divides out the rotor's scaling, leaving a
# pure rotation.)


def simplify_equal(a, b) -> bool:
    """True iff a and b are equal after simplifying each blade's difference.

    Needed where the values carry ``sqrt`` magnitudes: ``Gn.__eq__`` compares
    eager-simplified forms for identity, which can differ for equal expressions;
    simplifying the *difference* to 0 is the robust check.
    """
    da, db = a.to_blade_dict(), b.to_blade_dict()
    return all(
        sympy.simplify(sympy.sympify(da.get(k, 0)) - sympy.sympify(db.get(k, 0))) == 0
        for k in set(da) | set(db)
    )


def test_rotor_sandwich_equals_rotate_symbolic_2d():
    # general symbolic vectors -- a real symbolic proof, not just sample points
    a1, a2, b1, b2, w1, w2 = sympy.symbols(
        "a1 a2 b1 b2 w1 w2", real=True, positive=True
    )
    frm = gn({(1,): a1, (2,): a2})
    to = gn({(1,): b1, (2,): b2})
    w = gn({(1,): w1, (2,): w2})
    R = Gn.rotor_from_vectors(frm, to)
    assert simplify_equal(R * w * R.inverse(), Gn.rotate(frm, to)(w))


def test_rotor_sandwich_equals_rotate_3d():
    # 3D, concrete vectors (full symbolic 3D simplify is slow for the suite);
    # magnitudes are sqrt(...), so compare via simplify_equal
    frm = gn({(1,): 1, (2,): 2, (3,): 3})
    to = gn({(1,): 4, (2,): 5, (3,): 6})
    w = gn({(1,): 7, (2,): 1, (3,): 2})  # has both in-plane and perpendicular parts
    R = Gn.rotor_from_vectors(frm, to)
    assert simplify_equal(R * w * R.inverse(), Gn.rotate(frm, to)(w))


def test_rotor_rotate_across_representations():
    # the same identity holds (by value) for Gn, G2 and G3; the rotor built from
    # vectors of a specialized type is a Rotor of that algebra
    f2, t2, w2 = Vector2.basis_vector(1), Vector2.basis_vector(2), 2 * E1 + E2
    R2 = Vector2.rotor_from_vectors(f2, t2)
    assert type(R2) is Rotor2
    assert R2 * w2 * R2.inverse() == Vector2.rotate(f2, t2)(w2)

    f3 = Vector3.basis_vector(1)
    t3 = Vector3.basis_vector(2)
    w3 = F1 + 3 * F3
    R3 = Vector3.rotor_from_vectors(f3, t3)
    assert type(R3) is Rotor3
    assert R3 * w3 * R3.inverse() == Vector3.rotate(f3, t3)(w3)


def test_unnormalized_rotor_scales_then_normalizes():
    # the bare sandwich R v R~ scales by R.magnitude_squared(); inverse divides it out
    frm, to, w = E1, E2, E1  # 90 deg, e1 -> e2
    R = Vector2.rotor_from_vectors(frm, to)
    assert R * R.reverse() == gn({(): 2})  # |R|^2
    assert R * w * R.reverse() == gn({(2,): 2})  # scaled rotation
    assert R * w * R.inverse() == gn({(2,): 1})  # pure rotation
