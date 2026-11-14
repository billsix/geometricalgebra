# Bare-bones 2D book pages: rotation → projection → rotation → product → projection → rotation

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-14 (William Emerison Six <billsix@gmail.com>)

## BLUF

A run of short reStructuredText pages that does the 2D bootstrap end to end, with minimal prose and
all of the proofs, code and graphs: the precalculus rotation, then projection defined from it, then
rotation defined from projection, then the geometric product, then projection and rotation
redefined through the product. Duplicating material from the rest of the book is fine. Done means
the pages build in `make docs`, every code cell runs, and each step's proof is shown.

## Context

- The book: `book/docs/*.rst` with notebooks in `book/docs/notebooks/*.py` (jupytext percent
  format, executed at build) and ePiX figures in `book/figures/epix/*.py`
  (`tasks/reference/book-and-docs-pipeline.md`, `tasks/reference/book-outline.md`).
- Existing pages that cover pieces of the arc: `proof-rotate.rst` (`eq-rotate-formula`),
  `proof-projection.rst` (2D projection by standard position), `proof-rotate-from-a-to-b.rst`,
  `product-from-projection` (notebook), `geometric-product` (notebook).
- The arc and why it is not circular: `tasks/reference/reduction-to-standard-position.md` ("The full
  bootstrap arc"). Lean has each step in 2D: `StandardPosition2D.lean`, `RotateFromTo2D.lean`.
- `CLAUDE.md` rules that apply: the three forms (Lean, symbolic Python, prose + LaTeX) for each piece
  of math; the notation rules (parentheses apply, `*` multiplies, every angle named); a symbolic
  coefficient written `Scalar(s) * e_1`.

## Open questions

1. Where do the pages go: (a) a new section of the existing book's toctree, (b) a separate short
   document built alongside it? Recommendation: (a), as its own top-level section.
2. "Redefining" projection and rotation through the geometric product: projection as
   `(a · b) * b⁻¹` and rotation as the versor sandwich `R * v * R⁻¹`? Or something else?
3. Graphs: ePiX figures (the book's figure source) or matplotlib in the notebooks?
   Recommendation: ePiX, as elsewhere in the book.
4. Lean: cite the existing 2D theorems where they exist and add only what is missing, or none on
   these pages ("bare bones")?
