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

"""The zero-vector rule shared by every "rotate ``a`` to ``b``" factory.

From the zero vector to the zero vector is the identity; from zero to a nonzero
vector, or from a nonzero vector to zero, raises ``ValueError``
(``MultiVectorBase.require_rotation_endpoints``).
"""

import typing

import pytest

import gacalc.g3 as g3
import gacalc.gn as gn
from gacalc.base import MultiVectorBase
from gacalc.transforms import projection_rotation, versor_rotation


def rotate_by_rotor(
    from_vector: MultiVectorBase, to_vector: MultiVectorBase
) -> typing.Callable[[MultiVectorBase], MultiVectorBase]:
    """``rotor_from_vectors`` as a map, applied by the reverse sandwich."""
    R: MultiVectorBase = type(from_vector).rotor_from_vectors(from_vector, to_vector)
    return lambda v: R * v * R.reverse()


def rotate_by_versor(
    from_vector: MultiVectorBase, to_vector: MultiVectorBase
) -> typing.Callable[[MultiVectorBase], MultiVectorBase]:
    """``versor_from_vectors`` as a map, applied by the inverse sandwich."""
    R: MultiVectorBase = type(from_vector).versor_from_vectors(from_vector, to_vector)
    return lambda v: R * v * R.inverse()


FACTORIES: list[
    typing.Callable[
        [MultiVectorBase, MultiVectorBase],
        typing.Callable[[MultiVectorBase], MultiVectorBase],
    ]
] = [projection_rotation, versor_rotation, rotate_by_versor, rotate_by_rotor]
FACTORY_IDS: list[str] = [
    "projection_rotation",
    "versor_rotation",
    "versor_from_vectors",
    "rotor_from_vectors",
]
# (the zero vector, a nonzero vector) in Gn and in g3.
ALGEBRAS: list[tuple[MultiVectorBase, MultiVectorBase]] = [
    (0 * gn.e_1, 1 * gn.e_1 + 2 * gn.e_2),
    (g3.Vector.zero(), 1 * g3.e_1 + 2 * g3.e_2),
]


@pytest.mark.parametrize("factory", FACTORIES, ids=FACTORY_IDS)
@pytest.mark.parametrize(("zero", "a"), ALGEBRAS, ids=["Gn", "g3"])
def test_zero_to_zero_is_the_identity(
    factory: typing.Callable[
        [MultiVectorBase, MultiVectorBase],
        typing.Callable[[MultiVectorBase], MultiVectorBase],
    ],
    zero: MultiVectorBase,
    a: MultiVectorBase,
) -> None:
    assert factory(zero, zero)(a) == a


@pytest.mark.parametrize("factory", FACTORIES, ids=FACTORY_IDS)
@pytest.mark.parametrize(("zero", "a"), ALGEBRAS, ids=["Gn", "g3"])
@pytest.mark.parametrize("zero_first", [True, False], ids=["from-zero", "to-zero"])
def test_zero_to_a_direction_raises(
    factory: typing.Callable[
        [MultiVectorBase, MultiVectorBase],
        typing.Callable[[MultiVectorBase], MultiVectorBase],
    ],
    zero: MultiVectorBase,
    a: MultiVectorBase,
    zero_first: bool,
) -> None:
    endpoints: tuple[MultiVectorBase, MultiVectorBase] = (
        (zero, a) if zero_first else (a, zero)
    )
    with pytest.raises(ValueError, match="cannot rotate between the zero vector"):
        factory(*endpoints)
