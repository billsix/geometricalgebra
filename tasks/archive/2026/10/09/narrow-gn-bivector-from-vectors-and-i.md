# Narrow `Gn.bivector_from_vectors` / `Gn.i` to return `Gn`

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)

## BLUF

`MultiVectorBase.bivector_from_vectors(a, b)` and the `i(a, b)` classmethod were typed
`-> MultiVectorBase`. The generated graded classes narrow them (to `Bivector`), but the
hand-written `Gn` never did, so adopting the plane helpers in `Gn`-typed code (e.g.
`notebooks/displaymv.py`, `tests/test_conformance.py`) would *downgrade* a `Gn` binding to the
base type. This task added hand-written `Gn` overrides that narrow the return to `Gn`, with no
new logic, unblocking `tasks/archive/2026/10/09/use-bivector-from-vectors-and-i-in-notebooks-and-tests.md`.

## What was done

- `src/gacalc/gn.py`: a `Gn.bivector_from_vectors(cls, a, b) -> Gn` classmethod override that
  delegates to the base (`typing.cast(Gn, super().bivector_from_vectors(a, b))`); and `Gn.i`
  retyped `-> Gn` with its `plane` local narrowed to `Gn` (the body already chained through
  `bivector_from_vectors(...).normalize()`, and `normalize`/`outer_product` return `Self`, so the
  chain now resolves to `Gn`). No runtime logic changed.
- `tests/test_unit_bivector_i.py`: `test_gn_bivector_and_i_narrow_to_gn` asserts the narrowing
  statically (`typing.assert_type(..., Gn)`) and at runtime (`isinstance(..., Gn)`); the file's
  stale "statically typed MultiVectorBase" comment was corrected (the graded classes narrow to
  `Bivector`, `Gn` to `Gn`).
- `CHANGELOG.md` `[Unreleased]` › Changed: a non-breaking typing-refinement entry — runtime
  behavior and the Python names are unchanged, only the static return type is more precise.

Public parameter names and `N803` were left untouched (narrowing is return-type only, so there is
no breaking keyword-arg change).

## Gate

`make format` (ruff + ty, so the `assert_type` narrowing is checked) and `make test` (the new test runs) both green.

## Open questions

None.
