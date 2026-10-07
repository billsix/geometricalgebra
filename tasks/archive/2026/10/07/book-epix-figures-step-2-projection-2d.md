# Step 2: ePiX figures for projection and rejection in 2D — the result and the derivation

**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py`) ·
**Next:** `tasks/archive/2026/10/07/book-epix-figures-step-3-projection-3d.md`
**Status:** DONE 2026-10-07 (overnight autonomous run) — figures render, both pages wired, gate green, HTML clean.
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

- [x] Result figures: `proj1` (a, b, dashed line through b, foot of the perpendicular), `proj2`
      (projection blue along b + rejection green perpendicular, right-angle marker, labelled
      `proj_b a` / `rej_b a`), `proj3` (a = proj + rej tip-to-tail).
- [x] Derivation figures `sp1`–`sp5`: goal → rotation angle φ marked → rotated so b on x-axis (faint
      dashed originals) → projection = x-coord, rejection = y-coord (right angle) → rotated back.
      Shared vectors in `_projection_scene.py`; added `right_angle_at` to `_scene2d.py` for a
      right-angle marker at an arbitrary corner.
- [x] `projection.rst` (proj1-3) + `proof-projection.rst` (sp1 at the first TODO marker, sp2+sp3 at the
      second, sp4+sp5 in "Now the algebra") wired with alt text; `.. TODO prose` left for the maintainer.
      **Also fixed** the pre-existing `Title underline too short` warning in `proof-projection.rst`.
- [x] Verified: figures render; `make format` gate green; Sphinx HTML builds **with no warnings** and
      embeds all 8 PNGs. Full html+PDF build runs at the end of step 3.

## Notes / decisions

- The 2D derivation figures are drawn here per the decision; the page's prose is still 3D-framed, so a
  `.. TODO prose` note near the top of `proof-projection.rst` flags the 2D-then-3D restructuring as the
  maintainer's (the 3D "one plane at a time" pictures are step 3's follow-on).
- Vectors: a = 1.25 at 66° (rotation sequence's a), b = 1 at 20°; projection scalar ≈ 0.868, so in
  standard position a' is at 46° and its x-coordinate is the projection.

## Open questions

None — both decided 2026-10-07 (William Emerison Six <billsix@gmail.com>): the **2D** derivation is
drawn here (3D pictures are step 3's; the page's 2D-then-3D restructuring is the maintainer's prose
call), and `a` is the rotation sequence's (1.25 at 66°) with `b` at 20°, length 1.
