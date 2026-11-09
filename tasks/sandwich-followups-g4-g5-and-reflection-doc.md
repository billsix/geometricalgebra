# Sandwich follow-ups: 𝒢₄/𝒢₅ operand tests, and a reflection docstring for `Vector.sandwich`

**Status:** proposed — needs go-ahead (optional)
**Priority:** 9
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** the two optional leftovers of `tasks/archive/2026/11/09/generalize-sandwich-other-grades.md`
(archived 2026-11-09 per `tasks/review/2026/11/08/repo-review.md` §9.1)

## BLUF

Two small, optional pieces left when the sandwich generalization was finished. Done = both exist, or
are dropped on purpose.

1. A few tests that 𝒢₄/𝒢₅ `Versor.sandwich` (the inherited `MultiVectorBase.sandwich`) rotates
   bivector and trivector operands correctly. They need g4/g5 generated, so they belong in the slow
   `make test-all-dims` run (skip when `gacalc.g4` is absent).
2. A role-specific docstring for `Vector.sandwich`, which today falls back to the base "conjugation /
   rotation" text and calls `v` a versor. For a vector, `v x v⁻¹` is the reflection across the line
   of `v`. This is a small generator change: route a sandwich docstring by role through
   `dispatch_method` / `CUSTOM_METHOD_DOCS`.

## Context

- The sandwich work record: `tasks/archive/2026/11/09/generalize-sandwich-other-grades.md`.
- The 𝒢₂/𝒢₃ operand tests to mirror: `tests/test_sandwich_grades.py`.
- How generated docstrings are chosen: `tasks/reference/generated-docstrings.md`.

## Open questions

None.
