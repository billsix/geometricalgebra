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


import itertools

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase
from gacalc.gn import (
    MultiVector,
    a_1,
    a_2,
    a_3,
    b_1,
    b_2,
    b_3,
    e_1,
    e_2,
    e_3,
    e_4,
    one,
    projection_rotation,
    zero,
)
from gacalc.transforms import ComposableFunction


def test_multivector_add() -> None:
    a: MultiVector = 5 * e_1 + 6 * e_2
    b: MultiVector = 7 * e_1 + 8 * e_2
    assert (a + b) == (12 * e_1 + 14 * e_2)

    c: MultiVector = 7 * e_1 + 2 * e_2
    d: MultiVector = 1 * e_1 + 3 * e_3
    assert (c + d) == (8 * e_1 + 2 * e_2 + 3 * e_3)


def test_multivector_subtract() -> None:
    a: MultiVector = 5 * e_1 + 6 * e_2
    b: MultiVector = 7 * e_1 + 9 * e_2
    # doc-region-end test add
    assert (b - a) == (2 * e_1 + 3 * e_2)


def test_multivector_absolute_units() -> None:
    # test addition
    assert (1 * e_1 + 1 * e_2) == (1 * e_2 + 1 * e_1)

    # test scalar multiplication
    assert (e_1 * 2) == (1 * e_1 + 1 * e_1)
    assert (2 * e_1) == (1 * e_1 + 1 * e_1)
    assert (e_2 * 2) == (1 * e_2 + 1 * e_2)
    assert (2 * e_2) == (1 * e_2 + 1 * e_2)

    # test addition on relative units
    assert ((1 * e_1 + 1 * e_2) * 2) == ((1 * e_1 + 1 * e_2) + (1 * e_1 + 1 * e_2))

    # test permutations
    assert (e_1 * e_2 * e_3).magnitude_squared() == 1
    assert (e_1 * e_3 * e_2) == -1 * (e_1 * e_2 * e_3)
    assert (e_3 * e_1 * e_2) == (e_1 * e_2 * e_3)
    assert (e_3 * e_2 * e_1) == -1 * (e_1 * e_2 * e_3)
    assert (e_2 * e_1 * e_3) == -1 * (e_1 * e_2 * e_3)
    assert (e_2 * e_3 * e_1) == (e_1 * e_2 * e_3)

    # test internal representation
    # 2D
    assert (a_1 * e_1) * (b_2 * e_2) == MultiVector({(1, 2): a_1 * b_2})
    assert (b_2 * e_2) * (a_1 * e_1) == MultiVector({(1, 2): -a_1 * b_2})

    # 3D
    assert (a_1 * e_2) * (b_2 * e_3) == MultiVector({(2, 3): a_1 * b_2})
    assert (b_2 * e_3) * (a_1 * e_2) == MultiVector({(2, 3): -a_1 * b_2})

    # 3D
    assert (a_1 * e_3) * (b_2 * e_1) == MultiVector({(1, 3): -a_1 * b_2})
    assert (b_2 * e_1) * (a_1 * e_3) == MultiVector({(1, 3): a_1 * b_2})

    # 4D
    assert (a_1 * e_1) * (b_2 * e_4) == MultiVector({(1, 4): a_1 * b_2})
    assert (b_2 * e_4) * (a_1 * e_1) == MultiVector({(1, 4): -a_1 * b_2})

    # 4D
    assert (a_1 * e_4) * (b_2 * e_2) == MultiVector({(2, 4): -a_1 * b_2})
    assert (b_2 * e_2) * (a_1 * e_4) == MultiVector({(2, 4): a_1 * b_2})

    # 4D
    assert (a_1 * e_3) * (b_2 * e_4) == MultiVector({(3, 4): a_1 * b_2})
    assert (b_2 * e_4) * (a_1 * e_3) == MultiVector({(3, 4): -a_1 * b_2})

    # 4D
    assert (a_3 * e_2) * (a_1 * e_3) * (b_2 * e_4) == MultiVector(
        {(2, 3, 4): a_3 * a_1 * b_2}
    )
    assert (a_1 * e_3) * (a_3 * e_2) * (b_2 * e_4) == MultiVector(
        {(2, 3, 4): -a_3 * a_1 * b_2}
    )
    assert (a_1 * e_3) * (b_2 * e_4) * (a_3 * e_2) == MultiVector(
        {(2, 3, 4): a_3 * a_1 * b_2}
    )


