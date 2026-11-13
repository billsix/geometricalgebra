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

// Shared vertex shader for geometry drawn in a single solid colour set from a
// uniform: the ground (dark gray), the coordinate-axis arrows + origin sphere
// (per-axis colour), the NDC cube (white), and the frustum outline (white).
// The caller sets `color` before drawing.
//
// project() is appended at compile time from a per-demo snippet -- see
// per_vertex_color.vert for the rationale.  Static pipelines append
// project_identity.glsl, which makes this a plain model/view/projection pass.

layout (location = 0) in vec3 position;

uniform mat4 mMatrix;
uniform mat4 vMatrix;
uniform mat4 pMatrix;
uniform vec3 color;
uniform float field_of_view;
uniform float aspect_ratio;
uniform float near_z;
uniform float far_z;
uniform float time;

out VS_OUT {
  vec4 color;
} vs_out;

vec4 project(vec4 cameraSpace);

void main()
{
  gl_Position = pMatrix * vMatrix * project(mMatrix * vec4(position, 1.0));
  vs_out.color = vec4(color, 1.0);
}
