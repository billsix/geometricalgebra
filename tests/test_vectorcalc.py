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

"""The cross product (``gacalc.vectorcalc.cross``) -- ``a × b = (a ∧ b) I₃⁻¹``.

Pins the right-hand-rule **sign convention** (the task's "verify the sign" step:
the existing ``dual`` is ``A I⁻¹`` and ``I₃⁻¹ = −I₃``, which should give the
standard orientation -- these tests are the proof), checks the coordinate
formula symbolically and against ``numpy.cross`` numerically, gates the
**scalar-triple-product identity** ``a · (b × c) = signed_volume(a, b, c)``,
and exercises the 3-D guard.  See ``tasks/custom-symbols-and-vector-calc.md``.
"""

import numpy as np
import pytest
import sympy

import gacalc.g2 as g2
import gacalc.gn as gn
from gacalc.g3 import Vector, e_1, e_2, e_3
from gacalc.measure import signed_volume
from gacalc.vectorcalc import cross


def test_right_handed_basis() -> None:
    """The defining cyclic identities: e1 × e2 = e3, e2 × e3 = e1, e3 × e1 = e2."""
    assert cross(1 * e_1, 1 * e_2) == 1 * e_3
    assert cross(1 * e_2, 1 * e_3) == 1 * e_1
    assert cross(1 * e_3, 1 * e_1) == 1 * e_2


def test_anticommutative() -> None:
    a: Vector = 2 * e_1 + 3 * e_2 + 5 * e_3
    b: Vector = 7 * e_1 + 1 * e_2 + 4 * e_3
    assert cross(a, b) == -cross(b, a)


def test_result_is_a_graded_vector() -> None:
    """In g3 the wedge is a Bivector and its dual a Vector -- the graded types
    carry the cross product's grade-1 result precisely."""
    assert isinstance(cross(1 * e_1, 1 * e_2), Vector)


def test_matches_numpy_cross() -> None:
    a: Vector = 1.5 * e_1 + (-2.0) * e_2 + 0.5 * e_3
    b: Vector = 0.25 * e_1 + 4.0 * e_2 + (-1.0) * e_3
    # iteration yields the coefficient values in blade order = the coordinates
    assert np.allclose(
        np.array(list(cross(a, b)), dtype=float),
        np.cross(np.array(list(a), dtype=float), np.array(list(b), dtype=float)),
    )


def test_symbolic_coordinate_formula() -> None:
    a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
    a: Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: Vector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    assert cross(a, b) == (
        (a_2 * b_3 - a_3 * b_2) * e_1
        + (a_3 * b_1 - a_1 * b_3) * e_2
        + (a_1 * b_2 - a_2 * b_1) * e_3
    )


def test_scalar_triple_product_is_signed_volume() -> None:
    """a · (b × c) == signed_volume(a, b, c) -- why measure.signed_volume needs
    no vector-calc alias (see gacalc/vectorcalc.py's module docstring)."""
    a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
    c_1, c_2, c_3 = sympy.symbols("c_1 c_2 c_3")
    a: Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: Vector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    c: Vector = c_1 * e_1 + c_2 * e_2 + c_3 * e_3
    # sympify first: a Coef difference is int | float | Expr, and simplify's
    # overloads take only sympy types (here the values are symbolic anyway).
    assert (
        sympy.simplify(
            sympy.sympify(a.scalar_product(cross(b, c)) - signed_volume(a, b, c))
        )
        == 0
    )


def test_parallel_vectors_cross_to_zero() -> None:
    assert cross(2 * e_1, 3 * e_1) == Vector.zero()


def test_works_on_gn() -> None:
    assert cross(1 * gn.e_1, 1 * gn.e_2) == 1 * gn.e_3


def test_method_form_matches_free_function() -> None:
    a: Vector = 2 * e_1 + 3 * e_2 + 5 * e_3
    b: Vector = 7 * e_1 + 1 * e_2 + 4 * e_3
    assert a.cross(b) == cross(a, b)


def test_generated_closed_form_matches_definition() -> None:
    """g3.Vector.cross's Vector arm is a generator-baked closed form (no runtime
    wedge/dual).  With SYMBOLIC coefficients one equality is an algebraic
    identity over all inputs, so this proves the closed form against (a) the
    free function's wedge+dual path on g3 and (b) the same computation in the
    slow reference algebra ``Gn`` -- an independent oracle sharing no generated
    code.  The ``isinstance`` pins the RUNTIME result type (a ``Vector``, not a
    widened ``G``/``Gn``); the ``generated: Vector`` annotation is verified
    statically by the ``ty`` gate over tests, checking the ``Vector -> Vector``
    overload resolution."""
    a_1, a_2, a_3 = sympy.symbols("a_1 a_2 a_3")
    b_1, b_2, b_3 = sympy.symbols("b_1 b_2 b_3")
    a: Vector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
    b: Vector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3
    generated: Vector = a.cross(b)
    assert isinstance(generated, Vector)
    assert generated == cross(a, b)
    gn_a: gn.Gn = a_1 * gn.e_1 + a_2 * gn.e_2 + a_3 * gn.e_3
    gn_b: gn.Gn = b_1 * gn.e_1 + b_2 * gn.e_2 + b_3 * gn.e_3
    assert generated == cross(gn_a, gn_b)
    # the defining cyclic identities, through the closed form itself
    assert (1 * e_1).cross(1 * e_2) == 1 * e_3
    assert (1 * e_2).cross(1 * e_3) == 1 * e_1
    assert (1 * e_3).cross(1 * e_1) == 1 * e_2


def test_generated_cross_falls_back_for_foreign_operands() -> None:
    """The generated override's non-Vector arm delegates to the base
    pass-through: a Gn operand coerces (and still crosses correctly), a
    non-vector still raises vectorcalc's guard error."""
    assert (1 * e_1).cross(1 * gn.e_2) == 1 * gn.e_3
    with pytest.raises(ValueError, match="grade 1"):
        (1 * e_1).cross((1 * e_1).wedge(1 * e_2))


def test_non_vector_operand_raises() -> None:
    with pytest.raises(ValueError, match="grade 1"):
        cross(1 * e_1, (1 * e_1).wedge(1 * e_2))


def test_two_dimensional_representation_raises() -> None:
    with pytest.raises(ValueError, match="3-dimensional"):
        cross(1 * g2.e_1, 1 * g2.e_2)


def test_gn_basis_index_above_three_raises() -> None:
    with pytest.raises(ValueError, match="3-dimensional"):
        cross(1 * gn.e_1, 1 * gn.e_4)
