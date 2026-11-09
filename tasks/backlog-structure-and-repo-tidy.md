# Backlog structure and repo tidy: merge the proof-notebook tasks, fix stale task claims, add missing BLUF/Context, remove leftovers

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §9.1, §9.2, §10.4, §1.2

## BLUF

Bring the open backlog (`tasks/*.md`) to the task-doc conventions and remove three leftover files.
Done means:

- the three proof-notebook tasks are one umbrella with its children;
- the stale claims listed below are corrected;
- every open task has `## BLUF` and `## Context` and a standard status;
- `TODO.org` and the two leftover codemods are `git rm`'d.

## Context

Read first: the task-doc conventions (github.com/billsix/runClaudeInContainer
`tasks/reference/task-doc-conventions.md`) and the record's §9.1 and §9.2. The earlier
`tasks/archive/2026/11/09/backlog-hygiene.md` already did §9.1's first three items (it archived
`generalize-sandwich-other-grades`, re-rated `define-frame`, and reconciled frame coverage). Don't
redo them.

**Still open from §9.1** (re-check each before editing):

- **Three proof-notebook tasks overlap**, two stating the same `show_cancellation` / `\underbrace`
  requirement: `tasks/investigate-lean-to-python-proof-notebooks.md`,
  `tasks/reference-doc-lean-workflow-and-proof-notebooks.md` and
  `tasks/proof-notebooks-student-math-notation-style.md`. Make one the umbrella, per "Step tasks" in
  the conventions.
- **`tasks/frame-inverse-head-first-recursion.md`**: Q3 is marked "yes" while the next sentence
  recommends "no".
- **`tasks/apply-2026-11-06-naming-and-scope-rules.md`** still calls the frame-inverse task blocked;
  it was unblocked on 2026-11-07.
- **`tasks/frame-svd-investigation.md`** waits on a task that finished on 2026-11-04.
- **`tasks/annotation-auditor-floor-drift.md`** says 43 findings in 14 files; re-run
  `python tools/check_annotations.py` and use the current count.
- **`tasks/generalize-reject-reflect-higher-grade.md`** Q6 overlaps
  `tasks/line-to-line-rejection-invertible-function.md` and
  `tasks/vector-and-plane-invertible-project-reject.md`. Cross-link them, or move Q6.
- **`tasks/push-delicate-coordinate-core-tier.md`** lists deleted `_coord` lemmas as retained.
  Re-count the live ones with `grep -rn "_coord" proofs/GacalcProofs`.
- **`tasks/lean-proofs-remove-extras.md`** says it audited 32 files; there are now more. Correct the
  count. Its own fixes are its own work, not this task's.
- **`tasks/port-book-to-osbook-latex.md`**: its "revisit after" investigation was archived on
  2026-10-09. Say the condition is met and re-rate it.
- **`tasks/displaygraded-geometric-plots.md`** points at the archived `epix-plot-integration.md`.

**§9.2, re-checked 2026-11-09:**

- **No `## BLUF`:** affine-flats-lines-planes-from-points, branded-coordinate-space-types,
  composable-function-followups, displaygraded-geometric-plots, document-codegen-flow-pedagogical,
  generalize-reject-reflect-higher-grade, grassmann-absolute-relative-units,
  notebook-dot-wedge-projection-demo, parallelogram-foundational-narrative.
- **No `## Context`:** branded-coordinate-space-types, displaygraded-geometric-plots,
  generalize-reject-reflect-higher-grade, proof-notebooks-student-math-notation-style,
  push-delicate-coordinate-core-tier.
- **Non-standard statuses** ("on hold", "investigated"): `grep -ln "on hold\|investigated"
  tasks/*.md` finds lean-frame-class-invertible-function, port-cayley-graph-from-mvp-investigation,
  port-book-to-osbook-latex and define-frame. Check each hit, since the words may be prose.
- Two tasks say "Part of" the archived `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`.
- Four tasks use `2026/…/x.md` paths instead of repo-root-relative ones.
- grassmann's "do not re-raise unprompted" conflicts with its `Recheck:` field.

**Leftover files:**

- `TODO.org` (repo root): every item is done (§1.2).
- `tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py` and `prose_codemod.py` belong to the
  archived `tasks/archive/2026/08/13/drop-graded-type-dimension-suffixes.md` and should have been
  removed in its archive commit (§10.4). The other adhoc directory,
  `tasks/adhoc/typing-base-return-types-redesign/`, belongs to an open task; keep it.

## Plan

- [ ] Pick the proof-notebook umbrella, move the shared requirement into it, and give the children
  `Part of:` / `Depends on:` headers.
- [ ] Fix each §9.1 claim listed above, re-checking it first.
- [ ] Add BLUF and Context to the tasks listed. Write them from each task's own content, not
  placeholders.
- [ ] Normalize the statuses, the dead "Part of" pointers, the relative paths, and grassmann's Recheck.
- [ ] `git rm TODO.org tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py
  tasks/adhoc/drop-graded-type-dimension-suffixes/prose_codemod.py`.
- [ ] Gate: `grep -L "^## BLUF" tasks/*.md` and `grep -L "^## Context" tasks/*.md` print nothing.
  Every path cited in an edited task exists.

## Open questions

None.
