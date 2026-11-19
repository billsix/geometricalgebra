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

"""Compare the outputs of two directories of executed notebooks.

Each notebook in BEFORE is matched by file name with one in AFTER. The comparison is of
the code cells' outputs only, in order, by MIME type (text, LaTeX, Markdown and images),
so that cells whose source changed (a removed ``sys.path`` line, a new import) do not
count as a difference. A code cell with no outputs is skipped on both sides, since
removing an import-only cell shifts nothing a reader sees. Two things that change from
run to run of the same code are normalised: a memory address in a repr (``at 0x…``)
and a PNG's metadata (images are compared by their decoded pixels).

Usage::

    python tasks/adhoc/notebooks-one-directory/compare_outputs.py BEFORE AFTER [SKIP ...]

SKIP names MIME types to leave out (e.g. ``image/png`` if the PNG encoder is not
deterministic). Exits 1 if any notebook differs or is missing.
"""

import base64
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image

ADDRESS: re.Pattern[str] = re.compile(r"0x[0-9a-f]+")


def normalised(mime: str, data: str) -> str:
    """Return ``data`` with the run-to-run noise of its MIME type removed.

    Args:
        mime: the output's MIME type.
        data: the output's data, joined into one string.

    Returns:
        str: the pixels of a PNG (as hex), or the text with addresses blanked.
    """
    match mime:
        case "image/png":
            image: Image.Image = Image.open(io.BytesIO(base64.b64decode(data)))
            return f"{image.mode} {image.size} {image.tobytes().hex()}"
        case _:
            return ADDRESS.sub("0x", data)


def outputs(notebook: Path, skip: frozenset[str]) -> list[list[tuple[str, str]]]:
    """Return, per code cell that has outputs, its ``(mime, data)`` pairs in order.

    Args:
        notebook: the executed ``.ipynb``.
        skip: MIME types to leave out.

    Returns:
        list[list[tuple[str, str]]]: one list of pairs per code cell with outputs.
    """
    cells: list[dict[str, object]] = json.loads(notebook.read_text())["cells"]
    cell_outputs: list[list[tuple[str, str]]] = [
        [
            (mime, normalised(mime, "".join(data) if isinstance(data, list) else str(data)))
            for output in cell.get("outputs", [])  # type: ignore[union-attr]
            for mime, data in (
                output.get("data", {"text/plain": output.get("text", "")})
            ).items()
            if mime not in skip
        ]
        for cell in cells
        if cell["cell_type"] == "code"
    ]
    return [pairs for pairs in cell_outputs if pairs]


def main() -> None:
    """Compare BEFORE against AFTER and print each difference."""
    before: Path = Path(sys.argv[1])
    after: Path = Path(sys.argv[2])
    skip: frozenset[str] = frozenset(sys.argv[3:])
    differing: list[str] = [
        notebook.name
        for notebook in sorted(before.glob("*.ipynb"))
        if not (after / notebook.name).exists()
        or outputs(notebook, skip) != outputs(after / notebook.name, skip)
    ]
    name: str
    for name in differing:
        print(f"differs: {name}")
    print(f"{len(differing)} of {len(list(before.glob('*.ipynb')))} notebooks differ")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
