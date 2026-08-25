# Why the geometric product is associative (the elementary, match-rule proof)

**Reference document** — a self-contained proof that `Gn`'s geometric product is associative,
`(AB)C = A(BC)`, derived directly from the definition as implemented (concatenate blade
index-sequences, canonicalize with `decrease_grade`, extend bilinearly) — the *simple* route that
falls out of the match rules, not the tensor-algebra / Bergman Diamond-Lemma machinery. Harvested from
the completed task `tasks/archive/2026/08/25/prove-associativity-of-multiplication.md`. **Code anchors
verified 2026-08-25** against `src/gacalc/gn.py`; the computational check
`(A*B)*C == A*(B*C)` was re-run on symbolic 𝒢₃ full multivectors (True).

## What multiplication *is*, in `gn`

A **blade** is an index sequence `α = (a₁,…,a_p)` meaning `e_{a₁}···e_{a_p}`. Write `dg(·)` for
`decrease_grade` (the nested function inside `Gn._geometric_product`, `gn.py:131`) and `α ++ β` for
sequence concatenation. On blades the geometric product is, by definition,

>   `e_α · e_β  =  dg(α ++ β)`   (a signed canonical blade),

and on general multivectors it is extended **bilinearly** — `Gn` stores a multivector as a dict
`{blade: coefficient}`, and `_geometric_product` (`gn.py:130`) sums `dg` over every pair of terms
(one from each operand).

Two structural facts, both immediate:

- **(C) Concatenation is associative.** `(α ++ β) ++ γ = α ++ (β ++ γ)` — both are the single literal
  sequence `α ++ β ++ γ` (the free monoid on the indices).
- **(B) Blades are a basis.** The distinct canonical blades are linearly independent — precisely the
  assumption that makes the dict-of-blades representation well-formed (a multivector *is* its
  blade→coefficient map). So a signed canonical blade `λ·e_S` determines both `S` and `λ`: if
  `λ₁ e_{S₁} = λ₂ e_{S₂}` with `S₁, S₂` canonical, then `S₁ = S₂` and `λ₁ = λ₂`.

## The four `decrease_grade` arms (`gn.py:131`)

`dg` recurses over `blade` via structural `match`; the arms, exactly as implemented:

- `() | (_,)` — a scalar or single basis vector is already canonical: **return unchanged**.
- `(a, c, *rest) if a == c` — **drop the pair**, keep the coefficient: `e_a e_a = 1` (rule **R1**,
  Euclidean `+1`), a true identity → the element is unchanged.
- `(a, c, *rest) if a > c` — **swap** to `(c, a, *rest)` and **negate** the coefficient:
  `e_a e_c = − e_c e_a` (rule **R2**), a true identity → `λ·e_w` is unchanged.
- `(a, c, *rest) if a < c` — asserts no identity; it only **reorders which pair the recursion visits
  next** (canonicalize the tail `(c, *rest)`, then reinsert `a` in place). Any element-changing step it
  triggers is a nested R1/R2 arm.

## Lemma 1 (soundness — every arm preserves the element)

For any sequence `w` and coefficient `λ`, the value `λ · e_w ∈ 𝒢ₙ` is **unchanged** by `dg`. Proof:
each arm above either returns its input, or applies R1 / R2 — both true identities — or merely reorders
the recursion. By induction on the recursion, `dg` preserves `λ·e_w`. ∎

## Lemma 2 (well-definedness — `dg` depends on the element, not the path)

If two sequences represent the same element, `dg` sends them to the *same* signed canonical blade:
`λ·e_u = μ·e_v  ⟹  λ·dg(u) = μ·dg(v)`.

Proof: `dg(u)` is canonical (sorted, no repeats — the recursion stops only there) and, by Lemma 1,
`λ·e_{dg(u)} = λ·e_u`; likewise `μ·e_{dg(v)} = μ·e_v`. The right-hand sides are equal by hypothesis, so
`λ·e_{dg(u)} = μ·e_{dg(v)}` — two signed canonical blades naming one element. By **(B)** they are
identical. ∎

> This is the crux the tensor-algebra and Diamond-Lemma proofs work hard for (confluence); here it is a
> two-line corollary of **(B)**, because `Gn`'s representation *hands us* linear independence of blades
> for free. We are not proving the hard fact — the dict-of-blades data structure already assumes it — so
> the effort those other proofs spend on confluence simply evaporates.

## Theorem (associativity)

`(AB)C = A(BC)` for all `A, B, C ∈ 𝒢ₙ`.

Proof. Both sides are linear in each of `A, B, C`, so it suffices to check basis blades `A = e_α`,
`B = e_β`, `C = e_γ` (bilinearity extends to all multivectors). The left side:

>   `(e_α e_β) e_γ = dg( dg(α ++ β) ++ γ )`.

By Lemma 1, `e_{dg(α++β)} = e_{α++β}` as elements, so `dg(α++β) ++ γ` and `(α++β) ++ γ` represent the
same element; by Lemma 2, `dg( dg(α++β) ++ γ ) = dg( (α++β) ++ γ )`. Symmetrically,
`e_α (e_β e_γ) = dg( α ++ dg(β++γ) ) = dg( α ++ (β++γ) )`. Finally, by **(C)** the two raw
concatenations are identical, so both sides equal `dg(α ++ β ++ γ)`. Hence `(e_α e_β) e_γ =
e_α (e_β e_γ)`, and by linearity `(AB)C = A(BC)`. ∎

## Reading of the proof

Associativity is three small facts: (1) concatenation of index sequences is associative — trivial (C);
(2) `decrease_grade`'s arms are sound — they are literally R1 and R2 (Lemma 1); (3) the canonical blade
is unique — because blades are a basis (B ⇒ Lemma 2). No confluence machinery, no tensor algebra:
`(AB)C` and `A(BC)` are both `dg` of *the same* concatenation `α ++ β ++ γ`, differing only in an
intermediate `dg` that Lemma 2 shows is invisible.

## Honest caveat — (B) is assumed, not proved

The proof *assumes* **(B)**, that the 2ⁿ canonical blades are linearly independent. We do not prove it —
it is the founding premise of the `Gn` representation (storing a multivector as a blade→coefficient map
only makes sense if blades are a basis). A fully self-contained development would establish (B)
separately (a faithful matrix representation, or the tensor-algebra dimension count); given `gn`'s
design it is fair to take as granted. (Open question, left as *premise*: whether to discharge (B)
in-repo with a short linear-independence argument.)

**Signature.** Only R1 (`e_i e_i = 1`) uses the Euclidean `+1`; with `e_i e_i = ±1` the same proof goes
through unchanged. The library hardcodes `+1`.

## Verification & cross-links

- **Computational:** `(A*B)*C == A*(B*C)` holds for symbolic 𝒢₃ full multivectors (re-verified
  2026-08-25; also `notebooks/displaymv.py:405` has a 𝒢₂ instance cell).
- Code: `Gn._geometric_product` / its nested `decrease_grade` (`src/gacalc/gn.py:130`–).
- Origin: `tasks/archive/2026/08/25/prove-associativity-of-multiplication.md`.
- Builds on the "explain gn multiplication" material.
