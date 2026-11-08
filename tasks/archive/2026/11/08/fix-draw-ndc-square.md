# `nbplotutils.draw_ndc`: draw the square, not a pentagon

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1

## What was wrong

`draw_ndc` (`src/gacalc/nbplotutils.py`) is meant to draw the normalized-device-coordinate square
[−1, 1]². A stray comma split `(1.0) * ex + (1.0) * ey` into two list items, `(1.0) * ex,` and
`+(1.0) * ey,`. So:

- the polygon had five vertices, (−1,−1), (1,−1), (1,0), (0,1), (−1,1), and was missing the (1,1)
  corner;
- the corner labels, drawn by index, sat on the wrong points.

## What changed

- The two items are joined into `(1.0) * ex + (1.0) * ey`.
- **`tests/test_nbplotutils.py`** (new; `nbplotutils` had no tests). Using the `Agg` backend, it
  draws inside `create_graphs()` and checks that the one `Polygon` added has exactly the corners
  (−1,−1), (1,−1), (1,1), (−1,1), in order. It fails on the old code and passes on the new. It
  carries the project's LGPL header.

There is no changelog entry: `nbplotutils` is the notebooks' plotting helper, not consumer API.

## Verification

- `pytest -m "not slow"`: 811 passed, 2 skipped.
- `ruff` and `ty`: clean.
