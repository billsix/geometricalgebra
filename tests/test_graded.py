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

The graded types (Vector_n, Bivector_n, g3.Trivector, Rotor_n, Scalar_n) dispatch a
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

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
import gacalc.gn as gn
from gacalc.base import BladeCoef, MultiVectorBase
from gacalc.gn import Gn
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
    (3 * g1.Vector.e_1, "*", 2 * g1.Vector.e_1, g1.Scalar),
    # 2D -- vectors, bivector (5 * the unit bivector), rotor (scalar + bivector)
    (
        3 * g2.Vector.e_1 + 4 * g2.Vector.e_2,
        "*",
        g2.Vector.e_1 + 2 * g2.Vector.e_2,
        g2.Rotor,
    ),
    (
        3 * g2.Vector.e_1 + 4 * g2.Vector.e_2,
        "^",
        g2.Vector.e_1 + 2 * g2.Vector.e_2,
        g2.Bivector,
    ),
    (
        3 * g2.Vector.e_1 + 4 * g2.Vector.e_2,
        ".",
        g2.Vector.e_1 + 2 * g2.Vector.e_2,
        g2.Scalar,
    ),
    (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2, "*", 5 * g2.Bivector.e_12, g2.Vector),
    (5 * g2.Bivector.e_12, "*", 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2, g2.Vector),
    (2 * g2.Bivector.e_12, "*", 3 * g2.Bivector.e_12, g2.Scalar),
    (2 + 3 * g2.Bivector.e_12, "*", 1 + g2.Bivector.e_12, g2.Rotor),
    (2 + 3 * g2.Bivector.e_12, "*", 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2, g2.Vector),
    (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2, "*", 2 + 3 * g2.Bivector.e_12, g2.Vector),
    (2 * g2.Bivector.e_12, "*", 1 + g2.Bivector.e_12, g2.Rotor),
    # 3D
    (
        g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
        "*",
        4 * g3.Vector.e_1 + 5 * g3.Vector.e_2 + 6 * g3.Vector.e_3,
        g3.Rotor,
    ),
    (
        g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
        "^",
        4 * g3.Vector.e_1 + 5 * g3.Vector.e_2 + 6 * g3.Vector.e_3,
        g3.Bivector,
    ),
    (
        g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
        ".",
        4 * g3.Vector.e_1 + 5 * g3.Vector.e_2 + 6 * g3.Vector.e_3,
        g3.Scalar,
    ),
    (
        g3.Bivector.e_12 + 2 * g3.Bivector.e_13 + 3 * g3.Bivector.e_23,
        "*",
        4 * g3.Bivector.e_12 + 5 * g3.Bivector.e_13 + 6 * g3.Bivector.e_23,
        g3.Rotor,
    ),
    (
        g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
        "*",
        2 * g3.Trivector.e_123,
        g3.Bivector,
    ),
    (2 * g3.Trivector.e_123, "*", 3 * g3.Trivector.e_123, g3.Scalar),
    (
        1 + g3.Bivector.e_12 + g3.Bivector.e_13 + g3.Bivector.e_23,
        "*",
        2 + g3.Bivector.e_12,
        g3.Rotor,
    ),
    (
        g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
        "*",
        4 * g3.Bivector.e_12 + 5 * g3.Bivector.e_13 + 6 * g3.Bivector.e_23,
        g3.G,
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
    assert type(g2.Vector.e_1) is g2.Vector and g2.Vector.e_1 == g2.Vector.basis_vector(
        1
    )
    assert type(g2.Vector.e_2) is g2.Vector and g2.Vector.e_2 == g2.Vector.basis_vector(
        2
    )
    assert type(g2.Bivector.e_12) is g2.Bivector and g2.Bivector.e_12 == (
        g2.Vector.e_1 ^ g2.Vector.e_2
    )
    assert type(g2.G.e_12) is g2.G and g2.G.e_12 == widen(g2.Vector.e_1 ^ g2.Vector.e_2)
    assert type(g3.Vector.e_3) is g3.Vector and g3.Vector.e_3 == g3.Vector.basis_vector(
        3
    )
    assert type(g3.G.e_123) is g3.G
    assert type(g3.Trivector.e_123) is g3.Trivector and g3.Trivector.e_123 == (
        (g3.Vector.e_1 ^ g3.Vector.e_2) ^ g3.Vector.e_3
    )


def test_basis_constant_instance_fallthrough() -> None:
    # the stored field is coeff_e_1, so e_1 is NOT shadowed per-instance: both
    # the class and any instance see the same basis-vector constant, while
    # coeff_e_1 carries the component value
    v: g2.Vector = 5 * g2.Vector.e_1 + 2 * g2.Vector.e_2
    assert v.e_1 is g2.Vector.e_1 and v.e_2 is g2.Vector.e_2
    assert v.coeff_e_1 == 5 and v.coeff_e_2 == 2


def test_coefficient_readback() -> None:
    # coefficient(blade) reads the stored coefficient on a blade, any grade
    v: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    assert v.coefficient(g2.Vector.e_1) == 3 and v.coefficient(g2.Vector.e_2) == 4
    assert (7 * g2.Bivector.e_12).coefficient(g2.Bivector.e_12) == 7
    assert (5 * g3.Trivector.e_123).coefficient(g3.Trivector.e_123) == 5
    b3: g3.Bivector = 4 * g3.Bivector.e_12 + 5 * g3.Bivector.e_13 + 6 * g3.Bivector.e_23
    assert b3.coefficient(g3.Bivector.e_13) == 5


def test_linear_combination_construction() -> None:
    # the basis builds each graded type by linear combination / wedge
    assert type(3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) is g2.Vector
    assert (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) == 3 * gn.e_1 + 4 * gn.e_2
    assert type(g2.Vector.e_1 ^ g2.Vector.e_2) is g2.Bivector
    assert type(2 + 3 * g2.Bivector.e_12) is g2.Rotor and (
        2 + 3 * g2.Bivector.e_12
    ) == 2 * gn.one + 3 * (gn.e_1 ^ gn.e_2)
    assert (
        type(2 + g3.Bivector.e_12) is g3.Rotor
    )  # scalar + bivector narrows to the rotor type
    assert type((g3.Vector.e_1 ^ g3.Vector.e_2) ^ g3.Vector.e_3) is g3.Trivector
    # reflected ops work too
    assert (5 - g2.Bivector.e_12) == 5 * gn.one - (gn.e_1 ^ gn.e_2) and type(
        5 - g2.Bivector.e_12
    ) is g2.Rotor


def test_type_is_operation_driven_not_value_driven() -> None:
    # orthogonal vectors: the scalar (dot) part is exactly 0, but the type stays
    # g2.Rotor -- we never narrow by inspecting a (possibly float-fuzzy) value.
    r: MultiVectorBase = g2.Vector.e_1 * g2.Vector.e_2
    assert type(r) is g2.Rotor and r == gn.e_1 ^ gn.e_2
    # a pure blade is got by *asking* for it (wedge), never by luck of the values
    assert type(g2.Vector.e_1 ^ g2.Vector.e_2) is g2.Bivector


def test_dual_narrows() -> None:
    # left inferred (not annotated MultiVectorBase): the concrete union keeps
    # ``val.dual()`` (dimension-defaulting) and ``val.DIMENSION`` resolvable.
    cases = [
        (
            3 * g2.Vector.e_1 + 4 * g2.Vector.e_2,
            g2.Vector,
        ),  # 2D: vectors are the self-dual grade
        (5 * g2.Bivector.e_12, g2.Scalar),  # 2D: grade 2 -> grade 0
        (
            g3.Vector.e_1 + 2 * g3.Vector.e_2 + 3 * g3.Vector.e_3,
            g3.Bivector,
        ),  # 3D: vector -> bivector
        (
            (g3.Vector.e_1 + 2 * g3.Vector.e_2) ^ (3 * g3.Vector.e_1 + g3.Vector.e_3),
            g3.Vector,
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
        1 + g3.Bivector.e_12 + 2 * g3.Bivector.e_13 + 3 * g3.Bivector.e_23
    )  # a g3.Rotor
    assert type(r.r_vector_part(0)) is g3.Scalar
    assert type(r.r_vector_part(2)) is g3.Bivector
    assert type(r.even_part()) is g3.Rotor
    assert r.r_vector_part(2) == widen(r).r_vector_part(2)
    # a grade absent from the type projects to the zero scalar
    assert type((g3.Vector.e_1 + g3.Vector.e_2).r_vector_part(0)) is g3.Scalar
    assert type((g3.Vector.e_1 + g3.Vector.e_2).even_part()) is g3.Scalar


def test_plane_of_rotation() -> None:
    # the rotor that turns e1 -> e2 rotates in the e1-e2 plane
    r2: MultiVectorBase = g2.Vector.rotor_from_vectors(
        from_vector=g2.Vector.e_1, to_vector=g2.Vector.e_2
    )
    assert type(r2) is g2.Rotor
    assert r2.plane_of_rotation() == -(gn.e_1 ^ gn.e_2)  # the (oriented) unit plane
    r3: MultiVectorBase = g3.Vector.rotor_from_vectors(
        from_vector=g3.Vector.e_1, to_vector=g3.Vector.e_2
    )
    assert type(r3) is g3.Rotor
    plane: MultiVectorBase = r3.plane_of_rotation()
    assert type(plane) is g3.Bivector and plane == -(gn.e_1 ^ gn.e_2)


def test_exp_narrows_bivector_to_rotor() -> None:
    # the exponential map onto the rotors: exp of a bivector IS a rotor, and
    # the generated narrowing override types it that way.  It comes out unit
    # (cos^2 + sin^2 = 1) without normalizing.
    r2: g2.Rotor = g2.Bivector.e_12.exp()
    assert type(r2) is g2.Rotor
    assert sympy.simplify(sympy.sympify(r2.magnitude_squared())) == 1
    r3: g3.Rotor = (g3.Vector.e_1 ^ g3.Vector.e_2).exp()
    assert type(r3) is g3.Rotor
    assert sympy.simplify(sympy.sympify(r3.magnitude_squared())) == 1


def test_scalar_type() -> None:
    s5: g2.Scalar = g2.Scalar.from_scalar(5)
    v: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    assert type(s5 * v) is g2.Vector and s5 * v == 15 * gn.e_1 + 20 * gn.e_2
    assert type(3 * v) is g2.Vector and 3 * v == 9 * gn.e_1 + 12 * gn.e_2
    assert type(v * 2) is g2.Vector
    assert (
        type(g2.Bivector.e_12 * g2.Bivector.e_12) is g2.Scalar
    )  # a pure-scalar product result lands in g2.Scalar


def test_widen_fallback() -> None:
    # a sum with no covering graded type widens to the dimension's full type
    s: MultiVectorBase = (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) + 7 * g2.Bivector.e_12
    assert type(s) is g2.G and s == 3 * gn.e_1 + 4 * gn.e_2 + 7 * (gn.e_1 ^ gn.e_2)
    assert (
        type((3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) * g2.G.from_blade_dict({(1,): 1}))
        is g2.G
    )


def test_cross_type_equality() -> None:
    assert (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) == 3 * gn.e_1 + 4 * gn.e_2
    assert (3 * g2.Vector.e_1 + 4 * g2.Vector.e_2) == g2.G.from_blade_dict(
        {(1,): 3, (2,): 4}
    )
    assert g3.Bivector.e_12 == gn.e_1 ^ gn.e_2


def test_rotor_is_complex_2d() -> None:
    # the even subalgebra of g2.G is the complex numbers: e_12^2 == -1
    assert g2.Bivector.e_12 * g2.Bivector.e_12 == -gn.one


def test_rotor_is_quaternion_3d() -> None:
    # each unit bivector squares to -1 (the even subalgebra of g3.G is the quaternions).
    # bivector*bivector is *typed* g3.Rotor (generally scalar+bivector) -- here the
    # value is a pure scalar, but the type follows the operation, not the value.
    plane: g3.Bivector
    for plane in (g3.Bivector.e_12, g3.Bivector.e_13, g3.Bivector.e_23):
        sq: MultiVectorBase = plane * plane
        assert type(sq) is g3.Rotor and sq == -gn.one


def test_inherited_abc_methods() -> None:
    v: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    assert v.magnitude() == 5
    assert (
        v.normalize() == sympy.Rational(3, 5) * gn.e_1 + sympy.Rational(4, 5) * gn.e_2
    )
    assert (5 * g2.Bivector.e_12).reverse() == -5 * (gn.e_1 ^ gn.e_2)
    assert (g3.Vector.e_1 + 2 * g3.Vector.e_2 + 2 * g3.Vector.e_3).magnitude() == 3


def test_symbolic_product_matches_gn() -> None:
    a1: sympy.Symbol
    a2: sympy.Symbol
    b1: sympy.Symbol
    b2: sympy.Symbol
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    got: MultiVectorBase = (a1 * g2.Vector.e_1 + a2 * g2.Vector.e_2) * (
        b1 * g2.Vector.e_1 + b2 * g2.Vector.e_2
    )
    want: Gn = (a1 * b1 + a2 * b2) * gn.one + (a1 * b2 - a2 * b1) * (gn.e_1 ^ gn.e_2)
    assert got == want and type(got) is g2.Rotor


# --- the rotor sandwich equals projection_rotation(from, to) ------------------
# R = rotor_from_vectors(from, to) = |from||to| + to*from ; for any vector v,
#   R v R.inverse()  ==  projection_rotation(from, to)(v)
# (R.inverse() = R.reverse()/|R|^2 divides out the rotor's scaling, leaving a
# pure rotation.)


def simplify_equal(a: MultiVectorBase, b: MultiVectorBase) -> bool:
    """True iff a and b are equal after simplifying each blade's difference.

    Needed where the values carry ``sqrt`` magnitudes: ``Gn.__eq__`` compares
    eager-simplified forms for identity, which can differ for equal expressions;
    simplifying the *difference* to 0 is the reliable check.
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
    # the same identity holds (by value) for Gn, g2.G and g3.G; the rotor built from
    # vectors of a specialized type is a Rotor of that algebra
    w2: g2.Vector = 2 * g2.Vector.e_1 + g2.Vector.e_2
    r2: MultiVectorBase = g2.Vector.rotor_from_vectors(
        from_vector=g2.Vector.e_1, to_vector=g2.Vector.e_2
    )
    assert type(r2) is g2.Rotor
    assert r2 * w2 * r2.inverse() == projection_rotation(
        from_vector=g2.Vector.e_1, to_vector=g2.Vector.e_2
    )(w2)

    w3: g3.Vector = g3.Vector.e_1 + 3 * g3.Vector.e_3
    r3: MultiVectorBase = g3.Vector.rotor_from_vectors(
        from_vector=g3.Vector.e_1, to_vector=g3.Vector.e_2
    )
    assert type(r3) is g3.Rotor
    assert r3 * w3 * r3.inverse() == projection_rotation(
        from_vector=g3.Vector.e_1, to_vector=g3.Vector.e_2
    )(w3)


def test_unnormalized_rotor_scales_then_normalizes() -> None:
    # the bare sandwich R v R~ scales by R.magnitude_squared(); inverse divides it out
    frm: g2.Vector
    to: g2.Vector
    w: g2.Vector
    frm, to, w = g2.Vector.e_1, g2.Vector.e_2, g2.Vector.e_1  # 90 deg, e1 -> e2
    r: MultiVectorBase = g2.Vector.rotor_from_vectors(from_vector=frm, to_vector=to)
    assert r * r.reverse() == 2 * gn.one  # |R|^2
    assert r * w * r.reverse() == 2 * gn.e_2  # scaled rotation
    assert r * w * r.inverse() == gn.e_2  # pure rotation


def test_project_vector_onto_bivector_trivector_subtypes() -> None:
    # g2.Vector onto the 2D bivector -> itself (the bivector spans the whole plane)
    v2: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    proj2: MultiVectorBase = g2.Vector.project(onto=g2.Bivector.e_12)(v2)
    assert proj2 == v2 and type(proj2) is g2.Vector
    # g3.Vector onto a bivector plane -> the in-plane part, AS a g3.Vector: project is
    # grade-preserving, so it narrows back to the input's type (no widening to g3.G).
    e1: g3.Vector
    e3: g3.Vector
    e1, e3 = g3.Vector.e_1, g3.Vector.e_3
    proj3: MultiVectorBase = g3.Vector.project(onto=g3.Bivector.e_12)(e1 + e3)
    assert proj3 == e1 and type(proj3) is g3.Vector
    assert g3.Vector.project(onto=g3.Bivector.e_12)(e3) == g3.Vector.zero()
    # g3.Vector onto the trivector (all of 3-space) -> itself
    assert g3.Vector.project(onto=g3.Trivector.e_123)(e1 + e3) == e1 + e3
