# Open the book by showing vectors build (and supersede) every high-school geometry object

**Status:** proposed — needs go-ahead (decisions recorded 2026-11-21; no open questions)
**Priority:** 4
**Difficulty:** 6 (a survey of a textbook, then new early book pages with figures)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

Go through a high-school geometry textbook and list every **kind of geometric object** it defines
(point, line, segment, ray, angle, plane, polygon, circle, …). Then, near the start of the book, show
how each one is built from **vectors**, so the student sees that one object, the vector (with
scalars and, later, the wedge), replaces the textbook's separate primitives. Done = a
`tasks/reference/` survey listing each textbook object with its definition and its vector
construction, and book pages near the start that present those constructions with figures.

## Context

- Read first: `CLAUDE.md`, `tasks/reference/book-outline.md` (its §H "The formal algebra": "Look at
  how **geometry textbooks** define things", and appendix item 22, the maintainer's raw idea that
  this task makes concrete), `tasks/reference/openstax-math-pedagogy.md` (the two-column
  statement | reason format), `tasks/reference/content-area-volume.md` ("connect back to high-school
  math"), `tasks/reference/teaching-order-and-dependencies.md`.
- **Overlap:** `tasks/affine-flats-lines-planes-from-points.md` (blocked) covers lines and planes
  *through points* (not through the origin) as a library/representation question. This task is the
  book side and, for the early pages, needs only the parametric forms (`p + t·v`), which gacalc can
  already compute. Cross-link both ways; don't wait on that task.
- Expected vector constructions (to confirm against the textbook's list):
  - point = a position vector `p`; segment `AB` = `{a + t(b − a) : 0 ≤ t ≤ 1}`; ray =
    `t ≥ 0`; line = all `t`; midpoint = `(a + b)/2`;
  - angle = a pair of rays from a vertex; its measure from the dot product, its orientation from the
    wedge;
  - plane (in 3D) = `p + s·u + t·v`; parallel / perpendicular = the wedge / dot of direction vectors
    is zero;
  - triangle / polygon = a closed chain of vectors summing to zero; area from the wedge
    (`measure.area`);
  - circle = `{c + r·(cos θ e₁ + sin θ e₂)}` (gacalc's 𝒢₂ `Vector.rotate(θ)`);
  - congruence / similarity = rotation, translation, reflection, uniform scaling
    (`transforms.py`).
- Placement is part of the book's ordering, which the maintainer owns (book-outline §"Current
  reading order"). Part I begins with hook, canonical-form, one-dimension, …, vectors-as-number-lines,
  vector-addition.

## Plan

1. Survey the textbook (Decisions): every defined object, with chapter/page, its
   definition, and its notation. Write it to `tasks/reference/high-school-geometry-objects.md`,
   each row paired with its vector construction and the gacalc call that computes it.
2. Draft the book page(s) at the chosen place: per object, the textbook definition, the vector
   form, a figure, and the two-column derivation where there is one.
3. `make` the book (the targets in `tasks/reference/book-and-docs-pipeline.md`) and check the pages.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- **Placement:** a new page right after vector-addition for points, segments, rays, lines and polygons; angle, area and perpendicular are added on the pages that introduce the dot and wedge.
- **Claim:** vectors *build* each textbook object (the textbook names stay as names for sets of vectors), not "replace" them.

- **The textbook** (William Emerison Six <billsix@gmail.com>, 2026-11-21): Pearson *Geometry: Common Core*, Randall I. Charles, Basia Hall, Dan Kennedy, Laurie E. Bass, Art Johnson (with Stuart J. Murphy and Grant Wiggins), copyright 2012. Bookshare lists a 2012 edition as ISBN 978-0-13-318582-9; the 2013/2015 printings are 978-0-13-328115-6 (not checked against Pearson; confirm on the maintainer's copy). Chapter outline: 1 Tools of Geometry, 2 Reasoning and Proof, 3 Parallel and Perpendicular Lines, 4 Congruent Triangles (these four checked online, 2026-11-21: mathleaks.com/study/pearson-geometry-common-core-2013); the rest, from memory of this series and to confirm: 5 Relationships Within Triangles, 6 Polygons and Quadrilaterals, 7 Similarity, 8 Right Triangles and Trigonometry, 9 Transformations, 10 Area, 11 Surface Area and Volume, 12 Circles, 13 Probability. The survey's main source is chapter 1 (point, line, plane, segment, ray, angle, midpoint, bisector, the coordinate distance and midpoint formulas), with each later chapter's new objects added. **Gotcha: the book is copyrighted, not open.** The survey paraphrases its definitions and cites chapter/section; the book page quotes nothing beyond a short definition with a citation.
