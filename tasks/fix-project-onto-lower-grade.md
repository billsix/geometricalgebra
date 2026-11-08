# `project` returns 0 when the input's grade exceeds the blade's

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 2
**Difficulty:** 3
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1

## BLUF

`MultiVectorBase.project(onto=B)` returns an r-vector `A` unchanged when `r > grade(B)`. The right
answer is 0. Done means:

- projection of a higher-grade blade onto a lower-grade blade returns zero, in `Gn` and in the
  generated classes;
- a doctest and a conformance test pin it;
- `make test` is green.

## Context

**The bug.** Re-checked 2026-11-08:

```
>>> MultiVector.project(onto=e_1)(e_1 ^ e_2)   # gn
Gn(coefficient_of_blade={(1, 2): 1})
>>> g3.G.project(onto=g3.e_1)(g3.e_1 ^ g3.e_2)
g3.Bivector(coeff_e_12=1, coeff_e_13=0, coeff_e_23=0)
```

A projection is an outermorphism, so `P_B(e₁ ∧ e₂) = P_B(e₁) ∧ P_B(e₂) = e₁ ∧ 0 = 0` when
`B = e₁`.

**The code.** `src/gacalc/base.py`, `MultiVectorBase.project`:

- The inner `fn` sends every r-vector to the H&S p. 18 eq. 2.9c form `(A · B) * B⁻¹`.
- That form is valid for `r ≤ s`, where `s = grade(B)`. For `r > s`, the Hestenes inner product
  `A · B = ⟨A * B⟩_{|r−s|}` is not zero (e.g. `e₁₂ · e₁ = −e₂`), so 2.9c gives `−e₂ * e₁ = e₁₂`.
- The grade narrowing that follows (`r_vector_part(r)`) keeps that grade-r value.
- The general form, eq. 2.9a `(A · B) · B⁻¹`, gives the correct 0 for the same input.

**Fix shape.** In the r-vector branch, return the zero of the input's type when `r > s`. Keep 2.9c
for `r ≤ s` (it stays the fast, grade-preserving path).

**Existing tests that must stay green:**

- `tests/test_conformance.py::test_project_reject` (vectors, every algebra);
- `test_project_vector_onto_bivector_2d` and the `g3` plane cases at `tests/test_conformance.py:457-475`;
- `tests/test_graded.py:444`.

**Forms** (the CLAUDE.md "three forms" rule). This is a bug fix to an existing operation, not a new
mathematical result, so no Lean theorem or book page is added. The Lean projection theorems are
about vectors (`r ≤ s`) and are unaffected.

## Plan

- [ ] In `project`'s r-vector branch, return `type(value).zero()` when `value`'s grade exceeds
  `onto`'s top grade. The docstring states the `r ≤ s` domain of 2.9c and the zero result.
- [ ] Add doctests to `project`: bivector onto vector → 0; the 3D trivector onto the e₁₂ plane →
  0.
- [ ] Add a conformance test over `[Gn, G]` for 𝒢₂/𝒢₃: bivector onto vector, and trivector onto
  bivector.
- [ ] Gate: `make test` (the lean image's `pytest -m "not slow"`), plus `ruff`/`ty` on the touched
  files.
- [ ] `CHANGELOG.md` `[Unreleased]` › Fixed entry: a behaviour change consumers could notice.

## Open questions

None.
