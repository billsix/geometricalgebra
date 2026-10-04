# Lean proof — pseudoscalar square sign Iᵣ² = (−1)^(r(r−1)/2)

**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`.
**Status:** DONE for n = 1, 2, 3 on 2026-10-04, archived 2026-10-04; the general-n statement lives in
`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` (deferred). **Priority:** 7. **Difficulty:** 6.
**Durable record:** `tasks/reference/pseudoscalar-square-sign.md` (the hand proof),
`tasks/reference/lean-ga-proof-architecture.md` (coverage row `pseudoscalar_squared_sign`).

## BLUF

Decision Q5 of the umbrella fixed the statement as `Iᵣ² = (−1)^(r(r−1)/2)`. It is proved against each
from-scratch algebra's own `I²`: `G1.I_sq_eq_sign` (`+1`, r = 1), `G2.I_sq_eq_sign` (`−1`, r = 2),
`G3.I_sq_eq_sign` (`−1`, r = 3), each reading the sign off the algebra's `I_sq`. The general n was
pushed to the Gn task on 2026-10-04 (maintainer: "we can just do it for 1, 2, and 3 dimensions … and if
we can write it for a general n case, great, or push that to the task involving the general n case").

## What the Python already established (recorded for the general-n task)

`base.pseudoscalar_squared_sign(r)` is the closed form; it replaced (commits `45dcdc9` → `3a98012`) a
body that squared the unit pseudoscalar through the general-n `Gn` oracle, kept as a comment "so it
reads as a proof for a student". `tests/test_pseudoscalar_square_sign.py` gates the closed form equal
to the slow `Gn` squaring for a range of `r` plus the expected ±1 pattern, and `tests/test_conformance.py`
checks every generated algebra's `unit_pseudoscalar_squared` against `Gn`'s. So Python has a *computed*
general-n check; the *written* general proof is the reference doc's swap count / induction. The Lean
general-n version needs the dimension-general blade model, which is the Gn task's representation question.

## Decisions

- Statement form `Iᵣ²` only (not `Iᵣ·reverse(Iᵣ)`), decision Q5, 2026-09-27.
- n ≤ 3 here, general n in the Gn task (2026-10-04).
