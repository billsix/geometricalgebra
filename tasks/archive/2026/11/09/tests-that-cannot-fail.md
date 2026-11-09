# Tests that cannot fail: make them check something

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §6.1, §6.2

## What was wrong, and what changed

- **`tests/test_sandwich_grades.py::test_versor_sandwich_of_bivector_matches_gn_3d`** checked only
  the result's type. It now compares the specialized sandwich with the `Gn` reference, and with the
  value the quarter turn must give (`e_12 − 3 * e_13 + 2 * e_23` for `e_12 + 2 * e_13 + 3 * e_23`).
- **`tests/test_versor_extraction.py`** asserted `R.conjugate() == R.reverse()`, which is
  `conjugate`'s body. Both sites now assert the definition: the scalar part kept and the bivector
  part negated, `R.r_vector_part(0) - R.r_vector_part(2)`.
- **`tests/test_multivector.py::test_normalize`** asserted `normalize`'s own formula. It now asserts
  the properties: magnitude 1, and scaling back up by the original magnitude gives the original
  vector (2D and 3D, symbolic).
- **`tests/test_conformance.py`:** `CASES` lists only the specialized classes. The `(n, Gn)` rows
  compared `Gn` with itself.
- **`tests/test_transforms.py`'s reflect-then-project pipeline** now also asserts the reflection's own
  step (`e_1 + e_3 → e_1 − e_3`). Projecting onto the plane discards what the reflection flips, so
  the pipeline's result alone could not see a broken reflect.

## Verification

- The five touched files: 188 passed, 2 skipped.
- The full `make test` (lean image): 752 passed, 2 skipped. The count fell because of the dropped
  `Gn` rows.
- `ruff` and `ty`: clean.
