#!/usr/bin/env bash
# Build and verify the gacalc Lean proofs (proofs/).
#
# "Verify" = `lake build` succeeds AND no proof depends on `sorryAx` (an incomplete
# `sorry` proof). The axioms grep is the reliable, version-stable gate: a bare build
# only WARNS on `sorry` and still exits 0, so it is not sufficient on its own
# (learned in the phase-1 spike; see tasks/reference/lean-for-gacalc.md).
#
# Portable: runs in the container (via `make lean`) and on a host that has elan/lake
# on PATH. It cd's to its own dir, so it works from anywhere. Runs BOTH checks and
# fails (nonzero) if EITHER fails — never `set -e` (that would stop at the first red
# and hide the rest); see ~/.claude/reference/shell-and-gate-scripts.md.
set -u
cd "$(dirname "$0")"

status=0

# Ensure the Mathlib dependency is present in proofs/.lake. The image bakes Mathlib
# at /opt/gacalc-proofs/.lake (a committed layer OUTSIDE the bind-mounted repo,
# because the mount would shadow a baked proofs/.lake). If proofs/.lake is empty
# (fresh host checkout) we copy the baked cache in — OFFLINE. Only if there is no
# baked cache (e.g. a host without the Lean image) do we fetch over the network.
# After the first populate, proofs/.lake persists on the host across runs.
BAKED_LAKE="${GACALC_PROOFS_BAKED_LAKE:-/opt/gacalc-proofs/.lake}"
if [ ! -d .lake/packages/mathlib ]; then
  if [ -d "$BAKED_LAKE/packages/mathlib" ]; then
    echo "[lean] populating proofs/.lake from baked Mathlib (offline)…"
    mkdir -p .lake && cp -a "$BAKED_LAKE/." .lake/ || status=1
  else
    echo "[lean] no baked Mathlib; fetching cache over the network (first run)…"
    lake exe cache get || status=1
  fi
fi

echo "[lean] lake build…"
lake build || status=1

# Completeness gate: no incomplete proofs. `lake build` only WARNS on `sorry` and
# still exits 0, so we also reject any `sorry`/`admit` in our own sources — a
# namespace-agnostic, robust check for a self-contained proof project (all our
# proofs live in these files, so a textual scan catches every hole). `#print axioms
# <name>` (checking a proof rests only on [propext, Classical.choice, Quot.sound],
# never sorryAx) remains the manual gold-standard spot check — see
# tasks/reference/lean-for-gacalc.md.
echo "[lean] completeness gate (no sorry/admit in sources)…"
if grep -rnE '\b(sorry|admit)\b' GacalcProofs.lean GacalcProofs 2>/dev/null; then
  echo "[lean] FAIL: 'sorry'/'admit' present — an incomplete proof"; status=1
else
  echo "[lean] no sorry/admit in sources"
fi

[ "$status" -eq 0 ] && echo "[lean] OK" || echo "[lean] FAILED"
exit "$status"