def test_multivector_mult() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.magnitude_squared() == 25

    assert (a * a) == MultiVector.from_scalar(25)
    assert (a * a).is_scalar()

    i: MultiVector = MultiVector.unit_pseudoscalar(2)
    assert (a * i) == (-4 * e_1 + 3 * e_2)
    assert ((a * i) * i) == -3 * e_1 + -4 * e_2

    # general 2D vectors: the geometric product is the scalar dot plus the
    # bivector wedge -- read both parts off explicitly:
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    assert (u * v) == (
        MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2)  # dot: u·v
        + (a_1 * b_2 - a_2 * b_1) * e_1 * e_2  # wedge: (u∧v) e_12
    )
    # the same product, split via the pseudoscalar i:
    assert (u * v) == u.dot(v) + (u * i).dot(v) * i


def test_multivector_mult3d() -> None:
    def planewise_wedge(
        plane: MultiVectorBase, vec1: MultiVectorBase, vec2: MultiVectorBase
    ) -> MultiVectorBase:
        proj: ComposableFunction = MultiVector.project(plane)
        return proj(vec1).wedge(proj(vec2))

    # general 3D vectors:
    u: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    v: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

    # the geometric product = the scalar dot + the three bivector wedge parts:
    assert (u * v) == (
        MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2 + a_3 * b_3)  # dot
        + (a_1 * b_2 - a_2 * b_1) * e_1 * e_2  # wedge in the e_1 e_2 plane
        + (a_2 * b_3 - a_3 * b_2) * e_2 * e_3  # wedge in the e_2 e_3 plane
        + (a_3 * b_1 - a_1 * b_3) * e_3 * e_1  # wedge in the e_3 e_1 plane
    )

    # the dot product, explicitly:
    assert u.dot(v).scalar_part() == a_1 * b_1 + a_2 * b_2 + a_3 * b_3

    # and the product rebuilt as dot + (the wedge summed over the three planes):
    assert (u * v) == sum(
        [
            u.dot(v),
            *[
                planewise_wedge(plane=axis_1.wedge(axis_2), vec1=u, vec2=v)
                for axis_1, axis_2 in itertools.combinations(
                    [1 * e_1, 1 * e_2, 1 * e_3], 2
                )
            ],
        ],
        start=zero,
    )
    assert u.wedge(v) == sum(
        [
            planewise_wedge(plane=axis_1 * axis_2, vec1=u, vec2=v)
            for axis_1, axis_2 in itertools.combinations([1 * e_1, 1 * e_2, 1 * e_3], 2)
        ],
        start=zero,
    )


def test_multivector_dual() -> None:
    # the dual of a general 2D vector rotates it 90 degrees:
    u2: MultiVector = a_1 * e_1 + a_2 * e_2
    assert u2.dual(n=2) == a_2 * e_1 - a_1 * e_2

    # the dual of a general 3D vector is the perpendicular bivector:
    u3: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    assert u3.dual(n=3) == -a_3 * e_1 * e_2 - a_2 * e_3 * e_1 - a_1 * e_2 * e_3


def test_multivector_grade() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.r_vector_part(0) == zero
    assert a.scalar_part() == 0
    assert a.max_grade() == 1

    b: MultiVector = 3 * e_1 + 4 * e_2

    assert (b * b).scalar_part() == 25
    assert (b * b).r_vector_part(1) == zero
    assert (b * b).r_vector_part(2) == zero
    assert (b * b).max_grade() == 0

    c: MultiVector = -4 * e_1 + 3 * e_2
    assert (b * c).scalar_part() == 0
    assert (b * c).r_vector_part(1) == zero
    assert (b * c).r_vector_part(2) == 25 * e_1 * e_2
    assert (b * c).max_grade() == 2

    i3: MultiVector = e_1 * e_2 * e_3
    assert i3.scalar_part() == 0
    assert i3.r_vector_part(1) == zero
    assert i3.r_vector_part(2) == zero
    assert i3.r_vector_part(3) == i3
    assert i3.max_grade() == 3


