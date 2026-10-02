# Audit which gacalc math operations have no Lean coverage, then decide what to add

**Status:** DONE 2026-10-01. **Priority:** 7 **Difficulty:** 3
**Created:** 2026-09-30 **Completed:** 2026-10-01 (William Emerison Six <billsix@gmail.com>)

## Summary

Audited every public math method in `src/gacalc/{base,vectorcalc,measure}.py` against the actual
theorems in `proofs/GacalcProofs/*.lean` (by reading the theorems, not grep substrings) and wrote the
result as a method-by-method coverage map — HAS / PARTIAL / NONE with theorem names — into the
"Inventory" section of `tasks/reference/lean-ga-proof-architecture.md` (32 methods: 16 HAS / 5 PARTIAL /
11 NONE at the time of the audit). The earlier informal menu was corrected along the way:
`vectorcalc.cross` and the 3D vector `dual` had been wrongly listed as gaps, but `Cross.lean` already
proved both, and `signed_volume` was likewise already covered (`dot_cross_eq_signedVolume`).

## Decisions (maintainer, 2026-10-01)

1. **Which gaps become tasks → the whole menu** — file a task per genuine gap, not a chosen subset.
2. **Home for the map → extend the architecture doc's Inventory** (one source of truth), not a rival doc.
3. **Predicates/parts included** (`is_orthogonal_to`, `is_parallel_to`, `even_part`, `odd_part`,
   `r_vector_part`) rather than skipped as "obvious by construction".

## Outcome

Filed 7 gap tasks (grouped to avoid stub-spam): reflect, normalize, predicates, grade-projection,
contractions, measures, exp. All were subsequently proven in Lean and archived
(`tasks/archive/2026/10/02/lean-proof-*.md`); the only gap still open is general `content` (blocked on
the dimension-general `Gn` layer, `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`). Gaps
already owned by an existing task were NOT re-filed: general graded `inner_product`
(`lean-general-gn-product-and-hestenes-dot-wedge`), general mixed-grade `inverse`
(`lean-general-multivector-inverse`), and the dot/wedge/pseudoscalar 3D-from-rotation derivations
(`lean-proof-dot-product`/`-wedge-product`/`-pseudoscalar-square-sign`/`-rotation-from-scratch`).

This was an audit + decision task; the proving was the follow-on. Complements the umbrella
`tasks/investigate-lean-proofs-for-ga.md`.
