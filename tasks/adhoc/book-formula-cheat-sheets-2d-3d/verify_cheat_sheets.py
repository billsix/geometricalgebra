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

"""Check every coordinate formula on the cheat sheets against gacalc.

Each ``check`` compares what gacalc computes (left) with the coordinate form
written on ``book/docs/cheat-sheet-2d.rst`` / ``cheat-sheet-3d.rst`` (right),
built here by hand from the same symbols. Run from the repository root, in the
image, after ``python tools/gen_specialized.py``:
``PYTHONPATH=src python tasks/adhoc/book-formula-cheat-sheets-2d-3d/verify_cheat_sheets.py``.
Prints one line per check and exits 1 if any fails.
"""

from __future__ import annotations

import sys

import sympy

from gacalc import frame, measure, transforms, vectorcalc
from gacalc.base import MultiVectorBase, Real
from gacalc.gn import MultiVector, e_1, e_2, e_3
from gacalc.standardposition import rotation_from_to

FAILURES: list[str] = []


def check(name: str, got: MultiVectorBase | Real, expected: MultiVectorBase | Real) -> None:
    """Record whether ``got`` and ``expected`` are equal once simplified."""
    difference: MultiVectorBase | Real = got - expected
    coefficients: list[Real] = (
        list(difference.to_blade_dict().values())
        if isinstance(difference, MultiVectorBase)
        else [difference]
    )
    ok: bool = all(sympy.simplify(sympy.sympify(c)) == 0 for c in coefficients)
    print(("ok    " if ok else "FAIL  ") + name)
    if not ok:
        FAILURES.append(name)


def scalar(value: Real) -> MultiVector:
    """``value`` as a multivector."""
    return MultiVector.from_real(value)


def vector(coordinates: tuple[sympy.Symbol, ...]) -> MultiVector:
    """The vector with these coordinates along e_1, e_2, (e_3)."""
    return sum(
        (scalar(c) * basis for c, basis in zip(coordinates, (e_1, e_2, e_3), strict=False)),
        MultiVector.zero(),
    )


def symbols(names: str) -> tuple[sympy.Symbol, ...]:
    """Real symbols."""
    return tuple(sympy.symbols(names, real=True))


θ: sympy.Symbol = sympy.Symbol("theta", real=True)
m: sympy.Symbol = sympy.Symbol("m", positive=True)
# exp computes cos(|A|) + sin(|A|) * A / |A|, which sympy reduces only for a known sign.
φ: sympy.Symbol = sympy.Symbol("phi", positive=True)
e_12: MultiVector = e_1 * e_2
e_13: MultiVector = e_1 * e_3
e_23: MultiVector = e_2 * e_3
e_123: MultiVector = e_1 * e_2 * e_3


