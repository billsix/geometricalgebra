# Step 3: ePiX figures for projection and rejection in 3D onto the e_12, e_23 and e_31 planes

**Part of:** `tasks/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py` conventions), step 2
(the 2D cast and idioms) · **Next:** — (last step; the umbrella archives when this lands)
**Status:** proposed — needs go-ahead.
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

- [ ] `_scene3d.py`: a `frame_scene(camera, box)` context manager drawing the three axes with
      arrowheads and labels `x`, `y`, `z`, a light-filled coordinate plane helper (`plane(e_12)` etc.),
      `vector3`, a `drop_line` (dashed perpendicular from a point to a plane) and `foot` marker.
- [ ] Pick one camera position for the whole section (e.g. `epix.camera.at(Point(x=5, y=-7, z=4))`) and
      one `a` (e.g. `Point(x=1.0, y=0.7, z=0.9)`); record both in the helper as the section's constants.
- [ ] Figures: `proj3d_overview.py` (a with all three planes faint); `proj3d_e12.py`, `proj3d_e23.py`,
      `proj3d_e31.py` — each: the plane filled, `a`, its projection on the plane (blue, in-plane), the
      rejection (green, perpendicular stub) with the right-angle marker, `a = project + reject`.
- [ ] `projection-rejection-3d.rst`: `.. figure::` entries with alt text; `.. TODO prose`.
- [ ] Verify: `make docs` nested; check the PDF (vector) and PNG (flattened background) — and check the
      PNG at the HTML size, since 3D figures with thin dashed lines can be hard to read when small.
- [ ] Document the 3D helper in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures").

## Notes / decisions

## Open questions

1. Plane labels: `e_31` (the maintainer's wording, cyclic) or `e_13` (gacalc's `Bivector.e_13`)?
   Recommendation: `e_31` in the figures with a one-line note on the page that gacalc spells the blade
   `e_13 = -e_31`.
2. Three figures (one per plane, each showing projection and rejection) plus an overview, or six (one per
   operation per plane)? Recommendation: three plus the overview.
3. Should these 3D figures also show the "one plane at a time" standard-position reduction (the 3D
   derivation `proof-projection.rst` narrates), or only the results? Recommendation: results here; the
   derivation figures are a follow-on once the maintainer settles the page's 2D-then-3D structure
   (step 2, open question 1).
