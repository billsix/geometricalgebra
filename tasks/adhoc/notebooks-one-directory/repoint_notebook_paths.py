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

"""Repoint references to a notebook source from ``book/docs/notebooks/`` to ``notebooks/``.

Run after ``git mv book/docs/notebooks/*.py notebooks/``. In every tracked text file
except the frozen records (``tasks/archive/``, ``tasks/review/``) and this script's own
directory, it rewrites ``book/docs/notebooks/<name>.py`` and
``book/docs/notebooks/*.py`` to ``notebooks/...``. A bare ``book/docs/notebooks`` (the
build's ``.ipynb`` output directory, or prose about the old layout) is left for a hand
edit, and the script lists where those remain.

Idempotent: a second run changes nothing.

Usage::

    python tasks/adhoc/notebooks-one-directory/repoint_notebook_paths.py
"""

import re
import subprocess
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[3]
SOURCE: re.Pattern[str] = re.compile(r"\bbook/docs/notebooks/((?:[\w-]+|\*|[\w-]*\*)\.py)\b")


def main() -> None:
    """Rewrite the source references and list the bare directory mentions left over."""
    listed: str = subprocess.run(
        [
            "git",
            "grep",
            "-l",
            "book/docs/notebooks",
            "--",
            ":!tasks/archive",
            ":!tasks/review",
            ":!tasks/adhoc",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    path: Path
    for path in (REPO / name for name in listed.split()):
        text: str = path.read_text()
        if SOURCE.sub(r"notebooks/\1", text) != text:
            path.write_text(SOURCE.sub(r"notebooks/\1", text))
            print(f"rewrote {path.relative_to(REPO)}")
    remaining: str = subprocess.run(
        ["git", "grep", "-n", "book/docs/notebooks", "--", ":!tasks/archive", ":!tasks/review", ":!tasks/adhoc"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    print(remaining, end="")


if __name__ == "__main__":
    main()
