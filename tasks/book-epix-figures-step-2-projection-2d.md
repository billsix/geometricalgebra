# Step 2: ePiX figures for projection and rejection in 2D — the result and the derivation

**Part of:** `tasks/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py`) ·
**Next:** `tasks/book-epix-figures-step-3-projection-3d.md`
**Status:** proposed — needs go-ahead.
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>)

## BLUF

Two figure sets for the projection pages. (a) **What we want:** `project(a, b)` as the shadow of `a` on
the line through `b`, and `reject(a, b)` as the perpendicular remainder, with `a = project + reject` — for
`book/docs/projection.rst`. (b) **The precalculus derivation** for `book/docs/proof-projection.rst`: rotate
the whole picture so `b` lies on the x-axis, read the projection off as the x-coordinate (and the
rejection as the y-coordinate), rotate back — a step sequence like `rotate1`–`rotate8`, filling that page's
two `.. TODO figure` markers (lines 37 and 57) and adding the steps between. Done = figures render via
`make docs`, both pages reference them, both outputs checked.

## Context

- The derivation page is already written (agent draft 2026-09-30, for the maintainer's voice):
  `proof-projection.rst` §"The goal", "The idea: make it easy by moving the problem", "Rotating b onto the
  x-axis, one plane at a time", "Why we are allowed to do this", "Now the algebra", "The payoff". Its
  current text frames `a`, `b` in **3D** ("Rotating b onto the x-axis, one plane at a time" uses the xy
  then xz rotation); this step draws the **2D** case (one rotation) — see open question 1.
- Math: `src/gacalc/standardposition.py` `project_sp`/`reject_sp` and `_project_via_standard_position`
  (`rotate_in_xy_plane`, `align`, `rotate_back`); proofs `proofs/GacalcProofs/StandardPosition.lean`
  (`projectSP_eq_proj`/`rejectSP_eq_reject`), `Projection2D.lean`. Reference:
  `tasks/reference/reduction-to-standard-position.md`.
- Pattern + helpers: step 1's `_scene2d.py` (`vector`, `wedge`, `right_angle_marker`, `leg`); the
  rotation sequence shows how a derivation becomes a numbered figure series.

## Plan

- [ ] Result figures: `proj1.py` — `a`, `b`, the dashed line through `b`, the foot of the perpendicular;
      `proj2.py` — `project(a,b)` (blue, along `b`) and `reject(a,b)` (green, perpendicular) with the
      right-angle marker, labelled with the book's names; `proj3.py` — `a = project + reject` as a
      tip-to-tail sum (reuses step 1's idiom).
- [ ] Derivation figures (`sp1.py` …): the general picture → the rotation angle of `b` marked → everything
      rotated so `b` is on the x-axis (dashed originals faint) → the projection is the x-coordinate, the
      rejection the y-coordinate → rotated back. Share `a`, `b` constants in a `_projection_scene.py`.
- [ ] `projection.rst` + `proof-projection.rst`: replace the two `.. TODO figure` markers and add the
      series with alt text; keep `.. TODO prose` where the maintainer's text is missing.
- [ ] Verify: `make docs` nested; HTML + PDF; `make format` green.

## Notes / decisions

## Open questions

None — both decided 2026-10-07 (William Emerison Six <billsix@gmail.com>): the **2D** derivation is
drawn here (3D pictures are step 3's; the page's 2D-then-3D restructuring is the maintainer's prose
call), and `a` is the rotation sequence's (1.25 at 66°) with `b` at 20°, length 1.
