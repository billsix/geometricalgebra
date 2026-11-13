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

"""Coordinate frames joined by invertible functions, as a graph.

:mod:`gacalc.cayley.cayleygraph` holds the immutable graph and path tracing;
:mod:`gacalc.cayley.cayleyscene` turns a graph plus a declarative scene into a
timed animation.  Neither imports OpenGL.
"""
