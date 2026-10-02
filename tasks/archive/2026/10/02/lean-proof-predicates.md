# Lean proof — orthogonality / parallelism predicates (`is_orthogonal_to`, `is_parallel_to`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02. **Priority:** 5 **Difficulty:** 3

## Summary

gacalc's geometric predicates `is_orthogonal_to` (`base.py:1064`) and `is_parallel_to` (`base.py:1100`)
had no Lean theorem — perpendicularity appeared only as a hypothesis (`vec_mul_perp`,
`mul_eq_wedge_of_perp`, `reject_perp`, `dual_wedge_perp_*`), parallelism not at all.
`proofs/GacalcProofs/Predicates.lean` (𝒢₃ vectors) proved `perp_iff_mul_eq_wedge`
(`a·b = 0 ⟺ ab = a∧b`, both directions) and `wedge_parallel_smul` (`a∧(k·a) = 0`). `make lean` green,
sorry-free.

The work settled CLAUDE.md known-issue #2: the Python `is_parallel_to` had used `cosine == 1`
(same-direction only), which wrongly excluded **anti-parallel** vectors (cosine −1) that are
geometrically parallel. It was fixed to the correct wedge-zero criterion `a∧b = 0` — the form the Lean
pins — with a CHANGELOG entry and a new `test_is_parallel`.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
