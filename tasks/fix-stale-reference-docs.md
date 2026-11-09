# Fix the stale and false claims in the reference docs

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §1.1, §1.2, §2.1

## BLUF

Several `tasks/reference/` docs state things the tree contradicts. Done means each listed claim is
corrected, and the dated 2026-10-04 Lean corpus review leaves `tasks/reference/` for
`tasks/review/2026/10/04/`, under the deep-review convention.

## Context

The claims, each verified by the review:

- `lean-ga-proof-architecture.md`: the G1/G2/G3 order (pre-2026-10-29); "31 modules"; frames
  listed as remaining; `dot_is_sym_part` called a coordinate form; "Projection/Projection2D".
- `lean-for-gacalc.md`: "~650 tests"; "32 files"; extra linters "set in `proofs/lakefile.toml`"
  (none are).
- `design-decisions.md`: the notebooks have "no execution gate"; `cross` among the declined
  features; a `.dockerignore` "can't fix" the elpa duplication.
- `book-and-docs-pipeline.md`: Sphinx as dnf packages; the nbconvert TeX installed
  "unconditionally"; `api.rst` covering "every package module"; the
  `nb_execution_raise_on_error` gate unmentioned.
- `generated-algebra-generation-cost.md`: the registry "only defines up to Trivector"; a done
  to-do about scoping `check-generated`.
- `symbolic-equality.md`: recommends the removed `_simplify_equal`.
- `openstax-math-pedagogy.md` §9: a 2026-08-03 snapshot in the present tense.
- `reduction-to-standard-position.md`: cites an archived task as future work.
- `proofs/README.md`: "31 modules"; `frame.py` uncovered; the parallel predicate's one direction.
- `lean-proof-corpus-review-2026-10-04.md`: a dated record sitting in `tasks/reference/`.

## Plan

- [ ] Correct each claim.
- [ ] `git mv` the corpus review to `tasks/review/2026/10/04/lean-proof-corpus-review.md`, with a
  banner saying what is out of date, and repoint every reference to it.
- [ ] Verify that every path cited in the changed docs exists.

## Open questions

None.
