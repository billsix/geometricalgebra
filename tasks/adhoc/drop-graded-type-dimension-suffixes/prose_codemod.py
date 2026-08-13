#!/usr/bin/env python
"""Codemod: drop the dimension suffix from generated type names in PROSE.

Companion to ``codemod.py`` (which module-qualifies *code*). Prose — comments,
docstrings, markdown — describes the types generically (the generator is
dimension-parametric; ``Gn`` is the reference), so bare unsuffixed names read best:
``Vector2`` -> ``Vector``, ``G3`` -> ``G``, etc. It also collapses the now-redundant
per-algebra enumerations (``Scalar1``/``Scalar2``/``Scalar3`` -> ``Scalar``;
``G1``/``G2``/``G3`` -> ``G``; ``Vector1 / Vector2 / Vector3`` -> ``Vector``).

Leaves alone: the generic placeholders ``Vector_n`` / ``G_n`` / ``Scalar_n`` (no
digit), the math subscripts ``𝒢₂`` (not ASCII ``G2``), and ``G4`` (out of [1-3];
the README's future-algebra example is spot-fixed separately). Does NOT touch code
(``g2.Vector`` already has no ``Vector2`` to match; already-fixed doctests are safe).

Run from the repo root:  python .../prose_codemod.py <files...>
For src files, regenerate + run the suite afterward (emitted class-docstrings change).
"""

from __future__ import annotations

import pathlib
import re
import sys

_T = "Vector|Bivector|Trivector|Rotor|Scalar|G"
_SUFFIXED = re.compile(rf"\b({_T})([123])\b")


def transform(src: str) -> str:
    # 1. drop the suffix everywhere a suffixed name appears
    src = _SUFFIXED.sub(lambda m: m.group(1), src)
    # 2. collapse the now-repeated enumerations. Cover double- and single-backtick
    #    (markdown vs rst/py-docstring), slash- and space-slash-separated, plus bare.
    for tick in ("``", "`"):
        src = re.sub(rf"({tick}({_T}){tick})(?:/\1)+", r"\1", src)
        src = re.sub(rf"({tick}({_T}){tick})(?: / \1)+", r"\1", src)
    src = re.sub(rf"\b({_T})\b(?: / \1\b)+", r"\1", src)
    src = re.sub(rf"\b({_T})\b(?:/\1\b)+", r"\1", src)
    src = re.sub(rf"\b({_T})\b(?:, \1\b)+", r"\1", src)  # "[Gn, G, G, G]" -> "[Gn, G]"
    return src


def main(paths: list[str]) -> None:
    for p in paths:
        path = pathlib.Path(p)
        path.write_text(transform(path.read_text()))
        sys.stdout.write(f"prose-rewrote {p}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
