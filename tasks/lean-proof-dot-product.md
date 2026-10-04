# Lean proof — dot product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md` (for the from-rotation derivation)
**Next:** `tasks/lean-proof-wedge-product.md`

**Status:** in progress — the 2D and 3D coordinate forms are done; what remains is the **Mathlib bridge**
(decided 2026-10-04, William Emerison Six <billsix@gmail.com>: "map your G2 into Mathlib's EuclideanSpace
and show dot equals Mathlib's inner, so that Mathlib's library of theorems about inner (Cauchy–Schwarz,
symmetry) provably applies to yours — that sounds perfect") and the two-line 3D symmetric-part corollary.
**Priority:** 7
**Difficulty:** 5

## BLUF

The author's own Lean proof that the **dot product is the symmetric part of the geometric product**,
in **2D and 3D**, derived via the book's rotation methods — a **special case** each, **plus** a proof
that it is **equivalent to the general case** (the Euclidean coordinate sum / Mathlib's `@inner ℝ
(EuclideanSpace ℝ (Fin n))`), **plus** a reference to the existing general proof (`real_inner_comm`,
`inner_mul_le_norm_mul_norm`). "Done" = 2D and 3D both proved from the rotation-derived geometric
product with `make lean` green, each with its equivalence-to-general lemma.

## Context — read first

- Read `tasks/reference/lean-for-gacalc.md` and this task's umbrella.
- **2D already landed** (`proofs/GacalcProofs/G2.lean`): `dot_is_sym_part` (dot = scalar part of
  ½(uv+vu)) and `dot_eq_coord_sum` (equivalence: dot = u₁v₁+u₂v₂ = the general Euclidean dot). What
  remains for 2D is deriving it *from rotation* rather than from the hand-written `G2.mul` table —
  which is `tasks/lean-proof-rotation-from-scratch.md`'s job.
- **3D coordinate form done** (`G3.lean`, 2026-09-29/30): `dot_vec` (`dot (vec a) (vec b) = a₁b₁+a₂b₂+a₃b₃`),
  `dot_comm`, full bilinearity, and `vec_mul_eq_dot_add_wedge` (`ab = a·b + a∧b`). The named corollary
  "dot is the symmetric part" in 3D (`½(ab+ba)` has scalar part `a·b`) is not written yet; it follows from
  `vec_mul_eq_dot_add_wedge` + `wedge_antisymm` + `dot_comm`.
- **The from-rotation half is discharged** (maintainer, 2026-10-04): `Rotation2D.uvec_mul_uvec` (the product
  of two unit vectors is the rotor of the angle between them) with `uvec_dot` (= cos) is the book's
  derivation of the dot from rotation; no separate construction of the product from rotation is wanted.
- **The bridge to do.** Define `toE : G2 → EuclideanSpace ℝ (Fin 2)` (`![a.c1, a.c2]`, vectors only;
  likewise `G3 → EuclideanSpace ℝ (Fin 3)`) and prove `dot a b = ⟪toE a, toE b⟫_ℝ` for vectors (via
  `EuclideanSpace.inner_eq_star_dotProduct` / `PiLp.inner_apply`, then `Fin.sum_univ_two`/`_three` and
  `dot_vec`). Then *use* it: restate `real_inner_comm` and Cauchy–Schwarz (`abs_real_inner_le_norm`) on
  `G2`/`G3` through the map, so Mathlib's theorems demonstrably apply to the from-scratch dot. Also show
  `‖toE a‖ = magnitude a` (`EuclideanSpace.norm_eq` + `normSq_vec`) so the Cauchy–Schwarz statement reads
  in the corpus's own vocabulary. New file: `MathlibBridge.lean` (shared with the wedge and rotation bridges).

## Plan

- [x] 2D dot = symmetric part, in coordinates (`G2.dot_is_sym_part`).
- [x] 2D equivalence to the general Euclidean dot (`G2.dot_eq_coord_sum`).
- [x] 2D dot derived from rotation — discharged by `Rotation2D.uvec_mul_uvec`/`uvec_dot` (decision 2026-10-04).
- [x] 3D coordinate form (`G3.dot_vec`), bilinearity, `vec_mul_eq_dot_add_wedge`.
- [ ] 3D `dot_is_sym_part` corollary (two lines from the fundamental identity).
- [ ] `toE` into `EuclideanSpace ℝ (Fin 2)`/`(Fin 3)`; `dot_eq_inner`; `norm_toE = magnitude`.
- [ ] Cauchy–Schwarz and symmetry restated on `G2`/`G3` through the bridge, citing `abs_real_inner_le_norm`
      and `real_inner_comm`; `make lean` green; coverage/inventory rows in the architecture doc.

## Open questions

None blocking; the representation choice is inherited from the rotation step-task.
