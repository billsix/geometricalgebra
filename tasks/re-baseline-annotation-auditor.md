# Re-baseline the annotation auditor: classify the 18 rows added since the September sweep

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-10-09 (agent, from a finding in `tasks/archive/2026/10/09/coordinate-proofs-alongside-early-results.md`;
go-ahead William Emerison Six <billsix@gmail.com> pending)

## BLUF

`python tools/check_annotations.py` reports 47 rows in 15 files; `tasks/reference/type-annotation-exemptions.md`
documents a 29-row floor where every row is a listed exemption. The 18 extra rows are in files written
after the 2026-09-09 sweep that were never run through the auditor. "Done" = each of those rows is
either annotated or added to the exemptions doc with its reason, the doc's floor sentence is restated,
and `make format` is green.

## Context

- The auditor and its doc: `tools/check_annotations.py` (informational, not a gate) and
  `tasks/reference/type-annotation-exemptions.md` ("Current state (2026-10-09)" has the breakdown).
- The standard the rows are judged against: `CLAUDE.md` › "Coding standard (Python)" and the shared
  `python-coding-standard.md` ("annotate every binding"; loop targets declared on the line above;
  the *don't fight the checker* escape hatch).
- Where the rows are: `tools/check_epix_keywords.py` (7 — five loop targets, one alias, one invariant
  list param), `tools/detect_unused_hypotheses.py` (4 loop targets), `src/gacalc/standardposition.py`
  (3 locals: `cls`, `xy_magnitude`, `magnitude`), `tools/derive_lean_algebra.py` (2), `tests/test_graded.py`
  (3). Run `python tools/check_annotations.py --full` for the exact lines.

## Plan

1. Annotate the mechanical majority (loop targets → a declaration above the `for`; the three
   `standardposition` locals; the `test_graded` locals).
2. Judge the rest against the exemptions doc's existing five groups (an invariant `list` param that is
   mutated stays invariant; an alias stays an alias) and add each surviving exemption there with its reason.
3. Restate the floor sentence in the exemptions doc with the new count; `make format`.

## Open questions

None.
