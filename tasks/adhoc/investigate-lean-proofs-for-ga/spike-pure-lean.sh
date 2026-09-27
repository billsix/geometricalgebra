#!/usr/bin/env bash
# Lean 4 learning spike — PHASE 1 (pure Lean, no Mathlib).
#
# Purpose (task: tasks/investigate-lean-proofs-for-ga.md): prove one trivial lemma
# end-to-end so we can SEE (a) how a proof is written and checked, and (b) how an
# INCOMPLETE proof is detected — the mechanism the `make lean` CI gate will use to
# turn a broken proof red. No Mathlib here (that is phase 2); this must run in
# seconds and needs only `lean`/`lake` from the image's USE_LEAN toolchain.
#
# Run it (author's preferred method):
#   make shell-exec SCRIPT=tasks/adhoc/investigate-lean-proofs-for-ga/spike-pure-lean.sh
#
# Throwaway: everything is built under a container-ephemeral temp dir, so it leaves
# NO artifacts in the repo. Idempotent (fresh temp dir each run).
set -u  # not -e: we WANT to observe non-zero exits from the broken-proof step

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

echo "== lean/lake versions =="
lean --version
lake --version
echo

echo "== 1. a COMPLETE proof: 1 + 1 = 2, and a tiny GA-flavoured lemma =="
cat > Spike.lean <<'LEAN'
-- A trivial arithmetic fact, proved by `rfl` (both sides reduce to the same normal form).
theorem two : 1 + 1 = 2 := rfl

-- A slightly less trivial one, to show a real tactic proof.
-- (-1)^(even) = 1 : the shape of the pseudoscalar-square sign for r ≡ 0,1 (mod 4).
theorem neg_one_sq : (-1 : Int) ^ 2 = 1 := by decide

-- `#print axioms` reports which axioms a proof rests on. A COMPLETE proof rests
-- only on Lean's three standard axioms (propext, Classical.choice, Quot.sound) or
-- a subset — and crucially NOT on `sorryAx`.
#print axioms two
#print axioms neg_one_sq
LEAN
echo "--- lean Spike.lean (expect: axiom lines, exit 0) ---"
lean Spike.lean
echo "exit=$?"
echo

echo "== 2. an INCOMPLETE proof: how the gate catches a hole =="
cat > Broken.lean <<'LEAN'
-- `sorry` admits any goal WITHOUT proving it. Lean only WARNS about it.
theorem bogus : 1 + 1 = 3 := by sorry
#print axioms bogus
LEAN
echo "--- lean Broken.lean (note: sorry is only a WARNING; lean still exits 0) ---"
lean Broken.lean
echo "exit=$? (this is why a bare build is NOT a sufficient gate)"
echo

echo "== 3. the GATE mechanism: fail when any proof depends on sorryAx =="
# `#print axioms` on an incomplete proof lists `sorryAx`. Grep for it → fail.
if lean Broken.lean 2>&1 | grep -q "sorryAx"; then
  echo "GATE would FAIL: 'sorryAx' present -> the proof is incomplete (correct)."
else
  echo "GATE would pass (unexpected here)."
fi
# And the complete file must be clean:
if lean Spike.lean 2>&1 | grep -q "sorryAx"; then
  echo "GATE would FAIL on Spike.lean (unexpected)."
else
  echo "GATE would PASS on Spike.lean: no sorryAx -> proofs are genuine (correct)."
fi
echo

echo "== 4. a real lake LIBRARY project (the shape a proof project uses) =="
# GOTCHAS learned on the first spike run (2026-09-27, Lean 4.34.1 / Lake 5.0.0):
#   * `lake init <name>` defaults to an EXECUTABLE target, whose build ends in a
#     clang LINK step -> `clang: error: linker command failed` (and the lean image
#     has no full C toolchain). Proof code is a LIBRARY: `.olean` only, no linking.
#     So init a `lib`.
#   * `-DwarningAsError=true` is NOT a valid Lake 5.0.0 flag ("unknown short option
#     '-D'"). Warning-as-error would go in the lakefile's `leanOptions`; but we do
#     NOT rely on it — the `#print axioms` grep in step 3 is the reliable gate.
#   * NEVER pipe a build through `| tail` when you need its exit code: the pipe's
#     status is tail's (0), masking a real failure (the repo's "propagate every
#     step's failure" gate rule). Capture $? of the command itself.
mkdir proj && cd proj
lake init spike lib >/dev/null 2>&1
ROOT="$(ls *.lean 2>/dev/null | grep -iv lakefile | head -1)"
[ -z "$ROOT" ] && ROOT="Spike.lean"
cat > "$ROOT" <<'LEAN'
theorem two : 1 + 1 = 2 := rfl
LEAN
echo "--- lake build (clean library) ---"
lake build; build_status=$?    # capture the REAL exit code, not a pipe's
echo "clean lib build exit=$build_status (0 == success)"

echo
echo "== spike phase 1 complete =="
