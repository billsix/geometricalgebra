# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

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

import typing

import sympy

import gacalc.gn as gn
from gacalc.base import BladeCoef, MultiVectorBase
from gacalc.g1 import Vector1
from gacalc.g2 import G2, Bivector2, Rotor2, Vector2
from gacalc.g3 import G3, Bivector3, Rotor3, Trivector3, Vector3
from gacalc.gn import Gn
from gacalc.scalar import Scalar
from gacalc.transforms import projection_rotation


def widen(x: MultiVectorBase) -> Gn:
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


def test_product_table() -> None:
    a: MultiVectorBase
    opname: str
    b: MultiVectorBase
    expected: type[MultiVectorBase]
    for a, opname, b, expected in PRODUCT_TABLE:
        typed_op: typing.Callable
        gn_op: typing.Callable
        typed_op, gn_op = OPS[opname]
        result: MultiVectorBase = typed_op(a, b)
        label: str = f"{type(a).__name__} {opname} {type(b).__name__}"
        assert type(result) is expected, (
            f"{label}: expected {expected.__name__}, got {type(result).__name__}"
        )
        assert result == gn_op(widen(a), widen(b)), f"value mismatch for {label}"


def test_basis_blade_class_constants() -> None:
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


def test_basis_constant_instance_fallthrough() -> None:
    # the stored field is coeff_e_1, so e_1 is NOT shadowed per-instance: both
    # the class and any instance see the same basis-vector constant, while
    # coeff_e_1 carries the component value
    v: Vector2 = 5 * Vector2.e_1 + 2 * Vector2.e_2
    assert v.e_1 is Vector2.e_1 and v.e_2 is Vector2.e_2
    assert v.coeff_e_1 == 5 and v.coeff_e_2 == 2


def test_coefficient_readback() -> None:
    # coefficient(blade) reads the stored coefficient on a blade, any grade
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert v.coefficient(Vector2.e_1) == 3 and v.coefficient(Vector2.e_2) == 4
    assert (7 * Bivector2.e_12).coefficient(Bivector2.e_12) == 7
    assert (5 * Trivector3.e_123).coefficient(Trivector3.e_123) == 5
    b3: Bivector3 = 4 * Bivector3.e_12 + 5 * Bivector3.e_13 + 6 * Bivector3.e_23
    assert b3.coefficient(Bivector3.e_13) == 5


def test_linear_combination_construction() -> None:
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


def test_type_is_operation_driven_not_value_driven() -> None:
    # orthogonal vectors: the scalar (dot) part is exactly 0, but the type stays
    # Rotor2 -- we never narrow by inspecting a (possibly float-fuzzy) value.
    r: MultiVectorBase = Vector2.e_1 * Vector2.e_2
    assert type(r) is Rotor2 and r == gn.e_1 ^ gn.e_2
    # a pure blade is got by *asking* for it (wedge), never by luck of the values
    assert type(Vector2.e_1 ^ Vector2.e_2) is Bivector2


def test_dual_narrows() -> None:
    # left inferred (not annotated MultiVectorBase): the concrete union keeps
    # ``val.dual()`` (dimension-defaulting) and ``val.DIMENSION`` resolvable.
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
        got: str
        want: str
        got, want = type(d).__name__, expected.__name__
        assert type(d) is expected, f"dual({type(val).__name__}) -> {got}, want {want}"
        assert d == widen(val).dual(val.DIMENSION)


def test_grade_projection_narrows() -> None:
    r: MultiVectorBase = (
        1 + Bivector3.e_12 + 2 * Bivector3.e_13 + 3 * Bivector3.e_23
    )  # a Rotor3
    assert type(r.r_vector_part(0)) is Scalar
    assert type(r.r_vector_part(2)) is Bivector3
    assert type(r.even_part()) is Rotor3
    assert r.r_vector_part(2) == widen(r).r_vector_part(2)
    # a grade absent from the type projects to the zero scalar
    assert type((Vector3.e_1 + Vector3.e_2).r_vector_part(0)) is Scalar
    assert type((Vector3.e_1 + Vector3.e_2).even_part()) is Scalar


