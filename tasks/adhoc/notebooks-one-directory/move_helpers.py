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

"""Repoint the code at the ePiX helpers' new home, ``gacalc.epixscene``.

Run after ``git mv book/figures/epix/_<name>.py src/gacalc/epixscene/<name>.py`` for
the seven generic helpers. In the moved helpers, the figure scripts and their
figure-specific helper modules (``book/figures/epix/``), and the book notebooks, it:

- rewrites ``from _<name> import`` to ``from gacalc.epixscene.<name> import``;
- rewrites the docstring references ``:mod:`_<name>``` and ````_<name>```` to the
  package path, and the sibling file name ``_<name>.py`` to ``<name>.py``;
- deletes the notebooks' ``sys.path`` block, which the installed package makes unneeded.

Idempotent: a second run changes nothing. Prints each file it changed.

Usage (from anywhere)::

    python tasks/adhoc/notebooks-one-directory/move_helpers.py
"""

import re
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[3]
HELPERS: tuple[str, ...] = (
    "scene2d",
    "scene3d",
    "frame_scene",
    "bootstrap_live",
    "line_scene",
    "paper_scene",
    "venn_scene",
)
SYS_PATH_BLOCK: str = (
    "import pathlib\n"
    "import sys\n"
    "\n"
    "# The ePiX scene helpers live with the book's other figure sources.\n"
    'sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))\n'
    "\n"
)
NAMES: str = "|".join(HELPERS)
REWRITES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(rf"\bfrom _({NAMES}) import\b"), r"from gacalc.epixscene.\1 import"),
    (re.compile(rf":mod:`_({NAMES})`"), r":mod:`gacalc.epixscene.\1`"),
    (re.compile(rf"``_({NAMES})``"), r"``gacalc.epixscene.\1``"),
    (re.compile(rf"(?<![\w/])_({NAMES})\.py\b"), r"\1.py"),
)


def rewritten(text: str) -> str:
    """Return ``text`` with every rewrite applied and the ``sys.path`` block removed.

    Args:
        text: a file's contents.

    Returns:
        str: the new contents (equal to ``text`` when nothing applies).
    """
    pattern: re.Pattern[str]
    replacement: str
    for pattern, replacement in REWRITES:
        text = pattern.sub(replacement, text)
    return text.replace(SYS_PATH_BLOCK, "")


def main() -> None:
    """Rewrite every in-scope file in place and print the ones that changed."""
    files: list[Path] = [
        *sorted((REPO / "src" / "gacalc" / "epixscene").glob("*.py")),
        *sorted((REPO / "book" / "figures" / "epix").glob("*.py")),
        *sorted((REPO / "book" / "docs" / "notebooks").glob("*.py")),
    ]
    changed: list[Path] = [
        path for path in files if rewritten(path.read_text()) != path.read_text()
    ]
    path: Path
    for path in changed:
        path.write_text(rewritten(path.read_text()))
        print(path.relative_to(REPO))
    print(f"{len(changed)} files changed")


if __name__ == "__main__":
    main()
