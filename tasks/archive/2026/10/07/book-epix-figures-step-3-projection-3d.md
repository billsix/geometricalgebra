# Step 3: ePiX figures for projection and rejection in 3D onto the e_12, e_23 and e_31 planes

**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py` conventions), step 2
(the 2D cast and idioms) · **Next:** — (last step; the umbrella archives when this lands)
**Status:** DONE 2026-10-07 (overnight autonomous run) — figures render, page wired, gate green, full html+PDF build clean.
**Priority:** 5
**Difficulty:** 6 (first 3D figures: camera, depth cues, plane rendering)
**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's first 3D figures, for `book/docs/projection-rejection-3d.rst`: a vector `a` in 3D and its
**projection onto** and **rejection from** each coordinate plane — `e_12` (the xy-plane), `e_23` (yz) and
`e_31` (zx) — drawn with ePiX's 3D camera the same way the 2D figures use the disc-and-axes scene, via a
new `_scene3d.py` helper. Done = the figures render via `make docs`, the page references them, both
outputs checked, and the helper is documented in the book pipeline reference.

## Context

- ePiX is a 3D library projecting through a camera: `Point(x=, y=, z=)`, `epix.camera.at(Point)` (or
  `viewpoint`), `epix.Plane(p1, p2)`, `epix.E_1/E_2/E_3`, `clip_box`; see epix-mirror `notebooks/planes.py`,
  `cube.py`, `polyhedra.py`, `sphere.py` for camera placement and plane drawing, and `samples/README`.
  Depth cues available: dashed hidden lines (`line_style`), plane fill with transparency-like light fills,
  `arrow` works in 3D.
- Math: projection onto a plane = `a − reject_from_plane` = the part of `a` in the bivector `e_12`
  (etc.); `src/gacalc/standardposition.py` (`rotate_in_xy_plane`/`rotate_in_xz_plane`, the "one plane
  at a time" reduction) and `proofs/GacalcProofs/Projection3D.lean`, `ProjectionRotation3D.lean`,
  `StandardPosition.lean`. The page is a placeholder today ("restart from the geometric product in 3D"),
  as is `three-dimensions.rst`.
- Naming: the maintainer's wording is `e_12`, `e_23`, `e_31` (cyclic); gacalc's blade constant is
  `Bivector.e_13` (= −`e_31`). See open question 1.

## Plan

- [x] `_scene3d.py`: `frame_scene(camera, box)` context manager (figure + `epix.camera.at`), `axes3()`
      (three arrow axes + x/y/z labels), `plane3(plane, faint=)` (light-filled `e_12`/`e_23`/`e_31`
      patch via `epix.Path` of four 3D points), `vector3`, `project_onto(plane)`, and `right_angle_3d`
      (right-angle square at an arbitrary corner, two direction legs). (Used `right_angle_3d` rather than
      a separate drop-line/foot marker — the rejection stub + right angle reads cleanly.)
- [x] Camera `Point(x=9, y=-6, z=5)` (tuned from the suggested `(5,-7,4)` so the y-axis doesn't collide
      with `a`), `a = Point(x=1.0, y=0.7, z=0.9)` — both constants in `_scene3d.py`.
- [x] Figures: `proj3d_overview` (a + all three faint planes); `proj3d_e12`/`e23`/`e31` — plane filled,
      a, projection (blue, in-plane), rejection (green, perpendicular) with right-angle marker.
- [x] `projection-rejection-3d.rst`: `.. figure::` entries with alt text, `.. TODO prose`, and the
      `e_31 = -e_13` note.
- [x] Verified: figures render; `make format` gate green; **full `make docs` (HTML + LuaLaTeX PDF) built
      clean** — HTML embeds all 17 figures across the three sections, `geometry2.pdf` is 118 pages, no
      real Sphinx warnings. Checked the 3D PNGs at size (readable; e31 is tight but color-distinguished).
- [x] Documented `_scene3d` in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures").

## Notes / decisions

- `epix.Point` supports `+`, scalar `*` and `.norm()`; `fig.png`/`fig.eepic` only materialize after the
  `with` block. The plane patch is drawn first (behind), then `axes3()`, then the vectors.
- `check_epix_keywords.py` now exempts exception constructors (`ValueError` etc.) from the positional-arg
  check — a figure helper raising `ValueError(msg)` on an unknown plane is a legitimate positional call.
- `vector3` hoists its `epix.black()` / `Point(...)` defaults to module constants (ruff B008).

## Open questions

None — decided 2026-10-07 (William Emerison Six <billsix@gmail.com>): labels `e_31` with a page note
(`e_13 = -e_31` in gacalc); three figures (one per plane, projection + rejection) plus an overview;
results only here — the 3D standard-position derivation pictures are a follow-on after the maintainer
restructures `proof-projection.rst` as 2D-then-3D.
