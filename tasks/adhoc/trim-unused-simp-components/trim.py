#!/usr/bin/env python3
"""Greedily drop vacuous destructured-component hypotheses from getter-native proofs.

For each theorem with `obtain ⟨…⟩ := h` + `simp only [...]`, each obtain-bound name
that appears in a simp list AND nowhere else in the block is a candidate: remove it
from the simp list and set its obtain slot to `_`, rebuild, and keep the edit only if
`lake build` stays green. Safe by construction — every kept edit is build-verified (so
the theorem is still proven), and if the final full gate is not green the whole run is
rolled back to the original tree (the maintainer can only wake to a cleanly-trimmed
green tree or the untouched one).

Run inside the container from the repo (it drives `lake build` in proofs/). Paths are
relative to this script, never container-absolute:
    tasks/adhoc/trim-unused-simp-components/trim.py  ->  repo root = parents[3]

Task: tasks/trim-unused-simp-components.md
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[3]
PROOFS: Path = REPO / "proofs"
SRC: Path = PROOFS / "GacalcProofs"
LOG: Path = Path(__file__).resolve().parent / "trim.log"

TARGET_FILES: list[str] = [
    "G3.lean",
    "Sandwich.lean",
    "Reflect.lean",
    "Projection2D.lean",
    "Projection3D.lean",
    "Trig.lean",
    "ProjectionRotation2D.lean",
    "ProjectionRotation3D.lean",
]

# A theorem block runs from its `theorem`/`lemma` line to the next top-level marker.
BLOCK_START: re.Pattern[str] = re.compile(r"^(theorem|lemma)\s+(\w+)")
BLOCK_END: re.Pattern[str] = re.compile(
    r"^(theorem|lemma|def|noncomputable def|/--|/-!|/-|end\b"
    r"|namespace\b|section\b|@\[|#)"
)
OBTAIN: re.Pattern[str] = re.compile(r"obtain\s+⟨([^⟩]*)⟩\s*:=")
SIMP: re.Pattern[str] = re.compile(r"simp only \[(.*?)\]", re.DOTALL)
EMPTY_OBTAIN: re.Pattern[str] = re.compile(
    r"^\s*obtain\s+⟨\s*_(\s*,\s*_)*\s*⟩\s*:=\s*\w+\s*$"
)

loglines: list[str] = []


def log(msg: str) -> None:
    stamp: str = time.strftime("%H:%M:%S")
    line: str = f"[{stamp}] {msg}"
    print(line, flush=True)  # noqa: T201 — live progress for a long background run
    loglines.append(line)


def flush_log() -> None:
    LOG.write_text("\n".join(loglines) + "\n")


def lake_build(module: str | None = None) -> bool:
    """True iff the build succeeds (returncode 0, no 'error:' in output).

    With `module` ("G3" → GacalcProofs.G3) build only that module: a proof-internal
    trim can only affect its own file (the theorem *statement* is unchanged, so
    downstream modules can't break), which the final full gate confirms.
    """
    cmd: list[str] = ["lake", "build"]
    if module is not None:
        cmd.append(f"GacalcProofs.{module}")
    try:
        r: subprocess.CompletedProcess[str] = subprocess.run(
            cmd, cwd=PROOFS, capture_output=True, text=True, timeout=1800
        )
    except subprocess.TimeoutExpired:
        log("  !! lake build TIMED OUT (treated as failure)")
        return False
    return r.returncode == 0 and "error:" not in (r.stdout + r.stderr)


def module_of(f: str) -> str:
    return f[:-5] if f.endswith(".lean") else f


def full_gate() -> bool:
    r: subprocess.CompletedProcess[str] = subprocess.run(
        ["bash", "check.sh"], cwd=PROOFS, capture_output=True, text=True, timeout=1800
    )
    sys.stdout.write(r.stdout[-2000:])
    return r.returncode == 0


def find_blocks(text: str) -> list[tuple[str, int, int]]:
    """Return (theorem_name, start_line, end_line_excl) for each theorem/lemma block."""
    lines: list[str] = text.splitlines()
    starts: list[tuple[str, int]] = []
    for i, ln in enumerate(lines):
        m: re.Match[str] | None = BLOCK_START.match(ln)
        if m:
            starts.append((m.group(2), i))
    blocks: list[tuple[str, int, int]] = []
    for name, s in starts:
        e: int = len(lines)
        for j in range(s + 1, len(lines)):
            if BLOCK_END.match(lines[j]):
                e = j
                break
        blocks.append((name, s, e))
    return blocks


def candidates_for(block: str) -> list[str]:
    """Obtain-bound names that appear in a simp list and nowhere else in the block."""
    obtain_names: set[str] = set()
    for m in OBTAIN.finditer(block):
        for raw in m.group(1).split(","):
            tok: str = raw.strip()
            if tok and tok != "_":
                obtain_names.add(tok)
    simp_regions: list[str] = SIMP.findall(block)
    simp_blob: str = " ".join(simp_regions)
    simp_names: set[str] = {
        t.strip() for region in simp_regions for t in region.split(",")
    }
    cands: list[str] = []
    for nm in sorted(obtain_names):
        if nm not in simp_names:
            continue
        # count uses outside obtain binders and outside simp lists
        total: int = len(re.findall(rf"\b{re.escape(nm)}\b", block))
        in_obtain: int = sum(
            len(re.findall(rf"\b{re.escape(nm)}\b", m.group(1)))
            for m in OBTAIN.finditer(block)
        )
        in_simp: int = len(re.findall(rf"\b{re.escape(nm)}\b", simp_blob))
        if total - in_obtain - in_simp == 0:
            cands.append(nm)
    return cands


def remove_from_simp(region: str, nm: str) -> str:
    out: str = re.sub(rf"\b{re.escape(nm)}\s*,\s*", "", region, count=1)
    if out == region:
        out = re.sub(rf"\s*,\s*\b{re.escape(nm)}\b", "", region, count=1)
    if out == region:
        out = re.sub(rf"\b{re.escape(nm)}\b", "", region, count=1)
    return out


def apply_trim(text: str, name: str, nm: str) -> str | None:
    """In theorem `name`, drop `nm` from simp lists and `_` its obtain slot."""
    lines: list[str] = text.splitlines(keepends=True)
    for bn, s, e in find_blocks(text):
        if bn != name:
            continue
        seg: str = "".join(lines[s:e])

        def simp_sub(m: re.Match[str]) -> str:
            return "simp only [" + remove_from_simp(m.group(1), nm) + "]"

        seg2: str = SIMP.sub(simp_sub, seg)

        def obtain_sub(m: re.Match[str]) -> str:
            toks: list[str] = [t.strip() for t in m.group(1).split(",")]
            toks = ["_" if t == nm else t for t in toks]
            return "obtain ⟨" + ", ".join(toks) + "⟩ :="

        seg3: str = OBTAIN.sub(obtain_sub, seg2)
        if seg3 == seg:
            return None
        return "".join(lines[:s]) + seg3 + "".join(lines[e:])
    return None


def drop_candidates(plan: list[tuple[str, str, str]]) -> int:
    """Try each candidate; keep a drop iff its module still builds."""
    kept: int = 0
    for f, thm, nm in plan:
        path: Path = SRC / f
        before: str = path.read_text()
        trial: str | None = apply_trim(before, thm, nm)
        if trial is None or trial == before:
            log(f"  skip {f}:{thm}:{nm} (could not edit cleanly)")
            continue
        path.write_text(trial)
        if lake_build(module_of(f)):
            kept += 1
            log(f"  DROP {f}:{thm}:{nm}  (green)")
        else:
            path.write_text(before)
            log(f"  keep {f}:{thm}:{nm}  (needed — reverted)")
    return kept


def drop_empty_obtains(files: list[str]) -> int:
    """Delete an obtain binder that is now entirely `_` (a no-op; build-verified)."""
    removed: int = 0
    for f in files:
        path: Path = SRC / f
        changed: bool = True
        while changed:
            changed = False
            before: str = path.read_text()
            lines: list[str] = before.splitlines(keepends=True)
            for i, ln in enumerate(lines):
                if not EMPTY_OBTAIN.match(ln):
                    continue
                trial: str = "".join(lines[:i] + lines[i + 1 :])
                path.write_text(trial)
                if lake_build(module_of(f)):
                    removed += 1
                    changed = True
                    log(f"  rm no-op obtain  {f}:{ln.strip()}")
                else:
                    path.write_text(before)
                    log(f"  keep obtain (build needs it)  {f}:{ln.strip()}")
                break
    return removed


def main() -> int:
    files: list[str] = sys.argv[1:] if len(sys.argv) > 1 else TARGET_FILES
    log(f"repo={REPO} proofs={PROOFS} files={files}")
    snapshots: dict[str, str] = {f: (SRC / f).read_text() for f in files}

    log("baseline lake build…")
    if not lake_build():
        log("BASELINE NOT GREEN — aborting, no edits made.")
        flush_log()
        return 2

    # Enumerate candidates up front (names are stable across edits).
    plan: list[tuple[str, str, str]] = []  # (file, theorem, component)
    for f in files:
        text: str = snapshots[f]
        for bn, s, e in find_blocks(text):
            blk: str = "\n".join(text.splitlines()[s:e])
            if "obtain ⟨" not in blk or "simp only [" not in blk:
                continue
            for nm in candidates_for(blk):
                plan.append((f, bn, nm))
    log(f"{len(plan)} candidate component(s) across {len(files)} files")

    kept: int = drop_candidates(plan)
    removed: int = drop_empty_obtains(files)
    log(
        f"trimmed {kept}/{len(plan)} candidates; removed {removed} "
        f"no-op obtain(s); running full gate…"
    )

    if full_gate():
        log("FINAL GATE GREEN — trims kept.")
        flush_log()
        return 0
    log("FINAL GATE RED — rolling back ALL files to original.")
    for f, original in snapshots.items():
        (SRC / f).write_text(original)
    flush_log()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
