# Step 3: ePiX figures for projection and rejection in 3D onto the e_12, e_23 and e_31 planes

**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-10-07 (overnight autonomous run)
**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py`
conventions), step 2 (the 2D cast and idioms) · **Next:** — (last step)

The book's first 3D figures, for `book/docs/projection-rejection-3d.rst` (a placeholder before this
step): a vector `a` in 3D and its **projection onto** and **rejection from** each coordinate plane —
`e_12` (xy), `e_23` (yz), `e_31` (zx) — drawn with ePiX's 3D camera through a new `_scene3d.py` helper.
The camera and plane idioms came from epix-mirror's `notebooks/planes.py`, `cube.py`, `polyhedra.py`,
`sphere.py`; the math is `src/gacalc/standardposition.py` and
`proofs/GacalcProofs/Projection3D.lean`, `ProjectionRotation3D.lean`, `StandardPosition.lean`.

## What was done

- `_scene3d.py`: a `frame_scene(camera, box)` context manager (figure + `epix.camera.at`), `axes3()`
  (three arrow axes + x/y/z labels), `plane3(plane, faint=)` (a light-filled `e_12`/`e_23`/`e_31`
  patch via an `epix.Path` of four 3D points), `vector3`, `project_onto(plane)`, and `right_angle_3d`
  (right-angle square at an arbitrary corner, two direction legs). `right_angle_3d` was used instead of
  a separate drop-line/foot marker because the rejection stub plus right angle read cleanly.
- Camera `Point(x=9, y=-6, z=5)` (tuned from the suggested `(5,-7,4)` so the y-axis doesn't collide
  with `a`) and `a = Point(x=1.0, y=0.7, z=0.9)`, both constants in `_scene3d.py`.
- Figures: `proj3d_overview` (a + all three faint planes); `proj3d_e12`/`e23`/`e31` — plane filled,
  a, projection (blue, in-plane), rejection (green, perpendicular) with a right-angle marker.
- `projection-rejection-3d.rst`: `.. figure::` entries with alt text, `.. TODO prose`, and the
  `e_31 = -e_13` note.
- `_scene3d` was documented in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-07)

- Labels use the maintainer's cyclic `e_31`, with a page note that gacalc's blade constant is
  `Bivector.e_13` (`e_13 = -e_31`).
- Three figures (one per plane, projection + rejection) plus an overview.
- Results only here; the 3D standard-position derivation pictures were left as a follow-on, after the
  maintainer restructures `proof-projection.rst` as 2D-then-3D.

## Implementation notes

- `epix.Point` supports `+`, scalar `*` and `.norm()`; `fig.png`/`fig.eepic` only materialize after the
  `with` block. The plane patch is drawn first (behind), then `axes3()`, then the vectors.
- `check_epix_keywords.py` now exempts exception constructors (`ValueError` etc.) from the
  positional-arg check — a figure helper raising `ValueError(msg)` on an unknown plane is a legitimate
  positional call.
- `vector3` hoists its `epix.black()` / `Point(...)` defaults to module constants (ruff B008).

## Verification

Figures rendered; the `make format` gate was green; the **full `make docs` (HTML + LuaLaTeX PDF) built
clean** — HTML embedded all 17 figures across the three sections, `geometry2.pdf` was 118 pages, no
real Sphinx warnings. The 3D PNGs were checked at size (readable; e31 is tight but colour-distinguished).
