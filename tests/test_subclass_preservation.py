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
value types (``Vector`` / ``Bivector`` / ``Trivector`` / ``Rotor`` per module), the
per-algebra ``Scalar``, **and the full class ``G``**.  Nothing
subclasses ``G_n`` (the graded types are the value types; the general
dimension-agnostic representation is ``Gn`` in ``gn.py``, a separate class), so the
former "extension point" was unused -- making ``G_n`` final too lets the generated
code construct the concrete class directly everywhere instead of through
``type(self)``.  This is a static guarantee: ``ty`` rejects any subclass with
``error[subclass-of-final-class]`` -- e.g. ``class X(g2.G): ...`` is a type error (the
finality is emitted by ``tools/gen_specialized.py``).
"""

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3

_FINAL_TYPES: list[type] = [
    g1.Scalar,
    g2.Scalar,
    g3.Scalar,
    g1.Vector,
    g2.Vector,
    g2.Bivector,
    g2.Rotor,
    g3.Vector,
    g3.Bivector,
    g3.Trivector,
    g3.Rotor,
    g1.G,
    g2.G,
    g3.G,
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
    p: g2.G = g2.G(coeff_scalar=1.0, coeff_e_1=2.0)
    q: g2.G = g2.G(coeff_e_2=3.0, coeff_e_12=4.0)
    assert type(p + q) is g2.G
    assert type(p - q) is g2.G
    assert type(-p) is g2.G
    assert type(p * 2) is g2.G
    assert type(p.reverse()) is g2.G
    assert type(p * q) is g2.G  # full-class product is same-type
