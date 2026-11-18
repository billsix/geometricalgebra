# Write a reference doc: the Lean → symbolic-test → student-proof-notebook workflow

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Part of:** `tasks/proof-notebooks-student-math-notation-style.md` (the proof-notebook umbrella)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-09-30

## Outcome

`tasks/reference/lean-python-notebook-workflow.md` now records the maintainer's method and its
purpose. It also records the two things no doc had written down:

1. **Lean ↔ Python twins and drift.** A Lean theorem and each of its Python twins carry the same
   comment, `twin: <fully qualified Lean name>`: a `--` comment in Lean, a `#` comment in Python. In
   a notebook the comment goes in the first code cell, where students don't see it. `git grep` with
   a `'*.py' '*.lean'` pathspec lists one theorem's members, and a counting pipeline lists orphans.
   When one member's statement changes, the others change in the same commit.
2. **"Verify, don't derive."** A proof notebook should use exact canonical forms, make one move per
   `show_mult` row, and show both sides before their difference. The cancellation display (each
   cancelling term marked with `\underbrace{…}_{\text{cancel}}`) is not built yet. That is
   `tasks/investigate-lean-to-python-proof-notebooks.md`'s job.

The projection trio carries the first tags, as the worked example:
- `proofs/GacalcProofs/StandardPosition.lean`: `projectSP_eq_proj`, `rejectSP_eq_reject`;
- `tests/test_standardposition.py`: the two `*_matches_canonical_symbolic` tests;
- `book/docs/notebooks/proof-projection.py`.

Other pairs that already cite each other in prose get a tag when next touched; no backfill was done.
`CLAUDE.md` ("Every piece of math comes in three forms") points to the doc. Four task docs that cited
this task now cite the reference doc.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. One doc, two sections (author side, student side).
2. Comment tags on both sides, found by grep, with no checker script.

The task predated several changes, and the doc was written against the current tree:
- `show_mult` now lives in `gacalc.nbdisplay`;
- the book notebooks already follow the symbolic, both-sides style;
- proof pages now pair a `proof-*.rst` with a `proof-*.py` notebook.

## Verification

- `lake build GacalcProofs.StandardPosition` passed with the tags in place.
- ruff passed on the tagged test and notebook.
- The orphan-count pipeline printed 3 for `projectSP_eq_proj` (Lean, test, notebook) and 2 for
  `rejectSP_eq_reject`.
- Every path cited in the doc exists.
