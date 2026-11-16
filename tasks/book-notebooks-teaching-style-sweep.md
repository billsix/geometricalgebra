# Bring every book notebook up to the teaching-style standard

**Status:** proposed — needs go-ahead (questions answered 2026-11-16)
**Priority:** 6
**Difficulty:** 7 (22 notebooks, each a rewrite of its Markdown and cell layout, plus a book build)
**Started:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)

## BLUF

`tasks/reference/book-notebook-teaching-style.md` describes how the maintainer wants the book's
notebooks to teach: a guided lab, one idea per cell, starting from known algebra, prose math as
LaTeX, hand reductions as justified chains, `show_mult` tables where the expansion is the point, and
no developer noise. Revise every non-placeholder notebook in `book/docs/notebooks/` to meet it. Done
means: each notebook below passes that doc's checklist (recorded per notebook in this task), and
`make format`, `make test` and `make docs` pass.

## Context

- **Read first:** `tasks/reference/book-notebook-teaching-style.md` (the standard and its
  checklist), `tasks/reference/book-outline.md` ("Structural conventions": the companion-notebook
  structure this sweep must keep), and `CLAUDE.md` ("Math notation for readers"; "The book's
  notebooks are hand-written Python under the full standard").
- **The notebooks (22 with content, counted 2026-11-16):**
  - Part III bootstrap: `bootstrap-rotation.py`, `bootstrap-projection.py`,
    `bootstrap-rotation-from-projection.py`, `bootstrap-product.py`,
    `bootstrap-projection-from-product.py`, `bootstrap-rotation-from-product.py`.
  - Proof companions: `proof-projection.py`, `proof-projection-3d.py`, `proof-rotate-from-a-to-b.py`,
    `proof-cross.py`, `proof-reciprocal-frame.py`.
  - Frames: `frame-qr-2d.py`, `frame-qr-3d.py`.
  - Other chapters: `geometric-product.py`, `rotation-from-vectors.py`, `product-from-projection.py`,
    `levels-of-abstraction.py`, `vector-addition.py`, `rotate.py`, `three-dimensions.py`.
  - Not in scope: the ten 16-line placeholders (`canonical-form.py`, `defining-g2.py`, `dual.py`,
    `hook.py`, `one-dimension.py`, `projection-rejection-3d.py`, `projection.py`, `reflection.py`,
    `relative-graph-paper.py`, `vectors-as-number-lines.py`). They get the standard when written.
- **Related open tasks:**
  - The `show_mult` tables were added first, in
    `tasks/archive/2026/11/16/book-notebooks-show-mult-tables.md` (14 tables in 8 notebooks).
  - `tasks/proof-notebooks-student-math-notation-style.md` now holds only the backfill (a notebook
    for every proof); the style of the existing proof companions is this task's (Decision 1).
  - `tasks/live-epix-figure-background.md` edits the six bootstrap notebooks and both frame
    notebooks; do it first or after, not interleaved.
- **Already partly there:** the bootstrap notebooks follow the structure in `book-outline.md`, and
  `frame-qr-2d.py` already writes its prose math as `$…$`. Book notebooks carry no
  `# pyright: ignore` trailers.

## Plan

1. For each notebook, run the checklist in `tasks/reference/book-notebook-teaching-style.md` and
   record the gaps in a table in this task (one row per notebook).
2. Revise one group at a time (bootstrap, proofs, frames, other), smallest notebooks first in each
   group. Keep every check cell and its result; change Markdown, split cells, add lead-ins, convert
   prose math to LaTeX.
3. After each group: `make format` (ty over `book/docs/notebooks`), `tools/check_annotations.py`
   (no rows), `tools/check_epix_keywords.py`, and `make docs`, checking the rendered HTML pages.
4. Record anything the standard did not anticipate back into the reference doc.

## Gap survey (2026-11-16, before revision)

Codes: **L** prose math in backticks, not `$…$` LaTeX; **A** checks that show nothing or give the
answer first (`assert`, `== … # -> True`); **D** a list of coordinate differences instead of one
subtraction cell; **C** teaching prose in code comments instead of Markdown; **M** several ideas
in one cell; **O** opening does not say what the notebook shows or start from what the reader knows.

| Notebook | Gaps |
|---|---|
| `bootstrap-rotation.py`, `bootstrap-projection.py`, `bootstrap-rotation-from-projection.py`, `bootstrap-product.py`, `bootstrap-projection-from-product.py`, `bootstrap-rotation-from-product.py` | L (structure already follows `book-outline.md`) |
| `proof-projection.py` | L, A, D, C, M |
| `proof-projection-3d.py` | O, L, D, A, M |
| `proof-rotate-from-a-to-b.py` | L, A, C, M |
| `proof-cross.py` | L, D |
| `proof-reciprocal-frame.py` | A (12 sites); prose math already LaTeX |
| `frame-qr-2d.py`, `frame-qr-3d.py` | none found: prose math is LaTeX, checks are subtraction cells |
| `geometric-product.py` | L, A, C |
| `rotation-from-vectors.py` | L, C |
| `product-from-projection.py` | L, A, M |
| `levels-of-abstraction.py` | L, A, C |
| `vector-addition.py` | L, A, C |
| `rotate.py` | L, A |
| `three-dimensions.py` | L, A |

Not in scope of this sweep: adding live ePiX figures or a values cell to the Part I and proof
notebooks (the structure in `book-outline.md` was written for the Part III companions); recorded
here as a possible follow-up, not done.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

1. **This task owns the style of every book notebook**, including the proof companions; it took
   over the style half of `tasks/proof-notebooks-student-math-notation-style.md`, which keeps only
   the backfill of missing proof notebooks.
2. **The `show_mult` tables stay a separate task, done first**
   (`tasks/archive/2026/11/16/book-notebooks-show-mult-tables.md`); this sweep revises their lead-ins along with the
   rest of each notebook.
