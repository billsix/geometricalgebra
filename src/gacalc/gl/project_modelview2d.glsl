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

// project_modelview2d.glsl -- 2D orthographic squash (modelview2d demo).
// At time >= 65 the world's x/y scale interpolates to the 1/10 NDC scale.
vec4 project(vec4 cameraSpace){

    float scaleRatio = min((time - 65.0)/5.0, 1.0);
    float xVal = 1.0 + (1.0/10.0 - 1.0) * scaleRatio;
    float yVal = 1.0 + (1.0/10.0 - 1.0) * scaleRatio;
    mat4 scale_to_ndc = transpose(mat4(
         xVal,     0.0,     0.0,    0.0,
         0.0,      yVal,    0.0,    0.0,
         0.0,      0.0,     1.0,   0.0,
         0.0,      0.0,     0.0,    1.0));

    if (time < 65){
      scale_to_ndc =  mat4(1.0);
    }

     return scale_to_ndc * cameraSpace;
}
