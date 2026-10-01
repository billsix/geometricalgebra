# Lean proof — reflection (`reflect` / `reflected_across`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** proposed — needs go-ahead
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
