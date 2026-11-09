# `tools/` low cleanup: generator dead code and history comments, ePiX tool gaps, the unused-hypothesis detector

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §5.4

## BLUF

Fix the low-severity findings in the code generator and the repo tools. Done means each item below is
fixed or dropped with a reason, generation is unchanged (or changed on purpose), and `make format`,
`make test`, `make check-generated` and `make check-regions` pass.

## Context

Read first: `CLAUDE.md` › "Code generation" (generate first, read the real output, then change the
generator) and `tasks/reference/code-generator-architecture.md`. Re-checked 2026-11-09:
`ROTATE_90_METHOD_DOC` is now emitted (`tools/gen_specialized.py`, used in the `rotate_90_degrees`
class body), so the record's "never emitted" item is dropped.

**`tools/gen_specialized.py` and `tools/astbuild.py`** (line numbers from the record; match on
content):
- the `term_grade_key` docstring says a CSE temporary "sorts last", but the code raises `ValueError`
  (no current output reaches that path);
- `result_block_stmts` never uses its `owner` parameter;
- `astbuild.return_construct`'s non-final branch and `construct_type_self` are unreachable;
- `full_name_for(dim)` ignores `dim`;
- history comments: "the old cast(Self, …) was unsound", "replaces the old bespoke bodies",
  "until now", and "matching the string gen" (`astbuild.bool_or`);
- docstrings still use the old suffixed names `ScalarN`/`Scalar_n`/`Vector_n`.

**Other tools:**
- `tools/check_epix_keywords.py` scans only the top level of `book/figures/epix`, so the live figures
  drawn in `book/docs/notebooks/frame-qr-*.py` go unchecked (LEAD). It also skips chained calls.
- `tools/render_epix_figures.py` catches only `CalledProcessError`, so a `FileNotFoundError` from
  `flatten_png` stops the loop. Outputs of deleted figures are never removed.
- `tools/detect_unused_hypotheses.py` is report-only (exit 0) and wired to nothing. Its text search
  flags hypotheses consumed implicitly by `simp`/`field_simp`, and it duplicates Lean's
  `unusedVariables`. Delete it (Decisions, 1).

**Out of scope:** the unannotated bindings in §5.4 belong to `tasks/annotation-auditor-floor-drift.md`.

## Plan

- [ ] `make generate` and keep a copy of `src/gacalc/g*.py`.
- [ ] Fix the generator items, regenerate, and diff against the copy. Dead-code removal must leave the
  output byte-identical; a docstring fix changes only docstrings.
- [ ] Extend `check_epix_keywords.py` to the notebook figures, run it with `--fix`, and check the
  result.
- [ ] Make `render_epix_figures.py` report a missing file and go on, and remove orphaned outputs.
  Then run `make docs` (needs `BUILD_DOCS=1`).
- [ ] `git rm tools/detect_unused_hypotheses.py`, and remove any mention of it (`grep -rn detect_unused_hypotheses .`, excluding `tasks/archive/`).
- [ ] `make format`, `make test`, `make check-generated`, `make check-regions`.

## Decisions

1. Delete `tools/detect_unused_hypotheses.py` (William Emerison Six <billsix@gmail.com>, 2026-11-09): Lean's `unusedVariables` lint and the
   delete-and-rebuild method in `CLAUDE.md` › "Coordinates only when needed" already cover it.

## Open questions

None.
