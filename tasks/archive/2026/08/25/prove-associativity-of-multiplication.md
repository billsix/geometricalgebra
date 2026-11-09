# Prove associativity of the geometric product from its definition

**Created:** 2026-07-01 · **Completed:** 2026-08-25

Follow-up to `tasks/archive/2026/08/14/explain-gn-multiplication-for-highschoolers.md`. Proved that
`Gn`'s geometric product is **associative**, `(AB)C = A(BC)`, directly from multiplication as
implemented: concatenate blade index sequences, canonicalize with the `decrease_grade` match rules
(R1 `eᵢeᵢ = 1`; R2 `eᵢeⱼ = −eⱼeᵢ` for i ≠ j), and extend bilinearly. The goal was formal math by the
simple route that falls out of the match rules, not the tensor-algebra / Diamond-Lemma machinery.

**The proof now lives in `tasks/reference/geometric-product-associativity.md`**, which is canonical.
When it moved there, its code anchors were re-verified against `gn.py` (stale line numbers corrected)
and the symbolic 𝒢₃ check was re-run.

## The proof, in outline

Write `dg` for `decrease_grade` and `α ++ β` for concatenation; on blades `e_α · e_β = dg(α ++ β)`.

- **(C)** Concatenation is associative (the free monoid on the indices).
- **(B)** The canonical blades are a basis (linearly independent), the premise that makes the
  dict-of-blades representation well formed; so a signed canonical blade `λ·e_S` determines `S` and `λ`.
- **Lemma 1 (soundness):** every arm of `decrease_grade` preserves the element `λ·e_w`: the base arm
  returns its input, the `a == c` arm is R1, the `a > c` arm is R2, and the `a < c` arm only reorders
  which pair the recursion visits next.
- **Lemma 2 (well-definedness):** if `λ·e_u = μ·e_v`, then `λ·dg(u) = μ·dg(v)`, a two-line corollary
  of (B). This is the confluence step the heavier proofs work hard for; here `Gn`'s representation
  already assumes linear independence, so that effort disappears.
- **Theorem:** by bilinearity it suffices to check basis blades. By Lemmas 1 and 2,
  `(e_α e_β) e_γ = dg((α ++ β) ++ γ)` and `e_α (e_β e_γ) = dg(α ++ (β ++ γ))`, and by (C) these are the
  same concatenation. ∎

**Signature:** only R1 uses the Euclidean `+1`; the proof works unchanged with `eᵢeᵢ = ±1`.

## Decisions

- **Route:** the elementary match-rule proof (soundness + uniqueness via "blades are a basis"). The
  tensor-quotient and Bergman Diamond-Lemma proofs were noted only as the alternative that would also
  discharge (B).
- **(B) is cited as the representation's founding premise, not proved in the repo** (resolved as
  "premise for now"). A self-contained development would establish it separately, e.g. by a faithful
  matrix representation or the tensor-algebra dimension count.
- No new notebook cell was added: `notebooks/displaymv.py` already had a symbolic `(AB)C == A(BC)`
  demonstration (a 𝒢₂ instance).

## Verification

`(A*B)*C - A*(B*C) == 0` for symbolic `A, B, C ∈ 𝒢₃` (computed, and re-run when the proof moved to the
reference doc).