def test_plane_of_rotation() -> None:
    # the rotor that turns e1 -> e2 rotates in the e1-e2 plane
    r2: MultiVectorBase = Vector2.rotor_from_vectors(
        from_vector=Vector2.e_1, to_vector=Vector2.e_2
    )
    assert type(r2) is Rotor2
    assert r2.plane_of_rotation() == -(gn.e_1 ^ gn.e_2)  # the (oriented) unit plane
    r3: MultiVectorBase = Vector3.rotor_from_vectors(
        from_vector=Vector3.e_1, to_vector=Vector3.e_2
    )
    assert type(r3) is Rotor3
    plane: MultiVectorBase = r3.plane_of_rotation()
    assert type(plane) is Bivector3 and plane == -(gn.e_1 ^ gn.e_2)


def test_scalar_type() -> None:
    s5: Scalar = Scalar.from_scalar(5)
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert type(s5 * v) is Vector2 and s5 * v == 15 * gn.e_1 + 20 * gn.e_2
    assert type(3 * v) is Vector2 and 3 * v == 9 * gn.e_1 + 12 * gn.e_2
    assert type(v * 2) is Vector2
    assert (
        type(Bivector2.e_12 * Bivector2.e_12) is Scalar
    )  # a pure-scalar product result lands in Scalar


def test_widen_fallback() -> None:
    # a sum with no covering graded type widens to the dimension's full type
    s: MultiVectorBase = (3 * Vector2.e_1 + 4 * Vector2.e_2) + 7 * Bivector2.e_12
    assert type(s) is G2 and s == 3 * gn.e_1 + 4 * gn.e_2 + 7 * (gn.e_1 ^ gn.e_2)
    assert (
        type((3 * Vector2.e_1 + 4 * Vector2.e_2) * G2.from_blade_dict({(1,): 1})) is G2
    )


def test_cross_type_equality() -> None:
    assert (3 * Vector2.e_1 + 4 * Vector2.e_2) == 3 * gn.e_1 + 4 * gn.e_2
    assert (3 * Vector2.e_1 + 4 * Vector2.e_2) == G2.from_blade_dict({(1,): 3, (2,): 4})
    assert Bivector3.e_12 == gn.e_1 ^ gn.e_2


def test_rotor_is_complex_2d() -> None:
    # the even subalgebra of G2 is the complex numbers: e_12^2 == -1
    assert Bivector2.e_12 * Bivector2.e_12 == -gn.one


def test_rotor_is_quaternion_3d() -> None:
    # each unit bivector squares to -1 (the even subalgebra of G3 is the quaternions).
    # bivector*bivector is *typed* Rotor3 (generally scalar+bivector) -- here the
    # value is a pure scalar, but the type follows the operation, not the value.
    plane: Bivector3
    for plane in (Bivector3.e_12, Bivector3.e_13, Bivector3.e_23):
        sq: MultiVectorBase = plane * plane
        assert type(sq) is Rotor3 and sq == -gn.one


def test_inherited_abc_methods() -> None:
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    assert v.magnitude() == 5
    assert (
        v.normalize() == sympy.Rational(3, 5) * gn.e_1 + sympy.Rational(4, 5) * gn.e_2
    )
    assert (5 * Bivector2.e_12).reverse() == -5 * (gn.e_1 ^ gn.e_2)
    assert (Vector3.e_1 + 2 * Vector3.e_2 + 2 * Vector3.e_3).magnitude() == 3


def test_symbolic_product_matches_gn() -> None:
    a1: sympy.Symbol
    a2: sympy.Symbol
    b1: sympy.Symbol
    b2: sympy.Symbol
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    got: MultiVectorBase = (a1 * Vector2.e_1 + a2 * Vector2.e_2) * (
        b1 * Vector2.e_1 + b2 * Vector2.e_2
    )
    want: Gn = (a1 * b1 + a2 * b2) * gn.one + (a1 * b2 - a2 * b1) * (gn.e_1 ^ gn.e_2)
    assert got == want and type(got) is Rotor2


# --- the rotor sandwich equals projection_rotation(from, to) ------------------
# R = rotor_from_vectors(from, to) = |from||to| + to*from ; for any vector v,
#   R v R.inverse()  ==  projection_rotation(from, to)(v)
# (R.inverse() = R.reverse()/|R|^2 divides out the rotor's scaling, leaving a
# pure rotation.)


def simplify_equal(a: MultiVectorBase, b: MultiVectorBase) -> bool:
    """True iff a and b are equal after simplifying each blade's difference.

    Needed where the values carry ``sqrt`` magnitudes: ``Gn.__eq__`` compares
    eager-simplified forms for identity, which can differ for equal expressions;
    simplifying the *difference* to 0 is the robust check.
    """
    da: BladeCoef
    db: BladeCoef
    da, db = a.to_blade_dict(), b.to_blade_dict()
    return all(
        sympy.simplify(sympy.sympify(da.get(k, 0)) - sympy.sympify(db.get(k, 0))) == 0
        for k in set(da) | set(db)
    )


