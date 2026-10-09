# Add arrow heads to the vectors in the ePiX figures

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 5
**Difficulty:** 2
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Vectors in the book's ePiX figures now draw with a visible **arrow head**. The three shared vector
helpers (`_scene2d.py`'s `vector()` and `dashed_vector()`, `_scene3d.py`'s `vector3()`) switched from
`epix.line` + `epix.dot` to `epix.arrow(…, scale=1)` — the same primitive and head size the axes
already use. One change in the helpers covers every figure. `make docs` rebuilds clean.

## What was done

- `book/figures/epix/_scene2d.py`: `vector()` now draws `epix.arrow(tail=ORIGIN, head=head, scale=1)`
  (dropped the tip dot — the arrow head marks the tip); `dashed_vector()` draws the dashed arrow
  (`epix.dashed()` + `epix.arrow` + reset).
- `book/figures/epix/_scene3d.py`: `vector3()` draws `epix.arrow(tail=ORIGIN3, head=head, scale=1)`.
- Re-rendered and eyeballed `rotate-goal`, `rotate9`, `add1`, `add3` (solid + dashed vectors),
  `proj3d-overview` (3D): the heads are visible, match the axes' size, and dashed translated copies
  carry heads too.

## Verification

- Full `make docs` (nested) green — every figure re-rendered with arrow heads, HTML + PDF both built.
- `ruff check` / `ruff format --check` / `check_epix_keywords` clean on the two scene files.

## Open questions

None.
