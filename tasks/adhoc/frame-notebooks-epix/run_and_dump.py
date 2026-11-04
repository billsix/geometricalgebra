#!/usr/bin/env python3
"""Execute a book notebook's percent-format source and write every figure it built.

    python tasks/adhoc/frame-notebooks-epix/run_and_dump.py NOTEBOOK.py OUT_DIR

Runs the notebook in its own directory (as the book build does) and writes each
module-level ePiX figure (``fig``, ``fig_*``) to OUT_DIR/<name>.png, so the figures
can be inspected without a Sphinx build.
"""

from __future__ import annotations

import os
import pathlib
import sys
import types

notebook: pathlib.Path = pathlib.Path(sys.argv[1]).resolve()
out: pathlib.Path = pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
os.chdir(notebook.parent)
module: types.ModuleType = types.ModuleType("notebook")
sys.modules["notebook"] = module
exec(compile(notebook.read_text(), str(notebook), "exec"), module.__dict__)  # noqa: S102
name: str
for name, value in sorted(module.__dict__.items()):
    if name == "fig" or name.startswith("fig_"):
        png: bytes | None = value.png
        (out / f"{notebook.stem}-{name}.png").write_bytes(png or b"")
        print(f"{name}: {len(png or b'')} bytes")
