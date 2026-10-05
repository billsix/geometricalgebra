"""Codemod for tasks/consider-renaming-scalar-to-real.md (decisions of 2026-10-05).

Whole-word, content-keyed replacements over the tracked sites (not line numbers):
``BladeCoef`` → ``BladeReal``, ``Coef`` → ``Real``, ``from_scalar`` / ``from_coef`` → ``from_real``.
The two constructor definitions in ``base.py`` are merged by hand first (``from_real(real: Real)``);
this script then renames every remaining use. Idempotent: a second run changes nothing.
Excluded on purpose: ``tasks/reference/scalar-vs-real-naming.md`` (its map records the old names as
history), the task doc, ``CHANGELOG.md``, and ``tasks/archive``.

Run from the repo root inside the project container::

    python tasks/adhoc/consider-renaming-scalar-to-real/rename.py
"""

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCOPE = ["src", "tools", "tests", "notebooks", "README.md", "book", "CLAUDE.md", "tasks/reference"]
EXCLUDE = {"tasks/reference/scalar-vs-real-naming.md"}
RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bBladeCoef\b"), "BladeReal"),
    (re.compile(r"\bCoef\b"), "Real"),
    (re.compile(r"\bfrom_scalar\b"), "from_real"),
    (re.compile(r"\bfrom_coef\b"), "from_real"),
]

files: list[str] = subprocess.run(
    ["git", "ls-files", "--", *SCOPE], cwd=ROOT, check=True, text=True, capture_output=True
).stdout.split()
changed: int = 0
for rel in files:
    if rel in EXCLUDE or not rel.endswith((".py", ".md", ".rst", ".txt", ".toml")):
        continue
    path: pathlib.Path = ROOT / rel
    before: str = path.read_text()
    after: str = before
    for pattern, replacement in RULES:
        after = pattern.sub(replacement, after)
    if after != before:
        path.write_text(after)
        changed += 1
        print("rewrote", rel)
print(f"{changed} files changed")
