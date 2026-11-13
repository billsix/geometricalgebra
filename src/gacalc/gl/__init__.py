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

"""OpenGL windows, pipelines and visualizations; needs the ``gl`` extra.

Install with ``pip install "gacalc[gl]"`` (glfw, PyOpenGL, imgui-bundle, Pillow).
``import gacalc`` never imports this package.  This ``__init__`` itself imports
no GL module, so :data:`SHADER_DIR` is readable without the extra; the
submodules need it:

* :mod:`gacalc.gl.matrix_stack` -- the model / view / projection matrix stacks;
* :mod:`gacalc.gl._pipeline` -- GLFW + ImGui setup, shader compilation, VAOs;
* :mod:`gacalc.gl.cayley_gl` -- the GL toolkit for drawing the scenes of
  :mod:`gacalc.cayley`;
* :mod:`gacalc.gl.labels` -- TeX billboard labels, a no-op where ``texExpToPng``
  is absent.

The shared shaders ship as package data in :data:`SHADER_DIR`; pass it as the
``shader_dir`` of :func:`gacalc.gl._pipeline.build_pipeline`.

>>> import os
>>> sorted(f for f in os.listdir(SHADER_DIR) if f.endswith(".vert"))
['billboard.vert', 'per_vertex_color.vert', 'uniform_color.vert']
"""

import pathlib

#: The directory holding the package's shared GLSL shaders.
SHADER_DIR: str = str(pathlib.Path(__file__).resolve().parent)
