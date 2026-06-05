# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import dataclasses
import itertools
import numbers
import typing
from typing import NamedTuple

import sympy

from geometricalgebra.base import AbstractMultiVector, BladeCoef

# The representation-agnostic transform layer (InvertibleFunction, translate,
# rotate, scale, compose, ...) lives in geometricalgebra.transforms; it derives
# any basis it needs from the value's own type, so it preserves Gn / G1 / G2 /
# G3 / ... .  Re-exported here for backward compatibility with existing imports
# (`from geometricalgebra.gn import translate, rotate, ...`).
from geometricalgebra.transforms import (  # noqa: F401
    InvertibleFunction,
    compose,
    compose_intermediate_fns,
    compose_intermediate_fns_and_fn,
    identity,
    inverse,
    is_clockwise,
    is_counter_clockwise,
    rotate,
    rotate_90_degrees,
    rotate_around,
    scale_non_uniform,
    scale_non_uniform_2d,
    translate,
    uniform_scale,
)


class BladeDictionaryEntry(NamedTuple):
    blade: tuple[int, ...]
    coefficient: numbers.Real

    def as_multivector(self):
        return Gn(coefficient_of_blade=dict([(self.blade, self.coefficient)]))


@dataclasses.dataclass(slots=True)
class Gn(AbstractMultiVector):
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
    """

    coefficient_of_blade: BladeCoef

    def __post_init__(self):
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
    def from_blade_dict(cls, blade_coef) -> "Gn":
        return cls(coefficient_of_blade=dict(blade_coef))

    def to_blade_dict(self) -> BladeCoef:
        return self.coefficient_of_blade

    def _geometric_product(self, rhs: "AbstractMultiVector") -> typing.Self:
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
                            coefficient=typing.cast(
                                numbers.Real, -(basis_blade.coefficient)
                            ),
                        )
                    )
                case (a, c, *rest) if a < c:
                    sorted_blade_dictionary_entry = decrease_grade(
                        BladeDictionaryEntry(
                            blade=(c, *rest),
                            coefficient=basis_blade.coefficient,
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
        ) -> AbstractMultiVector:
            return b.as_multivector()

        product: "AbstractMultiVector" = sum(
            [
                blade_dictionary_entry_to_multivector(
                    decrease_grade(
                        BladeDictionaryEntry(
                            blade=(
                                *blade_left,
                                *blade_right,
                            ),
                            coefficient=typing.cast(
                                numbers.Real,
                                scalar_left * scalar_right,
                            ),
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
# (Gn is the canonical name; AbstractMultiVector is the shared base type.)
MultiVector = Gn


e_1: MultiVector = MultiVector({(1,): typing.cast(numbers.Real, 1)})
e_2: MultiVector = MultiVector({(2,): typing.cast(numbers.Real, 1)})
e_3: MultiVector = MultiVector({(3,): typing.cast(numbers.Real, 1)})
e_4: MultiVector = MultiVector({(4,): typing.cast(numbers.Real, 1)})
e_5: MultiVector = MultiVector({(5,): typing.cast(numbers.Real, 1)})
e_6: MultiVector = MultiVector({(6,): typing.cast(numbers.Real, 1)})
e_7: MultiVector = MultiVector({(7,): typing.cast(numbers.Real, 1)})
e_8: MultiVector = MultiVector({(8,): typing.cast(numbers.Real, 1)})
e_9: MultiVector = MultiVector({(9,): typing.cast(numbers.Real, 1)})
e_10: MultiVector = MultiVector({(10,): typing.cast(numbers.Real, 1)})
zero: MultiVector = MultiVector.from_scalar(0)
one: MultiVector = MultiVector.from_scalar(1)

a_1, a_2, a_3, b_1, b_2, b_3 = sympy.symbols("a_1 a_2 a_3 b_1 b_2 b_3")

sym_vec2_1: MultiVector = a_1 * e_1 + a_2 * e_2
sym_vec2_2: MultiVector = b_1 * e_1 + b_2 * e_2

sym_vec3_1: MultiVector = a_1 * e_1 + a_2 * e_2 + a_3 * e_3
sym_vec3_2: MultiVector = b_1 * e_1 + b_2 * e_2 + b_3 * e_3

sym_vec_plane: MultiVector = sym_vec3_1.wedge(sym_vec3_2)
