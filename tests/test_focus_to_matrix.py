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

"""Regression for a crash in modelviewprojection's visualizations when focusing
on a node.

gacalc's ``magnitude()`` goes through ``sympy.sqrt``, so rotor-based rotations
(``rotate_z``) hand back sympy-typed coefficients even for purely numeric input.
``cayleyscene.to_matrix`` must coerce to ``float64`` -- otherwise ``np.array``
infers ``dtype=object`` and ``np.linalg.inv`` (the perspective/ortho focus path)
fails with a dtype cast error.
"""

from collections.abc import Callable

import numpy as np

from gacalc.cayley import cayleygraph, cayleyscene
from gacalc.g3 import Vector, e_1, e_2, e_3
from gacalc.transforms import InvertibleFunction, plane_rotation, translate

#: rotation in the x-y plane (about the z axis)
rotate_z: Callable[[float], InvertibleFunction[Vector]] = plane_rotation(
    Vector.e_1, Vector.e_2
)


def _focus_matrix() -> np.ndarray:
    # mirror a focus path: an edge with a translate + a rotor-based rotation,
    # walked against the arrow (world -> paddle1), then realized as a matrix.
    edge: cayleygraph.Edge[str] = cayleygraph.Edge(
        src="paddle1",
        dst="world",
        steps=[
            ("T", translate(b=0.5 * e_1 + 0.3 * e_2 + 0.0 * e_3)),
            ("R_z", rotate_z(0.7)),
        ],
    )
    graph: cayleygraph.CayleyGraph = cayleygraph.CayleyGraph([edge])
    return cayleyscene.to_matrix(graph.path("world", "paddle1").function())


def test_to_matrix_is_float64_through_a_rotation() -> None:
    assert _focus_matrix().dtype == np.float64


def test_focus_matrix_is_invertible() -> None:
    # the perspective / ortho focus path inverts this matrix (np.linalg.inv);
    # an object-dtype matrix would raise a UFuncTypeError here.
    np.linalg.inv(_focus_matrix())
