#!/usr/bin/env python3
"""Codemod: rename the *unambiguous* 'rotor' identifier tokens to 'versor' across
gacalc (part of the breaking rename in tasks/rename-rotor-to-versor.md).

Handles ONLY the multi-word identifier tokens that mean the general (un-normalized)
versor everywhere they appear, so a global word-boundary substitution is safe:

    rotor_from_vectors -> versor_from_vectors
    rotor_rotation     -> versor_rotation
    rotor_inv          -> versor_inv
    rotor_extras       -> versor_extras

Deliberately does NOT touch (handled elsewhere, by hand, with unit-vs-general judgment):
  - `_unit_bivector_rotor_factory` / `rotor_for`  -- KEEP: these build a *unit* rotor.
  - the bare word `rotor` / `rotors`              -- unit in some places, general in others.
  - the `Rotor` type name                         -- separate code-scoped pass.

Idempotent: re-running makes no further changes (the patterns no longer match).
Paths are relative to the repo root (via `git rev-parse`), never container-absolute.
"""

import re
import subprocess
from pathlib import Path

ROOT: Path = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)

RENAMES: dict[str, str] = {
    r"\brotor_from_vectors\b": "versor_from_vectors",
    r"\brotor_rotation\b": "versor_rotation",
    r"\brotor_inv\b": "versor_inv",
    r"\brotor_extras\b": "versor_extras",
}

EXTS: tuple[str, ...] = (".py", ".md", ".rst", ".txt", ".toml", ".cfg")
# generated modules regenerate from the generator; archives stay historically accurate.
SKIP_EXACT: set[str] = {"src/gacalc/g1.py", "src/gacalc/g2.py", "src/gacalc/g3.py"}

tracked: list[str] = subprocess.check_output(
    ["git", "ls-files"], text=True, cwd=ROOT
).splitlines()
targets: list[str] = [
    f
    for f in tracked
    if f.endswith(EXTS) and not f.startswith("tasks/archive/") and f not in SKIP_EXACT
]

total: int = 0
rel: str  # loop target: annotated on the line above (can't annotate inline)
for rel in targets:
    path: Path = ROOT / rel
    text: str
    try:
        text = path.read_text()
    except (UnicodeDecodeError, IsADirectoryError):
        continue
    new: str = text
    count: int = 0
    pat: str  # unpack targets: declared above the loop
    repl: str
    for pat, repl in RENAMES.items():
        matched: int
        new, matched = re.subn(pat, repl, new)
        count += matched
    if count:
        print(f"{rel}: {count}")
        path.write_text(new)
        total += count

print(f"TOTAL replacements: {total}")
