# Decide float tolerance from the coefficients, not a threaded flag

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; overnight batch
`overnight-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-18 (scaffolded from the research in
`tasks/archive/2026/11/18/research-numeric-symbolic-mode-threading.md`)

## Outcome

`float_close_to_zero` is now `bool | None = None` at every site:
- `MultiVectorBase.is_orthogonal_to` / `is_parallel_to`;
- `transforms.require_on_line`, `coordinate_along` and the four line-to-line and line-to-plane
  factories, plus `transforms._is_zero`;
- `frame.are_linearly_independent` / `is_frame` / `require_frame`;
- the generated `Vector.line_to_line_*` / `line_*_plane_*` methods.

`None` means "a tolerance when the inputs hold floats, exact otherwise". It is resolved at the
comparison by two new public helpers in `src/gacalc/base.py`:
- `resolve_float_tolerance(flag, values)` returns the caller's `True`/`False`, or else
  `has_float_coefficients(values)`;
- `has_float_coefficients(values)` treats any Python `float` or sympy `Float` coefficient as float
  input.

A factory's call-time checks resolve against the call's input, which avoids the closure trap the
research described. An explicit `True` / `False` still decides.

- **`frame.py`:**
  - `_has_float` is gone, replaced by the shared helper;
  - `coefficients()` and the inverses' `coordinate()` no longer pass a flag, because
    `coordinate_along` decides from the same values;
  - `are_linearly_independent`'s doctest now shows the default being tolerant for floats, with
    `False` giving exactness.
- **The generator:** the emitted signature and docstring are updated. The plane maps' zero-shadow
  check calls `resolve_float_tolerance`, and only g3, which has those maps, imports it.
- **The intermediate layers still pass the flag on.** Passing `None` through is correct, since the
  bottom-level comparison resolves it against its own inputs, and it keeps an explicit override
  working end to end. The research's "stop passing it" was optional, and removing the parameters
  would have dropped the override.
- **Tests:**
  - `tests/test_float_tolerance_default.py` (5): floats are tolerant by default; `False` is exact
    for floats; exact input stays exact; `True` forces the tolerance; a factory built from exact
    vectors is tolerant when called on float input.
  - `tests/test_line_to_line_projection.py::test_coordinate_along` pinned the old exact default for
    floats. It now asserts the tolerant default and uses `float_close_to_zero=False` for the
    raising case.
- **Docs:**
  - `CHANGELOG.md` › Changed, with the behaviour change called out;
  - `tasks/reference/numeric-symbolic-mode.md` now opens with "Now: the recommendation is
    implemented", and its inventory is renamed "Before … (as researched)".

## Judgment calls

- **sympy `Float` counts as float input.** `tasks/archive/2026/11/18/inverse-float-versor-rounding.md`
  found that `Frame` produces sympy `Float`s from Python-float input. A check for Python `float`
  alone would have treated those as exact.
- **`_is_scalar_up_to_rounding`** (from the same batch) now uses `has_float_coefficients`, so there
  is one definition of "inexact".

## Verification

- ruff and `ty check` were clean on `base.py`, `transforms.py`, `frame.py` and the generator, and on
  the regenerated g1–g3 (`ty check --no-respect-ignore-files`, together with `base.py` and
  `transforms.py`).
- The host fast suite passed: 1898 passed, 2 skipped (GL excluded on the host).
- All seven slow `tests/test_frame_class.py` cases passed (24 min 45 s).
- The batch's final container gate covers GL, `format.sh`, the generator's determinism and the doc
  regions.
