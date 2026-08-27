# Notebook demo: dot = projected geometric product, wedge = rejected (2D + 3D)

**Status:** blocked
**Priority:** 6
**Difficulty:** 2
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open questions below (new notebook vs existing cells; base-vector
wording). The math is already proved — do NOT re-prove it.
**Recheck:** the Open questions below are answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"See if in the notebooks, for at least 2D and 3d, see if I can show that
the dot product of a and b is the geometric product of a and b projected onto a. Same thing for wedge,
but rejected. See if I can do the same for 3d."*

Demonstrate, in notebooks for 2D and 3D, that the parallel part of the geometric product is the dot
product and the perpendicular part is the wedge.

## Context (investigation 2026-08-27)

- **Already proved and boxed — this is a notebook *demonstration* task, not a proof task.** Archived
  `2026/08/03/verify-dot-wedge-as-projection-rejection-products.md` proved exactly `a_∥ b = a·b` and
  `a_⊥ b = a∧b` symbolically; the boxed theorem lives in
  `tasks/reference/dot-wedge-projection-rejection.md`.
- Notebooks already exist: `book/docs/notebooks/projection.ipynb`,
  `book/docs/notebooks/projection-rejection-3d.ipynb`.
- **Wording caveat:** the boxed theorem is stated projecting `a` onto **`b`**; the bullet says "projected
  onto **a**". Confirm the intended base vector so the demo matches the theorem (Q2).
- Overlaps `displaygraded-geometric-plots.md` concept 2 (`a*b = a·b + a∧b` tied to projection length +
  parallelogram area).

## Plan (draft)

- [ ] Add notebook cells demonstrating the boxed theorem in 2D and 3D, citing the reference doc.

## Open questions

1. **Where** — a new notebook, or add cells to the existing `projection.ipynb` /
   `projection-rejection-3d.ipynb`? *(Recommend: extend the existing two.)*
2. **Base vector** — the theorem projects `a` onto `b`; the bullet says "onto a". Which is intended?
