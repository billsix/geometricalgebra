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

"""Named measures -- ``area`` / ``volume`` / ``content`` (``gacalc.measure``).

Content is the unsigned k-dimensional measure of the parallelotope a set of vectors
spans (Williamson & Trotter, *Multivariable Mathematics*, 2nd ed. 1979: content p. 308,
recursive-height volume p. 146).

The symbolic tests are written **explicitly**, so each reads like the math it verifies:
``signed_area`` is the 2x2 determinant, ``signed_volume`` the 3x3, ``area``/``volume``
their magnitudes, ``content`` (both ``|wedge|`` and ``∏ |rejected heights|``) the
``|determinant|``, and the area of two vectors in 3-space is the Gram determinant
``|a|²|b|² − (a·b)²``. The general-symbolic 3D ``content_by_rejection`` is checked
numerically instead (its Gram–Schmidt form is too large for sympy to reduce).
"""

import math
import random

import pytest
import sympy

import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.gn import (
    Gn,
    e_1,
    e_2,
    e_3,
)
from gacalc.measure import (
    area,
    content,
    content_by_rejection,
    signed_area,
    signed_content,
    signed_volume,
    volume,
)


def _random_vector(dim: int) -> Gn:
    # random is fine here: these are test vectors, not cryptographic material.
    basis: list[Gn] = [e_1, e_2, e_3][:dim]
    v: Gn = Gn.zero()
    basis_vector: Gn
    for basis_vector in basis:
        v = v + random.uniform(-5.0, 5.0) * basis_vector  # noqa: S311
    return v


# --- basic values ----------------------------------------------------------


def test_unit_measures() -> None:
    assert content([e_1]) == 1  # length
    assert area(e_1, e_2) == 1  # unit square
    assert volume(e_1, e_2, e_3) == 1  # unit cube


def test_area_is_wedge_magnitude_oblique() -> None:
    # (e_1 + e_2) ∧ e_2 = e_1 ∧ e_2, so the parallelogram area is 1.
    assert area(e_1 + e_2, e_2) == 1
    # |a||b| sin θ: a = e_1, b = e_1 + e_2 -> 1 · √2 · sin45° = 1.
    assert area(e_1, e_1 + e_2) == 1


def test_area_volume_are_content_aliases() -> None:
    a, b, c = e_1 + e_2, e_2 + e_3, e_1 + e_3
    assert area(a, b) == content([a, b])
    assert volume(a, b, c) == content([a, b, c])


def test_content_of_dependent_set_is_zero() -> None:
    assert content([e_1, 2 * e_1]) == 0  # parallel -> zero area
    assert content([e_1, e_2, e_1 + e_2]) == 0  # coplanar -> zero volume


def test_non_vector_and_empty_raise() -> None:
    with pytest.raises(ValueError):
        content([e_1, e_1 ^ e_2])  # a bivector is not a vector
    with pytest.raises(ValueError):
        content([])


# --- explicit symbolic tests: the measures ARE the familiar determinants -----
#
# General symbolic vectors, written out so each test reads like the math you
# already know -- Bill's ``a1*e_1 + a2*e_2`` style.  These use ``g2``/``g3`` (not
# the dimensionless ``Gn``) so the ``signed_*`` measures, which need a fixed
# dimension, work.

_a1, _a2, _a3, _b1, _b2, _b3, _c1, _c2, _c3 = sympy.symbols(
    "a1 a2 a3 b1 b2 b3 c1 c2 c3"
)
_A2: g2.Vector = _a1 * g2.e_1 + _a2 * g2.e_2
_B2: g2.Vector = _b1 * g2.e_1 + _b2 * g2.e_2
_A3: g3.Vector = _a1 * g3.e_1 + _a2 * g3.e_2 + _a3 * g3.e_3
_B3: g3.Vector = _b1 * g3.e_1 + _b2 * g3.e_2 + _b3 * g3.e_3
_C3: g3.Vector = _c1 * g3.e_1 + _c2 * g3.e_2 + _c3 * g3.e_3

# The 2x2 and 3x3 determinants, written out once.
_DET2 = _a1 * _b2 - _a2 * _b1
_DET3 = (
    _c1 * (_a2 * _b3 - _a3 * _b2)
    - _c2 * (_a1 * _b3 - _a3 * _b1)
    + _c3 * (_a1 * _b2 - _a2 * _b1)
)


def test_signed_area_symbolic_is_the_2x2_determinant() -> None:
    assert signed_area(_A2, _B2) == _DET2  # signed area = the 2x2 determinant
    assert signed_area(_B2, _A2) == -_DET2  # switching the two negates it
    assert area(_A2, _B2) == sympy.sqrt(_DET2**2)  # unsigned area = |det|


def test_signed_volume_symbolic_is_the_3x3_determinant() -> None:
    assert signed_volume(_A3, _B3, _C3) == _DET3  # signed volume = the 3x3 det
    assert volume(_A3, _B3, _C3) == sympy.sqrt(_DET3**2)  # unsigned volume = |det|


