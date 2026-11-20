# Plots show labelled e₁ and e₂ instead of x and y axis labels

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-20

The maintainer's ask (2026-11-20, verbatim): *"plots shouldn't show x and y on the axes, I think
that makes it confusing. The only context where it should be there, is when showing how plots are
done in high school, in comparison to how we do them now. Instead, the E1 and e2 vectors should
always be shown in labeled. Does this make sense? We are using those basis vectors to show
direction, The idea of x is a coordinate in that direction, etc."* It did: a direction is a basis
vector, and `x` is a coordinate measured along it, the figure-level follow-on to
`tasks/archive/2026/10/09/coordinate-subscripts-indices-not-xyz.md`.

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. Faint, unlabelled axis lines stay for orientation, with labelled unit `e₁`, `e₂` (`e₃`) arrows
   from the origin. A full-length arrow labelled `e₁` would suggest `e₁` is that long.
2. `graph_paper_scene` keeps its `±5` tick numbers. (It also kept its `x`/`y`: see below.)

## What changed

- **`src/gacalc/epixscene/scene2d.py`:** new `basis_vectors()` (unit arrows, labelled, in the
  new colour `BASIS`, `epix.black(intensity=0.6)`, lighter than the black subject vectors, with
  matching labels) and `AXIS_LINE` (`intensity=0.4`; `intensity` is darkness). `unit_circle_scene`
  draws `AXIS_LINE` lines without arrowheads or labels and, after the figure's body,
  `basis_vectors()`, unless `basis=False`.
- **`scene3d.py`:** `basis_vectors3()` and `axes3()` the same way in 3D. **`frame_scene.py`**
  (`scene_2d`, `scene_3d`) and **`bootstrap_live.py`** (`scene_around`, which also fits the unit
  arrows in its box) add the basis vectors to their existing light axes, with `basis=False`.
- **`line_scene.graph_paper_scene` keeps `x` and `y`:** it is only used by `one-dimension`, to draw
  the high-school graph of `y = m * x + b` beside the book's number lines, which is the comparison
  the maintainer named. Its docstring says so.
- **`book/figures/epix/rotate_goal.py`** drew its own `x`/`y` axes; it is the book's own goal
  figure (the high-school picture on `proof-rotate.rst` is the Kulla SVG, left as is), so it now
  draws `AXIS_LINE` lines and `basis_vectors()`.
- **`nbplotutils.create_x_and_y`** labels its segments `e₁`, `e₂` (or `f(e₁)`, `f(e₂)` when
  `fn` is not the identity) in their colours. `create_graphs_3d` already labelled its axes
  `e₁`, `e₂`, `e₃`; `create_graphs` (2D) shows only tick numbers.
- **`paper_scene` is unchanged:** `carried_paper` already draws the labelled `e₁'`, `e₂'` of the
  carried sheet, which coincide with `e₁`, `e₂` before anything moves.

## Opted out (`basis=False`), with the reason in a comment at each call

- Figures that draw `e₁`/`e₂` themselves: `notebooks/defining-g2.py` (`fig_resolve`),
  `notebooks/vectors-as-number-lines.py` (`fig_axes`), `notebooks/frame-qr-2d.py`
  (`fig_forward`, which labels `e₁`, `e₂` and their images).
- Figures whose own vector lies along `e₁` at about unit length, so the basis arrow sat under it
  and its label collided: `rotate_ab_step1.py`, `rotate_ab_step2.py` (`|a| * e₁`), `sp3.py`,
  `sp4.py`, `boot_sp3.py`, `boot_sp4.py` (the standard-position `a'`/`b'`), `boot_rotate.py`
  (`cos(θ) * v`).
- Two figure labels moved instead, to clear the 3D `e₂` label: `proj3d_e12.py`'s `rej` label
  (now right of its arrow), `proj3d_e31.py`'s `proj` label (now above-left of its tip).

Not changed: the bootstrap notebooks' `$x$`/`$y$` labels on two segments
(`bootstrap-product.py`, `bootstrap-rotation-from-projection.py`, `product-from-projection.py`)
name the projection and rejection lengths, not axes.

## Verification

All 49 prebuilt figures were rendered with `tools/render_epix_figures.py` and looked at in
montages; the collisions above were found that way and fixed. The full book build
(`entrypoint/docs.sh` in the image, exit 0, no new Sphinx warnings) showed one more: in the live
3D figures the plane patch, drawn by the figure body, hid `e₂`. The scenes now draw the basis
vectors after the body (after the context manager's `yield`), and `basis_vectors` resets the line
style and fill first; a re-run of `three-dimensions.py` showed `e₂` on top. `format.sh` clean;
`pytest -m "not slow"` 1396 passed.
