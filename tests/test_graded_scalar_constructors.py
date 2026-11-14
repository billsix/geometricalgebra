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

"""The scalar classmethods on every graded type of 𝒢₁, 𝒢₂ and 𝒢₃.

``from_real`` refuses a type with no scalar slot instead of returning its zero
value, and ``unit_pseudoscalar_squared`` returns the scalar ``i²`` on every graded
type (at the type itself when it holds a scalar, else as the algebra's
``Scalar``).  The doctests on the generated methods show one type each; this file
covers every graded type of every generated algebra.
"""

import types

import pytest

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import MultiVectorBase, pseudoscalar_squared_sign

ALGEBRAS: list[tuple[types.ModuleType, int]] = [(g1, 1), (g2, 2), (g3, 3)]


def graded_types(module: types.ModuleType) -> list[type[MultiVectorBase]]:
    """Every graded type of ``module``: each ``MultiVectorBase`` class but ``G``."""
    return [
        value
        for name, value in vars(module).items()
        if isinstance(value, type)
        and issubclass(value, MultiVectorBase)
        and value.__module__ == module.__name__
        and name != "G"
    ]


CASES: list[tuple[types.ModuleType, int, type[MultiVectorBase]]] = [
    (module, n, cls) for module, n in ALGEBRAS for cls in graded_types(module)
]
IDS: list[str] = [f"g{n}.{cls.__name__}" for _, n, cls in CASES]


def holds_scalar(cls: type[MultiVectorBase]) -> bool:
    """Whether ``cls`` has a grade-0 slot: its ``one()`` is then its own type."""
    return type(cls.one()) is cls


def test_every_algebra_has_a_scalar_less_graded_type() -> None:
    """The cases below would be vacuous if no graded type lacked a scalar."""
    assert any(not holds_scalar(cls) for _, _, cls in CASES)


@pytest.mark.parametrize(("module", "n", "cls"), CASES, ids=IDS)
def test_from_real(
    module: types.ModuleType, n: int, cls: type[MultiVectorBase]
) -> None:
    """``from_real`` builds the scalar where there is a slot, else raises."""
    if holds_scalar(cls):
        assert cls.from_real(3).to_blade_dict() == {(): 3}
    else:
        with pytest.raises(ValueError, match=f"{cls.__name__} has no scalar part"):
            cls.from_real(3)


@pytest.mark.parametrize(("module", "n", "cls"), CASES, ids=IDS)
def test_zero_and_one_survive_from_real(
    module: types.ModuleType, n: int, cls: type[MultiVectorBase]
) -> None:
    """``zero()`` stays the type's own zero, and ``one()`` still multiplies as 1."""
    assert type(cls.zero()) is cls
    assert cls.zero().to_blade_dict() == {}
    e_1: MultiVectorBase = module.e_1
    assert cls.one() * e_1 == e_1


@pytest.mark.parametrize(("module", "n", "cls"), CASES, ids=IDS)
def test_unit_pseudoscalar_squared(
    module: types.ModuleType, n: int, cls: type[MultiVectorBase]
) -> None:
    """``i²`` is the scalar ``pseudoscalar_squared_sign(n)`` on every graded type."""
    expected_type: type[MultiVectorBase] = cls if holds_scalar(cls) else module.Scalar
    squared: MultiVectorBase = cls.unit_pseudoscalar_squared(n)
    assert type(squared) is expected_type
    assert squared.to_blade_dict() == {(): pseudoscalar_squared_sign(n)}
    assert (
        squared.to_blade_dict() == module.G.unit_pseudoscalar_squared().to_blade_dict()
    )
    # n defaults to the algebra's dimension (looked up through the module, since
    # the base signature has no default).
    assert getattr(module, cls.__name__).unit_pseudoscalar_squared() == squared
