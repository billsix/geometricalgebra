# `nbplotutils.draw_ndc`: draw the square, not a pentagon

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 3
**Difficulty:** 1
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.1

## BLUF

`draw_ndc` is meant to draw the normalized-device-coordinate square [−1, 1]². A stray comma in its
vertex list makes it draw five points instead. Done means it draws the four corners, its labels sit
on them, and a test pins it.

## Context

In `src/gacalc/nbplotutils.py`, `draw_ndc`'s vertex list reads:

```python
(1.0) * ex,
+(1.0) * ey,
```

where `(1.0) * ex + (1.0) * ey,` was meant. The list therefore has five vertices: (−1,−1), (1,−1),
(1,0), (0,1), (−1,1). So:

- the (1,1) corner is missing;
- the polygon is a pentagon;
- the four corner labels, drawn by index, land on the wrong points: "(1,1)" sits at (1,0).

`nbplotutils.py` has no tests (review §6.5), so a new `tests/test_nbplotutils.py` holds the
regression test. It uses matplotlib's non-interactive `Agg` backend. matplotlib comes with the image
through the `notebooks` extra.

## Plan

- [ ] Join the two list items into `(1.0) * ex + (1.0) * ey`.
- [ ] Add `tests/test_nbplotutils.py`: after `draw_ndc()`, the axes' polygon has exactly the four
  corners of [−1, 1]², in order. It carries the LGPL header copied from
  `tests/test_rotate_90_degrees.py`.
- [ ] Gate: the new test (fails on the old code), `ruff`, `ty`, `pytest -m "not slow"`.

## Open questions

None.
