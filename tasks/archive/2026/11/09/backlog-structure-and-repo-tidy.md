# Backlog structure and repo tidy: proof-notebook umbrella, stale task claims, BLUF/Context everywhere, leftovers removed

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §9.1, §9.2, §10.4, §1.2

## What changed

- **Proof-notebook umbrella.** `tasks/proof-notebooks-student-math-notation-style.md` (already
  self-described as an umbrella, and the lowest priority number of the three) is the parent. It gained
  a `## Context` naming its two children and holding the **shared requirement** both used to state:
  show the cancellation with `\underbrace{…}_{cancel}` through a `show_cancellation` helper, not a bare
  `0`.
  - `tasks/reference-doc-lean-workflow-and-proof-notebooks.md` (the *why*) has a `Part of:` header.
  - `tasks/investigate-lean-to-python-proof-notebooks.md` (the *how*) has a `Part of:` header instead
    of the archived Lean umbrella, and now points at the umbrella for the requirement.
- **Stale claims fixed:**
  - `frame-inverse-head-first-recursion` Q3 now says the "yes" overruled the original "no";
  - `apply-2026-11-06-naming-and-scope-rules` no longer calls that task blocked;
  - `annotation-auditor-floor-drift` has the current auditor count (42 findings in 15 files, 10 above
    the floor);
  - `generalize-reject-reflect-higher-grade` Q6 cross-links its two overlapping tasks;
  - `lean-proofs-remove-extras` notes 34 files now;
  - `port-book-to-osbook-latex` says its revisit condition is met (still parked), and its table row
    gives the investigation's answer;
  - `displaygraded-geometric-plots` points at the archived `epix-plot-integration.md`.
- **Structure:**
  - Every open task now has `## BLUF` and `## Context`. Six tasks whose `## Goal` already stated the
    task and its deliverable had it renamed to BLUF. `branded-coordinate-space-types`,
    `composable-function-followups` and `grassmann-absolute-relative-units` got new BLUFs.
    `displaygraded-geometric-plots` ("Why" renamed), `generalize-reject-reflect-higher-grade`,
    `branded-coordinate-space-types` and `push-delicate-coordinate-core-tier` got Context sections.
  - Statuses: "on hold" became `parked`, and "investigated" became `proposed — investigated …`.
    `grassmann` is no longer `blocked`, since its gate is the maintainer's answers, not an external
    condition. Its `Blocked on:`/`Recheck:` lines are gone, which ends the conflict with "do not
    re-raise".
  - The two "Part of" pointers to the archived Lean umbrella now say it is done and name
    `tasks/reference/lean-ga-proof-architecture.md`. The `2026/…` paths are repo-root-relative.
- **Removed:** `TODO.org` (every item done), and the two leftover codemods of the archived
  drop-graded-type-dimension-suffixes task. `tasks/adhoc/typing-base-return-types-redesign/` belongs
  to an open task and stays.

## Dropped as not reproduced

- `frame-svd-investigation`'s status already said its prerequisite was done.
- `push-delicate-coordinate-core-tier`: every `_coord` lemma it lists as retained still exists
  (checked by name with `grep -rw` in `proofs/GacalcProofs`).

## Verification

`grep -L "^## BLUF" tasks/*.md` and `grep -L "^## Context" tasks/*.md` print nothing. Every
`tasks/….md` path cited in an edited task exists, except two that the tasks name as files still to be
written: `tasks/reference/grassmann-units.md` and `tasks/reference/lean-python-notebook-workflow.md`.
