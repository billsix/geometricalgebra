# Library traps that return wrong results quietly: zero `unit_pseudoscalar`, `signed_content` on dependent `Gn`, mutable `Gn` blade dict

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §4.3

## BLUF

The review rated three §4.3 findings low, but each one quietly returns a wrong result or corrupts
state, so they need behaviour changes and tests rather than a text cleanup. Done means each is
confirmed or ruled out with a REPL repro, and each confirmed one is fixed with a test, or documented
as intended. `make test` must pass.

## Context

Read first: `CLAUDE.md` › "Architecture" and `tasks/reference/blade-dict-interchange.md` (the
eager/lazy contract, and the graded silent drop, the "exp() trap").

- **Graded classmethods that return zero silently** (VERIFIED in the record):
  `g3.Vector.unit_pseudoscalar(3)` returns a zero `Versor` instead of raising, because the
  pseudoscalar isn't a vector and the graded type drops its blade. `bases` and `symbolic_multivector`
  have the same trap. The likely fix is a `ValueError` naming the type, matching the "must be a
  vector" guard (`MultiVectorBase.require_vector`).
- **`signed_content` on `Gn` with a dependent set** (`[1 * e_1, 2 * e_1]`): it infers n = 1 and
  raises "wrong count", instead of returning the documented 0. This is a LEAD; reproduce it first.
- **`Gn` is not frozen, and `to_blade_dict()` returns its internal dict.** Mutating the returned dict
  would corrupt the shared `e_1` constants. This is a LEAD. If it is confirmed, return a copy (or a
  `MappingProxyType`) and measure the cost on `tools/bench.py`, because `Gn` is the slow oracle on
  purpose.

`make generate` before reading any generated code.

## Plan

- [ ] Reproduce each finding in a REPL, after `make generate`. Drop any that don't reproduce, and say
  so here.
- [ ] Write a failing test for each confirmed finding, then fix it, in `base.py`/`gn.py`/`measure.py`
  or in the generator (`tools/gen_specialized.py`) for the graded classmethods.
- [ ] Add a `CHANGELOG.md` `[Unreleased]` entry for any change in behaviour. A new `ValueError` is a
  breaking change.
- [ ] `make format`, `make test`.

## Open questions

None.
