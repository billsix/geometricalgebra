# Lean proof — reflection (`reflect` / `reflected_across`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02. **Priority:** 3 **Difficulty:** 2

## Summary

gacalc's `reflect(across=b)` (`base.py:1463`/`1555`) had no Lean theorem. `proofs/GacalcProofs/Reflect.lean`
(𝒢₃ vectors) defined `reflectVec` (= project − reject) and proved `reflectVec_eq`
(`reflect_d v = 2·proj_d v − v`) via the existing `reject_vec_eq` — structural, reusing the
`proj`/`reject`/`project_add_reject` leaves rather than a coordinate bash. The isometry
`normSq_reflectVec` (`|reflect_d v|² = |v|²`, reflection preserves length, for `d·d ≠ 0`) followed from
the `2·proj − v` coordinate form rewritten through `dot_self_vec_eq_normSq`/`normSq_vec`, then
`field_simp`/`ring`. `make lean` green, sorry-free.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
