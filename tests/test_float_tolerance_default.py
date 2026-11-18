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


"""The float tolerance is decided from the coefficients when a caller passes none.

``float_close_to_zero`` defaults to ``None`` on the comparisons and the line maps:
float input is compared with a tolerance, exact and symbolic input exactly, and an
explicit ``True``/``False`` still decides (``base.resolve_float_tolerance``;
``tasks/reference/numeric-symbolic-mode.md``).
"""

import pytest

from gacalc.base import MultiVectorBase
from gacalc.functions import InvertibleFunction
from gacalc.g2 import Vector, e_1, e_2
from gacalc.transforms import coordinate_along, line_to_line_projection

#: Off the e_1 line by a rounding-sized amount.
NEAR_E1: Vector = 2.0 * e_1 + 1e-12 * e_2


def test_float_input_is_tolerant_by_default() -> None:
    assert NEAR_E1.is_parallel_to(1.0 * e_1)
    assert (1.0 * e_2 + 1e-12 * e_1).is_orthogonal_to(1.0 * e_1)
    assert coordinate_along(NEAR_E1, along=1.0 * e_1) == 2.0


def test_explicit_false_is_exact_for_floats() -> None:
    assert not NEAR_E1.is_parallel_to(1.0 * e_1, float_close_to_zero=False)
    with pytest.raises(ValueError, match="not on the line"):
        coordinate_along(NEAR_E1, along=1.0 * e_1, float_close_to_zero=False)


def test_exact_input_stays_exact() -> None:
    assert (2 * e_1).is_parallel_to(1 * e_1)
    assert not (2 * e_1 + 1 * e_2).is_parallel_to(1 * e_1)


def test_explicit_true_is_tolerant_for_exact_input() -> None:
    """``True`` forces the tolerance even when nothing is a float."""
    assert (1 * e_1).is_orthogonal_to(1 * e_2, float_close_to_zero=True)


def test_factory_decides_at_call_time() -> None:
    """A map built from exact vectors is tolerant when called on float input."""
    projection: InvertibleFunction[MultiVectorBase] = line_to_line_projection(
        from_vector=1 * e_1 + 1 * e_2, to_vector=1 * e_1
    )
    image: MultiVectorBase = projection(2.0 * e_1 + (2.0 + 1e-12) * e_2)
    assert image.isclose(2.0 * e_1, abs_tol=1e-9)
