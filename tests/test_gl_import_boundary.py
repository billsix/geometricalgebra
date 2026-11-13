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

"""``import gacalc`` (and ``gacalc.cayley``) must not pull in any GL module.

The GL dependencies are the optional ``gl`` extra, so a plain ``pip install
gacalc`` has no glfw / PyOpenGL / imgui.  Each check runs in a fresh
interpreter, because this test session may already have imported them.
"""

import os
import pathlib
import subprocess
import sys

import pytest

GL_MODULES: tuple[str, ...] = ("glfw", "OpenGL", "imgui_bundle", "PIL")
#: this checkout's ``src/``: the subprocess must import it, not an installed gacalc
SRC: pathlib.Path = pathlib.Path(__file__).resolve().parents[1] / "src"


@pytest.mark.parametrize(
    "module", ["gacalc", "gacalc.g3", "gacalc.cayley.cayleyscene", "gacalc.gl"]
)
def test_import_loads_no_gl_module(module: str) -> None:
    probe: str = (
        f"import sys, {module}\n"
        f"print(sorted(m for m in {GL_MODULES!r} if m in sys.modules))\n"
    )
    result: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )
    assert result.stdout.strip() == "[]"
