# `project_sp`/`reject_sp`: raise on `b` along e₃, and accept `Gn` input

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1, §6.1 (found independently by two readers)

## What was wrong

- `gacalc.standardposition.project_sp(a, 1*g3.e_3)` returned `Vector(nan, nan, nan)`. When `b` lies
  along e₃, the first plane rotation divides by `|b's xy-part| = 0`. The module docstring documented
  this caveat, but nothing checked for it.
- `Gn` input crashed ("not enough values to unpack"). The module read coordinates with `list(v)`, and
  iterating a `Gn` omits zero coefficients.
- Nothing checked that the inputs were vectors, there was no doctest, and the tuple unpacks and the
  `cos: object`/`sin: object` parameters were unannotated.

## What changed (`src/gacalc/standardposition.py`)

- `MultiVectorBase.require_vectors([a, b], "project_sp")` runs first.
- A nested `coordinates(v)` reads `v.coefficient(e_1/e_2/e_3)`, so `Gn` works. Every binding is now
  annotated, and `cos`/`sin` are typed `Real`.
- A `ValueError` is raised when `b_x == 0 and b_y == 0`, pointing at the canonical `projected_onto`.
  The module docstring's caveat and the two `Raises:` sections say so.
- `project_sp` gains a doctest: an exact-magnitude `b`, plus the e₃ error.
- New tests in `tests/test_standardposition.py` cover:
  - `b` along e₃ raising, for numeric input and for a symbolic `b_3 * e_3`, through both functions;
  - a non-vector `b` raising;
  - `Gn` input matching `projected_onto`/`rejected_away_from`.

  With the old module, 4 of them fail.
- `CHANGELOG.md` `[Unreleased]` › Fixed has an entry.

## Verification

- `pytest -m "not slow"` on the sandbox Python: 810 passed, 2 skipped.
- `ruff check`/`ruff format` and `ty check` on the touched files: clean.