def test_rotor_sandwich_equals_rotate_symbolic_2d() -> None:
    # general symbolic vectors -- a real symbolic proof, not just sample points
    a1: sympy.Symbol
    a2: sympy.Symbol
    b1: sympy.Symbol
    b2: sympy.Symbol
    w1: sympy.Symbol
    w2: sympy.Symbol
    a1, a2, b1, b2, w1, w2 = sympy.symbols(
        "a1 a2 b1 b2 w1 w2", real=True, positive=True
    )
    frm: Gn = a1 * gn.e_1 + a2 * gn.e_2
    to: Gn = b1 * gn.e_1 + b2 * gn.e_2
    w: Gn = w1 * gn.e_1 + w2 * gn.e_2
    r: MultiVectorBase = Gn.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert simplify_equal(
        r * w * r.inverse(), projection_rotation(from_vector=frm, to_vector=to)(w)
    )


def test_rotor_sandwich_equals_rotate_3d() -> None:
    # 3D, concrete vectors (full symbolic 3D simplify is slow for the suite);
    # magnitudes are sqrt(...), so compare via simplify_equal
    frm: Gn = gn.e_1 + 2 * gn.e_2 + 3 * gn.e_3
    to: Gn = 4 * gn.e_1 + 5 * gn.e_2 + 6 * gn.e_3
    w: Gn = 7 * gn.e_1 + gn.e_2 + 2 * gn.e_3  # in-plane and perpendicular parts
    r: MultiVectorBase = Gn.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert simplify_equal(
        r * w * r.inverse(), projection_rotation(from_vector=frm, to_vector=to)(w)
    )


def test_rotor_rotate_across_representations() -> None:
    # the same identity holds (by value) for Gn, G2 and G3; the rotor built from
    # vectors of a specialized type is a Rotor of that algebra
    w2: Vector2 = 2 * Vector2.e_1 + Vector2.e_2
    r2: MultiVectorBase = Vector2.rotor_from_vectors(
        from_vector=Vector2.e_1, to_vector=Vector2.e_2
    )
    assert type(r2) is Rotor2
    assert r2 * w2 * r2.inverse() == projection_rotation(
        from_vector=Vector2.e_1, to_vector=Vector2.e_2
    )(w2)

    w3: Vector3 = Vector3.e_1 + 3 * Vector3.e_3
    r3: MultiVectorBase = Vector3.rotor_from_vectors(
        from_vector=Vector3.e_1, to_vector=Vector3.e_2
    )
    assert type(r3) is Rotor3
    assert r3 * w3 * r3.inverse() == projection_rotation(
        from_vector=Vector3.e_1, to_vector=Vector3.e_2
    )(w3)


def test_unnormalized_rotor_scales_then_normalizes() -> None:
    # the bare sandwich R v R~ scales by R.magnitude_squared(); inverse divides it out
    frm: Vector2
    to: Vector2
    w: Vector2
    frm, to, w = Vector2.e_1, Vector2.e_2, Vector2.e_1  # 90 deg, e1 -> e2
    r: MultiVectorBase = Vector2.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert r * r.reverse() == 2 * gn.one  # |R|^2
    assert r * w * r.reverse() == 2 * gn.e_2  # scaled rotation
    assert r * w * r.inverse() == gn.e_2  # pure rotation


def test_project_vector_onto_bivector_trivector_subtypes() -> None:
    # Vector2 onto the 2D bivector -> itself (the bivector spans the whole plane)
    v2: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    proj2: MultiVectorBase = Vector2.project(onto=Bivector2.e_12)(v2)
    assert proj2 == v2 and type(proj2) is Vector2
    # Vector3 onto a bivector plane -> the in-plane part, AS a Vector3: project is
    # grade-preserving, so it narrows back to the input's type (no widening to G3).
    e1: Vector3
    e3: Vector3
    e1, e3 = Vector3.e_1, Vector3.e_3
    proj3: MultiVectorBase = Vector3.project(onto=Bivector3.e_12)(e1 + e3)
    assert proj3 == e1 and type(proj3) is Vector3
    assert Vector3.project(onto=Bivector3.e_12)(e3) == Vector3.zero()
    # Vector3 onto the trivector (all of 3-space) -> itself
    assert Vector3.project(onto=Trivector3.e_123)(e1 + e3) == e1 + e3
