# Bring every book notebook up to the teaching-style standard

**Status:** proposed — needs go-ahead (open questions below)
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
  - `tasks/book-notebooks-show-mult-tables.md` adds the `show_mult` tables. Its three open questions
    (which products, concrete or symbolic, where `show_mult` lives) decide that part of this sweep.
  - `tasks/proof-notebooks-student-math-notation-style.md` covers the same goal for proof notebooks
    and adds a backfill of a notebook for every proof. It overlaps the proof-companion row above.
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

## Open questions

1. Should this task absorb the style half of `tasks/proof-notebooks-student-math-notation-style.md`,
   leaving that task only the backfill of missing proof notebooks? Recommended: yes.
2. Should the `show_mult` tables be done as part of this sweep, or stay a separate task done first?
   Recommended: separate and first, so this sweep revises the tables' lead-ins along with the rest.
