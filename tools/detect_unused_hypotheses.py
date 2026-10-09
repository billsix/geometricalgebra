#!/usr/bin/env python3
"""Detect signature hypotheses that are unreferenced in a theorem's proof body.

Scans proofs/GacalcProofs/*.lean for named binders whose type is a grade predicate
(IsVector/IsEvenVersor/IsBivector/IsTrivector) or a `≠ 0` guard, and reports the ones
whose bound name never appears in the proof body.

CAVEAT — a *candidate* list, not proof of unusedness: `field_simp`/`simp` use `≠ 0`
hypotheses from context WITHOUT naming them, so a name-absent guard may still be
load-bearing, and a hypothesis rewritten in place (`rw … at h`) is reported although
used. The build is the judge — drop one and `lake build` to confirm; a `ring`
timeout means the PROOF needs it, only a residual goal means the THEOREM does (see
tasks/reference/lean-ga-proof-architecture.md, "Hypotheses"). Read-only.

Usage (repo root, host or container): `python3 tools/detect_unused_hypotheses.py`.
Paths are relative to this script: tools/ -> repo = parents[1].
"""

from __future__ import annotations

import re
from pathlib import Path

SRC: Path = Path(__file__).resolve().parents[1] / "proofs" / "GacalcProofs"

THEOREM: re.Pattern[str] = re.compile(r"^(theorem|lemma)\s+(\w+)", re.MULTILINE)
# a named binder group: ( names : type )  or  { names : type }
BINDER: re.Pattern[str] = re.compile(
    r"[({]\s*([A-Za-z_][\w\s]*?)\s*:\s*([^{}()]*?)\s*[)}]"
)
PRED: re.Pattern[str] = re.compile(
    r"\b(IsVector|IsEvenVersor|IsBivector|IsTrivector)\b|≠\s*0"
)


def main() -> None:
    total: int = 0
    path: Path
    for path in sorted(SRC.glob("*.lean")):
        text: str = path.read_text()
        starts: list[tuple[str, int]] = [
            (m.group(2), m.start()) for m in THEOREM.finditer(text)
        ]
        idx: int
        name: str
        s: int
        for idx, (name, s) in enumerate(starts):
            e: int = starts[idx + 1][1] if idx + 1 < len(starts) else len(text)
            block: str = text[s:e]
            delim: int = block.find(":=")
            if delim < 0:
                continue
            sig: str = block[:delim]
            body: str = block[delim + 2 :]
            bm: re.Match[str]
            for bm in BINDER.finditer(sig):
                names: list[str] = bm.group(1).split()
                btype: str = bm.group(2)
                if not PRED.search(btype):
                    continue
                nm: str
                for nm in names:
                    if not re.search(rf"\b{re.escape(nm)}\b", body):
                        total += 1
                        print(  # noqa: T201 — this is a report script
                            f"{path.name}:{name}  UNUSED  ({nm} : {btype.strip()})"
                        )
    print(f"\n{total} unused hypothesis binder(s)")  # noqa: T201 — report script


if __name__ == "__main__":
    main()
