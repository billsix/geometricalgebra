# Lean proof — dot product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md` (for the from-rotation derivation)
**Next:** `tasks/lean-proof-wedge-product.md`

**Status:** in-progress — 2D landed in coordinates; from-rotation derivation + 3D remain
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
- **3D not started**: needs a `G3` structure (8-component 𝒢₃) or reuse of the rotation task's
  representation, then the same three deliverables. The phase-2 spike verified `real_inner_comm`
  (arbitrary-dimension dot symmetry) is a *proved* Mathlib theorem to reference.

## Plan

- [x] 2D dot = symmetric part, in coordinates (`G2.dot_is_sym_part`).
- [x] 2D equivalence to the general Euclidean dot (`G2.dot_eq_coord_sum`).
- [ ] 2D dot derived from the rotation-defined geometric product (needs the rotation step-task).
- [ ] 3D: build `G3`, prove dot = symmetric part + equivalence to `∑ uᵢvᵢ` / `@inner`.
- [ ] Reference the general Mathlib proofs in comments; `make lean` green.

## Open questions

None blocking; the representation choice is inherited from the rotation step-task.
