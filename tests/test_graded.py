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

import gacalc.gn as gn
from gacalc.g1 import Vector1
from gacalc.g2 import G2, Bivector2, Rotor2, Vector2
from gacalc.g3 import G3, Bivector3, Rotor3, Trivector3, Vector3
from gacalc.gn import Gn
from gacalc.scalar import Scalar


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
    (3 * Vector1.e_1, "*", 2 * Vector1.e_1, Scalar),
    # 2D -- vectors, bivector (5 * the unit bivector), rotor (scalar + bivector)
    (3 * Vector2.e_1 + 4 * Vector2.e_2, "*", Vector2.e_1 + 2 * Vector2.e_2, Rotor2),
    (3 * Vector2.e_1 + 4 * Vector2.e_2, "^", Vector2.e_1 + 2 * Vector2.e_2, Bivector2),
    (3 * Vector2.e_1 + 4 * Vector2.e_2, ".", Vector2.e_1 + 2 * Vector2.e_2, Scalar),
    (3 * Vector2.e_1 + 4 * Vector2.e_2, "*", 5 * Bivector2.e_12, Vector2),
    (5 * Bivector2.e_12, "*", 3 * Vector2.e_1 + 4 * Vector2.e_2, Vector2),
    (2 * Bivector2.e_12, "*", 3 * Bivector2.e_12, Scalar),
    (2 + 3 * Bivector2.e_12, "*", 1 + Bivector2.e_12, Rotor2),
    (2 + 3 * Bivector2.e_12, "*", 3 * Vector2.e_1 + 4 * Vector2.e_2, Vector2),
    (3 * Vector2.e_1 + 4 * Vector2.e_2, "*", 2 + 3 * Bivector2.e_12, Vector2),
    (2 * Bivector2.e_12, "*", 1 + Bivector2.e_12, Rotor2),
    # 3D
    (
        Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
        "*",
        4 * Vector3.e_1 + 5 * Vector3.e_2 + 6 * Vector3.e_3,
        Rotor3,
    ),
    (
        Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
        "^",
        4 * Vector3.e_1 + 5 * Vector3.e_2 + 6 * Vector3.e_3,
        Bivector3,
    ),
    (
        Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
        ".",
        4 * Vector3.e_1 + 5 * Vector3.e_2 + 6 * Vector3.e_3,
        Scalar,
    ),
    (
        Bivector3.e_12 + 2 * Bivector3.e_13 + 3 * Bivector3.e_23,
        "*",
        4 * Bivector3.e_12 + 5 * Bivector3.e_13 + 6 * Bivector3.e_23,
        Rotor3,
    ),
    (
        Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
        "*",
        2 * Trivector3.e_123,
        Bivector3,
    ),
    (2 * Trivector3.e_123, "*", 3 * Trivector3.e_123, Scalar),
    (
        1 + Bivector3.e_12 + Bivector3.e_13 + Bivector3.e_23,
        "*",
        2 + Bivector3.e_12,
        Rotor3,
    ),
    (
        Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
        "*",
        4 * Bivector3.e_12 + 5 * Bivector3.e_13 + 6 * Bivector3.e_23,
        G3,
    ),  # mixed -> widen
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


def test_basis_blade_class_constants():
    # each class exposes its basis blades as class constants of its own type,
    # equal to basis_vector(n) for the vector blades
    assert type(Vector2.e_1) is Vector2 and Vector2.e_1 == Vector2.basis_vector(1)
    assert type(Vector2.e_2) is Vector2 and Vector2.e_2 == Vector2.basis_vector(2)
    assert type(Bivector2.e_12) is Bivector2 and Bivector2.e_12 == (
        Vector2.e_1 ^ Vector2.e_2
    )
    assert type(G2.e_12) is G2 and G2.e_12 == widen(Vector2.e_1 ^ Vector2.e_2)
    assert type(Vector3.e_3) is Vector3 and Vector3.e_3 == Vector3.basis_vector(3)
    assert type(G3.e_123) is G3
    assert type(Trivector3.e_123) is Trivector3 and Trivector3.e_123 == (
        (Vector3.e_1 ^ Vector3.e_2) ^ Vector3.e_3
    )


def test_basis_constant_instance_fallthrough():
    # the stored field is coeff_e_1, so e_1 is NOT shadowed per-instance: both
    # the class and any instance see the same basis-vector constant, while
    # coeff_e_1 carries the component value
    v = 5 * Vector2.e_1 + 2 * Vector2.e_2
    assert v.e_1 is Vector2.e_1 and v.e_2 is Vector2.e_2
    assert v.coeff_e_1 == 5 and v.coeff_e_2 == 2


