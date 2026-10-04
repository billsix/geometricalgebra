# Narrow `Gn.bivector_from_vectors` / `Gn.i` to return `Gn` (typing prerequisite)

**Status:** proposed — filed on the maintainer's go-ahead 2026-10-04; implementation needs its own
go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)
**Next:** `tasks/use-bivector-from-vectors-and-i-in-notebooks-and-tests.md` (depends on this).

## BLUF

`MultiVectorBase.bivector_from_vectors(a, b)` and the concrete `i(a, b)` classmethods are typed
`-> MultiVectorBase`. The generated graded classes narrow them (Tier-2 narrowing in
`tools/gen_specialized.py`, so `g3.Vector.i(...)` is a `g3.Bivector`), but the hand-written `Gn` in
`src/gacalc/gn.py` never got the same treatment, so adopting the helpers in `Gn`-typed code
(`notebooks/displaymv.py`, `tests/test_conformance.py`) would *downgrade* a `Gn` binding to the
base type. This task adds hand-written overrides in `gn.py` typing `Gn.bivector_from_vectors(a, b)
-> Gn` and `Gn.i(a, b) -> Gn`. "Done" = both overrides exist with the narrowed return type, behaviour
unchanged (`i` still raises `ValueError` on parallel vectors), `ruff` + `ty` clean, the existing
`tests/test_unit_bivector_i.py` still passes, and a test pins the narrowed type.

## Context

- The wedge of two `Gn` vectors, and its normalization, *is* a `Gn`, so `-> Gn` (or `-> Self`) is
  sound; this is purely a typing change. Definitional equality `Gn.bivector_from_vectors(a, b) == a ^ b`
  is already confirmed (see the dependent task's Finding).
- `Gn.i` already exists in `gn.py` as a classmethod typed `-> MultiVectorBase`; `bivector_from_vectors`
  is inherited from `base.py` with no `Gn` override. Mirror the generated classes' narrowing shape, by
  hand (`Gn` is not generated; see `CLAUDE.md` › Module layout).
- Why it was filed: `tasks/use-bivector-from-vectors-and-i-in-notebooks-and-tests.md` has no clean
  adoption sites until this lands (its Finding of 2026-08-27, re-verified 2026-10-04).

## Plan

- [ ] Add `Gn.bivector_from_vectors(cls, a, b) -> Gn` (delegate to the base implementation, narrow
      the type; no new logic).
- [ ] Retype `Gn.i(cls, a, b) -> Gn` (same body).
- [ ] A test asserting the narrowed type statically (`ty`) and at runtime
      (`isinstance(Gn.i(a, b), Gn)`), next to `tests/test_unit_bivector_i.py`.
- [ ] `make format` (ruff + ty) and `make test` green; `CHANGELOG.md` `[Unreleased]`: additive typing
      refinement, non-breaking.

## Open questions

None.
