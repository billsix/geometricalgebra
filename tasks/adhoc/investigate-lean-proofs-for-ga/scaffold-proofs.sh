#!/usr/bin/env bash
# Scaffold the real gacalc Lean proofs project at /gacalc/proofs, empirically:
# let `lake` generate the project (so the Mathlib version pin comes from lake's own
# resolution, not a hand-guess), land the first REAL proof (2D Lagrange, already
# shown to compile in the phase-2 spike), build it, run the axioms gate, and DUMP
# the generated files so we know exactly what to commit.  (task:
# tasks/investigate-lean-proofs-for-ga.md — scaffold step.)
#
# Run: make shell-exec MINIMAL_IMAGE=1 USE_LEAN=1 \
#   SCRIPT=tasks/adhoc/investigate-lean-proofs-for-ga/scaffold-proofs.sh
#
# Idempotent: inits only if no lakefile; keeps proofs/.lake (gitignored) so the
# Mathlib cache persists for cheap re-runs.  cwd is the repo root (REPO_MOUNT).
set -u

cd proofs || { echo "no proofs/ dir"; exit 1; }

echo "== versions =="
lean --version; lake --version
echo

if [ ! -f lakefile.toml ] && [ ! -f lakefile.lean ]; then
  echo "== lake init (math template) — generates lakefile + lean-toolchain =="
  # init in-place; name is the Lean library/namespace root.
  lake init GacalcProofs math
  echo "== lake exe cache get — download prebuilt Mathlib (big, one-time) =="
  lake exe cache get 2>&1 | tail -6
else
  echo "== reusing existing proofs/ project (cache present) =="
fi
echo

echo "== land the first proof module: GacalcProofs/Lagrange.lean =="
mkdir -p GacalcProofs
cat > GacalcProofs/Lagrange.lean <<'LEAN'
import Mathlib

/-! # Lagrange's identity (2D), squared form.

    ‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²  — in coordinates, with a∧b = a₁b₂ − a₂b₁.
    This is the identity the book uses to derive sin/cos; proved here by `ring`.
    (First landed proof; the from-scratch rotation-based dot/wedge proofs and the
    special-case↔general equivalences follow as their own modules per the task's
    step-tasks.) -/
namespace GacalcProofs

theorem lagrange_2d (a1 a2 b1 b2 : ℝ) :
    (a1 ^ 2 + a2 ^ 2) * (b1 ^ 2 + b2 ^ 2)
      = (a1 * b1 + a2 * b2) ^ 2 + (a1 * b2 - a2 * b1) ^ 2 := by
  ring

end GacalcProofs
LEAN

# Make the library root import our module so `lake build` builds it. `lake init`
# created a root file named after the package; discover it rather than assume.
ROOT="$(ls *.lean 2>/dev/null | grep -iv lakefile | head -1)"
echo "root lib file: ${ROOT:-<none>}"
if [ -n "${ROOT:-}" ]; then
  printf 'import GacalcProofs.Lagrange\n' > "$ROOT"
fi
echo

echo "== lake build =="
lake build; build_status=$?
echo "lake build exit=$build_status"
echo

if [ "$build_status" -eq 0 ]; then
  echo "== axioms gate: no sorryAx allowed =="
  cat > CheckAxioms.lean <<'LEAN'
import GacalcProofs.Lagrange
#print axioms GacalcProofs.lagrange_2d
LEAN
  lake env lean CheckAxioms.lean
  rm -f CheckAxioms.lean
fi
echo

echo "======================================================================"
echo "GENERATED PROJECT FILES (what to commit):"
echo "--- tree (top level) ---"; ls -a
echo "--- lakefile.toml ---"; cat lakefile.toml 2>/dev/null || echo "(none; lakefile.lean below)"
echo "--- lakefile.lean ---"; cat lakefile.lean 2>/dev/null || echo "(none)"
echo "--- lean-toolchain ---"; cat lean-toolchain 2>/dev/null
echo "--- lake-manifest.json (mathlib pin lives here) ---"; head -40 lake-manifest.json 2>/dev/null
echo "== scaffold complete =="
