# Understand & document gacalc's symbolic equality; expand tests

**Status:** blocked
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open questions below (which "equal" is meant; and use it for what).
**Recheck:** the Open questions below are answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"Understand sympy equal better, expand on tests, figure out if I can use
how that works."*

Understand how symbolic equality works in gacalc, write it up, and expand tests around it — possibly
exposing it as a reusable predicate.

## Context (investigation 2026-08-27)

- **No reference doc covers *symbolic* equality.** `tasks/reference/approximate-float-equality.md` is
  strictly the **numeric** `isclose`/ULP story — a different mechanism. This task fills the missing
  symbolic sibling.
- The actual machinery: generated `__eq__` does per-field `sympy.simplify(sympify(x) - sympify(y)) == 0`
  (e.g. `src/gacalc/g2.py:109`). Test helpers: `_same_value` (`tests/test_conformance.py:401`),
  `simplify_equal` (`tests/test_graded.py:381`), and the inline `sympy.simplify(...) == 0` idiom
  (`tests/test_conformance.py:87`, `tests/test_measure.py:139`).
- Prior archived work touched symbolic tests but did **not** study equality itself:
  `2026/08/25/explicit-symbolic-tests-and-helper-cleanup.md`,
  `2026/08/26/symbolic-vector-doctests-for-measures.md`.

## Plan (draft)

- [ ] Write `tasks/reference/symbolic-equality.md` — the `simplify(a−b)==0` convention, the per-field
      `__eq__`, its limits (when `simplify` can't decide), vs numeric `isclose`.
- [ ] Expand tests around it; if wanted (Q2), expose a public predicate (e.g.
      `MultiVectorBase.symbolically_equal`).

## Open questions

1. **Which "equal"** — sympy's `Eq`/`.equals()`, or gacalc's existing `simplify(a−b)==0` convention?
2. **Use it for what** — a public `symbolically_equal` method, a doctest idiom, or a test predicate?
   *(This decides whether the deliverable is doc-only or doc + a new API.)*
