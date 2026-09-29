# Lean proof — pseudoscalar square sign Iᵣ² = (−1)^(r(r−1)/2)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** the `proofs/` scaffold (done); the 3D case reuses the `G3` representation from the
dot/wedge step-tasks.
**Next:** `tasks/investigate-lean-proofs-for-ga.md` (projection is DONE + archived 2026-09-29)

**Status:** in-progress — 2D landed; 3D + general remain
**Priority:** 7
**Difficulty:** 6

## BLUF

The author's own Lean proof that the **unit pseudoscalar squares to `(−1)^(r(r−1)/2)`** (decision Q5:
the `Iᵣ²` form, not `Iᵣ·reverse`), for **2D, 3D, then the general case**. Each special case proved
directly, plus the general statement, plus a reference to the on-paper proof already in
`tasks/reference/pseudoscalar-square-sign.md`. "Done" = 2D + 3D + general with `make lean` green.

## Context — read first

- Read `tasks/reference/pseudoscalar-square-sign.md` (the hand proof: swap-counting for grades 1–5,
  then induction; a `reverse`-based one-liner) and `tasks/reference/lean-for-gacalc.md`.
- **2D already landed** (`proofs/GacalcProofs/G2.lean`): `I_sq` (I² = −1) and `I_sq_eq_sign`
  (I² = (−1)^(2·(2−1)/2) = −1), from the hand-written 𝒢₂ table.
- **3D**: needs `I₃ = e₁e₂e₃` in a `G3` representation; `I₃² = (−1)^(3·2/2) = (−1)³ = −1`.
- **General**: the clean route is the swap-count / induction from the reference doc, likely over a
  Clifford-algebra or an indexed basis-blade model; Mathlib's `CliffordAlgebra` is the reference for
  the general statement (learn from it, keep the proof standalone).

## Plan

- [x] 2D: `I_sq`, `I_sq_eq_sign`.
- [ ] 3D: build `I₃` in `G3`; prove `I₃² = (−1)^(3·(3−1)/2)`.
- [ ] General: prove `Iᵣ² = (−1)^(r(r−1)/2)` (swap-count/induction per the reference doc).
- [ ] Reference Mathlib's CliffordAlgebra pseudoscalar facts; `make lean` green.

## Open questions

1. General-case model: indexed basis-blade list vs Mathlib `CliffordAlgebra`? (Pick when starting the
   general case; 2D/3D don't need it.)
