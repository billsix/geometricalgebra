#!/usr/bin/env bash
# Lean 4 learning spike — PHASE 2 (Mathlib reuse).
#
# Purpose (task: tasks/investigate-lean-proofs-for-ga.md): demonstrate REUSING
# already-proved Mathlib results, to answer two of the author's questions:
#   * "Is the dot product, defined for arbitrary dimension, proven by someone else,
#      or is it an axiom?"  -> a proved DEFINITION+THEOREMS, shown here.
#   * "How do I reference others' work?"  -> `import Mathlib` + cite lemmas by name.
#
# Run it (author's preferred method):
#   make shell-exec MINIMAL_IMAGE=1 USE_LEAN=1 \
#     SCRIPT=tasks/adhoc/investigate-lean-proofs-for-ga/spike-mathlib.sh
#
# IDEMPOTENT & PERSISTENT: it builds under a gitignored scratch dir in the mounted
# repo (mathlib-spike/, see the sibling .gitignore) so the multi-GB Mathlib cache
# SURVIVES between shell-exec runs. First run does the expensive setup (toolchain +
# `lake exe cache get`); later runs only rebuild the proof file (seconds). Clean up
# with: rm -rf tasks/adhoc/investigate-lean-proofs-for-ga/mathlib-spike
set -u

# shell-exec sets cwd to the repo root (REPO_MOUNT). Resolve the scratch dir
# relative to the repo root, never a container-absolute path.
SCRATCH="tasks/adhoc/investigate-lean-proofs-for-ga/mathlib-spike"
PROJ="$SCRATCH/mathspike"
mkdir -p "$SCRATCH"

echo "== versions =="
lean --version; lake --version
echo

if [ ! -f "$PROJ/lakefile.toml" ] && [ ! -f "$PROJ/lakefile.lean" ]; then
  echo "== first run: create a Mathlib project (lake 'math' template) =="
  ( cd "$SCRATCH" && lake new mathspike math )
  echo "--- lean-toolchain the template pinned (elan auto-downloads it): ---"
  cat "$PROJ/lean-toolchain" || true
  echo
  echo "== fetch prebuilt Mathlib cache (the big download; needs network) =="
  ( cd "$PROJ" && lake exe cache get ) 2>&1 | tail -8
else
  echo "== reusing existing mathlib-spike project (cache already present) =="
fi
echo

# The proof file: overwrite the library root with our reuse demonstrations.
ROOT="$PROJ/Mathspike.lean"
cat > "$ROOT" <<'LEAN'
import Mathlib

namespace GacalcSpike

-- (1) REUSE A MATHLIB TACTIC. The 2D Lagrange identity in coordinates
--     (‖a‖²‖b‖² = (a·b)² + ‖a∧b‖², with a∧b = a1*b2 - a2*b1 in 2D) is proved
--     instantly by Mathlib's `ring` tactic. This is gacalc's first real target.
theorem lagrange_2d (a1 a2 b1 b2 : ℝ) :
    (a1 ^ 2 + a2 ^ 2) * (b1 ^ 2 + b2 ^ 2)
      = (a1 * b1 + a2 * b2) ^ 2 + (a1 * b2 - a2 * b1) ^ 2 := by
  ring

-- (2) REUSE A NAMED MATHLIB THEOREM about the dot product in ARBITRARY dimension.
--     `EuclideanSpace ℝ (Fin n)` is n-dimensional Euclidean space; the dot product
--     is `@inner ℝ …` (a DEFINITION, not an axiom); `real_inner_comm` PROVES its
--     symmetry. We cite it by name.
--     (real_inner_comm x y : ⟪y, x⟫ = ⟪x, y⟫, so we take .symm for x-then-y.)
theorem dot_symm {n : ℕ} (x y : EuclideanSpace ℝ (Fin n)) :
    @inner ℝ _ _ x y = @inner ℝ _ _ y x :=
  (real_inner_comm x y).symm

end GacalcSpike
LEAN

echo "== build the proof file against Mathlib =="
( cd "$PROJ" && lake build ); build_status=$?   # real exit code, not a pipe's
echo "lake build exit=$build_status (0 == our proofs + Mathlib all check)"
echo

if [ "$build_status" -eq 0 ]; then
  echo "== #print axioms: prove these rest only on standard axioms (not sorryAx) =="
  cat > "$PROJ/Axioms.lean" <<'LEAN'
import Mathspike
#print axioms GacalcSpike.lagrange_2d
#print axioms GacalcSpike.dot_symm
#print axioms real_inner_comm
LEAN
  ( cd "$PROJ" && lake env lean Axioms.lean )
fi

echo
echo "== spike phase 2 complete =="
