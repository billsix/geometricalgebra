# 2D `projRotation` parallel — mirror the 3D rotation-from-project/reject triple in 𝒢₂

**Status:** DONE 2026-10-02
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-02 **Updated:** 2026-10-02 (William Emerison Six <billsix@gmail.com>)

## BLUF

Added a named 𝒢₂ `projRotation` mirroring the 3D triple in `proofs/GacalcProofs/ProjectionRotation.lean`,
with the degenerate base case made explicit — in 𝒢₂ the `f∧t` plane is the whole space, so
`reject = 0` and the rotation collapses to the rotor action `v·f̂·t̂`. Pedagogical consolidation, not
new mathematics; `make lean` green/sorry-free. The durable record lives in
`tasks/reference/reduction-to-standard-position.md` ("2D specialization") and
`tasks/reference/lean-ga-proof-architecture.md` (inventory).

## Delivered

New file `proofs/GacalcProofs/Projection2DRotation.lean` (namespace `GacalcProofs.G2`), registered by
`import GacalcProofs.Projection2DRotation` in the root `proofs/GacalcProofs.lean`. Defines
`projRotation f t v = (project_{f∧t} v)·f̂·t̂ + reject_{f∧t} v` and proves:

- `projRotation_carries_from_to` — `projRotation f t f = (|f|/|t|)·t`.
- `projRotation_isometry` — `normSq (projRotation f t v) = normSq v` (needs only `normSq f, normSq t ≠ 0`
  — straight from `normSq_mul_three_vec` + unit `f̂`/`t̂`, independent of route-equivalence).
- `projRotation_eq_sandwich` — `projRotation f t v = sandwich (versorFromVectors f t) v` (route P = route V).
- `projRotation_eq_vec_mul` + `reject_plane_eq_zero` — the `reject = 0` degeneration and the collapse to
  the rotor action, making the 3D↔2D parallel explicit.

Reused `Versor2D`/`Sandwich`/`Projection2D`/`AlgebraLaws`/`Normalize` lemmas; added small supporting
lemmas in-namespace (`normalizeVec` + its `mul_vec_self`/`magnitude_*` helpers, `normSq_mul_three_vec`,
and for route-equivalence `versorFromVectors_mul_vec_eq`, `reverse_versorFromVectors_mul`,
`key_reverse_sq`, `fhat_that_eq_reverse_mul_inverse`). Same structural √-handling as 3D: the one
√-bearing identity stays confined to `key_reverse_sq` (`|f||t|·R̃² = |R|²·(f t)`) and never expands
per-coordinate.

## Note on implementation vs. the original plan

The original plan expected to cite `Rotation.lean`'s `rot_normSq` / `sandwich_versor_eq_vec_mul_rotor` /
`rotorFromTo_carry` directly. In practice the clean route was `Versor2D`/`Sandwich`/`Projection2D` plus a
few small in-namespace helpers mirroring the 3D proof's structure — same result, slightly different
lemma basis. No new mathematics; the 2D case stays the degenerate base case of the 3D construction.

## Cross-references

- `proofs/GacalcProofs/ProjectionRotation.lean` — the 3D triple this mirrors.
- `tasks/reference/reduction-to-standard-position.md` — the full arc + the "2D specialization" entry.
- `tasks/reference/lean-ga-proof-architecture.md` — the `Projection2DRotation.lean` inventory entry.
- `tasks/lean-proof-rotation-from-scratch.md` — the versor-sandwich route (route V); this showed route
  P = route V also holds in 2D.
