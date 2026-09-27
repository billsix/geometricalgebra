#!/usr/bin/env python3
"""Codemod: rename the graded type `Rotor` -> `Versor` in the PROSE DOCS.

Companion to `codemod_rotor_type.py` (which did the same for code files). Capital
`Rotor` in these docs is *always* the type identifier -- the now-renamed even-grade
type -- so a word-boundary substitution is safe. The unit-vs-general judgment only
touches the lowercase word `rotor`/`rotors`, which is handled by hand and NOT here.

Scope (exactly the caller's target set):
    - tasks/reference/*.md  EXCEPT tasks/reference/unit-bivector-and-rotors.md
      (the human is editing that one)
    - README.md
    - CLAUDE.md

Leaves untouched: lowercase `rotor`/`rotors`, `_unit_bivector_rotor_factory`,
`rotor_for`, and everything outside the scope above (code, book, archives).

Word-boundary match on `Rotor`, so `Rotors` -> `Versors` too (prefix match under
\\b...), while lowercase is never touched. Idempotent: re-running changes nothing.
Paths are relative to the repo root (via `git rev-parse`), never container-absolute.
"""

import re
import subprocess
from pathlib import Path

ROOT: Path = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)

PAT: str = r"\bRotor"  # matches Rotor, Rotor_n, Rotors, Rotor.dual, Rotor(...)
REPL: str = "Versor"

reference_dir: Path = ROOT / "tasks" / "reference"
targets: list[Path] = [
    p
    for p in sorted(reference_dir.glob("*.md"))
    if p.name != "unit-bivector-and-rotors.md"
]
targets.append(ROOT / "README.md")
targets.append(ROOT / "CLAUDE.md")

total: int = 0
path: Path  # loop target: annotated above (can't annotate inline)
for path in targets:
    text: str = path.read_text()
    new: str
    count: int
    new, count = re.subn(PAT, REPL, text)
    if count:
        print(f"{path.relative_to(ROOT)}: {count}")
        path.write_text(new)
        total += count

print(f"TOTAL capital-Rotor -> Versor replacements: {total}")