def test_is_homogeneous_of_grade_r() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.is_homogeneous_of_grade_r(1)
    assert (a * a).is_homogeneous_of_grade_r(0)
    assert not (a * a).is_homogeneous_of_grade_r(1)
    assert not (a * a).is_homogeneous_of_grade_r(2)

    b: MultiVector = -4 * e_1 + 3 * e_2

    assert (a * b).is_homogeneous_of_grade_r(2)
    assert (a.wedge(b)).is_homogeneous_of_grade_r(2)

    c: MultiVector = 0 * e_1 + 5 * e_2
    assert not (a * c).is_homogeneous_of_grade_r(2)
    assert (a.wedge(c)).is_homogeneous_of_grade_r(2)


def test_is_vector() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.is_vector()
    assert not (a * a).is_vector()


def test_is_bivector() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    b: MultiVector = 0 * e_1 + 1 * e_2
    assert not (a * b).is_bivector()
    assert (a.wedge(b)).is_bivector()


def test_zero_multivector_is_homogeneous_of_every_grade() -> None:
    """The zero multivector has no present blades, so it is trivially homogeneous of
    EVERY grade -- consistent with ``is_scalar(zero) == True``.  The grade predicates
    must return that, not crash on ``max([])``.  Regression for the max_grade()-on-zero
    bug (across representations: general Gn, a graded type, and the full G)."""
    z: MultiVectorBase
    for z in (zero, g2.Vector.zero(), g2.G.zero(), g3.Bivector.zero()):
        assert z.max_grade() == 0
        assert z.is_scalar()
        assert z.is_vector()
        assert z.is_bivector()
        assert z.is_trivector()
        assert z.is_r_vector()
        assert z.is_homogeneous_of_grade_r(0)
        assert z.is_homogeneous_of_grade_r(1)
        assert z.is_homogeneous_of_grade_r(2)


def test_even_part_odd_part() -> None:
    u: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    v: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    # a vector is purely odd (grade 1):
    assert u.odd_part() == u
    assert u.even_part() == zero
    # a product of two vectors is purely even (scalar + bivector):
    assert (u * v).odd_part() == zero
    assert (u * v).even_part() == u * v
    # any multivector is the sum of its even and odd parts:
    assert (u * v) == (u * v).odd_part() + (u * v).even_part()


def test_multivector_dot() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.dot(a) == MultiVector.from_scalar(25)
    assert a.dot(a).is_scalar()
    c: MultiVector = -4 * e_1 + 3 * e_2
    assert a.dot(c) == zero

    # general 2D vectors: the dot product is the scalar a_1 b_1 + a_2 b_2:
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    assert u.dot(v) == MultiVector.from_scalar(a_1 * b_1 + a_2 * b_2)
    assert u.dot(v).is_scalar()


def test_is_orthogonal() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    c: MultiVector = -4 * e_1 + 3 * e_2
    assert a.is_orthogonal_to(c)


def test_multivector_cosine() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.cosine(a) == 1
    b: MultiVector = -4 * e_1 + 3 * e_2
    assert a.cosine(b) == 0

    # general 2D vectors: cos θ · |u| · |v| == u · v (the definition of cosine):
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    assert MultiVector.from_scalar(u.cosine(v) * abs(u) * abs(v)) == u.dot(v)


def test_multivector_wedge() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.wedge(a) == zero
    c: MultiVector = -4 * e_1 + 3 * e_2
    assert a.wedge(c) == 25 * e_1 * e_2

    # general 2D vectors: the wedge is the bivector (a_1 b_2 - a_2 b_1) e_12,
    # reachable the same three ways:
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    expected_wedge: MultiVector = (a_1 * b_2 - a_2 * b_1) * e_1 * e_2
    assert u.wedge(v) == expected_wedge  # the method
    assert (u ^ v) == expected_wedge  # the ^ operator
    assert MultiVector.outer_product_of_vectors(u, v) == expected_wedge  # the free fn


