// Copyright (c) 2025-2026 William Emerison Six
// SPDX-License-Identifier: LGPL-2.1-only
//
// This library is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License, version
// 2.1, as published by the Free Software Foundation.
//
// This library is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License (the LICENSE file in this repository)
// for more details.

#version 330 core

// Universal fragment shader: pass the interpolated vertex colour through.
// Used by every pipeline whose vertex shader emits the VS_OUT.color block
// (per_vertex_color.vert and uniform_color.vert).  The geometry-shader path
// uses passthrough_geom.frag instead.

out vec4 color;

in VS_OUT {
  vec4 color;
} fs_in;

void main()
{
   color = fs_in.color;
}
