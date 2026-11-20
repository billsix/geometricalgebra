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

"""Report every cancellation line in the executed notebooks that needs a look.

Reads ``data/executed/*.ipynb`` (written by ``execute_notebooks.sh``) and prints,
per notebook, each cancellation line (a ``text/latex`` output following the
"Terms with the same number cancel" caption) that either does not end in ``= 0``
(the terms did not cancel as written) or has no ``\\underbrace`` at all (nothing
to pair: both sides are single atoms). Exits 0; it is a report.
"""

import json
import pathlib

DATA: pathlib.Path = pathlib.Path(__file__).resolve().parent / "data"


def main() -> None:
    """Print the lines worth a look, then the totals."""
    total: int = 0
    flagged: int = 0
    path: pathlib.Path
    for path in sorted((DATA / "executed").glob("*.ipynb")):
        notebook: dict[str, object] = json.loads(path.read_text())
        cells: list[dict[str, object]] = notebook["cells"]  # type: ignore[assignment]
        cell: dict[str, object]
        for cell in cells:
            outputs: list[dict[str, object]] = cell.get("outputs", [])  # type: ignore[assignment]
            in_cancellation: bool = False
            output: dict[str, object]
            for output in outputs:
                data: dict[str, object] = output.get("data", {})  # type: ignore[assignment]
                markdown: str = "".join(data.get("text/markdown", ""))  # type: ignore[arg-type]
                if markdown:
                    in_cancellation = "same number cancel" in markdown
                    continue
                latex: str = "".join(data.get("text/latex", ""))  # type: ignore[arg-type]
                if not (in_cancellation and latex):
                    continue
                total += 1
                body: str = latex.strip().strip("$").strip()
                if not body.endswith("= 0") or "underbrace" not in body:
                    flagged += 1
                    print(f"{path.stem}: {body[:300]}")
    print(f"{total} cancellation lines, {flagged} flagged")


if __name__ == "__main__":
    main()
