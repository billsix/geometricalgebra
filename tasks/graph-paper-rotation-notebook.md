# Notebook: rotation as rotating the graph paper (a grid of points, then deformed paper with f(x)=x²)

**Status:** in-progress (experiment phase — will prototype and return with questions)
**Priority:** 5
**Difficulty:** 6
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

After rotation is defined, build a notebook of ePiX plots that rotates a **3×3 grid of input points**
(`0*e_1 + 0*e_2`, `1*e_1 + 0*e_2`, `0*e_1 + 1*e_2`, …), **leaving a point behind after each rotation**
and **aggregating on a final plot** that traces out the whole rotated grid. The payoff: reframe
rotation not as moving individual vectors/points but as **rotating the graph paper itself**, which
carries the points along. End by drawing the **transformed graph paper** and plotting **f(x) = x²** on
it, to connect to high-school math — it really is just deformed graph paper you can draw on. Its own
notebook, also built into the Sphinx book. **Experiment first:** prototype the figures, look at them,
and return with questions before finalizing (this is open-ended and figure-heavy, like the
similar-triangle step).

## Context (read first)

- **The idea's foundation** is `tasks/prove-rotation-is-distributive-2d.md` — rotation is linear, so
  rotating every grid point is the same as rotating the two basis vectors and carrying the grid with
  them. This notebook is the visual of that.
- **ePiX figures** live in `book/figures/epix/` and render to `_static/epix/*.png` for `.. figure::`
  includes (`tools/render_epix_figures.py`, `make docs`); conventions in
  `tasks/reference/book-and-docs-pipeline.md`. The **book notebooks** are `book/docs/notebooks/*.py`
  (jupytext, executed by myst_nb) and currently use gacalc (+ matplotlib via `nbplotutils`), **not**
  ePiX. Decide (see Open questions) whether this is a *notebook* that renders ePiX figures inline (an
  `epix.Figure` exposes `.png`, so a cell can display it), or a **page + a sequence of ePiX figure
  files** like the `rotate*` sequence, or both.
- **Rotation in gacalc:** `transforms.plane_rotation(e_1, e_2)(θ)` rotates a vector; `g2` has the
  quarter-turn. The grid points are `i*e_1 + j*e_2`.
- Scene helpers: `_scene2d.py` (`unit_circle_scene`/axes, `vector`, `polar`, grid?). There is **no
  graph-paper/grid helper yet** — part of the work is drawing grid lines (and the rotated grid lines),
  probably a new helper.

## Goal

A notebook (built into the book) that: (1) shows a 3×3 grid of points, (2) rotates them one by one,
leaving a trail, (3) aggregates into the rotated grid, (4) reframes it as the graph paper rotating, and
(5) draws the deformed graph paper with `f(x) = x²` on it. The reader should come away seeing a rotation
as "the paper turned, and everything drawn on it turned with it."

## Plan

- [ ] Prototype: draw a 3×3 grid of points and the grid lines; rotate by a fixed angle; render.
- [ ] Prototype the deformed graph paper (rotated grid lines) and `f(x)=x²` sampled and drawn on it.
- [ ] Decide the notebook-vs-figure-sequence shape; wire a first version into the book.
- [ ] Return to the maintainer with the rendered prototype and the open questions below.

## Open questions

1. **Notebook rendering ePiX inline, or a book page + a `rotate_grid*` figure sequence** (like the
   `rotate*` steps), or both? (`.py` notebook can display an `epix.Figure.png`; a figure sequence is
   the established pattern.) Recommend: an ePiX **figure sequence on a short book page** first, since
   that's the proven pipeline; add an interactive notebook if wanted.
2. **Grid extent:** the examples start at `(0,0),(1,0),(0,1)` — is the 3×3 grid `{0,1,2}×{0,1,2}`, or
   centered `{-1,0,1}×{-1,0,1}`? Centered reads better under rotation (symmetric about the origin, the
   fixed point). Recommend centered `{-1,0,1}²` unless you want it anchored at the origin.
3. **`f(x)=x²` on the deformed paper:** draw the parabola in the ORIGINAL coordinates and rotate the
   whole curve with the paper (so it's "the same parabola, paper turned"), or draw `y=x²` in the
   rotated frame? Recommend the former (rotate the drawn curve with the paper) — that's the "deformed
   graph paper you can draw on" point.
4. **Rotation angle** for the demo (e.g. 30°, 45°, the book's 66°)? Recommend a clean 45° or 30° so the
   grid deformation is obvious but still readable.
