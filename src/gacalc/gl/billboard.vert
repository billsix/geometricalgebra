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

// Camera-facing billboard for the TeX label textures.
//
// Each quad corner shares one world-space `center`; `offset` is the corner's
// displacement in NDC (already aspect-/pixel-scaled by the CPU).  Projecting the
// center to clip space and then adding `offset * clip.w` makes the offset
// survive the perspective divide as a CONSTANT NDC (screen) size -- so the label
// keeps the same on-screen size at any depth, and it works for the ortho 2D view
// too (there clip.w == 1).
layout (location = 0) in vec3 center;
layout (location = 1) in vec2 offset;
layout (location = 2) in vec2 uv;

uniform mat4 vMatrix;
uniform mat4 pMatrix;

out vec2 v_uv;

void main()
{
    vec4 clip = pMatrix * vMatrix * vec4(center, 1.0);
    clip.xy += offset * clip.w;
    gl_Position = clip;
    v_uv = uv;
}
