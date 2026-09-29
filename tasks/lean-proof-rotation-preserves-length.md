# Lean proof — a rotation preserves length (2D and 3D)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** `proofs/GacalcProofs/G2.lean` (+ its `sandwich_versor`), `proofs/GacalcProofs/G3.lean`,
`proofs/GacalcProofs/Rotation3D.lean` (the versor-from-vectors construction). Best done after the
3D versor sandwich lands (see `tasks/lean-proof-rotation-from-scratch.md`).

**Status:** proposed — needs go-ahead (filed 2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 6

## BLUF

Prove that a rotation **does not change the length** of the vector it rotates, in **𝒢₂ and 𝒢₃** —
the isometry property, the geometric heart of "it's a rotation." Stated on the versor sandwich:
`|R v R⁻¹| = |v|` (equivalently `dot (R v R⁻¹) (R v R⁻¹) = dot v v`). Because the sandwich uses the
scale-invariant *inverse* `R⁻¹` (not the reverse), it holds for an **un-normalized** versor. "Done" =
length-preservation proved for the 2D and 3D sandwiches, `make lean` green.

## Context — read first

- **2D already has a piece:** `Rotation.lean`'s `rot_normSq` proves the *coordinate* rotation `rot θ`
  on `ℝ × ℝ` preserves magnitude. This task wants the **GA / versor-sandwich** statement, `|R v R⁻¹|
  = |v|`, which is the form that generalizes to 3D and to the from-vectors versor.
- Needs `R⁻¹` in the algebra: `R⁻¹ = R̃ / |R|²` (even elements of `G2`/`G3` have a closed-form
  inverse); and `mag`/`dot` (in `G3.lean`, and their `G2` analogues). The identity is polynomial once
  the `1/|R|²` is cleared, so expect `field_simp` (needs `|R|² ≠ 0`) then `ext <;> ring`.
- Ties to the algebra-laws task (`tasks/lean-proof-algebra-laws-g2-g3.md`): the proof leans on
  associativity and `reverse` being an anti-automorphism.

## Plan

- [ ] **2D:** define `sandwich R v = R v R⁻¹` in `G2` (or reuse the from-vectors versor), prove
      `dot (sandwich R v) (sandwich R v) = dot v v` for an invertible versor `R` (`|R|² ≠ 0`).
- [ ] **3D:** the same for `G3`, on the `Rotation3D` versor / the plane-`a∧b` sandwich.
- [ ] Relate to the unit case (`R⁻¹ = R̃`, then `|R v R̃| = |v|`) and to `rot_normSq` (2D).
- [ ] `make lean` green; `proofs/README.md` updated.

## Open questions

1. Prove length-preservation for a **general** invertible versor `R`, or specifically for the
    `versor_from_vectors` `R` (the case we actually rotate with)? (Recommend the general even-versor
    statement — it is the real theorem and the from-vectors case is an instance.)
2. Magnitude-squared (`dot v v`) form to avoid `√`, or the `mag` (with `√`) form? (Recommend the
    squared form; `√` monotonicity gives the `mag` version as a trivial corollary.)
