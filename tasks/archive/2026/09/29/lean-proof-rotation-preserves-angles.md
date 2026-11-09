# Lean proof — a rotation preserves angles (2D and 3D)

**Completed:** 2026-09-29 (William Emerison Six <billsix@gmail.com>)
**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)

Proved that the versor sandwich `R v R⁻¹` **preserves angles**, in 𝒢₂ and 𝒢₃, via the clean algebraic
core: the sandwich **preserves the dot product**, `(R u R⁻¹)·(R v R⁻¹) = u·v`. With
length-preservation (`tasks/archive/2026/09/29/lean-proof-rotation-preserves-length.md`) this gives angle-invariance directly,
since `cos(angle) = (u·v)/(|u||v|)` and numerator and denominators are all unchanged. Landed in
`proofs/GacalcProofs/Sandwich.lean`, `make lean` green.

## What was proved

`sandwich_preserves_dot` in `proofs/GacalcProofs/Sandwich.lean`, for both `G2` and `G3`: for an even
versor `R` with `|R|² ≠ 0`, `dot (sandwich R u) (sandwich R v) = dot u v`. Proof: unfold +
`field_simp [hr]` + `ring`. (The infrastructure — `normSq`/`inverse`/`sandwich`/`evenVersor` — is
shared with the length task.)

## Decisions

- **Stop at dot-preservation rather than an explicit `angle`:** stopped at **dot-product preservation**
  — the algebraic core, from which angle-invariance is immediate (`cos = u·v/(|u||v|)`, all three
  quantities preserved). No explicit `angle` was introduced.
- **A local `angle` vs. Mathlib's:** not needed given the above. If the literal
  `angle (R u R⁻¹) (R v R⁻¹) = angle u v` is ever wanted, define `angle a b := arccos(a·b/(|a||b|))`
  locally (self-contained) rather than mapping into Mathlib's `EuclideanSpace`. Mathlib's angle-scaling
  lemmas are noted in `Rotation3D.lean`'s references.
