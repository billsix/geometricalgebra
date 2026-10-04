# Lean proof — wedge product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`.
**Status:** DONE 2026-10-04, archived 2026-10-04 (`make lean` green). **Priority:** 7. **Difficulty:** 5.
**Durable record:** `tasks/reference/lean-ga-proof-architecture.md` (inventory; coverage rows `wedge`,
`vectorcalc.cross`, `measure.signed_volume`).

## BLUF

The wedge product was proved to be the antisymmetric part of the geometric product in 2D and 3D, and
bridged to Mathlib: the 2D wedge is the `2×2` determinant, the 3D wedge's components are the three
minors, the dual of the 3D wedge is Mathlib's `crossProduct`, and the signed volume is `Matrix.det` of
the three coordinate rows.

## What was done

- 2D (2026-09-28, `G2.lean`): `wedge_is_antisym_part` (the `e₁₂` part of `½(ab − ba)` is `a₁b₂ − a₂b₁`)
  and `vec_mul` (`uv = dot + wedge·e₁₂`).
- 3D (2026-09-29/30, `G3.lean`, `Cross.lean`): `wedge_vec_eq_biv` (the three minors), `wedge_antisymm`,
  `cross_vec`, `dot_cross_eq_signedVolume`, `normSq_wedge_eq_lagrange`; on 2026-10-04 the object-form
  corollary `wedge_is_antisym_part` (`½(ab − ba) = a∧b` for vectors).
- Derived from rotation: discharged by `Rotation2D.uvec_wedge` (= sin of the angle), decision 2026-10-04.
- The bridge (2026-10-04, `MathlibBridge.lean`): `G2.wedge_eq_det` (`(a∧b).c12 = det !![a₁, a₂; b₁, b₂]`
  via `Matrix.det_fin_two_of`); `G3.wedge_c12_eq_det`/`_c13_`/`_c23_` (the minors); `G3.toF` (coordinates as
  `Fin 3 → ℝ`) with `toF_cross` (`toF (cross a b) = toF a ⨯₃ toF b`, Mathlib's `crossProduct`) and
  `signedVolume_eq_det` (`signedVolume a b c = det ![toF a, toF b, toF c]`, through Mathlib's
  `triple_product_eq_det`). Mathlib's `cross_anticomm`, `dot_self_cross`, `dot_cross_self` therefore
  apply to the from-scratch cross product through `toF_cross`.

## Decisions

- "Equivalence to the general case" for the wedge = determinant / cross product in Mathlib
  (maintainer, 2026-10-04: "show that it maps to the determinant, through anything in mathlib").
