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

"""``MultiVectorBase.symbolically_equal`` -- the one public home of the
``simplify(a - b) == 0`` value-equality test
(``tasks/reference/symbolic-equality.md``)."""

import sympy

import gacalc.g2 as g2
import gacalc.gn as gn
from gacalc.base import SymbolicSubstitution
from gacalc.gn import Gn


def test_structurally_different_but_equal_forms_are_symbolically_equal() -> None:
    x: sympy.Symbol = sympy.Symbol("x", real=True)
    a: g2.Vector = (x + 1) ** 2 * g2.Vector.e_1 + sympy.sin(x) ** 2 * g2.Vector.e_2
    b: g2.Vector = (x**2 + 2 * x + 1) * g2.Vector.e_1 + (
        1 - sympy.cos(x) ** 2
    ) * g2.Vector.e_2
    assert a.symbolically_equal(b)
    assert b.symbolically_equal(a)


def test_unequal_values_are_not_symbolically_equal() -> None:
    x: sympy.Symbol = sympy.Symbol("x", real=True)
    a: g2.Vector = x * g2.Vector.e_1
    assert not a.symbolically_equal((x + 1) * g2.Vector.e_1)
    assert not a.symbolically_equal(
        x * g2.Vector.e_2
    )  # a blade present on one side only


def test_numeric_values_compare_exactly() -> None:
    a: g2.Vector = g2.Vector(coeff_e_1=3.0, coeff_e_2=4.0)
    assert a.symbolically_equal(g2.Vector(coeff_e_1=3.0, coeff_e_2=4.0))
    assert not a.symbolically_equal(g2.Vector(coeff_e_1=3.0, coeff_e_2=4.0000001))


def test_compares_across_representations() -> None:
    x: sympy.Symbol = sympy.Symbol("x", real=True)
    specialized: g2.Vector = (x + 1) ** 2 * g2.Vector.e_1
    general: Gn = (x**2 + 2 * x + 1) * gn.e_1
    assert specialized.symbolically_equal(general)
    assert general.symbolically_equal(specialized)


def test_substitution_supplies_the_relation_sympy_cannot_find() -> None:
    # sqrt(4c⁴ + 4s²c²) is 2c only given s² = 1 − c²; without the relation the test
    # must stay conservative (False), with it the values are provably equal.
    c: sympy.Symbol
    s: sympy.Symbol
    c, s = sympy.symbols("c s", real=True, positive=True)
    pythagoras: SymbolicSubstitution = {s**2: 1 - c**2}
    a: g2.Vector = sympy.sqrt(4 * c**4 + 4 * s**2 * c**2) * g2.Vector.e_1
    b: g2.Vector = (2 * c) * g2.Vector.e_1
    assert not a.symbolically_equal(b)
    assert a.symbolically_equal(b, subs=pythagoras)