def test_component_reads_coefficients():
    # component(blade) reads the scalar coefficient; the reverse in its definition
    # keeps the sign right for grade >= 2 (e_12 * e_12 == -1)
    v = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert v.component(Vector2.e_1) == 3 and v.component(Vector2.e_2) == 4
    assert (7 * Bivector2.e_12).component(Bivector2.e_12) == 7
    assert (5 * Trivector3.e_123).component(Trivector3.e_123) == 5
    b3 = 4 * Bivector3.e_12 + 5 * Bivector3.e_13 + 6 * Bivector3.e_23
    assert b3.component(Bivector3.e_13) == 5


def test_linear_combination_construction():
    # the basis builds each graded type by linear combination / wedge
    assert type(3 * Vector2.e_1 + 4 * Vector2.e_2) is Vector2
    assert (3 * Vector2.e_1 + 4 * Vector2.e_2) == 3 * gn.e_1 + 4 * gn.e_2
    assert type(Vector2.e_1 ^ Vector2.e_2) is Bivector2
    assert type(2 + 3 * Bivector2.e_12) is Rotor2 and (
        2 + 3 * Bivector2.e_12
    ) == 2 * gn.one + 3 * (gn.e_1 ^ gn.e_2)
    assert (
        type(2 + Bivector3.e_12) is Rotor3
    )  # scalar + bivector narrows to the rotor type
    assert type((Vector3.e_1 ^ Vector3.e_2) ^ Vector3.e_3) is Trivector3
    # reflected ops work too
    assert (5 - Bivector2.e_12) == 5 * gn.one - (gn.e_1 ^ gn.e_2) and type(
        5 - Bivector2.e_12
    ) is Rotor2


def test_type_is_operation_driven_not_value_driven():
    # orthogonal vectors: the scalar (dot) part is exactly 0, but the type stays
    # Rotor2 -- we never narrow by inspecting a (possibly float-fuzzy) value.
    r = Vector2.e_1 * Vector2.e_2
    assert type(r) is Rotor2 and r == gn.e_1 ^ gn.e_2
    # a pure blade is got by *asking* for it (wedge), never by luck of the values
    assert type(Vector2.e_1 ^ Vector2.e_2) is Bivector2


def test_dual_narrows():
    cases = [
        (
            3 * Vector2.e_1 + 4 * Vector2.e_2,
            Vector2,
        ),  # 2D: vectors are the self-dual grade
        (5 * Bivector2.e_12, Scalar),  # 2D: grade 2 -> grade 0
        (
            Vector3.e_1 + 2 * Vector3.e_2 + 3 * Vector3.e_3,
            Bivector3,
        ),  # 3D: vector -> bivector
        (
            (Vector3.e_1 + 2 * Vector3.e_2) ^ (3 * Vector3.e_1 + Vector3.e_3),
            Vector3,
        ),  # 3D: bivector -> vector
    ]
    for val, expected in cases:
        d = val.dual()
        got, want = type(d).__name__, expected.__name__
        assert type(d) is expected, f"dual({type(val).__name__}) -> {got}, want {want}"
        assert d == widen(val).dual(val.DIMENSION)


def test_grade_projection_narrows():
    r = 1 + Bivector3.e_12 + 2 * Bivector3.e_13 + 3 * Bivector3.e_23  # a Rotor3
    assert type(r.r_vector_part(0)) is Scalar
    assert type(r.r_vector_part(2)) is Bivector3
    assert type(r.even_part()) is Rotor3
    assert r.r_vector_part(2) == widen(r).r_vector_part(2)
    # a grade absent from the type projects to the zero scalar
    assert type((Vector3.e_1 + Vector3.e_2).r_vector_part(0)) is Scalar
    assert type((Vector3.e_1 + Vector3.e_2).even_part()) is Scalar


def test_plane_of_rotation():
    # the rotor that turns e1 -> e2 rotates in the e1-e2 plane
    r2 = Vector2.rotor_from_vectors(from_vector=Vector2.e_1, to_vector=Vector2.e_2)
    assert type(r2) is Rotor2
    assert r2.plane_of_rotation() == -(gn.e_1 ^ gn.e_2)  # the (oriented) unit plane
    r3 = Vector3.rotor_from_vectors(from_vector=Vector3.e_1, to_vector=Vector3.e_2)
    assert type(r3) is Rotor3
    plane = r3.plane_of_rotation()
    assert type(plane) is Bivector3 and plane == -(gn.e_1 ^ gn.e_2)


def test_scalar_type():
    s5 = Scalar.from_scalar(5)
    v = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert type(s5 * v) is Vector2 and s5 * v == 15 * gn.e_1 + 20 * gn.e_2
    assert type(3 * v) is Vector2 and 3 * v == 9 * gn.e_1 + 12 * gn.e_2
    assert type(v * 2) is Vector2
    assert (
        type(Bivector2.e_12 * Bivector2.e_12) is Scalar
    )  # a pure-scalar product result lands in Scalar


