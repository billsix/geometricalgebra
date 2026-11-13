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

// The texExpToPng PNG is a glyph MASK: dvipng in this image renders the formula
// black-on-transparent regardless of `--fg`, but the alpha channel carries the
// glyph coverage.  So paint the glyphs a fixed colour here, using that alpha as
// the mask, rather than reading the texture's (black) RGB.  Straight (non-
// premultiplied) alpha; the caller enables SRC_ALPHA / ONE_MINUS_SRC_ALPHA.
in vec2 v_uv;

uniform sampler2D tex;

out vec4 fragColor;

void main()
{
    float coverage = texture(tex, v_uv).a;
    fragColor = vec4(1.0, 1.0, 1.0, coverage);
}
