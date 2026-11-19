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

"""The ePiX scene helpers the book's figures and notebooks draw with; needs ePiX.

ePiX (github.com/billsix/epix-mirror) is built from source and is not on PyPI, so these
modules import only where it is installed, as in the project's container image.
``import gacalc`` never imports this package, and this ``__init__`` imports nothing.

- :mod:`gacalc.epixscene.scene2d`: the 2D stage, colours and drawing primitives;
- :mod:`gacalc.epixscene.scene3d`: the 3D stage of the projection-in-space figures;
- :mod:`gacalc.epixscene.frame_scene`: live 2D and 3D scenes for the frame / QR
  notebooks;
- :mod:`gacalc.epixscene.bootstrap_live`: live scenes sized to fit their points;
- :mod:`gacalc.epixscene.line_scene`: graph paper and number lines;
- :mod:`gacalc.epixscene.paper_scene`: graph paper carried by a function of the plane;
- :mod:`gacalc.epixscene.venn_scene`: the 𝒢₂ subsets diagram.

Each module keeps its own CC0 dedication, stated in its docstring.
"""
