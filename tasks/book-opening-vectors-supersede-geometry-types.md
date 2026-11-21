# Open the book by showing vectors build every high-school geometry object

**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-21

Surveyed a high-school geometry textbook for every kind of object it defines, recorded each with its
vector construction, and added a book page right after vector-addition that builds the textbook's
first objects from vectors. The survey is `tasks/reference/high-school-geometry-objects.md`; read it
for the object list, the sources and what the book builds where.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- **Placement:** a new page right after vector-addition for points, segments, rays, lines and
  polygons; angle, area and perpendicular went on the page that introduces the dot and wedge.
- **Claim:** vectors *build* each textbook object (the textbook names stay as names for sets of
  vectors), not "replace" them.
- **The textbook:** Pearson *Geometry: Common Core*, Randall I. Charles, Basia Hall, Dan Kennedy,
  Laurie E. Bass, Art Johnson (with Stuart J. Murphy and Grant Wiggins), copyright 2012
  (2013/2015 printings ISBN 978-0-13-328115-6; confirm on the maintainer's copy). It is
  copyrighted: the survey paraphrases definitions and cites lesson numbers, and the book page
  quotes nothing.

## What was done

- **Survey** (`tasks/reference/high-school-geometry-objects.md`): every chapter and lesson title came
  from a school's public curriculum map for the book (mathleaks.com gave only chapters 1–4; the rest
  of its page loads by JavaScript). The map confirmed the 13-chapter outline the decision recorded
  from memory. Each object row gives the lesson, a paraphrased definition, the vector construction,
  the gacalc call and the book page that builds it (or "not built").
- **Book page** `book/docs/geometry-from-vectors.rst` ("Points, Segments, Lines and Polygons from
  Vectors"), after `vector-addition` in `book/docs/index.rst`: point as position vector
  (`eq-point`), segment `a + t * (b − a)` (`eq-segment`), midpoint with a reasoned chain
  (`eq-midpoint`) and its two equal halves, the distance formula (`eq-distance`), rays, opposite rays
  and the line (`eq-line`), collinear points, the triangle as a closed chain
  (`eq-triangle-closed`), perimeter, the midsegment, the median, the parallelogram (`eq-parallelogram`)
  iff its diagonals share a midpoint, and a "What has to wait" list (angle/area → dot and wedge,
  circle → rotate, congruence → translate/rotate/reflect, plane → Part II).
- **Dot and wedge page**: a new last section of `book/docs/product-from-projection.rst`, "Angle,
  area and perpendicular": an angle as two rays, its measure (`eq-angle-measure`), acute/right/
  obtuse/straight from the cosine, perpendicular (`u · v = 0`) and the perpendicular bisector through
  the quarter turn, parallel (`u ∧ v = 0`), area of the parallelogram and triangle
  (`eq-triangle-area`), the surveyor's formula, and the rectangle/rhombus/square tests. Sine and
  cosine are stated first, dot and wedge under them (`CLAUDE.md` "Presenting to students").
- **Figures** (ePiX, CC0): `book/figures/epix/geom_segment.py`, `geom_line.py`, `geom_triangle.py`,
  `geom_parallelogram.py`, `geom_angle.py`, sharing `book/figures/epix/_geometry_scene.py`.
- **Notebooks**: a new companion `notebooks/geometry-from-vectors.py` (symbolic throughout, live
  ePiX figures, `show_difference` for every check: the segment's ends, the midpoint at `t = ½` and
  its halves, the distance formula, ray points, the triangle's closure, the midsegment, the
  parallelogram's midpoint gap as minus half its side gap); `notebooks/product-from-projection.py`
  gained a section checking the side-dot-quarter-turn `= 0`, the perpendicular bisector's equal
  distances, and the surveyor's formula, with a live triangle figure.
- **Lean** `proofs/GacalcProofs/GeometryObjects2D.lean` (imported from `proofs/GacalcProofs.lean`):
  `segmentMidpoint_eq_segment_half`, `segmentMidpoint_halves`, `triangle_sides_sum_zero`,
  `parallelogram_iff_diagonals_bisect`, `midsegment_eq_half_side`, `wedge_sides_eq_surveyor`, each
  with a `twin:` tag matched in the notebooks. Perpendicular and parallel cite the existing
  `Predicates2D.lean` (`wedge_eq_zero_iff_parallel`).
- **Docs kept true**: `book/docs/proof-dependencies.dot` (nodes `segment`, `polygon`, `angle_area`),
  `tasks/reference/teaching-order-and-dependencies.md`, `tasks/reference/book-outline.md` (reading
  order, file layout, §D), `tasks/reference/book-and-docs-pipeline.md` (`_geometry_scene.py`),
  `notebooks/README.md`, `proofs/README.md`, and the cross-link in
  `tasks/affine-flats-lines-planes-from-points.md` (still blocked; the plane and intersections wait
  on it).

## Three forms, and what was skipped

- The six stated results have all three forms (Lean, symbolic notebook cell, page prose).
- **Lean skipped** for the angle measure `u · v = |u| * |v| * cos(θ)` (the book defines the angle's
  cosine through that quotient in `proof-rotate-from-a-to-b`, so it is a definition here), the
  distance formula (the definition of `magnitude`), and the perpendicular bisector's
  equal-distance property (a one-line consequence of the dot facts already proved; checked
  symbolically in the notebook only).
- **Not built**, by scope: circles, regular polygons, dilations and the plane (each named on the page
  as waiting for `rotate` or Part II), intersections (a solving question, the blocked affine-flats
  task), constructions, and the angle-pair vocabulary of lesson 1-5. `orthogonal.rst` is still a
  placeholder; perpendicular is taught in `product-from-projection` instead, and the survey points
  there.
- The reference cards (`cheat-sheet-2d`) were not changed: none of their formulas changed, and the
  new formulas (segment, midpoint) are not on a card.

## Gates

All run nested on 2026-11-21 against a freshly built full image (`make image`, every layer but the
late dependency layer from cache):

- `make format`: exit 0 (after `check_notebook_prose_width.py --fix` rewrapped one figure docstring).
- `make test`: exit 0, 1407 passed, 3 skipped, 12 deselected.
- `make check-notebooks`: exit 0, pyright 0 errors.
- `make lean`: exit 0; the axioms gate reports 1117 declarations on the standard three axioms. The
  run built the whole `GacalcProofs` library from an empty `proofs/.lake/build` (`G3.lean` alone took
  1725 s), so expect a long first run on a fresh checkout.
- `make docs`: exit 0, the overflow check reports 0 equations or tables too wide and 0 boxes too
  tall; no new Sphinx warnings from the changed pages. The rendered figures and live notebook
  figures were inspected and two labels moved off their lines.
- `tools/check_annotations.py` lists nothing in the new or changed notebooks.
