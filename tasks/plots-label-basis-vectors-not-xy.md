# Plots show labelled e₁ and e₂ instead of x and y axis labels

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's plots label their axes `x` and `y` (and `z`), which the maintainer finds confusing: in
this book a direction is a basis vector, and `x` is only a coordinate measured along that
direction. Every plot should instead draw and label the basis vectors `e₁`, `e₂` (`e₃` in 3D). The
one exception is a figure that shows how high school plots things, to compare with how the book
does it. Done means no figure or notebook plot outside those comparisons labels an axis with
`x`/`y`/`z`, every plot shows labelled basis vectors, and `make docs` passes.

## Context

- The maintainer's ask (2026-11-20, verbatim): *"plots shouldn't show x and y on the axes, I think
  that makes it confusing. The only context where it should be there, is when showing how plots
  are done in high school, in comparison to how we do them now. Instead, the E1 and e2 vectors
  should always be shown in labeled. Does this make sense? We are using those basis vectors to
  show direction, The idea of x is a coordinate in that direction, etc."* It makes sense, and it
  is the figure-level follow-on to `tasks/archive/2026/10/09/coordinate-subscripts-indices-not-xyz.md`,
  which moved coordinates from `a_x` to `a_1`.
- **Where the axis labels come from (studied 2026-11-20).** Almost all of them are drawn once, in
  the shared ePiX scene helpers, so the bulk of the change is a few lines:
  - `src/gacalc/epixscene/scene2d.py` `unit_circle_scene`: axis arrows to the box edge labelled
    `$x$`, `$y$`.
  - `src/gacalc/epixscene/line_scene.py` `graph_paper_scene`: grid axes labelled `$x$`, `$y$`
    plus `±5` tick labels.
  - `src/gacalc/epixscene/scene3d.py` `axes3`: `$x$`, `$y$`, `$z$`.
  - About 50 files under `book/figures/epix/` and `notebooks/` use these helpers, so every
    caller inherits the change; each caller is then checked for clutter (a figure that already
    draws its own `e₁`/`e₂` must not get a second pair).
  - matplotlib: `src/gacalc/nbplotutils.py` already labels the axes `\vec{\mathbf{e}}_1` /
    `\vec{\mathbf{e}}_2` with `set_xlabel`/`set_ylabel`; whether it also draws the vectors is to
    be checked.
- **Not axis labels, out of scope:** `notebooks/bootstrap-product.py`,
  `bootstrap-rotation-from-projection.py` and `product-from-projection.py` label two *segments*
  `$x$` and `$y$` (the projection and rejection lengths). Those name quantities, not axes.
- **Candidate high-school-comparison figures (keep `x`/`y`):** `book/docs/proof-rotate.rst` ("In
  high school you learned about sine, cosine…", the Kulla unit-circle SVG) and
  `book/docs/rotation-graph-paper.rst` ("the same parabola you know from high school"). To be
  confirmed per figure.
- Basis-vector notation is `\vec{\mathbf{e}}_1` (bold arrow, `tasks/archive/2026/11/19/basis-vector-bold-arrow-notation.md`).

## Plan

1. Give the scene helpers an option for the label style, defaulting to basis vectors: axis lines
   stay (unlabelled), and unit arrows `e₁`, `e₂` (`e₃`) are drawn from the origin and labelled. A
   `high_school=True` (name to settle) keeps today's `x`/`y` labels.
2. Pass the high-school option only at the comparison figures found above.
3. Walk the ~50 callers' rendered output for duplicate or overlapping basis-vector labels; fix
   per figure.
4. Check `nbplotutils` and any plotly/matplotlib cell in `notebooks/` for `x`/`y` axis titles.
5. `make docs`; look at the HTML and PDF figures.

## Open questions

1. Should the axis lines themselves stay (unlabelled), with short labelled `e₁`, `e₂` arrows on
   top, or should the full-length axis arrows go away and only the unit basis vectors remain?
   Recommendation: keep faint unlabelled axis lines for orientation and draw bold labelled unit
   `e₁`, `e₂`, since a full-length arrow labelled `e₁` would wrongly suggest `e₁` is that long.
2. `graph_paper_scene` labels ticks at `±5`. Keep those numbers once the axes lose `x`/`y`?
   Recommendation: keep them; they are coordinates along `e₁`/`e₂`, which is the point being made.
