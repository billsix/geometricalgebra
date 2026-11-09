# Tests low cleanup: licence headers, basis-constant conventions, weak asserts, duplicate tests to doctests

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §6.3, §6.4, §2.4

## What changed

- **Licence headers:** the LGPL-2.1-only header (copied from `tests/test_rotate_90_degrees.py`) was
  added to `tests/_helpers.py`, `test_isclose.py`, `test_odd3.py`, `test_operator_typing.py` and
  `test_pseudoscalar_square_sign.py`. The copyright year became `2025-2026` in
  `test_bivector_rotation.py`, `test_plane_rotation.py` and `test_vector_ergonomics.py`.
- **Basis constants:**
  - `test_plane_rotation.py` dropped its `E1`/`E2` aliases for `g2.e_1`/`g2.e_2`, and its
    `Gn.basis_vector(…)` for `gn.e_1`/`gn.e_2`;
  - `test_conformance.py`, `test_transforms.py` and `test_graded.py` use `g2.G.e_1`, `g3.G.e_1`,
    `g3.Vector.e_1` and so on. Their `e1`/`e3` aliases are gone, and coordinate sums are written
    `1 * g3.G.e_1 + 1 * g3.G.e_3`.
  - `cls.basis_vector(i)` stays where `cls` is a parameter, and so do the tests of `basis_vector`
    itself.
- **Bare coordinate blades:** `test_measure.py` and `test_bivector_rotation.py` now write `1 * e_k`.
- **Smaller items:**
  - the orphan `# doc-region-end test add` marker is gone;
  - the history comments in `test_numeric_magnitude.py`, `test_exp.py` and `test_operator_typing.py`
    describe current behaviour;
  - "Bill's" became "the maintainer's";
  - `assert symbolic.inverse() is not None` became `symbolic * symbolic.inverse() == g3.G.one()`;
  - the `is_frame` test pins `True`/`False` for both functions.
- **Moved-task citations:** eight test docstrings now cite their `tasks/archive/…` paths, reflowed to
  stay under 88 columns.
- **Duplicates moved to doctests:**
  - `test_kronecker_delta` was deleted, and its symmetry case became a doctest on
    `frame.kronecker_delta`;
  - `test_signed_content_on_gn_full_space` lost the two cases the `measure.signed_content` doctest
    already covers;
  - the `blade_label`/`field_name`/`blades_for_dim`/`_subscript`/`_superscript` tests became
    doctests in `tools/gen_specialized.py`;
  - `pseudoscalar_squared_sign` gained a doctest for grades 1–5. Its hand-counted test stays, since it
    checks the slow squaring path, not the closed form.

## Verification

`make test`: 775 passed, 2 skipped (this includes the next task's 5 new tests). `make format`,
`make check-regions` and `make check-generated` pass, and every cited `tasks/archive/…` path exists.