def test_content_two_ways_both_give_the_determinant_symbolic() -> None:
    """Content via the **wedge** (``content``) and via the **rejected heights**
    (``content_by_rejection``) both equal the magnitude of the determinant. Shown
    **squared**, where the determinant is a clean polynomial -- the raw magnitudes
    carry unsimplified square roots (and ``content_by_rejection`` carries the
    rejection denominators), so we ask sympy to reduce ``value² − det²`` to ``0``
    rather than comparing with ``==``.

    Done in **2D**: a general symbolic 3-vector 3D frame makes
    ``content_by_rejection`` a Gram–Schmidt of three symbolic vectors, whose
    squared product is too large for sympy to reduce in reasonable time -- the 3D
    case is covered numerically by
    :func:`test_content_equals_content_by_rejection_numeric` instead."""
    frame: list[g2.Vector] = [_A2, _B2]
    assert sympy.simplify(content(frame) ** 2 - _DET2**2) == 0
    assert sympy.simplify(content_by_rejection(frame) ** 2 - _DET2**2) == 0


def test_area_of_two_vectors_in_3d_is_the_gram_determinant() -> None:
    """Two vectors in 3-space (k = 2 < n = 3) have **no single determinant** -- but
    the area SQUARED is the sum of the three 2x2 minors squared, equivalently the
    **Gram determinant** ``|a|²|b|² − (a·b)²``.  (The ``k < n`` generalization of
    ``signed_area``'s 2x2 determinant; and ``area(_A3, _B3)`` literally returns the
    sqrt of those three minors.)"""
    minors_squared = (
        (_a1 * _b2 - _a2 * _b1) ** 2
        + (_a1 * _b3 - _a3 * _b1) ** 2
        + (_a2 * _b3 - _a3 * _b2) ** 2
    )
    gram_determinant = (_a1**2 + _a2**2 + _a3**2) * (_b1**2 + _b2**2 + _b3**2) - (
        _a1 * _b1 + _a2 * _b2 + _a3 * _b3
    ) ** 2
    assert sympy.expand(area(_A3, _B3) ** 2) == sympy.expand(minors_squared)
    assert sympy.expand(area(_A3, _B3) ** 2) == sympy.expand(gram_determinant)


def test_content_equals_content_by_rejection_numeric() -> None:
    random.seed(20260823)
    for dim in (2, 3):
        for _ in range(100):
            vectors: list[Gn] = [_random_vector(dim) for _ in range(dim)]
            assert math.isclose(
                float(content(vectors)),
                float(content_by_rejection(vectors)),
                rel_tol=1e-9,
                abs_tol=1e-9,
            )


def test_content_by_rejection_requires_a_frame() -> None:
    # dependent set: content is 0, but the height construction has no parallelotope.
    assert content([e_1, 2 * e_1]) == 0
    with pytest.raises(ValueError):
        content_by_rejection([e_1, 2 * e_1])


# --- signed (oriented) content, k = n --------------------------------------


def test_signed_area_is_the_2d_determinant() -> None:
    # (2 e_1 + e_2) and (e_1 + 3 e_2): det = 2·3 − 1·1 = 5.
    p = 2 * g2.e_1 + g2.e_2
    q = g2.e_1 + 3 * g2.e_2
    assert signed_area(p, q) == 5
    assert signed_area(q, p) == -5  # swap flips orientation
    assert abs(signed_area(p, q)) == content([p, q])  # |signed| == unsigned


def test_signed_volume_is_the_3d_determinant() -> None:
    x = g3.e_1
    y = g3.e_2
    z = g3.e_3
    assert signed_volume(x, y, z) == 1  # right-handed
    assert signed_volume(z, y, x) == -1  # swap flips
    assert abs(signed_volume(x, y, z)) == content([x, y, z])


def test_signed_content_dependent_full_set_is_zero() -> None:
    p = 2 * g2.e_1 + g2.e_2
    assert signed_area(p, 4 * g2.e_1 + 2 * g2.e_2) == 0  # parallel


def test_signed_content_needs_full_space_and_fixed_dimension() -> None:
    # k < n: two vectors in 3-space have no scalar sign (orientation is a bivector).
    x = g3.e_1
    y = g3.e_2
    with pytest.raises(ValueError):
        signed_content([x, y])
    # Gn has no fixed DIMENSION, so "full space" -- and the sign -- is undefined.
    with pytest.raises(ValueError):
        signed_content([e_1, e_2])


# --- pass-through methods on the base (discoverability sugar) ----------------


def test_measure_methods_delegate_to_free_functions() -> None:
    """``v.area(w)`` etc. are inherited on every vector type and match the free
    functions they delegate to."""
    a = 2 * g2.e_1 + g2.e_2
    b = g2.e_1 + 3 * g2.e_2
    assert a.area(b) == area(a, b)
    assert a.signed_area(b) == signed_area(a, b)
    x = g3.e_1
    y = g3.e_2
    z = g3.e_3
    assert x.volume(y, z) == volume(x, y, z)
    assert x.signed_volume(y, z) == signed_volume(x, y, z)