def two_d() -> None:
    """The 𝒢₂ sheet."""
    a1, a2, b1, b2, v1, v2, u1, u2 = symbols("a_1 a_2 b_1 b_2 v_1 v_2 u_1 u_2")
    A0, A1, A2, A12, B12, r0, r12 = symbols("A_0 A_1 A_2 A_12 B_12 r_0 r_12")
    a: MultiVector = vector((a1, a2))
    b: MultiVector = vector((b1, b2))
    v: MultiVector = vector((v1, v2))
    u: MultiVector = vector((u1, u2))
    A: MultiVector = scalar(A0) + vector((A1, A2)) + scalar(A12) * e_12
    B: MultiVector = scalar(B12) * e_12
    R: MultiVector = scalar(r0) + scalar(r12) * e_12
    I_inverse: MultiVector = -1 * e_12
    dot: Real = a1 * b1 + a2 * b2
    wedge: Real = a1 * b2 - a2 * b1
    norm_a: Real = sympy.sqrt(a1**2 + a2**2)
    norm_b: Real = sympy.sqrt(b1**2 + b2**2)
    quarter_v: MultiVector = scalar(-v2) * e_1 + scalar(v1) * e_2
    quarter_a: MultiVector = scalar(-a2) * e_1 + scalar(a1) * e_2

    check("2D basis e12*e12 = -1", e_12 * e_12, scalar(-1))
    check("2D a*b coordinates", a * b, scalar(dot) + scalar(wedge) * e_12)
    check("2D grade 0 of A", A.r_vector_part(0), scalar(A0))
    check("2D grade 1 of A", A.r_vector_part(1), vector((A1, A2)))
    check("2D grade 2 of A", A.r_vector_part(2), scalar(A12) * e_12)
    check(
        "2D reverse of A",
        A.reverse(),
        scalar(A0) + vector((A1, A2)) - scalar(A12) * e_12,
    )
    check("2D reverse of a vector", a.reverse(), a)
    check("2D reverse of B", B.reverse(), -1 * B)
    check("2D reverse of R", R.reverse(), scalar(r0) - scalar(r12) * e_12)
    check("2D |a|", a.magnitude(), norm_a)
    check("2D |B|", B.magnitude(), sympy.Abs(B12))
    check("2D |R|", R.magnitude(), sympy.sqrt(r0**2 + r12**2))
    check("2D a^-1", a.inverse(), a * scalar(1 / (a1**2 + a2**2)))
    check("2D B^-1", B.inverse(), scalar(-1 / B12) * e_12)
    check(
        "2D R^-1",
        R.inverse(),
        (scalar(r0) - scalar(r12) * e_12) * scalar(1 / (r0**2 + r12**2)),
    )
    check("2D a.b", a.inner_product(b), scalar(dot))
    check("2D a.b = <a*b>_0", (a * b).r_vector_part(0), scalar(dot))
    check("2D a.B", a.inner_product(B), scalar(B12) * (scalar(-a2) * e_1 + scalar(a1) * e_2))
    check("2D scalar.a = 0", scalar(A0).inner_product(a), MultiVector.zero())
    check("2D a^b", a.wedge(b), scalar(wedge) * e_12)
    check("2D a^b = <a*b>_2", (a * b).r_vector_part(2), scalar(wedge) * e_12)
    check("2D cos", a.cosine(b), dot / (norm_a * norm_b))
    check("2D |sin|", a.abs_sin(b), sympy.Abs(wedge) / (norm_a * norm_b))
    check("2D area", measure.area(a, b), sympy.Abs(wedge))
    check("2D signed area", measure.signed_area(a, b), wedge)
    check(
        "2D proj_a(b)",
        MultiVector.project(onto=a)(b),
        scalar(dot / (a1**2 + a2**2)) * a,
    )
    check(
        "2D rej_a(b)",
        MultiVector.reject(away_from=a)(b),
        scalar(wedge / (a1**2 + a2**2)) * quarter_a,
    )
    check(
        "2D ref_b(a)",
        MultiVector.reflect(across=b)(a),
        b * a * b.inverse(),
    )
    check(
        "2D ref_b(a) coordinates",
        MultiVector.reflect(across=b)(a),
        scalar(2 * dot / (b1**2 + b2**2)) * b - a,
    )
    check("2D quarter turn", v * e_12, quarter_v)
    check(
        "2D r(v; theta)",
        scalar(sympy.cos(θ)) * v + scalar(sympy.sin(θ)) * quarter_v,
        scalar(v1 * sympy.cos(θ) - v2 * sympy.sin(θ)) * e_1
        + scalar(v1 * sympy.sin(θ) + v2 * sympy.cos(θ)) * e_2,
    )
    check(
        "2D v*(cos + sin e12) = r(v; theta)",
        v * (scalar(sympy.cos(θ)) + scalar(sympy.sin(θ)) * e_12),
        scalar(sympy.cos(θ)) * v + scalar(sympy.sin(θ)) * quarter_v,
    )
    check("2D exp(phi e12)", (scalar(φ) * e_12).exp(), scalar(sympy.cos(φ)) + scalar(sympy.sin(φ)) * e_12)
    from_to: MultiVector = (scalar(dot) * v + scalar(wedge) * quarter_v) * scalar(
        1 / (norm_a * norm_b)
    )
    from gacalc.g2 import Scalar as Scalar2
    from gacalc.g2 import e_1 as g2_e_1
    from gacalc.g2 import e_2 as g2_e_2

    g2_a = Scalar2(a1) * g2_e_1 + Scalar2(a2) * g2_e_2
    g2_b = Scalar2(b1) * g2_e_1 + Scalar2(b2) * g2_e_2
    g2_v = Scalar2(v1) * g2_e_1 + Scalar2(v2) * g2_e_2
    turned = rotation_from_to(g2_a, g2_b)(g2_v)
    check(
        "2D R_a^b(v) (rotation_from_to)",
        scalar(turned.coefficient(g2_e_1)) * e_1 + scalar(turned.coefficient(g2_e_2)) * e_2,
        from_to,
    )
    R_ab: MultiVector = b * a + scalar(norm_a * norm_b)
    check("2D versor_from_vectors = b*a + |a||b|", MultiVector.versor_from_vectors(from_vector=a, to_vector=b), R_ab)
    check("2D R v R^-1 = R_a^b(v)", R_ab * v * R_ab.inverse(), from_to)
    check("2D dual of a", a.dual(2), a * I_inverse)
    check("2D dual of a coordinates", a.dual(2), scalar(a2) * e_1 - scalar(a1) * e_2)
    check("2D dual of B", B.dual(2), scalar(B12))
    check("2D dual of scalar", scalar(A0).dual(2), scalar(-A0) * e_12)
    check("2D uniform scale", transforms.uniform_scale(m=m)(v), scalar(m) * v)
    check("2D translate", transforms.translate(b=b)(v), vector((v1 + b1, v2 + b2)))
    m1, m2 = symbols("m_1 m_2")
    check("2D non-uniform scale", transforms.scale_non_uniform(m1, m2)(v), vector((m1 * v1, m2 * v2)))
    upper: list[MultiVectorBase] = frame.reciprocal_frame([u, v])
    determinant: Real = u1 * v2 - u2 * v1
    check("2D u^1 = v * (u^v)^-1", upper[0], v * u.wedge(v).inverse())
    check("2D v^1 = -u * (u^v)^-1", upper[1], -1 * u * u.wedge(v).inverse())
    check("2D u^1 coordinates", upper[0], vector((v2, -v1)) * scalar(1 / determinant))
    check("2D v^1 coordinates", upper[1], vector((-u2, u1)) * scalar(1 / determinant))
    check("2D i(a, b)", MultiVector.i(a, b), scalar(wedge / sympy.Abs(wedge)) * e_12)
    check("2D even part", A.even_part(), scalar(A0) + scalar(A12) * e_12)
    check("2D odd part", A.odd_part(), vector((A1, A2)))


