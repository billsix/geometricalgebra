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

// Fragment shader for the geometry-shader (thick-line) path: thick_lines.geom
// emits a flat `fColor` varying rather than the VS_OUT.color interface block,
// so this is identical to passthrough.frag but for the input name.

out vec4 color;

in vec4 fColor;

void main()
{
   color = fColor;
}
