# Prove associativity of the geometric product from its definition

**Status:** DONE 2026-08-25 — the proof is complete and now lives as a living reference doc:
**`tasks/reference/geometric-product-associativity.md`** (code anchors re-verified against `gn.py`,
line numbers corrected from the stale :103/:148 to :131/:130; the symbolic 𝒢₃ `(AB)C == A(BC)` check
re-run True). The optional `displaymv.py` demo cell already exists (`:405`). Open question (discharge
(B) in-repo vs cite as premise) resolved as **premise for now**. This doc is the work record; the
reference doc is canonical.
**Priority:** 3
**Difficulty:** 2
**Started:** 2026-07-01

## Goal

Follow-up to [[explain-gn-multiplication-for-highschoolers]]. Prove the geometric
product of `Gn` is **associative** — `(AB)C = A(BC)` — directly from the definition of
multiplication as implemented: concatenate blade index-sequences, then canonicalize with
the `decrease_grade` match rules (eᵢeᵢ = 1; eᵢeⱼ = −eⱼeᵢ for i ≠ j), extended by
linearity. Wanted as **formal math**, but the *simple* route — the one that falls out of
the match rules themselves — not the tensor-algebra / Diamond-Lemma machinery.

## The proof (elementary, from the `decrease_grade` match rules)

### What multiplication *is*, in `gn`

A **blade** is an index sequence `α = (a₁,…,a_p)` meaning `e_{a₁}···e_{a_p}`. Write
`dg(·)` for `decrease_grade` and `α ++ β` for sequence concatenation. On blades the
geometric product is, by definition,

>   `e_α · e_β  =  dg(α ++ β)`   (a signed canonical blade),

and on general multivectors it is extended **bilinearly** (`Gn` stores a multivector as a
dict `{blade: coefficient}`; the product is the sum over pairs of terms, `gn.py:148`).

Two structural facts we will use, both immediate:

- **(C) Concatenation is associative.** `(α ++ β) ++ γ = α ++ (β ++ γ)` — both are the
  single literal sequence `α ++ β ++ γ`. (The free monoid on the indices.)
- **(B) Blades are a basis.** The distinct canonical blades are linearly independent —
  this is precisely the assumption that makes the dict-of-blades representation
  well-formed (a multivector *is* its blade→coefficient map). So a signed canonical blade
  `λ·e_S` determines both `S` and `λ`: if `λ₁ e_{S₁} = λ₂ e_{S₂}` with `S₁,S₂` canonical,
  then `S₁ = S₂` and `λ₁ = λ₂`.

### Lemma 1 (soundness — each match arm preserves the element)

For any sequence `w` and coefficient `λ`, the value `λ · e_w ∈ 𝒢ₙ` is **unchanged** by
`dg`. Proof: inspect the four arms of `decrease_grade` (`gn.py:103`).

- `() | (_,)` — returns the input unchanged.
- `(a, c, *rest) if a == c` — drops the pair, keeping the coefficient: uses `e_a e_a = 1`
  (rule **R1**), a true identity, so the element is unchanged.
- `(a, c, *rest) if a > c` — swaps to `(c, a, *rest)` and negates the coefficient: uses
  `e_a e_c = − e_c e_a` (rule **R2**), a true identity, so `λ·e_w` is unchanged.
- `(a, c, *rest) if a < c` — asserts no identity; it only **reorders which pair the
  recursion visits next** (sort the tail, then reinsert `a`). Any element-changing step it
  triggers is a nested `R1`/`R2` arm.

Every arm therefore preserves `λ·e_w`; by induction on the recursion, `dg` does. ∎

### Lemma 2 (well-definedness — `dg` is a function of the element, not the path)

If two sequences represent the same element, `dg` sends them to the *same* signed
canonical blade: `λ·e_u = μ·e_v  ⟹  λ·dg(u) = μ·dg(v)`.

Proof: `dg(u)` is canonical (sorted, no repeats — it stops only there) and, by Lemma 1,
`λ·e_{dg(u)} = λ·e_u`; likewise `μ·e_{dg(v)} = μ·e_v`. The right-hand sides are equal by
hypothesis, so `λ·e_{dg(u)} = μ·e_{dg(v)}` — two signed canonical blades representing one
element. By **(B)** they are identical. ∎

