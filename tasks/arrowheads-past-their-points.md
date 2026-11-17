# ePiX arrowheads poke past the point they should end at

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-17 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/book-notebooks-symbolic-proof-style.md` (the notebooks whose figures show it);
`book/figures/epix/_frame_scene.py` (`arrow`, `dashed_arrow`); github.com/billsix/epix-mirror (the
ePiX the image builds, pinned by the Dockerfile's `EPIX_COMMIT`)

## BLUF

In the book's ePiX figures an arrow's visible tip does not stop at the point it is drawn to: it runs a
little past it, so arrows that meet at a point cross. The maintainer saw it in
`book/docs/notebooks/proof-projection.py`'s last figure, where the projection and the rejection add up
to $a$ and their arrowheads go through each other. Done means a figure's arrow tips end on their points
(measured on a rendered figure, not judged by eye), in both the prebuilt `_static/epix/` figures and
the live notebook figures.

## Context

**What ePiX does (read 2026-11-17 from `/opt/epix-src` in the image, the pinned epix-mirror):**

- `epix.arrow(tail, head, scale)` (`src/curves.cc`, `arrow`) builds an `arrow_data` whose **shaft runs
  the full length, tail to head**, and draws it with the current pen; then it draws the head
  (`src/arrow_data.cc`, `arrow_data::photo`).
- The head is a `pen_arrow` (`src/pen_arrow.cc`, `print_to`): a four-point polygon whose tip is exactly
  at `head`, with half-width `scale * arrowhead width` and height `ratio *` that (defaults
  `arrow_width(3)`, `arrow_ratio(5.5)`, `arrow_inset(0)` in `include/epix/state.h`).
- `eepic::print_fill` (`src/eepic.cc`) fills the polygon with hatch lines **and then strokes its
  outline with the line pen** (`set_pen_state(line)` + `print_paths`).

So the polygon's tip is at the point, but two things draw past it (worked out from the source, to be
confirmed by measurement):

1. **The outline stroke's miter at the tip.** The head is long and narrow (ratio 5.5, a tip half-angle
   of about $\arctan(1/5.5) \approx 10°$). A stroke of width $w$ with a miter join sticks out past a
   corner by $(w/2)/\sin(\text{half-angle})$, about $2.8 w$ here: roughly 3 pt for the book's 2.4 pt
   projection arrows, 2 pt for the 1.6 pt default.
2. **The shaft runs under the head to the tip** at full width $w$. Near the tip the head is narrower
   than the shaft, so the shaft's square end shows on both sides of the tip.

Separately, two arrows whose tips share a point (as $a$ and the rejection do) always overlap, because
each head extends back from the tip; that is geometry, not the overshoot. The order the arrows are
drawn in decides which head is on top.

**Our helpers:** `book/figures/epix/_frame_scene.py` `arrow()` sets `epix.pen(color, width)` (1.6 pt
default, 2.4 pt for projections, 1.1 pt dashed) and calls `epix.arrow(tail, head, scale=0.7)`. Every
book figure and live notebook figure goes through `epix.arrow`, directly or through these helpers.

## Possible solutions

- **A. Fix ePiX: stop the shaft at the head's base.** In epix-mirror, end the shaft at `base`
  (`head - ht * unit_dir`) instead of at the tip, so only the head reaches the point. That fixes cause
  2 for every figure; it needs an epix-mirror change and an `EPIX_COMMIT` bump.
- **B. Fix ePiX: no stroke past the tip.** In epix-mirror, either fill the head without stroking it, or
  stroke it with a round or bevel join (or a low miter limit), so the outline cannot extend past the
  tip. That fixes cause 1. It combines naturally with A.
- **C. Compensate in our helper.** In `_frame_scene.arrow()`, pull the head point back along the arrow
  by the overshoot before calling `epix.arrow`. The overshoot is in points, so the helper converts it to
  figure units from the figure's scale (`scene_around` knows its width in inches and its box). No ePiX
  change, but it is an approximation, depends on pen width and arrow direction, and must be repeated
  for every scene type (2D, 3D, the fixed-bounds book figures).
- **D. Draw shaft and head separately in our helper.** `epix.line` from the tail to the head's base
  with the wide pen, then `epix.arrow` over only the last stretch with a thin pen, so the head's stroke
  barely extends. Removes both causes without changing ePiX, but needs the same points-to-units
  conversion as C to find the head's base.
- **E. Draw order for arrows that share a tip.** Independent of the fix: draw the result vector (here
  $a$) last, or the parts last, so one head sits cleanly on top. A styling choice, made per figure.

**Recommended:** A + B in epix-mirror, which is the maintainer's own mirror and fixes every figure at
once; E per figure where tips meet. C and D are fallbacks if epix-mirror should stay unchanged.

## Verification

Render one figure with arrows of known endpoints (e.g. `proof-projection.py`'s last figure, and an
arrow along an axis) to PNG at high DPI and measure the last coloured pixel against the point's pixel
position, before and after. Re-render the book (`make docs`) and look at the projection, rotation and
frame figures.

## Open questions

1. **Where to fix it:** in epix-mirror (solutions A + B), or only in the book's helpers (C or D)?
   Recommended: epix-mirror.
2. **Shared tips:** when two arrows end at the same point, which head goes on top: the result (e.g.
   $a$) or the parts (projection, rejection)? Recommended: the parts on top, so the decomposition reads
   clearly.
