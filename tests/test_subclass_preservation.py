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

**Every generated value type is `@typing.final`** (not subclassable): the graded
value types (``Vector1/2/3``, ``Bivector2/3``, ``Trivector3``, ``Rotor2/3``), the
per-algebra ``ScalarN``, **and the full classes ``G1``/``G2``/``G3``**.  Nothing
subclasses ``G_n`` (the graded types are the value types; the general
dimension-agnostic representation is ``Gn`` in ``gn.py``, a separate class), so the
former "extension point" was unused -- making ``G_n`` final too lets the generated
code construct the concrete class directly everywhere instead of through
``type(self)``.  This is a static guarantee: ``ty`` rejects any subclass with
``error[subclass-of-final-class]`` -- e.g. ``class X(G2): ...`` is a type error (the
finality is emitted by ``tools/gen_specialized.py``).
"""

from gacalc.g1 import G1, Scalar1, Vector1
from gacalc.g2 import G2, Bivector2, Rotor2, Scalar2, Vector2
from gacalc.g3 import G3, Bivector3, Rotor3, Scalar3, Trivector3, Vector3

_FINAL_TYPES: list[type] = [
    Scalar1,
    Scalar2,
    Scalar3,
    Vector1,
    Vector2,
    Bivector2,
    Rotor2,
    Vector3,
    Bivector3,
    Trivector3,
    Rotor3,
    G1,
    G2,
    G3,
]


def test_all_generated_types_are_final() -> None:
    # ``@typing.final`` sets ``__final__ = True`` (Python 3.11+); ty additionally
    # rejects any subclass at check time.  A downstream consumer uses these types
    # directly (not by subclassing) -- see modelviewprojection.
    for value_type in _FINAL_TYPES:
        assert getattr(value_type, "__final__", False), (
            f"{value_type.__name__} should be @typing.final"
        )


def test_full_class_products_construct_concretely() -> None:
    # G_n arithmetic returns exactly G_n (no type(self) indirection to preserve a
    # subclass, since there are none).
    p: G2 = G2(coeff_scalar=1.0, coeff_e_1=2.0)
    q: G2 = G2(coeff_e_2=3.0, coeff_e_12=4.0)
    assert type(p + q) is G2
    assert type(p - q) is G2
    assert type(-p) is G2
    assert type(p * 2) is G2
    assert type(p.reverse()) is G2
    assert type(p * q) is G2  # full-class product is same-type
