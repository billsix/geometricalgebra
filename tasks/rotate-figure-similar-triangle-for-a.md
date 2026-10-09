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

## Open questions

(To be filled from the experiment — this task deliberately returns with questions before finalizing.)
