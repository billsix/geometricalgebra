# Fill the five remaining placeholder book notebooks

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md` (filled the first five
and listed these as its follow-up); `tasks/notebook-dot-wedge-projection-demo.md` (blocked; it
names the `projection` and `projection-rejection-3d` stubs)

## BLUF

Five notebooks under `book/docs/notebooks/` are still the 16-line jupytext stub whose only code cell
is `1 + 1`, and each is pulled into the book by its page's toctree: `canonical-form.py`, `hook.py`,
`projection.py`, `projection-rejection-3d.py` and `vectors-as-number-lines.py`. Done means each is
either filled with a companion lesson in the book's notebook style, or dropped from its page's
toctree and deleted where the page does not need one. `make docs` must execute every notebook that
remains.

## Context

Read first:
- `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md`: how the first five were done.
  It covers the cell style, the live ePiX figure helpers (`_line_scene.py`, `_paper_scene.py`,
  `_venn_scene.py` in `book/figures/epix/`), the run-and-check loop and the gates.
- `tasks/reference/book-notebook-teaching-style.md`, `tasks/reference/book-outline.md`
  ("Structural conventions" and sections A–D, F), and
  `tasks/reference/teaching-order-and-dependencies.md`. A page may use only results taught
  before it.

Per stub, as found on 2026-11-19:
- `hook.py` (page `hook.rst`, the book's first page): the outline's §A asks for exciting pictures
  of rotation, projection and reflection. Nothing is taught yet, so this would be pictures only.
  Decide whether a notebook earns its place here.
- `canonical-form.py` (page `canonical-form.rst`): the canonical-form-over-decimals stance.
  Exact values such as `sqrt(2)/2` against floats are natural sympy material.
- `projection.py` (page `projection.rst`): the page also includes the real `proof-projection.py`.
  Either fill this stub (for example with the dot/wedge view of projection, the subject of the
  blocked `tasks/notebook-dot-wedge-projection-demo.md`) or drop it from the toctree.
- `projection-rejection-3d.py` (page `projection-rejection-3d.rst`): the page's own proofs
  `proof-projection-3d` and `proof-cross` are filled. Coordinate with the blocked task above,
  whose remaining work is the 3D projection/rejection cells.
- `vectors-as-number-lines.py` (page `vectors-as-number-lines.rst`): a vector as a relative number
  line. It sits between `one-dimension` (which already draws number lines with
  `_line_scene.py`) and `relative-graph-paper`.

## Plan

1. Ask the maintainer the open questions, and record the decisions here.
2. Fill or drop each stub, one commit each, running the notebook and its gates as the first task
   did.
3. Run `make docs` and `make format`, write the done-record, and archive.

## Open questions

1. For `hook.py`: fill it with picture-only cells, or drop it from `hook.rst`'s toctree?
   Recommendation: drop it. Nothing is taught yet, and the page itself can carry the pictures.
2. For `projection.py`: fill it with the dot/wedge projection demo, which would also unblock
   `tasks/notebook-dot-wedge-projection-demo.md`, or drop it, since `proof-projection.py` already
   covers the page? Recommendation: fill it with the demo.
