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


from __future__ import annotations

import dataclasses
import itertools
import typing
from collections.abc import Mapping
from typing import NamedTuple

import sympy

from gacalc.base import (
    Blade,
    BladeCoef,
    Coef,
    MultiVectorBase,
    _require_canonical_blades,
)

# The representation-agnostic transform layer (InvertibleFunction, translate,
# scale, compose, ...) lives in gacalc.transforms; it derives any basis
# it needs from the value's own type, so it preserves Gn / G1 / G2 / G3 / ... .
# Re-exported here for backward compatibility with existing imports
# (`from gacalc.gn import translate, scale_non_uniform, ...`).
from gacalc.transforms import (  # noqa: F401
    InvertibleFunction,
    Linearity,
    compose,
    compose_intermediate_fns,
    compose_intermediate_fns_and_fn,
    identity,
    inverse,
    plane_rotation,
    projection_rotation,
    scale_non_uniform,
    to_matrix,
    translate,
    uniform_scale,
)


class BladeDictionaryEntry(NamedTuple):
    blade: Blade
    coefficient: Coef

    def as_multivector(self) -> Gn:
        return Gn(coefficient_of_blade=dict([(self.blade, self.coefficient)]))


@dataclasses.dataclass(slots=True)
class Gn(MultiVectorBase):
    """An element (multivector) of 𝒢ₙ, the geometric algebra of n-dimensional
    Euclidean space ℝⁿ (Hestenes' notation).

    𝒢ₙ has 2ⁿ basis blades.  This is the general, dimension-agnostic
    representation, storing a dict from blade (a tuple of basis-vector indices,
    e.g. ``(1, 2)`` ≙ e₁e₂) to coefficient.  G2 and G3 will be specialized,
    faster representations of 𝒢₂ and 𝒢₃.

    Terminology: 𝒢ₙ denotes the *algebra*; an instance of this class is an
    *element of* 𝒢ₙ.  The class is named after its algebra as a shorthand.

    This representation eagerly ``sympy.simplify``s every coefficient in
    ``__post_init__``.  That is the dominant cost (profiling shows ~100%), and
    it is kept here on purpose: Gn is allowed to be slow.  The specialized
    G2/G3 simplify lazily instead.

    Gn is also what the code generator *runs on sympy symbols* (not numbers) to
    derive those specialized closed forms -- so the fast paths are provably
    consistent with this reference.  See the module docstring of
    ``tools/gen_specialized.py`` for that pipeline.
    """

    coefficient_of_blade: BladeCoef

    def __post_init__(self) -> None:
        # simplify all coefficients
        self.coefficient_of_blade = {
            blade: sympy.simplify(self.coefficient_of_blade[blade])  # type: ignore
            for blade in self.coefficient_of_blade.keys()
        }
        # prune zero coefficient_of_blade
        self.coefficient_of_blade = {
            blade: self.coefficient_of_blade[blade]
            for blade in self.coefficient_of_blade.keys()
            if self.coefficient_of_blade[blade] != 0
        }

    @classmethod
    def from_blade_dict(cls, blade_coef: Mapping[Blade, Coef]) -> Gn:
        _require_canonical_blades(blade_coef)
        return cls(coefficient_of_blade=dict(blade_coef))

    def to_blade_dict(self) -> BladeCoef:
        return self.coefficient_of_blade

    def _geometric_product(self, rhs: MultiVectorBase) -> typing.Self:
        def decrease_grade(
            basis_blade: BladeDictionaryEntry,
        ) -> BladeDictionaryEntry:
            match basis_blade.blade:
                case () | (_,):
                    # a scalar or a single basis vector is already canonical
                    return basis_blade
                case (a, c, *rest) if a == c:
                    return decrease_grade(
                        BladeDictionaryEntry(
                            blade=(*rest,), coefficient=basis_blade.coefficient
                        )
                    )
                case (a, c, *rest) if a > c:
                    return decrease_grade(
                        BladeDictionaryEntry(
                            blade=(c, a, *rest),
                            coefficient=-(basis_blade.coefficient),
                        )
                    )
                case (a, c, *rest) if a < c:
                    sorted_blade_dictionary_entry: BladeDictionaryEntry = (
                        decrease_grade(
                            BladeDictionaryEntry(
                                blade=(c, *rest),
                                coefficient=basis_blade.coefficient,
                            )
                        )
                    )
                    match sorted_blade_dictionary_entry.blade:
                        case (b, *_) if a < b:
                            return BladeDictionaryEntry(
                                blade=(a, *sorted_blade_dictionary_entry.blade),
                                coefficient=sorted_blade_dictionary_entry.coefficient,
                            )
                        case _:
                            return decrease_grade(
                                BladeDictionaryEntry(
                                    blade=(a, *sorted_blade_dictionary_entry.blade),
                                    coefficient=sorted_blade_dictionary_entry.coefficient,
                                )
                            )
                case _:
                    raise ValueError("This code should never be able to be executed")

        def blade_dictionary_entry_to_multivector(
            b: BladeDictionaryEntry,
        ) -> MultiVectorBase:
            return b.as_multivector()

        product: MultiVectorBase = sum(
            [
                blade_dictionary_entry_to_multivector(
                    decrease_grade(
                        BladeDictionaryEntry(
                            blade=(
                                *blade_left,
                                *blade_right,
                            ),
                            coefficient=scalar_left * scalar_right,
                        )
                    )
                )
                for (blade_left, scalar_left), (
                    blade_right,
                    scalar_right,
                ) in itertools.product(
                    self.coefficient_of_blade.items(),
                    rhs.to_blade_dict().items(),
                )
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, product)


# Backward-compatible alias: ``MultiVector`` is the general representation Gn.
# (Gn is the canonical name; MultiVectorBase is the shared base type.)
MultiVector = Gn


e_1: MultiVector = MultiVector({(1,): 1})
e_2: MultiVector = MultiVector({(2,): 1})
e_3: MultiVector = MultiVector({(3,): 1})
e_4: MultiVector = MultiVector({(4,): 1})
e_5: MultiVector = MultiVector({(5,): 1})
e_6: MultiVector = MultiVector({(6,): 1})
e_7: MultiVector = MultiVector({(7,): 1})
e_8: MultiVector = MultiVector({(8,): 1})
e_9: MultiVector = MultiVector({(9,): 1})
e_10: MultiVector = MultiVector({(10,): 1})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_1: sympy.Symbol
a_2: sympy.Symbol
a_3: sympy.Symbol
b_1: sympy.Symbol
b_2: sympy.Symbol
b_3: sympy.Symbol
a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")

sym_vec2_1: MultiVector = a_1 * e_1 + a_2 * e_2
sym_vec2_2: MultiVector = b_1 * e_1 + b_2 * e_2

sym_vec3_1: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
sym_vec3_2: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

sym_vec_plane: MultiVector = sym_vec3_1.wedge(sym_vec3_2)
