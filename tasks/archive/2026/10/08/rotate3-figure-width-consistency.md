# Make the rotate3 figure the same width as its sibling rotate figures

**Status:** done — 2026-10-08 (gates green; normalized pre-squash)
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The `rotate3` figure (in `book/docs/proof-rotate.rst`, after "rotate by 90°") rendered **much wider**
than its siblings — its long upper-left label `(\cos(\beta+\pi/2),\ \sin(\beta+\pi/2))` had forced a
widened box (`lower_left=(-2.7,-1.3)` vs the default `-1.6`), and `unit_circle_scene` scales the
physical size with the box width. Fixed by returning to the default box and reformatting that one label
as a column vector so it fits: `rotate3` now renders **537×457 px**, matching the siblings (was 833).
`make format` + `make docs` green.

## What was done

- **`book/figures/epix/rotate3.py`** — dropped the widened box override back to the default
  `unit_circle_scene()`, and reformatted the long upper-left label from a horizontal pair into a
  **column vector** `\begin{bmatrix}\cos(\beta+\pi/2)\\\sin(\beta+\pi/2)\end{bmatrix}` (the book already
  uses bmatrix column vectors in the algebra sections), placed centered above the perpendicular vector's
  head (`offset=(6,16)`, `align=c`) so it clears the vector line. The shorter `(\cos\beta,\sin\beta)`
  label stays horizontal, matching `rotate1`/`rotate2`.
- **Result:** `rotate3` 537×457 px (was 833 wide), matching `rotate2` (537) / `rotate1` (564). Verified
  by render→view + PIL size check.
- **Sibling scan:** `rotate1`/`2`/`4`/`5`/`6` already use the default box. **`rotate7` (645×547) and
  `rotate8` (681×583) are larger** — but for a different reason: they are also **taller**
  (`upper_right.y = 1.9`/`2.1`) to show the result vector reaching up, and their width comes from the
  inherently-wide *sum* label `r(\cos\theta\,\vec{x'}+\sin\theta\,\vec{y'})` (not a coordinate pair that
  column-stacks cleanly). Left as-is: larger by design for the content, and `rotate3` was the flagged
  egregious outlier. Normalizing `rotate7`/`8` too would be a follow-on (relocate/reformat the
  result-sum label).

## History (commit chronology — for the squash)

1. `b28faa5` *added tasks* — filed this task (then proposed; committed alongside other task-adds).
2. `e8e56cc` *made image smaller* — the `rotate3.py` fix + this task doc's done record (on `master`,
   after the `rotateFromAToB` merge). The archive `git mv` follows as its own commit.

## Related

- `book/figures/epix/rotate3.py` (the fixed figure) and `_scene2d.py` (`unit_circle_scene`,
  `UNIT_SCALE_IN` — the box-drives-size mechanism).
- `book/docs/proof-rotate.rst` — the page the figure sits on.
- `tasks/archive/2026/10/08/fix-epix-figure-label-placement.md` — prior label-placement work (same
  render→view discipline).
