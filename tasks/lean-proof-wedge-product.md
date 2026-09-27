# Lean proof — wedge product (2D and 3D), from scratch + equivalence to general

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** `tasks/lean-proof-rotation-from-scratch.md`
**Next:** `tasks/lean-proof-pseudoscalar-square-sign.md`

**Status:** in-progress — 2D landed in coordinates; from-rotation derivation + 3D remain
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
- **3D not started**: the wedge is a bivector with three components (the three 2×2 minors); needs the
  `G3` representation. Note `‖a∧b‖²` in 3D = the sum of squared minors, already proved as
  `GacalcProofs.lagrange_3d` — a useful cross-check.

## Plan

- [x] 2D wedge = antisymmetric part, in coordinates (`G2.wedge_is_antisym_part`).
- [ ] 2D wedge derived from the rotation-defined geometric product (rotation step-task).
- [ ] 3D: `G3` bivector; wedge = antisymmetric part (three components) + equivalence to the minors.
- [ ] Reference the general result; `make lean` green.

## Open questions

None blocking; representation inherited from the rotation step-task.
