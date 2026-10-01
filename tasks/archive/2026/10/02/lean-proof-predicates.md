# Lean proof — orthogonality / parallelism predicates (`is_orthogonal_to`, `is_parallel_to`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-01 — `proofs/GacalcProofs/Predicates.lean`: `perp_iff_mul_eq_wedge` (`a·b=0 ⟺ ab=a∧b`, both directions) and `wedge_parallel_smul` (`a∧(k·a)=0`). `make lean` green, sorry-free. **Reported discrepancy:** Python `is_parallel_to` uses `cosine==1` (same-direction only), narrower than the geometric wedge-zero parallel (which includes anti-parallel) — CLAUDE.md known-issue #2; the Lean wedge-zero form is the correct one.
**Priority:** 5
**Difficulty:** 3

## BLUF

Prove the defining characterisations of gacalc's two geometric predicates —
`is_orthogonal_to` (`base.py:1064`) and `is_parallel_to` (`base.py:1100`). Perpendicularity
currently appears in Lean only as a *hypothesis* (`vec_mul_perp`, `mul_eq_wedge_of_perp`,
`reject_perp`, `dual_wedge_perp_*`), never as the predicate itself; parallelism not at all. "Done" =
theorems tying each predicate to its geometric meaning, `make lean` green.

## Approach

`is_orthogonal_to` tests `inner_product == 0`; prove the equivalences already latent in the leaves —
`a ⊥ b ⟺ dot a b = 0 ⟺ a b = a∧b` (`mul_eq_wedge_of_perp`) ⟺ the rejection is the whole vector.
`is_parallel_to` tests the wedge vanishing (`a ∧ b = 0`); prove `a ∥ b ⟺ wedge a b = 0 ⟺ b` is a
scalar multiple of `a` (for the vector case), using `wedge_self_vec`/`wedge_antisymm` and
`normSq_wedge_vec`. **Note:** the Python `is_parallel_to` carries a self-flagged "not sure if I'm
doing this correctly" comment (CLAUDE.md known-issue #2) — the Lean proof should settle the correct
characterisation; if the code is wrong, report it rather than proving the code's version.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
