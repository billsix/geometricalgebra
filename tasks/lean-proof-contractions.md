# Lean proof — left & right contraction (`left_contraction`, `right_contraction`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 5

## BLUF

Prove, from scratch in Lean, gacalc's left and right contractions — `left_contraction` (`<`,
`base.py:862`, grade `m−k`) and `right_contraction` (`>`, `base.py:907`, grade `k−m`), Taylor 2021
p.103. Both are **entirely absent** from the proofs. Grouped (they are mirror operations). "Done" =
coordinate definitions + the characterising laws (2D + 3D), `make lean` green.

## Approach

Define `leftContraction A B = ⟨A B⟩_{s−r}` and `rightContraction A B = ⟨A B⟩_{r−s}` on the
`G2`/`G3` struct via the grade-projection selector (see `lean-proof-grade-projection`, a natural
dependency). Prove: for two vectors both contractions reduce to the scalar `dot` (and **include
grade 0**, unlike the Hestenes `inner_product` — the intentional difference flagged in
`tasks/reference/contraction-and-dot-definitions.md`); the vector·bivector left contraction equals
`inner_vb` (`Projection.lean:132`); and `(A < B) = (B > A)~`-style duality. Beware the terminology
trap recorded in the architecture doc: contractions are NOT the Hestenes inner product, though they
coincide for vector·bivector. Coordinate (`ext <;> ring`) leaves, then structural corollaries.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
