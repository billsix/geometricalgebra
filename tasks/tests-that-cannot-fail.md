# Tests that cannot fail: make them check something

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §6.1, §6.2

## BLUF

Several tests compare a value with itself or check nothing that could break. Done means each one
asserts a property that a wrong implementation would fail, and the suite stays green.

## Context

- `tests/test_sandwich_grades.py::test_versor_sandwich_of_bivector_matches_gn_3d` checks only the
  result's type; its docstring promises a comparison with `Gn`.
- `tests/test_versor_extraction.py` asserts `R.conjugate() == R.reverse()`, and `conjugate` *is*
  `return self.reverse()` (`base.py`).
- `tests/test_multivector.py::test_normalize` asserts `u.normalize() == u * abs(u)**-1`, which is
  `normalize`'s own body.
- `tests/test_conformance.py`'s `CASES` include `(n, Gn)` rows, which compare `Gn` with `Gn`.
- `tests/test_transforms.py`'s reflect-then-project pipeline can't see a broken reflect, because
  projecting onto the plane discards exactly what the reflection flips.

## Plan

- [ ] Compare the bivector sandwich with the `Gn` reference and with the expected value.
- [ ] State `conjugate` by its definition (keep the scalar part, negate the bivector part).
- [ ] State `normalize` by its properties (magnitude 1; scaled back up, the original vector).
- [ ] Drop the `Gn` rows from `CASES`.
- [ ] Assert the reflection's own step in the pipeline test.
- [ ] Gate: `pytest -m "not slow"`, `ruff`, `ty`.

## Open questions

None.
