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

"""Subclassing policy for the generated types.

The graded value types (``Vector1/2/3``, ``Bivector2/3``, ``Trivector3``,
``Rotor2/3``) and the shared ``Scalar`` are **`@typing.final`** -- they are leaf
value types and must not be subclassed.  This is a static guarantee: `ty` rejects
any subclass with ``error[subclass-of-final-class]`` (see tools/gen_specialized.py).
Because they are final, the generated code may treat ``type(self)`` as the exact
concrete class.

The **full classes ``G1``/``G2``/``G3`` stay subclassable** -- the general
``Gₙ``-representation is the natural extension point -- and their same-type ops
construct via ``type(self)``, so a subclass gets its own type back from arithmetic.
"""

from gacalc.g1 import Vector1
from gacalc.g2 import G2, Bivector2, Rotor2, Vector2
from gacalc.g3 import Bivector3, Rotor3, Trivector3, Vector3
from gacalc.scalar import Scalar

_FINAL_TYPES: list[type] = [
    Scalar,
    Vector1,
    Vector2,
    Bivector2,
    Rotor2,
    Vector3,
    Bivector3,
    Trivector3,
    Rotor3,
]


def test_graded_and_scalar_types_are_final() -> None:
    # ``@typing.final`` sets ``__final__ = True`` (Python 3.11+); ty additionally
    # rejects any subclass at check time.  A downstream consumer uses these types
    # directly (not by subclassing) -- see modelviewprojection.
    for graded in _FINAL_TYPES:
        assert getattr(graded, "__final__", False), (
            f"{graded.__name__} should be @typing.final"
        )


def test_full_classes_are_not_final() -> None:
    # The full G_n classes remain subclassable (the extension point).
    assert not getattr(G2, "__final__", False)


class MyG2(G2):
    """A downstream subclass of the full class, adding non-algebra API."""


def test_full_class_subclass_preserved() -> None:
    p: MyG2 = MyG2(coeff_scalar=1.0, coeff_e_1=2.0)
    q: MyG2 = MyG2(coeff_e_2=3.0, coeff_e_12=4.0)
    assert type(p + q) is MyG2
    assert type(p - q) is MyG2
    assert type(-p) is MyG2
    assert type(p * 2) is MyG2
    assert type(p.reverse()) is MyG2
    assert type(p * q) is MyG2  # full-class product is same-type


def test_full_class_mixed_operand_uses_left_type() -> None:
    sub: MyG2 = MyG2(coeff_e_1=1.0)
    base: G2 = G2(coeff_e_2=1.0)
    assert type(sub + base) is MyG2
