# `project` returns 0 when the input's grade exceeds the blade's

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1

## What was wrong

`MultiVectorBase.project(onto=B)` (`src/gacalc/base.py`) sent every r-vector to H&S p. 18 eq. 2.9c,
`(A · B) * B⁻¹`. That form is valid only for `r ≤ s`, where `s = grade(B)`. For `r > s`, the
Hestenes inner product is the nonzero grade-`(r − s)` part of `A * B` (`e₁₂ · e₁ = −e₂`), so the
function returned the input unchanged:

- `project(onto=e_1)(e_1 ^ e_2)` gave `e_12` in `Gn`, and `Bivector(e_12=1)` in `g3`.
- The right answer is 0: a projection is an outermorphism, so `P(e₁ ∧ e₂) = e₁ ∧ 0`.

## What changed

- **`project`'s r-vector branch** returns the zero of the input's type when the input's grade
  exceeds `onto.max_grade()`. A comment explains why 2.9c doesn't apply. The `r ≤ s` path is
  unchanged.
- **The docstring** states 2.9c's `r ≤ s` domain, and gains a doctest:
  `project(onto=e_1)(e_1 ^ e_2) == zero`.
- **`tests/test_conformance.py::test_project_higher_grade_onto_lower_grade_is_zero`** checks `Gn`
  and the generated `G` of 𝒢₂/𝒢₃ on three cases: a bivector onto a vector in 2D and in 3D, and the
  trivector onto a bivector. It fails on the old code (4 failed) and passes on the new.
- **`CHANGELOG.md` `[Unreleased]` › Fixed** has an entry. This is a behaviour change for the
  affected inputs.

No Lean theorem or book page was added. This is a fix to an existing operation, and the Lean
projection theorems cover vectors (`r ≤ s`) only.

## Verification

- `pytest -m "not slow"` on the sandbox Python: 796 passed, 2 skipped.
- `ruff check`/`ruff format` and `ty check` on the touched files: clean.
- The containerized gate runs once for the whole batch, at its end.