def test_widen_fallback():
    # a sum with no covering graded type widens to the dimension's full type
    s = (3 * Vector2.e_1 + 4 * Vector2.e_2) + 7 * Bivector2.e_12
    assert type(s) is G2 and s == 3 * gn.e_1 + 4 * gn.e_2 + 7 * (gn.e_1 ^ gn.e_2)
    assert (
        type((3 * Vector2.e_1 + 4 * Vector2.e_2) * G2.from_blade_dict({(1,): 1})) is G2
    )


def test_cross_type_equality():
    assert (3 * Vector2.e_1 + 4 * Vector2.e_2) == 3 * gn.e_1 + 4 * gn.e_2
    assert (3 * Vector2.e_1 + 4 * Vector2.e_2) == G2.from_blade_dict({(1,): 3, (2,): 4})
    assert Bivector3.e_12 == gn.e_1 ^ gn.e_2


def test_rotor_is_complex_2d():
    # the even subalgebra of G2 is the complex numbers: e_12^2 == -1
    assert Bivector2.e_12 * Bivector2.e_12 == -gn.one


def test_rotor_is_quaternion_3d():
    # each unit bivector squares to -1 (the even subalgebra of G3 is the quaternions).
    # bivector*bivector is *typed* Rotor3 (generally scalar+bivector) -- here the
    # value is a pure scalar, but the type follows the operation, not the value.
    for plane in (Bivector3.e_12, Bivector3.e_13, Bivector3.e_23):
        sq = plane * plane
        assert type(sq) is Rotor3 and sq == -gn.one


def test_inherited_abc_methods():
    v = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert v.magnitude() == 5
    assert (
        v.normalize() == sympy.Rational(3, 5) * gn.e_1 + sympy.Rational(4, 5) * gn.e_2
    )
    assert (5 * Bivector2.e_12).reverse() == -5 * (gn.e_1 ^ gn.e_2)
    assert (Vector3.e_1 + 2 * Vector3.e_2 + 2 * Vector3.e_3).magnitude() == 3


def test_symbolic_product_matches_gn():
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    got = (a1 * Vector2.e_1 + a2 * Vector2.e_2) * (b1 * Vector2.e_1 + b2 * Vector2.e_2)
    want = (a1 * b1 + a2 * b2) * gn.one + (a1 * b2 - a2 * b1) * (gn.e_1 ^ gn.e_2)
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
    frm = a1 * gn.e_1 + a2 * gn.e_2
    to = b1 * gn.e_1 + b2 * gn.e_2
    w = w1 * gn.e_1 + w2 * gn.e_2
    R = Gn.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert simplify_equal(
        R * w * R.inverse(), Gn.rotate(from_vector=frm, to_vector=to)(w)
    )


def test_rotor_sandwich_equals_rotate_3d():
    # 3D, concrete vectors (full symbolic 3D simplify is slow for the suite);
    # magnitudes are sqrt(...), so compare via simplify_equal
    frm = gn.e_1 + 2 * gn.e_2 + 3 * gn.e_3
    to = 4 * gn.e_1 + 5 * gn.e_2 + 6 * gn.e_3
    w = 7 * gn.e_1 + gn.e_2 + 2 * gn.e_3  # has both in-plane and perpendicular parts
    R = Gn.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert simplify_equal(
        R * w * R.inverse(), Gn.rotate(from_vector=frm, to_vector=to)(w)
    )


def test_rotor_rotate_across_representations():
    # the same identity holds (by value) for Gn, G2 and G3; the rotor built from
    # vectors of a specialized type is a Rotor of that algebra
    w2 = 2 * Vector2.e_1 + Vector2.e_2
    R2 = Vector2.rotor_from_vectors(from_vector=Vector2.e_1, to_vector=Vector2.e_2)
    assert type(R2) is Rotor2
    assert R2 * w2 * R2.inverse() == Vector2.rotate(
        from_vector=Vector2.e_1, to_vector=Vector2.e_2
    )(w2)

    w3 = Vector3.e_1 + 3 * Vector3.e_3
    R3 = Vector3.rotor_from_vectors(from_vector=Vector3.e_1, to_vector=Vector3.e_2)
    assert type(R3) is Rotor3
    assert R3 * w3 * R3.inverse() == Vector3.rotate(
        from_vector=Vector3.e_1, to_vector=Vector3.e_2
    )(w3)


def test_unnormalized_rotor_scales_then_normalizes():
    # the bare sandwich R v R~ scales by R.magnitude_squared(); inverse divides it out
    frm, to, w = Vector2.e_1, Vector2.e_2, Vector2.e_1  # 90 deg, e1 -> e2
    R = Vector2.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert R * R.reverse() == 2 * gn.one  # |R|^2
    assert R * w * R.reverse() == 2 * gn.e_2  # scaled rotation
    assert R * w * R.inverse() == gn.e_2  # pure rotation
