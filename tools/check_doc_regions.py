#!/usr/bin/env python
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

"""Verify gacalc's ``doc-region`` markers are safe to include from a book.

gacalc's source (hand-written ``functions.py`` / ``transforms.py`` and the
generated ``g1``/``g2``/``g3``/``scalar.py``) carries ``# doc-region-begin
<name>`` / ``# doc-region-end <name>`` markers so *modelviewprojection*'s book
can ``literalinclude`` slices of it.  A Sphinx ``:start-after:`` /
``:end-before:`` query fails **silently** if the anchors are not well-formed, so
this makes three failure modes loud (exit 1), **per file**:

1. **Exact duplicate** -- two regions with the same name; a query always selects
   the first, so the second is unreachable.  (A set-based check misses this, the
   way the ``x`` property getter/setter collision was nearly missed -- so the raw
   occurrence count is used.)
2. **Prefix collision** -- one name is a prefix of another; Sphinx matches the
   first line *containing* the anchor text, so the shorter can pull the longer's
   region.
3. **Unbalanced** -- a ``begin`` with no matching ``end`` (or vice versa).

The generated modules are gitignored, so run ``make generate`` (or
``make check-regions``, which regenerates first) before this.  Checked for
begin- and end-markers separately, since the two directives select on their own
marker kind.
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

_SRC: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent / "src" / "gacalc"

# Only genuine marker COMMENTS (``# doc-region-...``); the bare string
# ``doc-region-begin`` inside a regex/docstring must not count.
_BEGIN: re.Pattern[str] = re.compile(
    r"#\s*doc-region-begin (?P<name>.+?)[ \t]*$", re.MULTILINE
)
_END: re.Pattern[str] = re.compile(
    r"#\s*doc-region-end (?P<name>.+?)[ \t]*$", re.MULTILINE
)


def _errors_in(path: pathlib.Path) -> list[str]:
    text: str = path.read_text()
    rel: str = str(path.relative_to(_SRC.parent.parent))
    errors: list[str] = []
    begins: list[str] = [m.group("name") for m in _BEGIN.finditer(text)]
    ends: list[str] = [m.group("name") for m in _END.finditer(text)]

    marker_kind: str
    names: list[str]
    for marker_kind, names in (("begin", begins), ("end", ends)):
        counts: collections.Counter[str] = collections.Counter(names)
        name: str
        count: int
        for name, count in sorted(counts.items()):
            if count > 1:
                errors.append(
                    f"{rel}: doc-region-{marker_kind} '{name}' appears "
                    f"{count} times -- a query always selects the first"
                )
        unique: list[str] = sorted(counts)
        shorter: str
        longer: str
        for shorter in unique:
            for longer in unique:
                if shorter != longer and longer.startswith(shorter):
                    errors.append(
                        f"{rel}: doc-region-{marker_kind} '{shorter}' is a "
                        f"prefix of '{longer}' -- a query for the shorter can "
                        f"match the longer's line"
                    )

    unmatched_begin: set[str] = set(begins) - set(ends)
    unmatched_end: set[str] = set(ends) - set(begins)
    for name in sorted(unmatched_begin):
        errors.append(f"{rel}: doc-region-begin '{name}' has no matching end")
    for name in sorted(unmatched_end):
        errors.append(f"{rel}: doc-region-end '{name}' has no matching begin")
    return errors


def main() -> int:
    if not _SRC.exists():
        sys.stderr.write(f"no {_SRC}; run `make generate` first\n")
        return 1
    errors: list[str] = []
    path: pathlib.Path
    for path in sorted(_SRC.glob("*.py")):
        errors.extend(_errors_in(path))

    if not errors:
        sys.stdout.write(
            "gacalc doc-region markers OK: unique, prefix-free, balanced.\n"
        )
        return 0
    sys.stdout.write("DOC-REGION MARKER PROBLEMS:\n")
    problem: str
    for problem in errors:
        sys.stdout.write(f"  {problem}\n")
    sys.stdout.write(f"\n{len(errors)} problem(s).\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
