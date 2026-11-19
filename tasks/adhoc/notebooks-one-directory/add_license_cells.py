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

"""Give every notebook the project's license header, in a cell the book does not print.

``CLAUDE.md`` requires the LGPL-2.1-only header on every ``.py`` file. In a notebook
it sits in its own code cell right after the jupytext header, tagged ``remove-cell``
so myst-nb leaves it out of the rendered page. For each ``notebooks/*.py`` this:

- tags an existing untagged header cell (``# %%`` followed by the header) ``remove-cell``;
- inserts a tagged header cell after the jupytext header where there is none.

The header text is copied from ``tests/test_rotate_90_degrees.py``, the file
``CLAUDE.md`` names as the source. Idempotent: a second run changes nothing.

Usage::

    python tasks/adhoc/notebooks-one-directory/add_license_cells.py
"""

from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[3]
HEADER: str = "".join(
    (REPO / "tests" / "test_rotate_90_degrees.py").read_text().splitlines(True)[:12]
)
TAGGED: str = '# %% tags=["remove-cell"]\n'


def with_license_cell(text: str) -> str:
    """Return a notebook's text with a tagged license cell after its jupytext header.

    Args:
        text: the percent-format notebook's contents.

    Returns:
        str: the new contents (equal to ``text`` when the cell is already there).

    Raises:
        ValueError: if the notebook has no jupytext header to put the cell after.
    """
    if TAGGED + "\n" + HEADER in text or TAGGED + HEADER in text:
        return text
    if "# %%\n\n" + HEADER in text:
        return text.replace("# %%\n\n" + HEADER, TAGGED + HEADER, 1)
    yaml_end: int = text.find("\n# ---\n", 1)
    if not text.startswith("# ---\n") or yaml_end < 0:
        raise ValueError("no jupytext header")
    cut: int = yaml_end + len("\n# ---\n")
    return text[:cut] + "\n" + TAGGED + HEADER + text[cut:]


def main() -> None:
    """Rewrite every notebook in place and print the ones that changed."""
    path: Path
    changed: int = 0
    for path in sorted((REPO / "notebooks").glob("*.py")):
        text: str = path.read_text()
        if with_license_cell(text) != text:
            path.write_text(with_license_cell(text))
            changed += 1
            print(path.relative_to(REPO))
    print(f"{changed} files changed")


if __name__ == "__main__":
    main()
