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

"""Rewrite ``Vector(x, y, z)`` constructor calls as basis-constant sums.

gacalc's ``CLAUDE.md`` asks for vectors built from the basis constants with every
coefficient written out (``2 * e_1 + 1 * e_2``), not the constructor.  Code moved
from modelviewprojection uses the constructor, so this rewrites, in each file
named on the command line:

* ``Vector(a, b, c)`` -> ``a * e_1 + b * e_2 + c * e_3`` (a negative later
  coefficient becomes ``- 5.0 * e_3``), parenthesized when a ``*``, ``/`` or
  ``.`` follows it, so precedence is unchanged;
* ``Vector(coeff_e_1=a, coeff_e_2=b, coeff_e_3=c)`` the same way.

Each coefficient is kept exactly as written (``0.0`` stays ``0.0``, ``1`` stays
``1``), so numeric types and therefore numeric paths are unchanged.  Only calls
whose three arguments contain no parentheses or commas are rewritten; anything
else is reported for a hand edit.  The script does not add the ``e_1, e_2,
e_3`` import.  It is idempotent: a second run finds no constructor calls.

Usage (from the repo root)::

    python3 tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/basis_vectors.py FILE...
"""

import pathlib
import re
import sys

ARG: str = r"\s*([^,()=]+?)\s*"
POSITIONAL: re.Pattern[str] = re.compile(r"\bVector\(" + ARG + "," + ARG + "," + ARG + r"\)")
KEYWORD: re.Pattern[str] = re.compile(
    r"\bVector\(\s*coeff_e_1=" + ARG + r",\s*coeff_e_2=" + ARG + r",\s*coeff_e_3=" + ARG + r"\)"
)
LEFTOVER: re.Pattern[str] = re.compile(r"\bVector\((?!\))")


def as_sum(coefficients: tuple[str, str, str]) -> str:
    """``("-9.0", "1.0", "-5.0")`` -> ``"-9.0 * e_1 + 1.0 * e_2 - 5.0 * e_3"``."""
    terms: list[str] = [f"{coefficients[0]} * e_1"]
    for coefficient, blade in zip(coefficients[1:], ("e_2", "e_3"), strict=True):
        match coefficient.startswith("-"):
            case True:
                terms.append(f"- {coefficient[1:]} * {blade}")
            case False:
                terms.append(f"+ {coefficient} * {blade}")
    return " ".join(terms)


def rewrite(text: str, pattern: re.Pattern[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        coefficients: tuple[str, str, str] = (match.group(1), match.group(2), match.group(3))
        expression: str = as_sum(coefficients)
        following: str = text[match.end() : match.end() + 3].lstrip()
        return f"({expression})" if following[:1] in ("*", "/", ".") else expression

    return pattern.sub(replace, text)


status: int = 0
for name in sys.argv[1:]:
    path: pathlib.Path = pathlib.Path(name)
    before: str = path.read_text()
    after: str = rewrite(rewrite(before, KEYWORD), POSITIONAL)
    if after != before:
        path.write_text(after)
        print(f"rewrote {name}")
    for number, line in enumerate(after.splitlines(), start=1):
        if LEFTOVER.search(line):
            print(f"  hand edit: {name}:{number}: {line.strip()}")
            status = 1
sys.exit(status)
