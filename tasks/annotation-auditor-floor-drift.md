# Annotation auditor reports 43 findings; the exemptions doc says the floor is 32 — fix the code or the doc

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>): "make a task to investigate
tools/check_annotations.py reports 43 findings, but tasks/reference/type-annotation-exemptions.md still
says the floor is 32, and to make a decision to either fix something that's broken, or update the md
file to reflect the reality".

## BLUF

`python tools/check_annotations.py` reports **43 findings in 14 files**, while
`tasks/reference/type-annotation-exemptions.md` says the floor (re-baselined 2026-10-09) is **32 rows in
12 files**, every one a listed exemption or a classified-out alias/enum. Its rule is that "a row it
reports that is not in that doc is a genuine gap". For each of the 11 extra rows, decide: **annotate the
code** (a real gap) or **add it to the doc with its reason** (a real exemption). Done = the auditor's
count equals the doc's stated floor, every row is accounted for in the doc, and the doc's duplicated §5
bullet is fixed.

## Context (read first)

- `tasks/reference/type-annotation-exemptions.md` — the exemption catalogue and the floor.
- `tools/check_annotations.py` — the auditor (`--full` prints every row; `--kind`, `--path` narrow
  it). Informational, not a gate.
- `tasks/reference/python-coding-standard-gacalc.md` "Annotation sweep" and the shared
  `python-coding-standard.md` "annotate every binding" rule (a loop target is annotated by declaring it
  on the line above the `for`).
- The 2026-10-09 re-baseline record: `tasks/archive/2026/10/09/re-baseline-annotation-auditor.md`.

## Snapshot (agent, 2026-11-06; re-run before acting)

By kind, against the doc's floor:

| kind | now | doc floor | difference |
|---|---|---|---|
| ALIAS | 10 | 10 | — |
| ENUM | 3 | 3 | — |
| ANY | 9 | 9 | — |
| RET | 2 | 2 | — |
| PARAM | 1 | 1 | — |
| LOCAL | 4 | 4 | — |
| INVAR | 6 | 3 | +3 |
| LOOP | 8 | 0 | +8 |

The 11 extra rows (all added after the 2026-10-09 re-baseline):

- `tools/reorder_lean.py` (added 2026-10-28, commit `2076c75`): INVAR `_has_decl(buf)`,
  `split_blocks(body_lines)`, `reorder(plan)`; LOOP `group`, `k`, `key`. **These rows are gone:** the
  tool was removed on 2026-11-08 (`tasks/archive/2026/11/08/reorder-lean-tool-stale-plans.md`).
- `tests/test_frame.py`: LOOP `k` at four sites (tests added 2026-10-26 to 2026-10-29).
- `tests/test_graded.py`: LOOP `val`. The doc's §5 lists `test_graded`'s `cases`/`val`/`d` as LOCAL
  exemptions, so check whether this row is that exemption in a new shape or a new site.

**The duplicated §5 bullet:** §5 lists `tests/test_odd3.py`'s `conjugated` twice, in two wordings.
Merge them into one.

## Plan

1. Re-run `python tools/check_annotations.py --full` and refresh the snapshot.
2. For each extra row, decide and record:
   - **LOOP rows:** most likely real gaps. Annotate by declaring the loop target on the line above the
     `for` (the house fix used in the 2026-10-09 re-baseline). Only exempt one if the declaration would
     lose type information (the §5 pattern).
   - **INVAR rows in `reorder_lean.py`:** none remain; the tool was removed on 2026-11-08 (see the
     row list above).
3. Fix the code for the gaps; add the true exemptions to the doc with their reasons; merge the
   duplicated §5 bullet; update the floor paragraph (count, file count, split, date, and this task as
   the record).
4. Gates: `make test`, `make format` (ruff + ty). Confirm the auditor's count equals the new floor.

## Open questions

None yet. If any row has no clear answer once read, raise it here before deciding.
