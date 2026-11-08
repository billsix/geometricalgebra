# `tools/reorder_lean.py`: retire it, or update it, before anyone runs it

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 3
**Difficulty:** 1 to retire; ~3 to update and wire in
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.1

## BLUF

`tools/reorder_lean.py` reorders declarations in the `G1`/`G3` Lean files to a stored PLAN. The
PLANs date from before the 2026-10-29 teaching-order reorder, so running it would undo that work.
Done means the tool can no longer mislead: either it is removed, or its PLANs match the files and
its `--check` runs as a gate.

## Context

What the review found (re-check before acting):

- `python tools/reorder_lean.py G1 --check` reports "WOULD change". Its PLAN orders
  `mul, wedge, add, smul`, but the files now put `add`/`sub`/`neg`/`smul` before `mul`
  (`tasks/reference/algebra-teaching-order.md` Part III).
- The `G3` PLAN aborts on 18 names it doesn't place.
- There is no `G2` PLAN.
- Its docstring says `--check` "can gate drift", but no `make` target or script runs it.
- `pyproject.toml` carries a per-file ruff exemption for it (`E501`, `T201`).
- Its last commit is `2076c75` ("extracted to tools").

Its job was done by `tasks/archive/2026/10/29/reorder-gn-lean-to-teaching-order.md`, and nothing
calls it.

## Plan

Depends on open question 1.

- **If (a) retire:**
  - [ ] `git rm tools/reorder_lean.py`, and remove its `pyproject.toml` exemption.
  - [ ] Fix any doc that names it (`git grep reorder_lean`).
  - [ ] The archived reorder task keeps the history; `git log` recovers the script.
- **If (b) update:**
  - [ ] Regenerate the G1/G2/G3 PLANs from the current files.
  - [ ] Wire `--check` for all three into `proofs/check.sh` or a `make` target.

## Decisions

1. Open question 1 was answered **(a) retire the tool (`git rm`, drop its ruff exemption).** (William Emerison Six <billsix@gmail.com>, 2026-11-08.)

## Open questions

None.
