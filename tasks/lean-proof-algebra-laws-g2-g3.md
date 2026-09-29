# Lean proof — the algebra laws of 𝒢₂ and 𝒢₃ (associativity, distributivity, …)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** `proofs/GacalcProofs/G2.lean`, `proofs/GacalcProofs/G3.lean` (the from-scratch algebras;
their `mul`/`add`/`smul`/`one` and the multiplication tables are in place).

**Status:** proposed — needs go-ahead (filed 2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 4

## BLUF

Prove that the from-scratch `G2` and `G3` really are **associative, unital ℝ-algebras**: the geometric
product is **associative** and **distributes over addition** (both sides), `one` is a two-sided
identity, and scalars pull through the product. These are the axioms our transcribed-from-`Gn`
product must satisfy for everything built on it (the sandwich, projection, the rotation proofs) to
rest on solid ground. Each is a polynomial identity in the coordinate fields, so the expected proof
is `ext <;> ring` (a large but automatic expansion for `G3`'s 8 fields). "Done" = the laws below
proved for both `G2` and `G3`, `make lean` green.

## Context — read first

- `G2`/`G3` are coordinate structs with `@[ext]`; `mul`, `add`, `sub`, `smul`, `neg`, `one`, `zero`
  are defined; the multiplication tables (`e_1_sq`, anticommutation, `I_sq`) already confirm the
  transcription. What is *not* yet proved is that the product obeys the ring axioms in general.
- **The GA-specific relations are partly done.** `e_i_sq` (eᵢ²=1), `e_i_mul_e_j`/`e_2_mul_e_1`
  (distinct basis vectors anticommute) are in the tables; the general **anticommutation for
  perpendicular vectors** (`a·b = 0 ⟹ a b = −b a`) follows from the just-landed
  `vec_mul_eq_dot_add_wedge` (`a b = a·b + a∧b`) + `wedge` antisymmetry — a short corollary.

## Plan (the laws to prove, for BOTH `G2` and `G3`)

- [ ] **Associativity:** `mul (mul a b) c = mul a (mul b c)` — `ext <;> ring` (watch `G3` `ring`
      timing; if slow, `ring_nf` or split by component).
- [ ] **Left/right distributivity:** `mul a (add b c) = add (mul a b) (mul a c)` and the right form.
- [ ] **`one` is a two-sided identity:** `mul one a = a`, `mul a one = a`.
- [ ] **Scalar compatibility:** `mul (smul k a) b = smul k (mul a b) = mul a (smul k b)`.
- [ ] **(GA) anticommutation for perpendicular vectors:** `dot a b = 0 ⟹ mul a b = neg (mul b a)`
      — corollary of `vec_mul_eq_dot_add_wedge` + `wedge` antisymmetry (add `wedge_comm_neg` if needed).
- [ ] `make lean` green; `proofs/README.md` mentions the algebra-laws lemmas.

## Is there anything else? (scoping note)

The above is the full **associative unital ℝ-algebra** axiom set (add is already a commutative group
componentwise — provable trivially if we want it stated). GA-specific facts worth having beyond
anticommutation: `reverse` is an anti-automorphism (`reverse (a b) = reverse b * reverse a`) and the
contraction/grade relations — but those belong with the dot/wedge/pseudoscalar step-tasks, not here.
This task is deliberately the **ring axioms + basis anticommutation**; flag anything else as it comes up.

## Open questions

1. State the laws as universally-quantified over `G2`/`G3` values (cleanest), or only over `vec`/basis
    literals where a proof needs it? (Recommend general values — `ext <;> ring` handles the full struct.)
