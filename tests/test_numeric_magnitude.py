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

"""magnitude()/inverse() keep numeric input numeric (no sympy leak).

A ``float`` |A|² yields a Python ``float`` magnitude, so the rotor path stays
float-typed end to end and downstream numeric pipelines don't get sympy-typed
coefficients (which would become numpy ``dtype=object`` arrays). ``int`` and
symbolic inputs keep exactness. See tasks/magnitude-numeric-for-numeric-input.md.
"""

import sympy

from gacalc.g3 import Vector3
from gacalc.gn import sym_vec3_1
from gacalc.transforms import inverse, rotor_rotation


def test_magnitude_of_float_vector_is_python_float():
    v = Vector3(coeff_e_1=3.0, coeff_e_2=4.0, coeff_e_3=0.0)
    assert type(v.magnitude()) is float
    assert type(abs(v)) is float
    assert v.magnitude() == 5.0


def test_inverse_of_float_vector_stays_float():
    v = Vector3(coeff_e_1=2.0, coeff_e_2=0.0, coeff_e_3=0.0)
    inv = v.inverse()
    assert type(inv.coeff_e_1) is float


def test_rotor_rotation_of_float_vectors_stays_float_forward_and_inverse():
    # the focus path walks transforms *against the arrows* (inverse), so both
    # directions must stay numeric.
    v = Vector3(coeff_e_1=1.0, coeff_e_2=0.0, coeff_e_3=0.0)
    to = Vector3(coeff_e_1=0.0, coeff_e_2=1.0, coeff_e_3=0.0)
    f = rotor_rotation(v, to)
    for rotated in (f(v), inverse(f)(v)):
        assert type(rotated.coeff_e_1) is float
        assert type(rotated.coeff_e_2) is float
        assert type(rotated.coeff_e_3) is float


def test_symbolic_magnitude_stays_symbolic():
    # symbolic coefficients must still go through sympy.sqrt.
    assert isinstance(abs(sym_vec3_1), sympy.Expr)
