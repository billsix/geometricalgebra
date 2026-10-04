# Notebook demo: dot = projected geometric product, wedge = rejected (2D + 3D)

**Status:** blocked
**Priority:** 6
**Difficulty:** 2
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — the 2D half was found already
done in `notebooks/displayg2.py`; Context and Q1 re-posed accordingly.
**Blocked on:** maintainer answers the Open questions below (where the 3D cells go; base-vector
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
- **The 2D demonstration is already DONE** (found 2026-10-04): `notebooks/displayg2.py`, section
  "Dot and wedge are the parallel and perpendicular parts of the product" (commit `adb4b1d`,
  2026-08-03 — it predates this task) — `a_par = Vector.project(onto=b)(a)`,
  `a_perp = Vector.reject(away_from=b)(a)`, `a_par * b == a.dot(b)`, `a_perp * b == a.wedge(b)`,
  `show_mult` of each, and `a_par * b + a_perp * b == a * b`, citing the reference doc. **The 3D
  counterpart does not exist** — `notebooks/displayg3.py` has no projection/rejection split.
  Remaining work = the 3D cells.
- The book notebooks `book/docs/notebooks/projection.py` and
  `book/docs/notebooks/projection-rejection-3d.py` exist but are still the `1 + 1` placeholder
  stubs (the `.ipynb` are gitignored build artifacts; the `.py` is the source).
- Related, drafted 2026-09-30 but NOT subsuming this task: `book/docs/proof-projection.rst` +
  `book/docs/notebooks/proof-projection.py` demonstrate the standard-position `project_sp`/`reject_sp`
  and `project + reject == a`, not the dot/wedge split.
- **Wording caveat:** the boxed theorem is stated projecting `a` onto **`b`**; the bullet says "projected
  onto **a**". Confirm the intended base vector so the demo matches the theorem (Q2).
- Overlaps `displaygraded-geometric-plots.md` concept 2 (`a*b = a·b + a∧b` tied to projection length +
  parallelogram area).

## Plan (draft)

- [x] 2D cells demonstrating the boxed theorem, citing the reference doc — already in
      `notebooks/displayg2.py` (2026-08-03).
- [ ] 3D cells (where per Q1), citing the reference doc.

## Open questions

1. **Where do the 3D cells go** — mirror the 2D section into `notebooks/displayg3.py` (the
   demo-notebook twin of `displayg2.py`), or seed the still-empty book notebook
   `book/docs/notebooks/projection-rejection-3d.py` (currently a `1 + 1` stub)? *(Recommend:
   `displayg3.py`, matching where the 2D half lives; the book stub can quote it later.)*
2. **Base vector** — the theorem projects `a` onto `b`; the bullet says "onto a". Which is intended?
