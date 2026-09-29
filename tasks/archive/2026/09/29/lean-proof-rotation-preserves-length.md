# Lean proof — a rotation preserves length (2D and 3D)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Status:** DONE 2026-09-29 (William Emerison Six <billsix@gmail.com>)
**Priority:** 7 · **Difficulty:** 6

## BLUF

Proved that the versor sandwich `R v R⁻¹` **does not change length**, in 𝒢₂ and 𝒢₃ — the isometry
property. Landed in `proofs/GacalcProofs/Sandwich.lean`, `make lean` green.

## What landed

`proofs/GacalcProofs/Sandwich.lean` defines, for both `G2` and `G3`: `normSq` (`|R|² = ⟨R R̃⟩₀`),
`inverse` (`R⁻¹ = R̃/|R|²`), `sandwich` (`R v R⁻¹`), and an `evenVersor` constructor (the elements of
the even subalgebra — ≅ ℂ in 2D, ≅ the quaternions in 3D — whose nonzero elements are the rotations).
Then:

- `sandwich_preserves_normSq_vec` — for an even versor `R` with `|R|² ≠ 0`, `|R v R⁻¹|² = |v|²`.
  Proved for `G2` and `G3` as a corollary of `sandwich_preserves_dot` (below) with `u = v`.

Proof method: unfold + `field_simp [hr]` (clears the `1/|R|²`) + `ring`.

## Resolved

- **Open Q1 (general versor vs. `versor_from_vectors`):** proved for a **general even versor**
  (`evenVersor`) — the real theorem; the from-vectors versor is an instance.
- **Open Q2 (√ vs. squared):** used the **magnitude-squared** (`dot`) form throughout, so the proof is
  `√`-free; the `mag`-with-`√` version is a trivial `Real.sqrt` corollary if ever wanted.
- The earlier `Rotation.lean` `rot_normSq` (the coordinate `rot θ` preserves magnitude in 2D) is the
  angle-parameterized cousin; this is the GA/versor-sandwich form that also covers 3D.