def test_multivector_unit_pseudoscalar() -> None:
    assert MultiVector.unit_pseudoscalar(1) == e_1
    assert MultiVector.unit_pseudoscalar(2) == e_1 * e_2
    assert MultiVector.unit_pseudoscalar(3) == e_1 * e_2 * e_3

    i1: MultiVector = MultiVector.unit_pseudoscalar(1)
    assert i1 * i1 == one
    assert MultiVector.unit_pseudoscalar_squared(1) == one
    i2: MultiVector = MultiVector.unit_pseudoscalar(2)
    assert i2 * i2 == -one
    assert MultiVector.unit_pseudoscalar_squared(2) == -one
    i3: MultiVector = MultiVector.unit_pseudoscalar(3)
    assert i3 * i3 == -one
    i4: MultiVector = MultiVector.unit_pseudoscalar(4)
    assert i4 * i4 == one
    i5: MultiVector = MultiVector.unit_pseudoscalar(5)
    assert i5 * i5 == one
    i6: MultiVector = MultiVector.unit_pseudoscalar(6)
    assert i6 * i6 == -one
    i7: MultiVector = MultiVector.unit_pseudoscalar(7)
    assert i7 * i7 == -one
    i8: MultiVector = MultiVector.unit_pseudoscalar(8)
    assert i8 * i8 == one
    i9: MultiVector = MultiVector.unit_pseudoscalar(9)
    assert i9 * i9 == one
    i10: MultiVector = MultiVector.unit_pseudoscalar(10)
    assert i10 * i10 == -one
    i11: MultiVector = MultiVector.unit_pseudoscalar(11)
    assert i11 * i11 == -one
    i12: MultiVector = MultiVector.unit_pseudoscalar(12)
    assert i12 * i12 == one
    i13: MultiVector = MultiVector.unit_pseudoscalar(13)
    assert i13 * i13 == one
    i14: MultiVector = MultiVector.unit_pseudoscalar(14)
    assert i14 * i14 == -one
    i15: MultiVector = MultiVector.unit_pseudoscalar(15)
    assert i15 * i15 == -one


def test_multivector_reverse() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert (a * a).reverse() == a * a

    b: MultiVector = 5 * e_1 + 10 * e_2
    assert (b * a).reverse() == a * b

    # for two general 2D vectors, reversing v u gives u v (reverse flips the
    # order of the basis vectors in each blade):
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    assert (v * u).reverse() == u * v


def test_multivector_reverse_3d() -> None:
    u: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    v: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    assert (v * u).reverse() == u * v


def test_multivector_inverse() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert a.magnitude_squared() == 25
    assert a.magnitude_squared() * a.inverse() == a

    # a general 2D vector: |u|² · u⁻¹ == u, and u⁻¹ u == 1
    u2: MultiVector = a_1 * e_1 + a_2 * e_2
    assert u2.magnitude_squared() * u2.inverse() == u2
    assert (u2.inverse() * u2).scalar_part() == 1

    # a general 3D vector:
    u3: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    assert u3.magnitude_squared() * u3.inverse() == u3
    assert (u3.inverse() * u3) == one

    # a bivector -- the plane spanned by two general 3D vectors -- is invertible too:
    v3: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    plane: MultiVector = u3 ^ v3
    assert (plane * plane.inverse()) == one
    assert (plane.inverse() * plane) == one


def test_project_and_reject() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2
    assert MultiVector.project(onto=e_1)(a) == 3 * e_1
    assert MultiVector.reject(away_from=e_1)(a) == 4 * e_2

    assert MultiVector.project(onto=[1 * e_1, 1 * e_2])(a) == a
    assert MultiVector.reject(away_from=[1 * e_1, 1 * e_2])(a) == zero

    assert MultiVector.project(onto=e_1)(2 * a) == 6 * e_1
    assert MultiVector.reject(away_from=e_1)(2 * a) == 8 * e_2

    assert MultiVector.project(onto=2 * e_1)(a) == 3 * e_1
    assert MultiVector.reject(away_from=2 * e_1)(a) == 4 * e_2

    # 1-element sequence (regression: must use outer_product_of_vectors, not the
    # instance method outer_product, which only happens to work for exactly 2
    # elements -- a 1-element span used to raise TypeError on the missing rhs)
    assert MultiVector.project(onto=[1 * e_1])(a) == 3 * e_1
    assert MultiVector.reject(away_from=[1 * e_1])(a) == 4 * e_2

    # for general 2D vectors, projecting v onto u and rejecting v from u split v
    # into its parallel and perpendicular parts, which sum back to v:
    u: MultiVector = a_1 * e_1 + a_2 * e_2
    v: MultiVector = b_1 * e_1 + b_2 * e_2
    parallel: MultiVectorBase = MultiVector.project(onto=u)(v)
    perpendicular: MultiVectorBase = MultiVector.reject(away_from=u)(v)
    assert v == parallel + perpendicular


