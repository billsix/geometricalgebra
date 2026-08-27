# Center the parallelogram as the foundational shape (area, linear transforms)

**Status:** blocked
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open questions below (book-narrative vs code/notebook deliverable;
which primitives).
**Recheck:** the Open questions below are answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"Make sure to put in somewhere that the parallelogram is the most important
shape in this series, show that the parallelograms area is the same as a rectangle, with the base times
height, and make sure to show that other primitives are drawn on top of that after a linear
transformation. Make sure to make the connection between high school algebra, I mean geometry, and how
fundamental parallelograms are, and that two vectors implicitly define a parallelogram."*

Centralize the thesis that the parallelogram is the foundational primitive: its area = base×height (like
a rectangle), other primitives are drawn on top of it after a linear transform, tie to high-school
geometry, and note that two vectors implicitly define a parallelogram.

## Context (investigation 2026-08-27)

- **The math is already documented; the *thesis/narrative* is not centralized.**
  `tasks/reference/content-area-volume.md:13,30-47` already states "area of the parallelogram on a and
  b," `|v₁||v₂|sinθ`, and "base × height = the parallelogram" (height = V₂ rejected from V₁). Pedagogy
  lives in `openstax-math-pedagogy.md` and `book-outline.md`.
- Archived: `2026/08/24/area-volume-content.md`, `2026/06/27/wedge-magnitude-sin-notebook.md`,
  `2026/08/25/name-perpendicular-vector-not-height.md`.
- `displaygraded-geometric-plots.md` (active) covers the oriented-parallelogram = bivector = signed-area
  plot — the *code* side of this.

## Plan (draft)

- [ ] **UPDATE `tasks/reference/content-area-volume.md`** (and/or `book-outline.md` as a chapter thesis)
      to add the "parallelogram is THE foundational primitive; other primitives are linear transforms of
      it; high-school-geometry grounding; two vectors imply a parallelogram" narrative.
- [ ] If a code/notebook demo is wanted (Q1), track it with `displaygraded-geometric-plots.md`.

## Open questions

1. **Deliverable** — is this a **book-narrative** thesis (goes in `content-area-volume.md` /
   `book-outline.md`), or a **code/notebook** deliverable (a demo drawing primitives as linear transforms
   of a base parallelogram), or both?
2. **"Other primitives drawn on top after a linear transformation"** — which primitives (triangle,
   circle, ellipse)?
