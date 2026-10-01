# Lean proof — `normalize`

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-01 — `proofs/GacalcProofs/Normalize.lean`: `normalizeVec` (= `(1/|v|)·v`), `normSq_normalizeVec` (= 1) and `magnitude_normalizeVec` (= 1) for `normSq v ≠ 0`, 𝒢₃ vectors. `make lean` green, sorry-free.
**Priority:** 4
**Difficulty:** 2

## BLUF

Prove that gacalc's `normalize` (`base.py:645`) returns a unit-magnitude element — `normalize A =
A / |A|` with `|normalize A| = 1` for `|A| ≠ 0`. No Lean theorem covers it yet. "Done" = the
unit-magnitude theorem (vector case at least, 2D + 3D), `make lean` green.

## Approach

**Cheap.** `normalize A = (1/|A|)·A` (a `smul`), so `normSq (normalize A) = (1/|A|)²·normSq A = 1`
by `normSq_smul` (already proved in `Sandwich.lean`) and `|A|² = normSq A` (`magnitude_sq_vec`).
Phrase nondegeneracy as `normSq (vec …) ≠ 0` per the versor-hypothesis convention, and keep the
proof squared (avoid `√`) — state `normSq (normalize A) = 1`, then lift to `magnitude = 1` via the
existing magnitude bridge. Mostly a definition + one `rw` chain on existing leaves.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
