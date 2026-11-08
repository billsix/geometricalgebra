# `project_sp`/`reject_sp`: raise on `b` along e₃, and accept `Gn` input

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 2
**Difficulty:** 2
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1, §6.1 (found independently by two readers)

## BLUF

`gacalc.standardposition.project_sp(a, b)` returns `Vector(nan, nan, nan)` without raising when `b`
lies along e₃. It also crashes on `Gn` input. Done means:

- it raises a named `ValueError` for a `b` along e₃;
- it checks that both inputs are vectors;
- it reads coordinates in a way that works for `Gn` too;
- it has a doctest and tests for those cases.

## Context

**The bugs.** Re-checked 2026-11-08:

```
>>> project_sp(1*g3.e_1, 1*g3.e_3)
g3.Vector(coeff_e_1=nan, coeff_e_2=nan, coeff_e_3=nan)
```

The first plane rotation divides by `|xy-part| = 0`. The module docstring documents this caveat,
but nothing checks for it.

With `Gn` input, `b_x, b_y, b_z = list(b)` fails ("not enough values to unpack"), because iteration
over a `Gn` omits zero coefficients. `src/gacalc/standardposition.py` reads coordinates with
`list(v)` in four places.

**Rules that apply** (`CLAUDE.md`):

- check "must be a vector" with `MultiVectorBase.require_vectors`;
- read a coefficient with `value.coefficient(blade)`;
- annotate every binding — the tuple unpacks and the `cos: object`/`sin: object` parameters are
  flagged in the review (§4.3).

**Existing tests:** `tests/test_standardposition.py`, numeric and symbolic on `g3`.

## Plan

- [ ] Validate the inputs with `require_vectors([a, b], "project_sp")`.
- [ ] Read coordinates through one `coordinates(v)` helper built on `coefficient(e_i)`. Annotate
  every binding, and type `cos`/`sin` as `Real`.
- [ ] Raise `ValueError` when `b`'s xy-part is zero, with a message pointing at the canonical
  `projected_onto`. Update the module docstring's caveat and the `Raises:` sections.
- [ ] Add a doctest to `project_sp`.
- [ ] Add tests: `b` along e₃ raises (numeric and symbolic `b = b_3 * e_3`); a non-vector input
  raises; `Gn` input matches `projected_onto`.
- [ ] Gate: `pytest -m "not slow"`, `ruff`, `ty`. Add a `CHANGELOG.md` Fixed entry.

## Open questions

None.
