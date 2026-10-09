# Re-baseline the annotation auditor: classify the rows added since the September sweep

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-10-09 (agent, from a finding in the coordinate-proofs task; go-ahead
William Emerison Six <billsix@gmail.com>)

## BLUF

`python tools/check_annotations.py` reported 47 rows against a documented 29-row floor; the 18
extra rows were loop targets and locals in files written after the 2026-09-09 sweep that had
never been run through the auditor. Each was resolved: the mechanical majority annotated, two
read-only `list` params widened to `Sequence`, and one local (`test_odd3.conjugated`) added to
the exemptions with its reason. The floor is restated at **32 rows, every one a listed exemption
or a classified-out alias/enum**, and `make format` is green.

## What was done

**Annotated (the mechanical majority):**
- Loop targets, with a type declaration on the line above each `for`:
  `tools/check_epix_keywords.py` (`tint`; `arg`/`param`; `lineno`/`col`/`name` in two loops;
  `report`), `tools/detect_unused_hypotheses.py` (`path`; `idx`/`name`/`s`; `bm`; `nm`),
  `tools/derive_lean_algebra.py` (`grade`).
- `src/gacalc/standardposition.py` locals: `cls: type[MultiVectorBase]`, and
  `xy_magnitude`/`magnitude` typed `Real` (added `Real` to the import).

**Widened two read-only `list` params to the covariant `Sequence`** (clears the INVAR flag, since
neither is an out-parameter): `check_epix_keywords.apply(edits)` and
`derive_lean_algebra.dump(all_blades)`.

**Exempted, with the reason in `tasks/reference/type-annotation-exemptions.md` §5:**
`tests/test_odd3.py`'s `conjugated` — annotating it widens `coeff_e_123` to `Real`, and sympy's
stubs have no `simplify` overload for a bare `int`/`float`, so the annotation would fail the next
line; the in-code comment already explains this.

**Restated the floor** in the exemptions doc: **32 rows in 12 files** = 13 classified-out (10 type
aliases, 3 enum members, which the auditor prints but does not treat as gaps) + 19 listed
exemptions (9 `Any`, 2 returns, 1 param, 3 invariant params, 4 locals).

## Gate

`make format` green (ruff + ty, so every new annotation type-checks); `make test` unaffected (no
runtime logic changed); `python tools/check_annotations.py` = 32 rows, matching the restated floor.

## Open questions

None.
