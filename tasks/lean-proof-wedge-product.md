# Lean proof — wedge product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md`
**Next:** `tasks/lean-proof-pseudoscalar-square-sign.md`

**Status:** in progress — 2D and 3D coordinate forms done; what remains is the **bridge to Mathlib's
determinant / cross product** (decided 2026-10-04, William Emerison Six <billsix@gmail.com>: "show that it
maps to the determinant, through anything in mathlib, if possible") and the 3D antisymmetric-part corollary.
**Priority:** 7
**Difficulty:** 5

## BLUF

The author's own Lean proof that the **wedge product is the antisymmetric part of the geometric
product**, in **2D and 3D**, derived via the book's rotation methods — a **special case** each,
**plus** a proof of **equivalence to the general case** (the coordinate minors / the general wedge),
**plus** a reference to the existing general proof. "Done" = 2D and 3D both proved with `make lean`
green, each with its equivalence-to-general lemma.

## Context — read first

- Read `tasks/reference/lean-for-gacalc.md` and the umbrella.
- **2D already landed** (`proofs/GacalcProofs/G2.lean`): `wedge_is_antisym_part` (wedge = e₁e₂ part of
  ½(uv−vu) = u₁v₂−u₂v₁) and `vec_mul` (uv = dot + wedge·e₁e₂). The minor u₁v₂−u₂v₁ is the general 2D
  wedge, so the equivalence is immediate; the remaining 2D work is deriving it *from rotation*.
- **3D coordinate form done** (`G3.lean`, `Cross.lean`): `wedge_vec_eq_biv` (the three minors), `wedge_antisymm`,
  `cross_vec`, `dot_cross_eq_signedVolume`, `normSq_wedge_eq_lagrange`. The named "wedge is the
  antisymmetric part" corollary in 3D is not written; it follows from `vec_mul_eq_dot_add_wedge` + `dot_comm`.
- **The from-rotation half is discharged** (maintainer, 2026-10-04): `Rotation2D.uvec_wedge` (= sin of the
  angle, from `uvec_mul_uvec`) is the book's derivation.
- **The bridge to do.** 2D: `(wedge (vec a) (vec b)).c12 = Matrix.det !![a₁, a₂; b₁, b₂]` via
  `Matrix.det_fin_two_of`. 3D: the wedge's three components are the three 2×2 minors of the `2×3` matrix
  `![a, b]` (state each as a `Matrix.det_fin_two_of`), and the dual of the wedge is Mathlib's cross product:
  `toE (dual (wedge a b)) = crossProduct (toE a) (toE b)` (`Mathlib.LinearAlgebra.CrossProduct`, notation
  `⨯₃`, dot `⬝ᵥ`), so Mathlib's `cross_anticomm`, `dot_self_cross`, `dot_cross_self` and `triple_product_eq_det`
  (the scalar triple product is `Matrix.det ![a, b, c]`) carry over — the last one also bridges
  `signedVolume` to a determinant. Same `MathlibBridge.lean` as the dot bridge.

## Plan

- [x] 2D wedge = antisymmetric part, in coordinates (`G2.wedge_is_antisym_part`).
- [x] 2D wedge derived from rotation — discharged by `Rotation2D.uvec_wedge` (decision 2026-10-04).
- [x] 3D coordinate form (`wedge_vec_eq_biv`, `cross_vec`, `dot_cross_eq_signedVolume`).
- [ ] 3D `wedge_is_antisym_part` corollary.
- [ ] 2D: `wedge_eq_det` (`Matrix.det_fin_two_of`); 3D: the three minors as determinants.
- [ ] 3D: `dual (wedge a b)` ↦ `crossProduct`; `signedVolume` ↦ `Matrix.det` via `triple_product_eq_det`;
      Mathlib's cross-product lemmas restated through the bridge; `make lean` green; architecture-doc rows.

## Open questions

None blocking; representation inherited from the rotation step-task.
