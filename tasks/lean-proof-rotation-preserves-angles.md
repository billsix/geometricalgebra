# Lean proof — a rotation preserves angles (2D and 3D)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** `tasks/lean-proof-rotation-preserves-length.md` (the companion isometry proof; the two
together give angle-preservation), `proofs/GacalcProofs/G2.lean`, `G3.lean`, `Rotation3D.lean`.

**Status:** proposed — needs go-ahead (filed 2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 6

## BLUF

Prove that a rotation **preserves angles** between vectors, in **𝒢₂ and 𝒢₃**. The clean algebraic
statement is that the versor sandwich preserves the **dot product**:
`dot (R u R⁻¹) (R v R⁻¹) = dot u v`. Combined with length-preservation
(`tasks/lean-proof-rotation-preserves-length.md`), this gives angle-preservation directly, since
`cos(angle) = (u·v)/(|u||v|)` and both numerator and denominators are unchanged. "Done" = dot-product
preservation proved for the 2D and 3D sandwiches (and, if we introduce an `angle`, the explicit
`angle (R u R⁻¹) (R v R⁻¹) = angle u v`), `make lean` green.

## Context — read first

- **Dot-preservation is the primitive; angle-preservation is the corollary.** Proving `u·v` is
  invariant under the sandwich is a polynomial identity (like the length proof, one step more with two
  distinct vectors). It, plus `|R u R⁻¹| = |u|` and `|R v R⁻¹| = |v|`, yields angle-preservation
  without any trig, via `cos(angle) = (u·v)/(|u||v|)`.
- **If we want the explicit `angle` statement**, define `angle a b := Real.arccos (dot a b / (mag a *
  mag b))` locally (or take the deferred route of mapping into `EuclideanSpace ℝ (Fin 3)` and using
  Mathlib's `InnerProductGeometry.angle`). Mathlib's angle-scaling lemmas
  (`Mathlib/Geometry/Euclidean/Angle/Unoriented/Basic.lean`: `angle_smul_*`, `angle_normalize_*`) are
  the relevant reference — the same ones noted for the bisector proof in `Rotation3D.lean`.
- Leans on the algebra laws (`tasks/lean-proof-algebra-laws-g2-g3.md`) and `reverse` as an
  anti-automorphism.

## Plan

- [ ] **2D:** `dot (R u R⁻¹) (R v R⁻¹) = dot u v` in `G2`, for an invertible versor `R`.
- [ ] **3D:** the same in `G3` (on the `Rotation3D` / plane-`a∧b` sandwich).
- [ ] **Angle corollary:** with length-preservation, conclude the angle (via `cos = u·v/(|u||v|)`) is
      unchanged — either as the ratio identity, or an explicit `angle` equality if we define `angle`.
- [ ] `make lean` green; `proofs/README.md` updated.

## Open questions

1. Stop at **dot-product preservation** (the algebraic core; angle-invariance is then immediate), or
    also introduce an explicit `angle` and state `angle (R u R⁻¹) (R v R⁻¹) = angle u v`? (Recommend
    landing dot-preservation first; add the explicit `angle` only if the maintainer wants the literal
    "angles preserved" statement machine-checked.)
2. Local `angle := arccos(u·v/(|u||v|))` vs. the deferred map into `EuclideanSpace ℝ (Fin 3)` for
    Mathlib's `angle`? (Recommend the local definition — self-contained, no equivalence bridge needed.)
