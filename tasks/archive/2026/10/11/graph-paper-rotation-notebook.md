# Rotation as rotating the graph paper (a grid of points, then deformed paper with f(x)=x²)

**Status:** complete
**Completed:** 2026-10-11
**Priority:** 5
**Difficulty:** 6
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Built a book page, **"Rotation is turning the graph paper"** (`book/docs/rotation-graph-paper.rst`), as
a five-figure ePiX sequence that rotates a 4×4 grid `{0,1,2,3}²` about the origin by 30°, point by point
then all at once, then reframes it as the **whole sheet of graph paper turning** (the points ride
along), and finally plots `y = x²` on the tilted frame — the same high-school parabola, on turned paper.
It follows the distributivity result (`geometric-product.rst`): once the paper turns, the two basis
vectors turn and everything drawn on it comes along. `make docs` builds clean.

## What was done (maintainer decisions, 2026-10-11)

- **Figure sequence** (not an inline notebook) — the proven ePiX pipeline:
  `book/figures/epix/graphpaper1`…`5.py` sharing `_graphpaper_scene.py` (constants `ANGLE = 30°`,
  `COORDS = {0,1,2,3}`, and `rotate`/`grid_points`/`draw_grid`/`parabola_points` helpers), all one frame
  so the grid appears to rotate in place.
  1. the grid of points; 2. a few points rotated with arrows; 3. all 16 rotated (blue over faint
  original); 4. the grid **lines** rotated too — the sheet turned; 5. `y = x²` on the rotated frame.
- **Grid `{0,1,2,3}²`** (maintainer's choice, anchored at the origin = the fixed point).
- **`y = x²` drawn in the rotated frame** (points `(x, x²)` placed at `rotate(x, x²)`), so the parabola
  sits on the tilted paper. `x ∈ [0, 1.8]` so it stays on the grid.
- **30°** rotation.
- A book page in the toctree after `geometric-product`, with prose tying the sequence to the
  distributivity/natural-basis idea and ending on "a rotation is deformed graph paper".

## Notes

- `check_epix_keywords` treats an unknown callee **with a positional arg** as a failure, so the scene
  module's helper calls all pass arguments by keyword and avoid `list.append` (uses comprehensions) —
  recorded here because any future scene helper must do the same.

## Verification

Each figure rendered and eyeballed (graphpaper4 shows the sheet turned, graphpaper5 the parabola on it).
`ruff`/`ruff format`/`check_epix_keywords` clean on the figures and scene module; `make docs` builds
HTML + PDF, the new page and all five figures included, no broken references.

## Open questions

None — all four were answered by the maintainer (2026-10-11): figure sequence; `{0,1,2,3}²`; `y=x²` in
the rotated frame; 30°.
