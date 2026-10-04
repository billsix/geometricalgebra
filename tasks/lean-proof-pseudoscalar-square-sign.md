# Lean proof — pseudoscalar square sign Iᵣ² = (−1)^(r(r−1)/2)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** the `proofs/` scaffold (done); the 3D case reuses the `G3` representation from the
dot/wedge step-tasks.
**Next:** `tasks/investigate-lean-proofs-for-ga.md` (projection is DONE + archived 2026-09-29)

**Status:** in progress — scope settled 2026-10-04 (William Emerison Six <billsix@gmail.com>): prove the
formula for **n = 1, 2, 3** against the actual `I²` of each from-scratch algebra ("we can just do it for 1,
2, and 3 dimensions, and that it's equal to the I² for those"); the **general-n** statement is pushed to
`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`, which records what the Python already
established (below). 2D and 1D are done; 3D is one lemma.
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
- **1D done** (`G1.lean`, 2026-10-04): `I_sq : I² = +1` and `I_sq_eq_sign` (`(−1)^(1·0/2) = 1`).
- **3D**: `G3.I_sq` (`I₃² = −1`) exists; the `I_sq_eq_sign` phrasing `(mul I I).s = (−1)^(3·2/2)` is one line.
- **General n — pushed to the Gn task.** What the Python already established, for that task to build
  on: `base.pseudoscalar_squared_sign(r)` is the closed form `(−1)^(r(r−1)/2)`; it REPLACED (commit
  `3a98012`, after `45dcdc9` had the unoptimized form) a body that literally squared the unit pseudoscalar
  through the general-n `Gn` oracle (`int(Gn.unit_pseudoscalar_squared(r).scalar_part())`, kept as a
  comment in the source "so it reads as a proof for a student"). The two are gated equal forever by
  `tests/test_pseudoscalar_square_sign.py` (closed form vs the slow `Gn` squaring, for a range of `r`, plus
  the expected ±1 pattern), and `tests/test_conformance.py` checks every generated algebra's
  `unit_pseudoscalar_squared` against `Gn`'s. The hand proof (swap counting for r = 1..5, induction, and the
  reverse-based one-liner) is `tasks/reference/pseudoscalar-square-sign.md`. So the Python side has a
  *computed* general-n check (the `Gn` oracle) and a *written* general proof; the Lean general-n version
  needs the dimension-general blade model, which is exactly that task's open representation question.

## Plan

- [x] 2D: `I_sq`, `I_sq_eq_sign`.
- [x] 1D: `G1.I_sq`, `G1.I_sq_eq_sign` (2026-10-04).
- [ ] 3D: `G3.I_sq_eq_sign` (`(mul I I).s = (−1)^(3·(3−1)/2)`, from the existing `I_sq`).
- [ ] Record the three cases in the architecture doc; `make lean` green; then archive — the general case
      lives in the Gn task.

## Open questions

None here — the general-case model question moved with the general case to
`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`.
