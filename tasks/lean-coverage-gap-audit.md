# Audit which gacalc math operations have no Lean coverage, then decide what to add

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## BLUF

Produce and maintain a **coverage map**: for every major public math method in gacalc, does a
Lean theorem cover it (yes / partial / none)? Then use the "none/partial" column as the menu for a
decision on what to prove next. "Done" for THIS task = the map is written into
`tasks/reference/lean-ga-proof-architecture.md` (which already has an "Inventory" section — extend
it, don't make a rival doc) and the maintainer has picked which gaps become `lean-proof-*` tasks.
This is an **audit + decision** task, not authorization to write proofs. It complements the
umbrella `tasks/investigate-lean-proofs-for-ga.md` (which tracks planned Lean work) — cross-link,
don't duplicate.

## Context (read first)

- Ground truth for "what's proven" = `proofs/GacalcProofs/*.lean` (gate `make lean`, green
  2026-09-30). Public methods = `src/gacalc/base.py` (+ `vectorcalc.py`, `measure.py`).
- The architecture doc `tasks/reference/lean-ga-proof-architecture.md` already has a file
  inventory + a "Remaining" list; the umbrella task lists completed/planned children. Neither is a
  method-by-method has-Lean/no-Lean table — that's the deliverable.

## Starting map (verified 2026-09-30 — refresh before trusting; Lean is gitignored-free but moves)

**HAS Lean coverage:** geometric product + algebra laws (`AlgebraLaws.lean`); wedge/outer product
(`G3.lean:68`, antisymmetry `G3.lean:315`); scalar product/`dot` (`G3.lean:154`) and the split
`ab=a·b+a∧b` (`G3.lean:195/227`); reverse (+ G3 anti-automorphism `Sandwich.lean:354`); magnitude
(`normSq_*`, multiplicative `Sandwich.lean:359`); **inverse — blade/versor cases only**
(`Projection.lean:87`, `Sandwich.lean:129/142/172`); dual (`G2.lean:200`, `Projection.lean:46/51`);
pseudoscalar square (2D+3D: `I_sq` `G2.lean:182`/`G3.lean:141`); projection/rejection
(`Projection.lean` + `Projection2D.lean`); sandwich/rotation isometry (`Sandwich.lean`,
`RotateComponents.lean`, `Rotation*.lean`); cosine/trig (`Trig.lean`); Lagrange (`Lagrange.lean`).

**NO Lean coverage (the menu):**
- `reflect` / `reflected_across` — `base.py:1439`/`1531` (rotation is done, reflection is not).
- `left_contraction` / `right_contraction` (`<`/`>`) — `base.py:862`/`907` — entirely absent.
- general graded `inner_product` — `base.py:735` — only the vector·bivector case exists
  (`inner_vb`, `Projection.lean:132`).
- `cross` — `vectorcalc.py:34` — only its building block `dual(a∧b)⊥a,b` exists.
- `exp` (exponential map) — `base.py:1818` — none.
- `normalize` — `base.py:645` — none.
- measures `area`/`volume`/`signed_area`/`signed_volume` — `base.py:1552/1573/1588/1612` — none
  (only `normSq_wedge_vec` is adjacent).
- `even_part`/`odd_part` — `base.py:1277/1290`; grade projection `r_vector_part` `base.py:985`;
  `is_orthogonal_to`/`is_parallel_to` `base.py:1064/1100` — none.
- general (mixed-grade) `inverse` — explicitly deferred (`tasks/lean-general-multivector-inverse.md`).
- **general** pseudoscalar-square and the from-rotation derivation of dot/wedge — in-progress in
  existing tasks (see overlap), not this task's target.

## Overlap check (do NOT re-file these — they already exist)

`tasks/investigate-lean-proofs-for-ga.md` (umbrella), `lean-proof-dot-product.md`,
`lean-proof-wedge-product.md`, `lean-proof-rotation-from-scratch.md`,
`lean-proof-pseudoscalar-square-sign.md`, `lean-general-multivector-inverse.md`,
`lean-general-gn-product-and-hestenes-dot-wedge.md`. The menu above deliberately lists only the
methods **none** of those cover (reflect, contractions, cross, exp, normalize, measures,
even/odd, orthogonal/parallel predicates). Some also appear in
`tasks/lean-candidates-from-symbolic-tests.md` (which reaches the same gaps from the *test* side) —
reconcile the two so a method isn't double-proposed.

## Open questions

1. **Prioritise the menu.** My lean at high value / low cost: `reflect` (trivial from
   project−reject, both already in Lean), `cross` (from `dual`+wedge, already in Lean),
   3D vector `dual`. Higher cost: contractions, general inner product, measures, `exp`, frame
   theory. Which tier do you want turned into tasks?
2. **Home for the map:** extend `lean-ga-proof-architecture.md`'s inventory (my lean) or a new
   `tasks/reference/lean-coverage-map.md`? Extending keeps one source of truth.
3. **Predicates/parts** (`is_orthogonal_to`, `even_part`, `r_vector_part`): worth Lean theorems at
   all, or are these "obvious by construction" and not worth the ceremony?
