#!/usr/bin/env python
"""Codemod: module-qualify gacalc's renamed types in internal consumers.

gacalc dropped the dimension suffix from its generated types (``Vector2`` ->
``Vector``, ``G2`` -> ``G``, ``Scalar3`` -> ``Scalar``, ...); the *module* now
carries the dimension. This rewrites internal consumers (the test suite and
``tools/bench.py``) from the old flat suffixed names to the module-qualified
idiom:

  * an import ``from gacalc.g2 import Vector2, G2, ...`` becomes
    ``import gacalc.g2 as g2`` (these imports pull only renamed types), and
  * every ``Vector2`` / ``G2`` / ``Bivector3`` / ... becomes
    ``g2.Vector`` / ``g2.G`` / ``g3.Bivector`` / ... .

Class-constant access rides along for free (``Vector2.e_1`` -> ``g2.Vector.e_1``).
The regex is case-sensitive on the CapWord type names, so the lowercase module
aliases (``g2mod`` in test_conformance) are untouched.

Scope: pass the target files as argv (the caller lists tests/*.py + tools/bench.py).
NOT run on ``src/`` (its doctests import by name and print reprs — hand-edited) nor
on the notebooks (they import bare module constants ``e_1``, handled separately).

Run from the repo root:  python tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py <files...>
Verified by the test suite going green afterward; revert with ``git checkout`` if not.
"""

from __future__ import annotations

import pathlib
import re
import sys

_TYPES = "Vector|Bivector|Trivector|Rotor|Scalar|G"
# Type<dim> -> g<dim>.Type   (case-sensitive: only CapWord type names match).
_NAME_RE = re.compile(rf"\b({_TYPES})([123])\b")
# A whole `from gacalc.gN import ...` line (these pull only renamed types in the
# targeted files), replaced by a module alias.
_IMPORT_RE = re.compile(r"^(?P<indent>[ \t]*)from gacalc\.g(?P<n>[123]) import .*$")


def transform(src: str) -> str:
    out_lines: list[str] = []
    aliased: set[str] = set()  # modules already given an `import ... as gN` line
    for line in src.splitlines():
        m = _IMPORT_RE.match(line)
        if m is not None:
            n = m.group("n")
            if n in aliased:
                continue  # collapse a second `from gacalc.gN import ...` line
            aliased.add(n)
            out_lines.append(f"{m.group('indent')}import gacalc.g{n} as g{n}")
            continue
        out_lines.append(line)
    body = "\n".join(out_lines)
    if src.endswith("\n"):
        body += "\n"
    # qualify the names in the body (imports are already module aliases, which
    # the case-sensitive regex leaves alone)
    return _NAME_RE.sub(lambda mm: f"g{mm.group(2)}.{mm.group(1)}", body)


def main(paths: list[str]) -> None:
    for p in paths:
        path = pathlib.Path(p)
        new = transform(path.read_text())
        path.write_text(new)
        sys.stdout.write(f"rewrote {p}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
