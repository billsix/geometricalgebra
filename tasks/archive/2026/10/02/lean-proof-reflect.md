# Lean proof — reflection (`reflect` / `reflected_across`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-01 — `proofs/GacalcProofs/Reflect.lean`: `reflectVec` (= proj − reject) and `reflectVec_eq` (`reflect_d v = 2·proj_d v − v`, via `reject_vec_eq`), 𝒢₃ vectors. `make lean` green, sorry-free. **Isometry now proved too (2026-10-02):** `normSq_reflectVec` (`|reflect_d v|² = |v|²`, a reflection preserves length), via the `2·proj − v` coordinate form + `field_simp`/`ring`. Fully done.
**Priority:** 3
**Difficulty:** 2

## BLUF

Prove, from scratch in Lean, that gacalc's `reflect(across=b)` reflects a vector across the
line/blade `b` — the operation at `base.py:1463`/`1555` has no Lean theorem yet. "Done" = a theorem
(2D and 3D) characterising the reflection, `make lean` green.

## Approach

This is **cheap**: `reflect_b(a) = project_b(a) − reject_b(a)`, and both `project`/`reject` are
already proved (`proj`, `reject`, `project_add_reject` in `Projection.lean`/`Projection2D.lean`).
Define `reflect` from those and prove (a) `reflect_b(a) = 2·project_b(a) − a` (equivalently
`project − reject`), reusing `project_add_reject` (`project + reject = a`); and (b) reflection is an
isometry (`|reflect_b a| = |a|`), which follows from the projection/rejection being orthogonal
components plus `normSq_wedge_vec`/`reject_perp`. Keep it structural (`rw` on the existing leaves),
not a coordinate bash. Check the Python sign/orientation convention (`reflect` vs the vector-reflection
formula `b a b⁻¹`) and state the theorem to match it.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
