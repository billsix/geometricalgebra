# Retire `tools/reorder_lean.py`

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.1
**Decision:** retire the tool, not update it. William Emerison Six <billsix@gmail.com>, 2026-11-08,
choosing option (a) over (b) "update its PLANs and wire `--check` in".

## What was wrong

`tools/reorder_lean.py` reorders declarations in the `G1`/`G3` Lean files to a stored per-file PLAN.
It did its one job in `tasks/archive/2026/10/29/reorder-gn-lean-to-teaching-order.md`, then went
stale:

- `G1 --check` reported "WOULD change", because its PLAN was the pre-2026-10-29 order (`mul, wedge,
  add, smul`). Applying it would have undone the teaching order.
- The `G3` PLAN aborted on 18 names it didn't place.
- There was no `G2` PLAN.
- Nothing ran its `--check`, although its docstring said it "can gate drift".

## What changed

- `git rm tools/reorder_lean.py`. `git log --all -- tools/reorder_lean.py` recovers it.
- Its per-file ruff exemption (`E501`, `T201`) and the comment above it are gone from
  `pyproject.toml`.
- `tasks/reference/lean-ga-proof-architecture.md` no longer tells readers to run its `--check`. It
  records that the reorder used this one-shot tool, which is now removed. New declarations keep the
  order by hand, per `CLAUDE.md` and `tasks/reference/algebra-teaching-order.md`.
- `tasks/annotation-auditor-floor-drift.md` notes that the tool's audit rows are gone.

## Verification

- `pyproject.toml` parses (`tomllib`), and `ruff check .` is clean.
- `git grep reorder_lean` outside the archive and the review finds only the two updated docs.
- `tools/check_annotations.py` now reports 42 findings in 15 files.
