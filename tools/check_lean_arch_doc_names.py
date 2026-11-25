#!/usr/bin/env python3
"""List backticked names in the architecture doc that no Lean file declares.

Reads ``tasks/reference/lean-ga-proof-architecture.md`` between the ``## Inventory``
heading and the ``## Hypotheses`` heading, collects every backticked identifier, and
reports the ones that are neither a declaration in ``proofs/GacalcProofs/*.lean`` (the
last dotted component is compared, so ``G3.cross_vec`` and ``cross_vec`` both match) nor
a known non-declaration (a Python name, a Mathlib name, a file name). Read-only; the
document is the reference for the Lean proofs, and this finds the names it still cites
that a refactor deleted or renamed.

Usage: ``python tools/check_lean_arch_doc_names.py``
(a report, not a gate: it never fails a build)
"""

from __future__ import annotations

import pathlib
import re

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
DOC: pathlib.Path = REPO / "tasks" / "reference" / "lean-ga-proof-architecture.md"
PROOFS: pathlib.Path = REPO / "proofs" / "GacalcProofs"

DECL: re.Pattern[str] = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(?:noncomputable\s+)?"
    r"(?:theorem|lemma|def|abbrev|instance|structure|inductive)\s+([^\s({:\[]+)",
    re.MULTILINE,
)
TICKED: re.Pattern[str] = re.compile(r"`([^`\n]+)`")
IDENT: re.Pattern[str] = re.compile(r"^[A-Za-z_][A-Za-z0-9_.'₀-₉]*$")

# Backticked words that are not Lean declarations of this repository (Python names,
# Mathlib, files, prose).
KNOWN_OTHER: frozenset[str] = frozenset()


def main() -> None:
    """Print each undeclared backticked identifier and how often it appears."""

    def section(text: str) -> str:
        """The inventory-and-coverage part of the document.

        Args:
            text: The whole document.

        Returns:
            str: the text from ``## Inventory`` up to ``## Hypotheses``.
        """
        start: int = text.index("## Inventory")
        end: int = text.index("## Hypotheses")
        return text[start:end]

    def declared_names() -> set[str]:
        """Every declared name in the proofs, by last dotted component.

        Returns:
            set[str]: the short names.
        """
        names: set[str] = set()
        path: pathlib.Path
        for path in sorted(PROOFS.glob("*.lean")):
            text: str = path.read_text()
            match: str
            for match in DECL.findall(text):
                names.add(match.split(".")[-1])
        return names

    declared: set[str] = declared_names()
    files: set[str] = {path.stem for path in PROOFS.glob("*.lean")}
    counts: dict[str, int] = {}
    token: str
    for token in TICKED.findall(section(DOC.read_text())):
        for word in re.split(r"[\s,;()/]+", token):
            word = word.strip("*.:")
            if not word or not IDENT.match(word):
                continue
            short: str = word.split(".")[-1]
            if (
                short in declared
                or word in files
                or short in files
                or word in KNOWN_OTHER
            ):
                continue
            counts[word] = counts.get(word, 0) + 1
    name: str
    for name in sorted(counts):
        print(f"{counts[name]:3d}  {name}")


if __name__ == "__main__":
    main()
