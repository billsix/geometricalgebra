# Lean: bring the 3D grade-pure predicate set to parity with 2D

**Status:** proposed — needs go-ahead.
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The 3D follow-up agreed when the 2D grade-predicate work landed (originating task
`lean-product-wedge-functions-and-grade-predicates.md`, done 2026-10-28 for 2D per the "2D now, 3D
later" go-ahead). `G3.lean` has `IsVector`/`IsBivector`/`IsTrivector` and `IsEvenVersor`/`IsRotor`
(`Sandwich.lean`) but **no `IsScalar`**, and none of the grade-of-result lemmas that 𝒢₂ now has. Add
`IsScalar` to `G3` with its `eq_…_of_is…` bridge + `is…_…` recognizer, and the grade-of-result lemmas
that exercise the predicates, mirroring the 2D set.

## Context (cold start)

- The 2D set and the pattern to mirror are documented in `tasks/reference/lean-ga-proof-architecture.md`
  → "The 2D grade-pure predicate set (`G2.lean`, 2026-10-28)". Read it first.
- 2D reference implementation (`G2.lean`): `IsScalar`/`IsVector`/`IsBivector`, each with
  `eq_smul_one_of_isScalar`/`eq_vec_of_isVector`/`eq_smul_e12_of_isBivector` bridges and
  `isScalar_one`/`isVector_vec`/`isBivector_e12` recognizers; plus `isScalar_mul_self_of_isVector`
  (`a a` is a scalar) and `isBivector_wedge_of_isVector` (`a∧b` is a bivector, in `Projection2D.lean`).
- `G3.IsScalar` is `a.c1 = 0 ∧ a.c2 = 0 ∧ a.c3 = 0 ∧ a.c12 = 0 ∧ a.c13 = 0 ∧ a.c23 = 0 ∧ a.c123 = 0`
  (only `s` nonzero) — the 3D analogue of the 2D two-clause version.

## Plan

1. Add `G3.IsScalar` + `eq_smul_one_of_isScalar` bridge + `isScalar_one` recognizer (mirror 2D).
2. Add the grade-of-result lemmas that read well in 3D: `isScalar_mul_self_of_isVector` (`a a` scalar);
   consider `isBivector_wedge_of_isVector` (`a∧b` is a grade-2 bivector in 3D) and
   `isTrivector_wedge3_of_isVector` (`a∧b∧c` is a trivector) — add the ones that have, or plausibly gain,
   a consumer; don't add speculative dead pred+lemma pairs (the 2D-side judgment).
3. `make lean` green; completeness gate OK. No new book page unless a result is genuinely student-facing
   (the predicates mirror existing Python `is_*`; follow the three-forms rule as "new work when asked,"
   not a backfill).

## Open questions

1. Scope to `IsScalar` + `a²`-is-scalar only (the strict parity gap), or also add the wedge/wedge3
   grade-of-result lemmas? Recommend: add `IsScalar` + `isScalar_mul_self_of_isVector` for sure; add the
   wedge grade lemmas only if a current theorem would use them. Confirm.