def three_d() -> None:
    """The 𝒢₃ sheet."""
    a1, a2, a3, b1, b2, b3, c1, c2, c3 = symbols("a_1 a_2 a_3 b_1 b_2 b_3 c_1 c_2 c_3")
    v1, v2, v3 = symbols("v_1 v_2 v_3")
    B12, B13, B23, t, r0, r12, r13, r23 = symbols("B_12 B_13 B_23 t r_0 r_12 r_13 r_23")
    a: MultiVector = vector((a1, a2, a3))
    b: MultiVector = vector((b1, b2, b3))
    c: MultiVector = vector((c1, c2, c3))
    v: MultiVector = vector((v1, v2, v3))
    B: MultiVector = scalar(B12) * e_12 + scalar(B13) * e_13 + scalar(B23) * e_23
    T: MultiVector = scalar(t) * e_123
    R: MultiVector = scalar(r0) + scalar(r12) * e_12 + scalar(r13) * e_13 + scalar(r23) * e_23
    I_inverse: MultiVector = -1 * e_123
    dot: Real = a1 * b1 + a2 * b2 + a3 * b3
    w12: Real = a1 * b2 - a2 * b1
    w13: Real = a1 * b3 - a3 * b1
    w23: Real = a2 * b3 - a3 * b2
    norm_a: Real = sympy.sqrt(a1**2 + a2**2 + a3**2)
    norm_b: Real = sympy.sqrt(b1**2 + b2**2 + b3**2)
    determinant: Real = c1 * w23 - c2 * w13 + c3 * w12

    check("3D I*I = -1", e_123 * e_123, scalar(-1))
    check("3D I commutes with e1", e_123 * e_1, e_1 * e_123)
    check("3D e12*e3 = I", e_12 * e_3, e_123)
    check("3D a*b coordinates", a * b, scalar(dot) + scalar(w12) * e_12 + scalar(w13) * e_13 + scalar(w23) * e_23)
    check("3D reverse of B", B.reverse(), -1 * B)
    check("3D reverse of T", T.reverse(), -1 * T)
    check("3D reverse of R", R.reverse(), scalar(r0) - (R - scalar(r0)))
    check("3D |a|", a.magnitude(), norm_a)
    check("3D |B|", B.magnitude(), sympy.sqrt(B12**2 + B13**2 + B23**2))
    check("3D |T|", T.magnitude(), sympy.Abs(t))
    check("3D |R|", R.magnitude(), sympy.sqrt(r0**2 + r12**2 + r13**2 + r23**2))
    check("3D a^-1", a.inverse(), a * scalar(1 / norm_a**2))
    check("3D B^-1", B.inverse(), -1 * B * scalar(1 / (B12**2 + B13**2 + B23**2)))
    check("3D T^-1", T.inverse(), scalar(-1 / t) * e_123)
    check("3D R^-1", R.inverse(), R.reverse() * scalar(1 / (r0**2 + r12**2 + r13**2 + r23**2)))
    check("3D a.b", a.inner_product(b), scalar(dot))
    check(
        "3D a.B",
        a.inner_product(B),
        vector((-a2 * B12 - a3 * B13, a1 * B12 - a3 * B23, a1 * B13 + a2 * B23)),
    )
    check("3D a^b", a.wedge(b), scalar(w12) * e_12 + scalar(w13) * e_13 + scalar(w23) * e_23)
    check("3D a^B", a.wedge(B), scalar(a1 * B23 - a2 * B13 + a3 * B12) * e_123)
    check("3D a^b^c", a.wedge(b).wedge(c), scalar(determinant) * e_123)
    check("3D cross = (a^b) I^-1", vectorcalc.cross(a, b), a.wedge(b) * I_inverse)
    check("3D cross coordinates", vectorcalc.cross(a, b), vector((w23, -w13, w12)))
    check("3D dual of a", a.dual(3), a * I_inverse)
    check("3D dual of a coordinates", a.dual(3), scalar(-a3) * e_12 + scalar(a2) * e_13 - scalar(a1) * e_23)
    check("3D dual of B coordinates", B.dual(3), vector((B23, -B13, B12)))
    check("3D dual of T", T.dual(3), scalar(t))
    check("3D cos", a.cosine(b), dot / (norm_a * norm_b))
    check("3D |sin|", a.abs_sin(b), sympy.sqrt(w12**2 + w13**2 + w23**2) / (norm_a * norm_b))
    check("3D area", measure.area(a, b), sympy.sqrt(w12**2 + w13**2 + w23**2))
    check("3D signed volume", measure.signed_volume(a, b, c), determinant)
    check("3D volume", measure.volume(a, b, c), sympy.Abs(determinant))
    check("3D proj_a(b)", MultiVector.project(onto=a)(b), scalar(dot / norm_a**2) * a)
    check("3D rej_a(b)", MultiVector.reject(away_from=a)(b), b - scalar(dot / norm_a**2) * a)
    check("3D proj_B(v) = (v.B)B^-1", MultiVector.project(onto=B)(v), v.inner_product(B) * B.inverse())
    check("3D rej_B(v) = (v^B)B^-1", MultiVector.reject(away_from=B)(v), v.wedge(B) * B.inverse())
    check("3D proj_e12(v)", MultiVector.project(onto=e_12)(v), vector((v1, v2)))
    check("3D rej_e12(v)", MultiVector.reject(away_from=e_12)(v), scalar(v3) * e_3)
    check("3D ref_b(a) = b a b^-1", MultiVector.reflect(across=b)(a), b * a * b.inverse())
    check("3D ref_b(a) coordinates", MultiVector.reflect(across=b)(a), scalar(2 * dot / norm_b**2) * b - a)
    check("3D ref_B(v) = -B v B^-1", MultiVector.reflect(across=B)(v), -1 * B * v * B.inverse())
    check("3D ref_e12(v)", MultiVector.reflect(across=e_12)(v), vector((v1, v2, -v3)))
    turned: MultiVectorBase = transforms.plane_rotation(e_1, e_2)(θ)(v)
    check(
        "3D plane rotation in e12",
        turned,
        vector((v1 * sympy.cos(θ) - v2 * sympy.sin(θ), v1 * sympy.sin(θ) + v2 * sympy.cos(θ), v3)),
    )
    half: MultiVector = scalar(sympy.cos(θ / 2)) - scalar(sympy.sin(θ / 2)) * e_12
    check("3D R v R~ with R = cos(t/2) - sin(t/2) i", half * v * half.reverse(), turned)
    check(
        "3D exp(-i phi/2)",
        (scalar(-φ / 2) * e_12).exp(),
        scalar(sympy.cos(φ / 2)) - scalar(sympy.sin(φ / 2)) * e_12,
    )
    R_ab: MultiVector = b * a + scalar(norm_a * norm_b)
    check("3D versor_from_vectors", MultiVector.versor_from_vectors(from_vector=a, to_vector=b), R_ab)
    check(
        "3D versor_rotation = R v R^-1",
        transforms.versor_rotation(from_vector=a, to_vector=b)(v),
        R_ab * v * R_ab.inverse(),
    )
    upper: list[MultiVectorBase] = frame.reciprocal_frame([a, b, c])
    volume_inverse: MultiVectorBase = a.wedge(b).wedge(c).inverse()
    check("3D a^1 = (b^c) V^-1", upper[0], b.wedge(c) * volume_inverse)
    check("3D b^1 = -(a^c) V^-1", upper[1], -1 * a.wedge(c) * volume_inverse)
    check("3D c^1 = (a^b) V^-1", upper[2], a.wedge(b) * volume_inverse)
    check("3D a^1 = (b x c)/det", upper[0], vectorcalc.cross(b, c) * scalar(1 / determinant))
    check("3D b^1 = (c x a)/det", upper[1], vectorcalc.cross(c, a) * scalar(1 / determinant))
    check("3D c^1 = (a x b)/det", upper[2], vectorcalc.cross(a, b) * scalar(1 / determinant))
    check("3D uniform scale", transforms.uniform_scale(m=m)(v), scalar(m) * v)
    check("3D translate", transforms.translate(b=b)(v), vector((v1 + b1, v2 + b2, v3 + b3)))
    m1, m2, m3 = symbols("m_1 m_2 m_3")
    check("3D non-uniform scale", transforms.scale_non_uniform(m1, m2, m3)(v), vector((m1 * v1, m2 * v2, m3 * v3)))
    check("3D i(a, b)", MultiVector.i(a, b), a.wedge(b) * scalar(1 / sympy.sqrt(w12**2 + w13**2 + w23**2)))
    check("3D even part", (scalar(r0) + a + B + T).even_part(), scalar(r0) + B)
    check("3D odd part", (scalar(r0) + a + B + T).odd_part(), a + T)
    check("3D reverse of A0 + a + B + T", (scalar(r0) + a + B + T).reverse(), scalar(r0) + a - B - T)


two_d()
three_d()
print(f"{len(FAILURES)} failed")
sys.exit(1 if FAILURES else 0)
