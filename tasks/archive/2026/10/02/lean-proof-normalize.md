# Lean proof — `normalize`

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-01. **Priority:** 4 **Difficulty:** 2

## Summary

gacalc's `normalize` (`base.py:645`) had no Lean theorem. `proofs/GacalcProofs/Normalize.lean` (𝒢₃
vectors) defined `normalizeVec = (1/|v|)·v` and proved it has unit magnitude —
`normSq_normalizeVec = 1` and `magnitude_normalizeVec = 1` for `normSq v ≠ 0` — via `normSq_smul`
(Sandwich) and `magnitude_sq_vec`, kept squared to avoid `√`. A definition plus one `rw` chain on
existing leaves. `make lean` green, sorry-free.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
