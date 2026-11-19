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

"""``import gacalc`` (and the notebook helpers) must not pull in ePiX.

ePiX is built from source and is not on PyPI, so a plain ``pip install gacalc`` has no
``epix``; only ``gacalc.epixscene``'s submodules may import it. Each check runs in a
fresh interpreter, because this test session may already have imported it.
"""

import os
import pathlib
import subprocess
import sys

import pytest

#: this checkout's ``src/``: the subprocess must import it, not an installed gacalc
SRC: pathlib.Path = pathlib.Path(__file__).resolve().parents[1] / "src"


@pytest.mark.parametrize(
    "module",
    ["gacalc", "gacalc.g2", "gacalc.g3", "gacalc.nbdisplay", "gacalc.epixscene"],
)
def test_import_loads_no_epix(module: str) -> None:
    probe: str = (
        f"import sys, {module}\n"
        "print(sorted(m for m in sys.modules"
        " if m == 'epix' or m.startswith('epix.')))\n"
    )
    result: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(SRC)},
    )
    assert result.stdout.strip() == "[]"
