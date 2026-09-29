# Lean proof — the algebra laws of 𝒢₂ and 𝒢₃ (associativity, distributivity, …)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Status:** DONE 2026-09-29 (William Emerison Six <billsix@gmail.com>)
**Priority:** 7 · **Difficulty:** 4

## BLUF

Proved that the from-scratch `G2` and `G3` are **associative, unital ℝ-algebras**. Landed in
`proofs/GacalcProofs/AlgebraLaws.lean`, `make lean` green.

## What landed

`proofs/GacalcProofs/AlgebraLaws.lean` proves, for **both** `G2` and `G3`, each by `ext <;> ring`
(including `G3`'s 8-field associativity — `ring` handled it without timing out):

- `mul_assoc` — the geometric product is associative.
- `mul_add` / `add_mul` — it distributes over addition on both sides.
- `one_mul` / `mul_one` — `one` is a two-sided identity.
- `smul_mul` / `mul_smul` — scalars pull through the product.
- `vec_anticomm_perp` — **orthogonal vectors anticommute** (`u·v = 0 ⟹ u v = −(v u)`); the `G3`
  version is a corollary of `vec_mul_perp` (`a b = a∧b`) + wedge antisymmetry, the `G2` version
  states orthogonality as `u₁v₁ + u₂v₂ = 0`.

The fundamental identity `a b = a·b + a∧b` for vectors (`vec_mul_eq_dot_add_wedge`) and its
`vec_mul_perp` corollary had already landed in `G3.lean` (they support the reduce-to-2D sandwich).

## Resolved

- **Open question (state over general values vs. literals):** stated over **general** `G2`/`G3`
  values for the ring axioms (`ext <;> ring` handles the full struct); the GA anticommutation is over
  `vec` literals (it is a statement about vectors).
- **Scope:** deliberately the ring axioms + basis anticommutation. `reverse` as an anti-automorphism
  and the grade/contraction relations belong to the dot/wedge/pseudoscalar step-tasks, not here.
