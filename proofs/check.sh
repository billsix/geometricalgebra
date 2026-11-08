#!/usr/bin/env bash
# Build and verify the gacalc Lean proofs (proofs/).
#
# "Verify" = `lake build` succeeds AND every GacalcProofs declaration rests only on
# Lean's standard axioms (propext, Classical.choice, Quot.sound). A bare build only
# WARNS on `sorry` and still exits 0, so it is not sufficient on its own. The axioms
# gate (scripts/CheckAxioms.lean) catches `sorry` (sorryAx), a user `axiom`, and
# `native_decide` (Lean.ofReduceBool); a quick source grep for sorry/admit runs first.
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

# Quick completeness check: no `sorry`/`admit` in our own sources. Fast, and it names
# the line, but it is textual: it cannot see a user `axiom`, `native_decide`, or a hole
# that doesn't spell the word. The axioms gate below is the real check.
echo "[lean] source grep (no sorry/admit)…"
if grep -rnE '\b(sorry|admit)\b' GacalcProofs.lean GacalcProofs 2>/dev/null; then
  echo "[lean] FAIL: 'sorry'/'admit' present — an incomplete proof"; status=1
else
  echo "[lean] no sorry/admit in sources"
fi

# Axioms gate: every declaration in a GacalcProofs.* module may rest only on
# propext, Classical.choice and Quot.sound. scripts/CheckAxioms.lean logs an error
# for each declaration with any other axiom, so `lean` exits nonzero. It is not part
# of the GacalcProofs library, so `lake build` does not build it. (~3 min: it loads
# all of GacalcProofs and walks each declaration's dependencies.)
echo "[lean] axioms gate…"
lake env lean scripts/CheckAxioms.lean || status=1

[ "$status" -eq 0 ] && echo "[lean] OK" || echo "[lean] FAILED"
exit "$status"
