# Write the "Orthogonal" book page (still a placeholder)

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), noticed while finishing
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.

## BLUF

`book/docs/orthogonal.rst` is a one-line placeholder ("Define orthogonal, related to angles"). Perpendicular
lines and the perpendicular bisector are now taught on `book/docs/product-from-projection.rst` ("Angle,
area and perpendicular"). Decide what this page adds (orthogonal as a property of vectors and of
subspaces, orthogonal frames, the link to the projection/rejection split) or fold it away, then write it
in the book's style. Done = the page has content and a companion notebook, or it is removed from the
toctree with its outline entry updated.

## Context

- Read first: `CLAUDE.md` (the three-forms rule, math-notation rules, "one name per operation",
  companion notebooks with symbolic steps, live ePiX and `show_difference`), `tasks/reference/book-outline.md`
  (§G "Orthogonal — define it, related to angles"), `tasks/reference/teaching-order-and-dependencies.md`
  (it may only use results taught before it; update the dependency graph), and the new section on
  `book/docs/product-from-projection.rst` so the two pages don't repeat each other.
- Related library code: `src/gacalc/frame.py` (orthogonal frames), `transforms.py`
  (`line_to_line_projection` / `rejection`).

## Open questions

1. Keep the page (orthogonality of vectors and frames, after the dot product), or fold it into
   `product-from-projection` and drop it from the book? Recommend keeping it, about orthogonal
   decomposition and frames, since perpendicular lines are already covered.
