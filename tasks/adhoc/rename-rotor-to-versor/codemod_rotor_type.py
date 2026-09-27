#!/usr/bin/env python3
"""Codemod: rename the graded type `Rotor` -> `Versor` in CODE files only.

The graded even-grade type does not enforce unit magnitude, so `Versor` is the
accurate name (a *rotor* is the unit special case). This pass touches only source
files where `Rotor` is unambiguously the type identifier:

    tools/*.py, src/gacalc/*.py (except generated g1/g2/g3.py), tests/*.py,
    notebooks/*.py

Docs / book / tasks (prose, where "Rotor" may mean the unit concept) are handled
separately, by hand, with the unit-vs-general rule.

Word-boundary match on `Rotor` (capitalized), so lowercase `rotor` and the unit
`_unit_bivector_rotor_factory` / `rotor_for` are untouched. Idempotent. Paths are
relative to the repo root.
"""

import re
import subprocess
from pathlib import Path

ROOT: Path = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)

PATTERN: re.Pattern[str] = re.compile(r"\bRotor\b")
SKIP_EXACT: set[str] = {"src/gacalc/g1.py", "src/gacalc/g2.py", "src/gacalc/g3.py"}


def is_code(rel: str) -> bool:
    """True for the hand-written code files this pass may edit."""
    if rel in SKIP_EXACT:
        return False
    return rel.startswith(
        ("src/gacalc/", "tools/", "tests/", "notebooks/")
    ) and rel.endswith(".py")


tracked: list[str] = subprocess.check_output(
    ["git", "ls-files"], text=True, cwd=ROOT
).splitlines()
total: int = 0
rel: str  # loop target: annotated on the line above
for rel in tracked:
    if not is_code(rel):
        continue
    path: Path = ROOT / rel
    text: str = path.read_text()
    new: str
    n: int
    new, n = PATTERN.subn("Versor", text)
    if n:
        print(f"{rel}: {n}")
        path.write_text(new)
        total += n

print(f"TOTAL Rotor->Versor: {total}")