def test_reflect() -> None:
    a: MultiVector = 3 * e_1 + 4 * e_2 + 5 * e_3

    # reflect across vectors
    assert MultiVector.reflect(across=e_1)(a) == 3 * e_1 + -4 * e_2 + -5 * e_3
    assert MultiVector.reflect(across=e_2)(a) == -3 * e_1 + 4 * e_2 + -5 * e_3
    assert MultiVector.reflect(across=e_3)(a) == -3 * e_1 + -4 * e_2 + 5 * e_3

    # reflect across planes
    assert (
        MultiVector.reflect(across=[1 * e_1, 1 * e_2])(a)
        == 3 * e_1 + 4 * e_2 + -5 * e_3
    )
    assert MultiVector.reflect(across=e_1 * e_2)(a) == 3 * e_1 + 4 * e_2 + -5 * e_3

    # reflect across a 1-element span (regression: 1-element sequence must not
    # crash -- same outer_product arity bug as project/reject)
    assert MultiVector.reflect(across=[1 * e_1])(a) == MultiVector.reflect(across=e_1)(
        a
    )
    assert MultiVector.reflect(across=e_1 ^ e_2)(a) == 3 * e_1 + 4 * e_2 + -5 * e_3

    assert (
        MultiVector.reflect(across=[1 * e_2, 1 * e_3])(a)
        == -3 * e_1 + 4 * e_2 + 5 * e_3
    )
    assert (
        MultiVector.reflect(across=[1 * e_3, 1 * e_1])(a)
        == 3 * e_1 + -4 * e_2 + 5 * e_3
    )
    assert (
        MultiVector.reflect(across=[1 * e_1, 1 * e_3])(a)
        == 3 * e_1 + -4 * e_2 + 5 * e_3
    )


def test_normalize() -> None:
    # normalizing a vector divides it by its own magnitude:
    u2: MultiVector = a_1 * e_1 + a_2 * e_2
    assert u2.normalize() == u2 * (abs(u2) ** (-1))
    u3: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    assert u3.normalize() == u3 * (abs(u3) ** (-1))


def test_rotate() -> None:
    # rotate across planes
    a: MultiVector = 3 * e_1 + 4 * e_2 + 5 * e_3
    # rotate across e_1 e_2 plane
    assert (
        projection_rotation(from_vector=e_1, to_vector=e_2)(a)
        == -4 * e_1 + 3 * e_2 + 5 * e_3
    )
    assert (
        projection_rotation(from_vector=e_2, to_vector=e_1)(a)
        == 4 * e_1 - 3 * e_2 + 5 * e_3
    )
    # rotate across e_2 e_3 plane
    b: MultiVector = 5 * e_1 + 3 * e_2 + 4 * e_3
    assert (
        projection_rotation(from_vector=e_2, to_vector=e_3)(b)
        == 5 * e_1 + -4 * e_2 + 3 * e_3
    )
    assert (
        projection_rotation(from_vector=e_3, to_vector=e_2)(b)
        == 5 * e_1 + 4 * e_2 - 3 * e_3
    )
    # rotate across e_3 e_1 plane
    c: MultiVector = 4 * e_1 + 5 * e_2 + 3 * e_3
    assert (
        projection_rotation(from_vector=e_3, to_vector=e_1)(c)
        == 3 * e_1 + 5 * e_2 + -4 * e_3
    )
    assert (
        projection_rotation(from_vector=e_1, to_vector=e_3)(c)
        == -3 * e_1 + 5 * e_2 + 4 * e_3
    )
