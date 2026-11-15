# Sandwich follow-ups: 𝒢₄/𝒢₅ operand tests, and a reflection docstring for `Vector.sandwich`

**Created:** 2026-11-09
**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`
**Source:** the two optional leftovers of `tasks/archive/2026/11/09/generalize-sandwich-other-grades.md`
(archived 2026-11-09 per `tasks/review/2026/11/08/repo-review.md` §9.1)

## Outcome

1. **𝒢₄/𝒢₅ sandwich tests**: `tests/test_sandwich_grades.py::test_versor_sandwich_higher_grades_matches_gn`.
   For each of `Bivector`, `Trivector`, `FourVector` (and `FiveVector` in 𝒢₅), it builds an operand
   with a distinct integer on every blade and checks that the quarter turn `e_1 → e_2` keeps its type
   and agrees exactly with the `Gn` reference. Their `Versor` inherits `MultiVectorBase.sandwich`, so
   this checks that base method on every operand grade. The cases are collected only when
   `gacalc.g4` / `gacalc.g5` import, following `tests/test_conformance.py`: they run under
   `make test-all-dims` and in any tree where g4/g5 exist, and CI (g1–g3 only) skips them. All 7
   passed against this tree's g4/g5 (generated 2026-11-13).
2. **`Vector.sandwich` docstring**: the generator re-declares `sandwich` on the generated `Vector` of
   𝒢₁–𝒢₃ as a pass-through to `MultiVectorBase.sandwich`, so the new `CUSTOM_METHOD_DOCS` entry
   `vector|sandwich` gives it its own text: reflection across the line of `v`, `v * x * v⁻¹`, equal to
   `x.reflected_across(across=v)`, a vector as an improper versor, and only `v`'s direction mattering.
   It has per-dimension doctests: 𝒢₁, where the reflection is the identity, and 𝒢₂/𝒢₃. Before this,
   `Vector` inherited the base docstring, which describes a rotating versor. `_OperandT` is now imported
   for `n <= 3`. The header comments and `tasks/reference/code-generator-architecture.md` were updated
   to match, including the line-to-line imports added earlier in the batch.

## Judgment calls made during the work

- **A pass-through override, not a closed form.** The role-keyed docstring lookup only reaches methods
  the class defines, and `Vector` had no `sandwich` of its own. A specialized reflection closed form
  was not the task. Re-declaring the method changes no behaviour or typing (same
  `_OperandT -> _OperandT` signature).
- **The 𝒢₄/𝒢₅ tests are not marked `slow`.** They take well under a second each and are skipped where
  g4/g5 are absent, which is the everyday and CI case.
