# Lean proof: reverse is an anti-automorphism — reverse(A B) = reverse(B) reverse(A)

**Created:** 2026-09-30 · **Completed:** 2026-09-30 (William Emerison Six <billsix@gmail.com>; work
squashed into `3f6e933`)

## Goal

Prove in Lean that reversal reverses the order of a product, `reverse(A * B) = reverse(B) * reverse(A)`,
and the named vector corollaries the maintainer asked for (item 3 of the maintainer's request list):
`reverse(a * b) = b * a` (2D) and `reverse(a * b * c) = c * b * a` (3D). The general 𝒢₃ law
`GacalcProofs.G3.reverse_mul` already existed in `Sandwich.lean` (`by simp only [reverse, mul]; ext <;>
ring`, used only by `inverse_mul`, added incidentally for `sandwich_comp`); missing were the 𝒢₂ version,
a 𝒢₂ `reverse_vec`, and the named corollaries. It mirrors Python's `reverse` in `src/gacalc/base.py`.

## Decisions (resolved as recommended)

1. **Corollaries take `IsVector` hypotheses** on the flat struct (the 𝒢₃ idiom), not
   `vec`-constructed inputs — more general and matching `reverse_vec`.
2. **`(ab)~ = ba` in both 2D and 3D; the three-vector chain `(abc)~ = cba` in 3D only**, as asked.

## What was proved

- **𝒢₂** (`proofs/GacalcProofs/G2.lean`): `reverse_mul` (the anti-automorphism), `reverse_vec`,
  `reverse_of_isVector`, `reverse_mul_vec` (`(ab)~ = ba`).
- **𝒢₃** (`proofs/GacalcProofs/Sandwich.lean`): `reverse_of_isVector`, `reverse_mul_vec` (`(ab)~ = ba`),
  `reverse_mul3_vec` (`(abc)~ = cba`, via `reverse_mul` twice + `mul_assoc`).

The inventory in `tasks/reference/lean-ga-proof-architecture.md` was updated. A show-mult-style proof
notebook for this was left to `tasks/investigate-lean-to-python-proof-notebooks.md`. Distinct from
`tasks/lean-general-multivector-inverse.md`, which only uses `reverse_mul`.

## Verification

`proofs/check.sh` (`make lean`): build completed successfully, no `sorry` / `admit`.
