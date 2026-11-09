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

"""Shared helpers for the gacalc test suite."""

import random

from gacalc.gn import Gn, e_1, e_2, e_3


def random_vector(dim: int) -> Gn:
    """A random ``dim``-D vector with float coefficients in ``[-5, 5)``.

    For the float-tolerant numeric conformance checks; ``random`` is fine here --
    these are test vectors, not cryptographic material.  Seed ``random`` in the
    caller for reproducibility.
    """
    basis: list[Gn] = [1 * e_1, 1 * e_2, 1 * e_3][:dim]
    return sum(
        (random.uniform(-5.0, 5.0) * basis_vector for basis_vector in basis),  # noqa: S311
        start=Gn.zero(),
    )
