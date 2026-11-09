# Number the 2026-11-08 review's follow-ups (`[F1]`…`[F38]`) and cite the IDs from its tasks

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** conversation, 2026-11-09 (the review-status tool's first run on this repo)

## BLUF

The status tool reports every follow-up of `tasks/review/2026/11/08/repo-review.md` as matched "by
§" only, so its 31 "done" rows can't be trusted. The record predates follow-up IDs. Done means:

- each of the record's 38 "Suggested follow-ups" bullets starts with an ID `[F1]`…`[F38]`, added
  under a dated note;
- each task that cites the record names the IDs it covered in its `**Source:**` line;
- `python3 ~/.claude/reference/review_status.py` reports no "(by §)" rows.

## Context

- **The tool and its conventions** live in github.com/billsix/runClaudeInContainer, in
  `tasks/reference/review_status.py` and `tasks/reference/repo-review-conventions.md` ("The record's
  layout", "Lifecycle"); the record is mounted at `~/.claude/reference/`. The tool matches a bullet
  with an ID only by ID, and a bullet without one by section, marked "(by §)". It was built in that
  repo's `tasks/archive/2026/11/09/review-status-tool.md`.
- **Why section matching is not enough here.** A section holds several findings, so one archived task
  marks every bullet in its section done. On 2026-11-09 the tool reported: 38 follow-ups, 31 done,
  0 open, 7 untracked, with all 31 "done" matched by section only. Two examples:
  - "Optional: Pin or lock the image's dependencies (§8.1)" shows done because of
    `jupyter-bind-localhost` and `dockerfile-masked-install-and-entrypoint`, which also cite §8.1.
  - "Optional: Merge the three proof-notebook tasks (§9.1)" shows done because of `backlog-hygiene`.
- **The record is frozen.** The conventions allow two exceptions, both made under a dated note:
  correcting the reviewer's own factual error, and answering an open question. Numbering the bullets
  changes no finding, but it is a third kind of edit (see Open questions).
- **The citing tasks.** 24 archived done-records, in `tasks/archive/2026/11/08/` and
  `tasks/archive/2026/11/09/`, each with a `**Source:**` line on line 4. List them with
  `grep -rn "Source:\*\*.*2026/11/08/repo-review" tasks`. Several cite sections that span more than
  one bullet (e.g. `fix-library-medium-bugs` §4.2 covers "Fix the medium library bugs" but not
  "Replace the bare asserts", which is also §4.2). Read each done-record to decide which bullets it
  actually covered.
- **Two untracked items worth checking:** the §5.2 `check_annotations.py` bullet is handled by the
  open `tasks/annotation-auditor-floor-drift.md`, whose `**Source:**` line doesn't cite the record.
  Adding the record and the ID there would make that bullet show as open.

## Plan

- [ ] Number the 38 bullets `[F1]`…`[F38]` in document order across all three tiers, under one dated
  note at the top of "Suggested follow-ups": (William Emerison Six <billsix@gmail.com>, <date>:
  follow-up IDs added for `review_status.py`; no finding changed).
- [ ] For each of the 24 citing tasks, read the done-record, decide which IDs it covered, and append
  them to its `**Source:**` line (`… §4.2 F14`). Keep the line on one line.
- [ ] Add the record, §5.2 and its ID to `tasks/annotation-auditor-floor-drift.md`'s `**Source:**`.
- [ ] Re-run `python3 ~/.claude/reference/review_status.py` from the repo root. Expect no "(by §)" rows
  and an honest done/open/untracked split, and record the before/after counts here.
- [ ] In runClaudeInContainer (and its runCrush mirror), add the retro-numbering of follow-ups to the
  conventions' list of allowed dated edits, if question 1 is answered yes.

## Open questions

1. Is retro-numbering a frozen record's follow-ups an allowed edit (under a dated note, since no
   finding changes)? Recommendation: yes, and add it to `repo-review-conventions.md` as the third
   exception. The alternative is to leave the record alone and put the ID → bullet map in this task,
   which the tool cannot read.
