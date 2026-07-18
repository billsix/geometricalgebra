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

"""Subclasses of the generated types survive same-type operations.

The generated closed-form ops construct same-type results via ``type(self)``
(see tools/gen_specialized.py), so a downstream subclass -- e.g.
modelviewprojection's pygame-``Vector2`` work-alike backed by
:class:`gacalc.g2.Vector2` -- gets its own type back from arithmetic.
Grade-changing results (``Vector2 * Vector2 -> Rotor2``) deliberately stay
the registered concrete type: the subclass has no say over a different
grade's class.
"""

from gacalc.base import Coef
from gacalc.g2 import G2, Bivector2, Rotor2, Vector2
from gacalc.g3 import Vector3
from gacalc.scalar import Scalar


class MyV2(Vector2):
    """A downstream subclass adding non-algebra API (like the pygame shim)."""

    @property
    def x(self) -> Coef:
        return self.coeff_e_1


class MyG2(G2):
    pass


class MyV3(Vector3):
    pass


class MyScalar(Scalar):
    pass


def test_same_type_linear_ops_preserve_subclass() -> None:
    a: MyV2 = MyV2(coeff_e_1=1.0, coeff_e_2=2.0)
    b: MyV2 = MyV2(coeff_e_1=3.0, coeff_e_2=4.0)
    assert type(a + b) is MyV2
    assert type(a - b) is MyV2
    assert type(-a) is MyV2
    assert type(a * 2) is MyV2
    assert type(2 * a) is MyV2
    assert type(a.reverse()) is MyV2
    assert (a + b).x == 4.0  # the subclass's own API survives arithmetic


def test_mixed_operand_uses_left_type() -> None:
    sub: MyV2 = MyV2(coeff_e_1=1.0, coeff_e_2=0.0)
    base: Vector2 = Vector2(coeff_e_1=0.0, coeff_e_2=1.0)
    assert type(sub + base) is MyV2


def test_grade_changing_results_stay_registered_types() -> None:
    a: MyV2 = MyV2(coeff_e_1=1.0, coeff_e_2=0.0)
    b: MyV2 = MyV2(coeff_e_1=0.0, coeff_e_2=1.0)
    assert type(a * b) is Rotor2  # geometric product widens
    assert type(a ^ b) is Bivector2  # wedge changes grade
    assert type(a + Rotor2(coeff_scalar=1.0, coeff_e_12=0.0)) is G2


def test_full_class_subclass_preserved() -> None:
    p: MyG2 = MyG2(coeff_scalar=1.0, coeff_e_1=2.0)
    q: MyG2 = MyG2(coeff_e_2=3.0, coeff_e_12=4.0)
    assert type(p + q) is MyG2
    assert type(p - q) is MyG2
    assert type(-p) is MyG2
    assert type(p.reverse()) is MyG2
    assert type(p * q) is MyG2  # full-class product is same-type


def test_g3_subclass_preserved() -> None:
    a: MyV3 = MyV3(coeff_e_1=1.0)
    b: MyV3 = MyV3(coeff_e_2=1.0)
    assert type(a + b) is MyV3
    assert type(a * 2.0) is MyV3


def test_scalar_subclass_preserved() -> None:
    s: MyScalar = MyScalar(coeff_scalar=2.0)
    assert type(s * 3) is MyScalar
    assert type(3 * s) is MyScalar
    assert type(s + 1) is MyScalar
    assert type(-s) is MyScalar
    assert type(s.reverse()) is MyScalar
    assert type(s.even_part()) is MyScalar


def test_sandwich_returns_operand_subclass() -> None:
    # base.sandwich documents "returns a value of x's own type"; the
    # generated closed-form Rotor sandwich honors that for subclasses too.
    r: Rotor2 = Rotor2(coeff_scalar=1.0, coeff_e_12=0.0)
    v: MyV2 = MyV2(coeff_e_1=1.0, coeff_e_2=2.0)
    assert type(r.sandwich(v)) is MyV2


def test_values_unchanged_by_construction_path() -> None:
    a: MyV2
    b: MyV2
    a, b = MyV2(coeff_e_1=1.0, coeff_e_2=2.0), MyV2(coeff_e_1=3.0, coeff_e_2=4.0)
    plain: Vector2 = Vector2(coeff_e_1=1.0, coeff_e_2=2.0) + Vector2(
        coeff_e_1=3.0, coeff_e_2=4.0
    )
    assert (a + b).to_blade_dict() == plain.to_blade_dict()
