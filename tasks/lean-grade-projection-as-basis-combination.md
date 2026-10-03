# Express grade projection (and similar struct-literal results) as basis-blade combinations in Lean

**Status:** done — G2 converted to basis form (`make lean` green); G3 kept struct-literal (per-case
decision). Staged; maintainer reviews/commits. Easily reversible (one file).
**Priority:** 7
**Difficulty:** 5
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>, stream-of-consciousness notes).
**Part of:** the Lean proof initiative, `tasks/investigate-lean-proofs-for-ga.md`.
**See also:** `tasks/reference/lean-ga-proof-architecture.md`; the Python-side mirror convention
"Build vectors from the basis constants" in gacalc's `CLAUDE.md`; sibling Lean-readability task
`tasks/lean-expand-match-usage.md`.

## BLUF

Definitions like `rVectorPart` (grade-r projection) in `proofs/GacalcProofs/GradeProjection.lean`
build their results as raw coordinate struct-literals — `| 0 => ⟨a.s, 0, 0, 0⟩`,
`| 2 => ⟨0, 0, 0, a.c12⟩`. The maintainer would prefer these written as **linear combinations of the
basis blades** (the Lean mirror of gacalc's Python rule "build from the basis constants"), e.g.
`a.s • e_0` / `a.c12 • e_12`, so the grade algebra reads mathematically rather than as positional
field-stuffing. The bridge lemma already exists (`vec_eq_smul`, `G2.lean:125`:
`vec x y = add (smul x e_1) (smul y e_2)`). **Spike first** on one definition, because field-literal
structs make `ring`/`simp`/`decide` proofs trivial and a basis-combination form can make them
harder (more unfolding lemmas); keep the rewrite only where proofs stay clean. "Done" = the chosen
definitions read as basis combinations, `make lean` green + `sorry`-free, with no material proof-size
regression — or a documented decision to stop after the spike.

## Context — how to read this cold

`rVectorPart` is defined for both algebras in `GradeProjection.lean` (G2 at `:16`, G3 at `:48`) and
underpins `evenPart`/`oddPart` and the contractions (`Contractions.lean` `leftContraction`/
`rightContraction`). Each case currently emits a coordinate struct-literal selecting one grade's
components. gacalc already carries basis constants in Lean (`e_1`, `e_2`, `e_12`, …) and a
`smul`/`add` algebra, and `vec_eq_smul` proves the vector case equals its basis combination — so the
machinery to express `⟨…⟩` as `Σ cᵢ • eᵢ` exists.

The tension is proof ergonomics: the downstream proofs (`Contractions.lean:26,32` do
`simp only [leftContraction, rVectorPart, mul, vec, scalar, dot, zero]`) lean on the struct-literal
form unfolding cleanly under `simp`/`ring`. A basis-combination definition must still unfold to the
same normal form for those `ring` closes to keep working.

## Method

1. **Spike** on `rVectorPart` for G2 only: rewrite the four match arms as basis-blade combinations,
   add whatever `smul`/`add`/basis unfolding `simp` lemmas are needed, and re-run `make lean`.
2. Measure: did the dependent proofs (`evenPart`/`oddPart`, G2 contractions) stay green with no
   material growth? If yes, extend to G3 and any other struct-literal-result definitions. If the
   proofs bloat, **stop and record that** — the field-literal form wins on ergonomics.
3. `make lean` green + `sorry`-free throughout.

## Decisions (resolved 2026-10-03, William Emerison Six <billsix@gmail.com>)

1. **Readability of the definitions is the goal.** Keep the proofs closing however they do; do not
   pursue rewriting the proofs themselves into basis-combination `rw` chains. If making a definition
   a basis combination forces the dependent proofs to grow materially, that definition keeps its
   struct-literal form (readability must not cost proof health). The spike decides each case.

## Outcome (2026-10-03, done autonomously, staged)

**G2 `rVectorPart` → basis combinations (KEPT, `make lean` green).** The four match arms now read:
`0 => smul a.s one`, `1 => add (smul a.c1 e_1) (smul a.c2 e_2)`, `2 => smul a.c12 e_12`,
`_ => ⟨0,0,0,0⟩` (the degenerate catch-all; G2 has no `zero` const). Proof cost, as predicted by the
spike: `rVectorPart_idem` lost its one-line `rcases … <;> rfl` and is now
`rcases … <;> simp only [rVectorPart, add, smul, one, e_1, e_2, e_12] <;> ext <;> ring`; the
`complete`/`even_add_odd` proofs gained those same 5 constants in their `simp only` sets. Moderate,
localized, no new lemmas/bridge machinery. Verified green in the baked `gacalc` image
(`GradeProjection` built in 3.4s, no `sorry`/`admit`).

**G3 `rVectorPart` → KEPT struct-literal (deliberately NOT converted).** Two per-case reasons:
(1) readability does **not** improve — G3's grade-2 arm would be a nested three-term
`add (add (smul a.c12 e_12) (smul a.c13 e_13)) (smul a.c23 e_23)`, noisier than
`⟨0,0,0,0,a.c12,a.c13,a.c23,0⟩`, which shows the grade-2 slots plainly; (2) higher proof cost with
external blast radius — `Contractions.lean`'s `leftContraction_vec_vec`/`rightContraction_vec_vec`
currently close with a bare `simp only […]` and would need the basis constants added plus an
`ext <;> ring`. So for G3 the basis form costs proof health without a readability win — exactly the
"keep struct-literal" case from the decision above.

**Net:** a per-algebra split (G2 basis, G3 struct), sanctioned by "the spike decides each case." If
the maintainer prefers consistency, it flips trivially either way — revert the one G2 hunk for
all-struct, or apply the documented G3 rewrite (+ the two `Contractions.lean` proof tweaks) for
all-basis.

## Open questions

None — resolved 2026-10-03 (maintainer): **keep the per-algebra split** (G2 basis / G3 struct).
Task complete.
