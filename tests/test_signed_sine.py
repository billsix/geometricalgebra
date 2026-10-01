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

"""The 𝒢₂ signed sine: ``Vector.sine`` = ``(a ∧ b).coeff_e_12 / (|a| |b|)``.

The scalar, oriented companion to the unsigned, any-dimension
``MultiVectorBase.abs_sin``.  These pin: the signed value and that swapping the
operands negates it (the turn direction); the relation ``abs(sine) == abs_sin``;
exactness on integer and symbolic coefficients and the Lagrange identity
``cosine² + sine² == 1``; the raise on a zero-length operand; and that the
method is 𝒢₂-only (no ``sine`` on 𝒢₁ or 𝒢₃'s ``Vector``).
"""

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g3 as g3
from gacalc.g2 import Vector, e_1, e_2


def test_signed_value_and_swap_negates() -> None:
    a: Vector = 1.0 * e_1 + 0.0 * e_2
    b: Vector = 0.0 * e_1 + 1.0 * e_2
    assert a.sine(b) == 1.0  # +90°: e₁ toward e₂ is the positive turn
    assert b.sine(a) == -1.0  # swapping the operands negates the signed sine


def test_parallel_vectors_have_zero_sine() -> None:
    a: Vector = 3.0 * e_1 + 4.0 * e_2
    assert a.sine(a) == 0.0
    assert a.sine(5.0 * a) == 0.0  # scaling does not change the direction


def test_abs_of_signed_sine_equals_abs_sin() -> None:
    # The signed 𝒢₂ sine and the unsigned base-class abs_sin agree in magnitude.
    a: Vector = 3.0 * e_1 + 4.0 * e_2
    b: Vector = -1.0 * e_1 + 2.0 * e_2
    assert abs(a.sine(b)) == pytest.approx(a.abs_sin(b))
    assert abs(b.sine(a)) == pytest.approx(a.abs_sin(b))  # unsigned is symmetric


def test_signed_sine_symbolic_is_the_signed_area_over_magnitudes() -> None:
    a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
    u: Vector = a_1 * e_1 + a_2 * e_2
    v: Vector = b_1 * e_1 + b_2 * e_2
    # sine · |u| · |v| == the signed area (a₁b₂ − a₂b₁), the e₁₂ coefficient of u ∧ v.
    assert (
        sympy.simplify(
            sympy.sympify(u.sine(v) * abs(u) * abs(v) - (a_1 * b_2 - a_2 * b_1))
        )
        == 0
    )


def test_cosine_squared_plus_signed_sine_squared_is_one() -> None:
    # Lagrange's identity, with the SIGNED sine (sin² is unaffected by the sign).
    a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2", real=True)
    u: Vector = a_1 * e_1 + a_2 * e_2
    v: Vector = b_1 * e_1 + b_2 * e_2
    assert sympy.simplify(sympy.sympify(u.cosine(v) ** 2 + u.sine(v) ** 2)) == 1


def test_zero_length_operand_raises() -> None:
    zero_vector: Vector = 0.0 * e_1 + 0.0 * e_2
    unit: Vector = 1.0 * e_1 + 0.0 * e_2
    with pytest.raises(ZeroDivisionError):
        zero_vector.sine(unit)


def test_signed_sine_is_g2_only() -> None:
    # The signed sine needs a single turn direction, which only 𝒢₂ has.
    assert not hasattr(g1.Vector, "sine")
    assert not hasattr(g3.Vector, "sine")
