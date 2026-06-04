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

"""Backward-compatible umbrella for the geometric algebra package.

The implementations now live in focused, one-class-at-a-time modules:

    base.py   AbstractMultiVector (the abstract base) + type aliases
    gn.py     Gn (general 𝒢ₙ) + basis constants + transforms + MultiVector alias
    g1.py     G1   (𝒢₁)
    g2.py     G2   (𝒢₂)
    g3.py     G3   (𝒢₃)

New code should import the one it needs directly, e.g.::

    from geometricalgebra.g2 import G2

This module simply re-exports the names that used to live here, so existing
``from geometricalgebra.multivector import ...`` imports keep working.
"""

from geometricalgebra.base import (
    AbstractMultiVector,
    BladeCoef,
    MultiVectorFn,
)
from geometricalgebra.gn import (
    BladeDictionaryEntry,
    Gn,
    InvertibleFunction,
    MultiVector,
    a_1,
    a_2,
    a_3,
    b_1,
    b_2,
    b_3,
    compose,
    compose_intermediate_fns,
    compose_intermediate_fns_and_fn,
    e_1,
    e_2,
    e_3,
    e_4,
    e_5,
    e_6,
    e_7,
    e_8,
    e_9,
    e_10,
    identity,
    inverse,
    is_clockwise,
    is_counter_clockwise,
    one,
    rotate,
    rotate_90_degrees,
    rotate_around,
    scale_non_uniform_2d,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
    sym_vec_plane,
    translate,
    uniform_scale,
    zero,
)

__all__ = [
    "AbstractMultiVector",
    "BladeCoef",
    "BladeDictionaryEntry",
    "Gn",
    "InvertibleFunction",
    "MultiVector",
    "MultiVectorFn",
    "a_1",
    "a_2",
    "a_3",
    "b_1",
    "b_2",
    "b_3",
    "compose",
    "compose_intermediate_fns",
    "compose_intermediate_fns_and_fn",
    "e_1",
    "e_2",
    "e_3",
    "e_4",
    "e_5",
    "e_6",
    "e_7",
    "e_8",
    "e_9",
    "e_10",
    "identity",
    "inverse",
    "is_clockwise",
    "is_counter_clockwise",
    "one",
    "rotate",
    "rotate_90_degrees",
    "rotate_around",
    "scale_non_uniform_2d",
    "sym_vec2_1",
    "sym_vec2_2",
    "sym_vec3_1",
    "sym_vec3_2",
    "sym_vec_plane",
    "translate",
    "uniform_scale",
    "zero",
]
