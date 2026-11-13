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

"""Copy modelviewprojection's GLSL shaders into ``src/gacalc/gl/``.

A shader that starts with mvp's licence header (a ``// Copyright`` comment block,
up to the first blank line) has that block replaced by gacalc's LGPL-2.1-only
header written as ``//`` comments; a shader without one gets the header added
above its first line, so its own leading comments are kept.  Either way every
shader carries the same header.  GLSL allows comments before ``#version``.
Rerunning overwrites the copies from the source.

Usage (from the repo root)::

    python3 tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/copy_shaders.py MVP_ROOT
"""

import pathlib
import sys

SUFFIXES: tuple[str, ...] = (".vert", ".frag", ".geom", ".glsl")

repo: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
source_dir: pathlib.Path = (
    pathlib.Path(sys.argv[1]) / "src" / "modelviewprojection" / "mvpvisualization"
)
target_dir: pathlib.Path = repo / "src" / "gacalc" / "gl"

python_header: list[str] = []
for line in (repo / "tests" / "test_rotate_90_degrees.py").read_text().splitlines():
    if not line.startswith("#"):
        break
    python_header.append(line)
glsl_header: list[str] = ["//" + line[1:] for line in python_header]

for shader in sorted(p for p in source_dir.iterdir() if p.suffix in SUFFIXES):
    lines: list[str] = shader.read_text().splitlines()
    body_start: int = 0
    if lines and lines[0].startswith("// Copyright"):
        while body_start < len(lines) and lines[body_start].strip():
            body_start += 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
    text: str = "\n".join([*glsl_header, "", *lines[body_start:]]) + "\n"
    (target_dir / shader.name).write_text(text)
    print(f"copied {shader.name}")
