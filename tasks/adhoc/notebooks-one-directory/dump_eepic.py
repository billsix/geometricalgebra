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

"""Write every prebuilt ePiX figure's eepic text to a directory, for comparison.

The rendered PDFs and PNGs carry metadata that changes from run to run, so they cannot
show that moving the scene helpers changed no figure. The eepic text is what ePiX
draws, and it is the same on every run of unchanged code. Run this before and after
the move, then ``diff -r`` the two directories.

Usage (in the image, from the repository root)::

    python tasks/adhoc/notebooks-one-directory/dump_eepic.py OUT_DIR
"""

import os
import subprocess
import sys
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[3]
FIGURES: Path = REPO / "book" / "figures" / "epix"

# Runs in a fresh interpreter whose working directory is the figure's directory, as in
# tools/render_epix_figures.py, so each figure sees only the imports it would there.
_CHILD: str = "import runpy, sys; print(runpy.run_path(sys.argv[1])['fig'].eepic)"


def main() -> None:
    """Dump ``<name>.eepic`` for every figure script into the directory ``sys.argv[1]``."""
    out: Path = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    figure: Path
    for figure in sorted(FIGURES.glob("[!_]*.py")):
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, "-c", _CHILD, str(figure)],
            cwd=figure.parent,
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        (out / f"{figure.stem}.eepic").write_text(result.stdout)
    print(f"{len(list(out.glob('*.eepic')))} figures written to {out}")


if __name__ == "__main__":
    main()