> This is the crux the tensor-algebra and Diamond-Lemma proofs work hard for
> (confluence); here it is a two-line corollary of **(B)**, because `Gn`'s
> representation *hands us* linear independence of blades for free. In other words:
> we are not proving the hard fact — the dict-of-blades data structure already assumes
> it — so all the effort those other proofs spend on confluence simply evaporates.

### Theorem (associativity)

`(AB)C = A(BC)` for all `A, B, C ∈ 𝒢ₙ`.

Proof. Both sides are linear in each of `A, B, C`, so it suffices to check them on basis
blades `A = e_α`, `B = e_β`, `C = e_γ` (linearity then extends to all multivectors).
Compute the left side:

>   `(e_α e_β) e_γ = dg( dg(α ++ β) ++ γ )`.

By Lemma 1, `e_{dg(α++β)} = e_{α++β}` as elements, hence `dg(α++β) ++ γ` and
`(α++β) ++ γ` represent the same element (both are that element times `e_γ` on the right).
By Lemma 2,

>   `dg( dg(α ++ β) ++ γ ) = dg( (α ++ β) ++ γ )`.

Symmetrically,

>   `e_α (e_β e_γ) = dg( α ++ dg(β ++ γ) ) = dg( α ++ (β ++ γ) )`.

Finally, by **(C)** the two raw concatenations are identical, `(α ++ β) ++ γ = α ++ (β ++
γ)`, so both sides equal `dg(α ++ β ++ γ)`. Therefore `(e_α e_β) e_γ = e_α (e_β e_γ)`, and
by linearity `(AB)C = A(BC)`. ∎

### Reading of the proof

Associativity is really three separate, small facts:

1. **concatenation of index sequences is associative** — trivial (C);
2. **`decrease_grade`'s arms are sound** — they are literally R1 and R2, true identities (Lemma 1);
3. **the canonical blade is unique** — because blades are a basis, the fact `Gn`'s dict
   representation already presumes (B ⇒ Lemma 2).

No confluence machinery, no tensor algebra: `(AB)C` and `A(BC)` are both `dg` of *the same*
concatenation `α ++ β ++ γ`, differing only in an intermediate `dg` that Lemma 2 shows is
invisible.

**One honest caveat (belongs right here):** the proof *assumes* fact **(B)**, that the 2ⁿ
canonical blades are linearly independent. We do not prove (B) — it is the foundational
premise of the whole `Gn` representation (storing a multivector as a blade→coefficient map
only makes sense if blades are a basis). A fully self-contained development would establish
(B) separately (e.g. by exhibiting a faithful matrix representation, or via the
tensor-algebra dimension count); given `gn`'s design it is fair to take as granted.

**Signature.** Only `e_i e_i = 1` (R1) uses the Euclidean `+1`; with `e_i e_i = ±1` the same
proof goes through unchanged. The library hardcodes `+1`.

## Plan

- [x] Restate the multiplication rules as used by `decrease_grade` (R1, R2 + concatenation + linearity)
- [x] Reduce associativity to single-blade associativity via bilinearity
- [x] Argue single-blade associativity from concatenation-assoc + soundness + uniqueness of the canonical blade
- [ ] (Optional) Add a symbolic `(AB)C == A(BC)` demonstration in `notebooks/displaymv.py`
      — note: the notebook already has such a cell at `displaymv.py:405` (𝒢₂ instance); a
      dedicated, labeled cell could be added if wanted.

## Notes / decisions

- Builds on [[explain-gn-multiplication-for-highschoolers]].
- Chosen route: the **elementary match-rule proof** above (soundness + uniqueness via
  "blades are a basis"), *not* the tensor-quotient / Bergman Diamond-Lemma proofs — those
  are the heavier standard arguments; noted only as the alternative that would also
  discharge caveat (B).
- Verified computationally: `(A*B)*C - A*(B*C) == 0` for symbolic `A,B,C ∈ 𝒢₃`.

## Open questions

- Do we want caveat (B) discharged in-repo (a short linear-independence argument), or is
  citing it as the representation's founding premise sufficient? Left as premise for now.
