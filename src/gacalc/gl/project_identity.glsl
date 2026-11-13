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

// project_identity.glsl -- appended to a shared .vert for STATIC pipelines.
// No projection animation: model / view / projection are applied directly by
// the .vert's main(), so project() is the identity on camera space.
vec4 project(vec4 cameraSpace)
{
    return cameraSpace;
}
