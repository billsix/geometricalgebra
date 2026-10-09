# Show vector `a` as a similar (scaled-up) right triangle in the rotate figures

**Status:** in-progress (experiment phase — will return with follow-up questions)
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

In the `proof-rotate` figure sequence, the rotation of `a` is derived on the **unit circle** (the right
triangle with legs `cos(θ)` and `sin(θ)`), then scaled back to length `r`. The maintainer wants a step —
the last one, or near it — that also draws vector `a`'s **own** right triangle (legs `r·cos(θ)`,
`r·sin(θ)`, hypotenuse the full-length rotated `a`) **alongside** the unit triangle, so the high-school
"same angles ⇒ similar ⇒ proportional sides" is visible: the little unit triangle and the big `a`
triangle are the same shape. Risk: with `a` only slightly longer than unit (`R = 1.25`), the two
triangles' labels may overlap. If so, the maintainer wants `a`'s magnitude increased so they separate.

**This task is an experiment first.** The agent will build candidate figures (the overlaid similar
triangles, at `R = 1.25` and larger), render them, look at the results, and **come back with follow-up
questions and the work** before anything lands in the book.

## Context (read first)

- The figures are ePiX Python under `book/figures/epix/`, rendered by `tools/render_epix_figures.py`
  to `_static/epix/<name>.{pdf,png}`. Scene constants + helpers:
  `book/figures/epix/_rotation_scene.py` (`BETA = 66°`, `THETA = 66°`, `R = 1.25` = |a|) re-exporting
  from `book/figures/epix/_scene2d.py` (`polar`, `unit_circle_scene`, `vector`, `leg(tail, head, color,
  text, angle, offset)`, `right_angle_marker(angle)` — **origin-only**, `wedge`).
- **`rotate8.py` is the current last step** ("scale back to length r"): it already draws the unit
  triangle (`leg` ORIGIN→`foot` = `cos(θ)`, `leg` `foot`→`rotated` = `sin(θ)`) and the result vector at
  `radius=R`, with the long `r * (cos(θ) * x' + sin(θ) * y')` label. It does **not** draw the scaled-up
  similar triangle (legs `r·cos(θ)`, `r·sin(θ)`).
- `rotate6`/`rotate7` establish the unit triangle and the rotated direction. The prose is
  `book/docs/proof-rotate.rst` (the "Now the algebra" section ends on the result formula).
- Length equality across these figures was just verified
  (`tasks/archive/2026/10/09/verify-rotated-vector-length-in-rotate-figures.md`); the ePiX pipeline and
  conventions are in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures": every arg by keyword,
  every binding typed).

## Goal

A figure (a new `rotate9`, or an enhanced `rotate8` — to be decided after the experiment) that overlays
the unit right triangle (`cos θ`, `sin θ`) and `a`'s scaled-up similar right triangle (`r·cos θ`,
`r·sin θ`, hypotenuse = the rotated full-length `a`), with labels readable (not overlapping), driving
home the similar-triangles proportionality. The `a` magnitude (`R`) may be increased from 1.25 if needed
for label separation — a change that must stay consistent across the shared `_rotation_scene.py` (every
`rotate*` figure uses the same `R`).

## Plan

- [ ] Render the current `rotate8` as a baseline.
- [ ] Build an experimental figure overlaying the two similar triangles at `R = 1.25`; render; inspect
      for label overlap.
- [ ] If crowded, try larger `R` (e.g. 1.6, 2.0); render; inspect. Note the trade-off (larger `R` means
      `a` sits further outside the unit circle, changing every `rotate*` figure's framing).
- [ ] Come back to the maintainer with the rendered candidates and the follow-up questions (new step vs.
      enhance rotate8; chosen `R`; overlay vs. side-by-side; label placement).

## Experiment results (2026-10-09)

Built an overlaid figure (`tasks/adhoc/rotate-figure-similar-triangle-for-a/expsimilar.py`) — the unit
triangle (`cos θ`, `sin θ`, hypotenuse dashed) and `a`'s scaled-up triangle (`r·cos θ`, `r·sin θ`,
hypotenuse the solid `a`), sharing the origin corner and the `θ` wedge. Rendered at three magnitudes and
viewed the PNGs:

- **R = 1.25 (current shared value): too crowded.** The two triangles are nearly the same size, so
  `sin(θ)`/`r·sin(θ)` sit on top of each other and `cos(θ)`/`r·cos(θ)` collide — unreadable. Confirms the
  maintainer's overlap worry.
- **R = 1.6: readable `sin` legs.** The two green `sin` legs separate into distinct parallel lines with
  readable labels, and `a` sits just outside the unit circle.
- **R = 2.0: very clear `sin` separation, but `a` extends well outside the circle**, which reframes the
  whole sequence more.
- **The `cos` legs are COLLINEAR at every R.** Both run from the origin along `x'`, so the short one
  (`cos θ`) is a sub-segment of the long one (`r·cos θ`) — the *lines* coincide; only the *labels* can be
  moved apart. This is pedagogically fine (it literally shows `cos θ` is `r·cos θ` scaled down), but the
  two `cos` labels must be repositioned (short leg vs. far end) — a label fix independent of R.
- **R is shared across all eight `rotate*` figures** via `_rotation_scene.py`, so bumping it changes the
  framing of `rotate1`–`rotate7` too, not just this step.

Experiment script saved at `tasks/adhoc/rotate-figure-similar-triangle-for-a/expsimilar.py` (render by
copying it into `book/figures/epix/` and `python tools/render_epix_figures.py expsimilar`).

## Open questions

1. **New step, or enhance `rotate8`?** `rotate8` already draws the unit triangle + the full-length
   result; I can add the scaled-up triangle there, or make a dedicated **`rotate9`** "similar triangles"
   step. Recommend a **new `rotate9`** — `rotate8` is already busy with the long result-formula label.
2. **Magnitude.** Keep the shared `R = 1.25` (too crowded here), bump the shared `R` for the whole
   sequence (1.6 or 2.0), or use a **larger `R` only for this figure**? Recommend a **local larger `R`
   (~1.6) for just this figure** (or `rotate9`), leaving `rotate1`–`rotate8` at 1.25 so their framing
   doesn't change. If you'd rather the whole sequence match, 1.6 reads better than 1.25 and keeps `a`
   near the circle.
3. **`cos`-leg presentation.** OK to keep the overlay with the two `cos` legs collinear (labels
   separated), or do you want the unit triangle drawn **translated/side-by-side** so all six sides are
   distinct? Recommend the overlay (the nesting IS the proportionality).
4. **Which three images do you want to see?** I have R = 1.25 / 1.6 / 2.0 rendered; say if you want
   different magnitudes or the `cos`-label-separated version before I finalize.
