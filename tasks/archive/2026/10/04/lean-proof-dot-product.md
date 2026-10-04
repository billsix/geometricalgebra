# Lean proof — dot product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella).
**Status:** DONE 2026-10-04, archived 2026-10-04 (`make lean` green). **Priority:** 7. **Difficulty:** 5.
**Durable record:** `tasks/reference/lean-ga-proof-architecture.md` (inventory: `G2.lean`, `G3.lean`,
`MathlibBridge.lean`; coverage map row `dot`; "Program decisions").

## BLUF

The dot product was proved to be the symmetric part of the geometric product in 2D and 3D, derived via
the book's rotation methods, and bridged to the general case: the from-scratch `dot` equals Mathlib's
`inner` on `EuclideanSpace ℝ (Fin n)`, so Mathlib's theorems about the inner product (symmetry,
Cauchy–Schwarz) provably apply to it.

## What was done

- 2D (2026-09-28, `G2.lean`): `dot_is_sym_part` (the scalar part of `½(ab + ba)` is `a₁b₁ + a₂b₂`) and
  `dot_eq_coord_sum` (the coordinate form of the general Euclidean dot).
- 3D (2026-09-29/30, `G3.lean`): `dot_vec` (coordinate form), `dot_comm`, full bilinearity,
  `vec_mul_eq_dot_add_wedge` (`ab = a·b + a∧b`); and on 2026-10-04 the object-form corollary
  `dot_is_sym_part` (`½(ab + ba) = (a·b)·1` for vectors).
- Derived from rotation (discharged 2026-10-04 by the maintainer's decision): `Rotation2D.uvec_mul_uvec`
  (the product of two unit vectors is the rotor of the angle between them) with `uvec_dot` (= cos) is
  the book's derivation; no construction of the product itself from rotation was wanted.
- The bridge (2026-10-04, `MathlibBridge.lean`): `G2.toE`/`G3.toE` map a vector's coordinates into
  `EuclideanSpace ℝ (Fin 2)`/`(Fin 3)` (`WithLp.toLp 2 ![…]`); `dot_eq_inner` (`dot a b = inner (toE a)
  (toE b)`, via `EuclideanSpace.inner_toLp_toLp`), `norm_toE` (`‖toE a‖ = magnitude a`, via
  `EuclideanSpace.norm_eq`); then, by citing Mathlib through the bridge, `dot_comm_of_inner`
  (`real_inner_comm`) and `abs_dot_le_magnitude_mul` — Cauchy–Schwarz `|a·b| ≤ |a||b|` on 𝒢₂ and 𝒢₃
  vectors (`abs_real_inner_le_norm`).

## Decisions

- "Equivalence to the general case" for the dot = the `EuclideanSpace`/`inner` bridge (maintainer,
  2026-10-04: "that sounds perfect"), not merely the coordinate sum.
- The bridge is a separate module; the constructions stay standalone (decision 2026-09-28).
