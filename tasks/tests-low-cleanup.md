# Tests low cleanup: licence headers, basis-constant and coordinate conventions, weak asserts, duplicate doctests

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §6.3, §6.4, §2.4

## BLUF

Bring `tests/` in line with the repo's conventions, and replace tests that duplicate a doctest with
the doctest. Done means every item below is fixed, and `make format` and `make test` pass with the
same or a higher test count, apart from the deleted duplicates.

## Context

Read first:
- `CLAUDE.md` › "Conventions the agent must obey" (basis constants, explicit unit coefficients, no
  local aliases) and "Dev workflow" › License headers;
- the cross-project `doctests-by-default.md` (github.com/billsix/runClaudeInContainer
  `tasks/reference/`).

Re-checked 2026-11-09:

- **Licence headers:**
  - No header at all: `tests/_helpers.py`, `test_isclose.py`, `test_odd3.py`,
    `test_operator_typing.py`, `test_pseudoscalar_square_sign.py`. Copy the header verbatim from
    `tests/test_rotate_90_degrees.py`.
  - `Copyright (c) 2026` instead of `2025-2026`: `test_bivector_rotation.py`,
    `test_plane_rotation.py`, `test_vector_ergonomics.py`.
- **`basis_vector` or aliases where a constant exists** (record lines):
  - `test_plane_rotation.py:41-42` (`E1`/`E2`) and `:93`
  - `test_conformance.py:459,470`
  - `test_transforms.py:254-259,470-512`
  - `test_graded.py:448-450`

  Keep any that test `basis_vector` itself; tests may call the public API under test.
- **Bare blades used as coordinate vectors:** `test_measure.py:205-207`,
  `test_bivector_rotation.py:58-60`.
- **Smaller items:**
  - the orphan `# doc-region-end test add` at `tests/test_multivector.py:56`, which has no start
    marker (check `make check-regions` and the book's `literalinclude`s before removing it);
  - history comments at `test_numeric_magnitude.py:68`, `test_exp.py:63` and in
    `test_operator_typing.py`;
  - a bare "Bill's" in `test_measure.py:67` and `test_vector_ergonomics.py:18`: use "the maintainer's";
  - weak asserts: `assert symbolic.inverse() is not None` (`test_numeric_magnitude.py:87`), and an
    `is_frame == are_linearly_independent` check that pins no truth value (`test_frame.py:105-106`).
- **Moved-task citations (§2.4, tests):**
  - `tests/test_vector_ergonomics.py` and `tests/test_plane_rotation.py` →
    `upgrade-rotation-and-ctc-vector-mapping.md`;
  - `tests/test_blade_symbols.py` and `tests/test_vectorcalc.py` → `custom-symbols-and-vector-calc.md`;
  - `tests/test_numeric_magnitude.py` → `magnitude-numeric-for-numeric-input.md`;
  - `tests/test_conformance.py` → `graded-typed-module-basis-constants.md`.

  Repoint each to its `tasks/archive/…` path.
- **Duplicate tests that should be doctests (§6.4):**
  - `test_frame.py::test_kronecker_delta` duplicates the doctest in `frame.py`; delete it.
  - `test_measure.py::test_signed_content_on_gn_full_space` largely duplicates the `measure.py`
    doctest; delete it, or keep only what the doctest lacks.
  - `test_generator.py`'s `blade_label`/`field_name`/`blades_for_dim`/`_subscript` tests: move them
    into doctests on those functions in `tools/gen_specialized.py` (`testpaths` already includes
    `tools`).
  - `test_pseudoscalar_square_sign.py::test_hand_counted_grades_one_through_five`: check whether
    `pseudoscalar_squared_sign` now has a doctest that covers it.

## Plan

- [ ] Headers and copyright years.
- [ ] The convention fixes and the smaller items.
- [ ] Repoint the citations, and check that each path exists.
- [ ] Move or delete the duplicate tests, then record the before/after counts from `make test`.
- [ ] `make format`, `make test`, `make check-regions`.

## Open questions

None.
