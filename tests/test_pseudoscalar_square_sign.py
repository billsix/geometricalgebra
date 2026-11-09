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

"""The r-dimensional unit pseudoscalar squares to (-1)^(r(r-1)/2), Euclidean.

This is the permanent, executable half of the hand proof in
``tasks/reference/pseudoscalar-square-sign.md``.  It asserts the closed form the
library uses for the reversion / pseudoscalar-square sign
(``base.pseudoscalar_squared_sign``) against an *independent* computation: it
literally builds ``I_r = e_1 * e_2 * ... * e_r`` and squares it in ``Gn``, then reads
the scalar.  Because the check re-squares the pseudoscalar rather than
re-deriving the formula, it keeps guarding the equivalence even after the Phase-2
optimization makes the helper *be* the closed form (see
``tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md``).
"""

from gacalc.base import pseudoscalar_squared_sign
from gacalc.gn import Gn

# Well past the 𝒢₃ the library ships, and well past one full period-4 cycle of
# the +,-,-,+ sign pattern, so a mis-stated exponent can't hide.
MAX_GRADE: int = 12


def closed_form_sign(r: int) -> int:
    """The proven closed form: (-1) raised to the triangular number r(r-1)/2."""
    return (-1) ** ((r * (r - 1)) // 2)


def test_pseudoscalar_square_matches_closed_form() -> None:
    """Squaring I_r in Gn agrees with (-1)^(r(r-1)/2) for every grade 0..N."""
    r: int
    for r in range(MAX_GRADE + 1):
        squared: int = int(Gn.unit_pseudoscalar_squared(r).scalar_part())
        assert squared == closed_form_sign(r), (
            f"I_{r} squared to {squared:+d}, expected {closed_form_sign(r):+d}"
        )


def test_helper_agrees_with_independent_squaring() -> None:
    """The library helper returns the same sign as the independent squaring.

    Guards the Phase-2 substitution: whatever body ``pseudoscalar_squared_sign``
    carries (the slow squaring now, the closed form after Phase 2), it must equal
    actually squaring the pseudoscalar in ``Gn``.
    """
    r: int
    for r in range(MAX_GRADE + 1):
        assert pseudoscalar_squared_sign(r) == int(
            Gn.unit_pseudoscalar_squared(r).scalar_part()
        )


def test_hand_counted_grades_one_through_five() -> None:
    """The five cases worked out by hand in the reference doc: +, -, -, +, +."""
    expected_by_grade: dict[int, int] = {1: +1, 2: -1, 3: -1, 4: +1, 5: +1}
    r: int
    expected: int
    for r, expected in expected_by_grade.items():
        assert int(Gn.unit_pseudoscalar_squared(r).scalar_part()) == expected
