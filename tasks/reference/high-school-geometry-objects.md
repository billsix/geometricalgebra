# High-school geometry objects, and the vectors that build them

**Reference document.** Lists every kind of geometric object a standard US high-school geometry
textbook defines, each paired with its vector construction, the gacalc call that computes it and
the place in "Geometry 2" that teaches it. Updated in place; never archived. Created 2026-11-21
(William Emerison Six <billsix@gmail.com>) by
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.

**The claim the book makes** (the maintainer's decision, 2026-11-21): vectors **build** each
textbook object. The textbook's names stay, as names for sets of vectors ("the segment from
`a` to `b`" is the set `{a + t * (b − a) : 0 ≤ t ≤ 1}`); the book does not say vectors replace
them.

## The textbook, and how it was surveyed

- **The book:** Pearson *Geometry: Common Core*, Randall I. Charles, Basia Hall, Dan Kennedy,
  Laurie E. Bass, Art Johnson (with Stuart J. Murphy and Grant Wiggins), copyright 2012 (2013/2015
  printings ISBN 978-0-13-328115-6). It is **copyrighted and was not read**. Its lesson titles come
  from public lists: the first four chapter titles from
  `https://mathleaks.com/study/pearson-geometry-common-core-2013` (the rest of that page loads by
  JavaScript), and every chapter and lesson title, with the page where each lesson's exercises
  start, from a school's public curriculum map for this book
  (`https://docs.google.com/document/d/1E0W3Azq7wITJcm_-5PPAt2zIVPwfijEA`, read 2026-11-21; it
  names neither the book nor the edition, but its lesson numbers and titles match the series).
- **Definitions are paraphrased** in standard high-school wording, not copied. The page numbers
  below are where a lesson's exercises begin, per that map, so the lesson's own definitions sit a
  few pages earlier. **Confirm both against the maintainer's copy** before quoting the book.
- **The Common Core standards** the book is written to (HSG-CO.A.1: precise definitions of angle,
  circle, perpendicular line, parallel line and line segment "based on the undefined notions of
  point, line, distance along a line, and distance around a circular arc"; HSG-GPE.B.4–7:
  coordinates for proofs, slopes of parallel and perpendicular lines, dividing a segment in a
  ratio, perimeter and area by the distance formula) name the same objects.

Chapters: 1 Tools of Geometry · 2 Reasoning and Proof · 3 Parallel and Perpendicular Lines ·
4 Congruent Triangles · 5 Relationships Within Triangles · 6 Polygons and Quadrilaterals ·
7 Similarity · 8 Right Triangles and Trigonometry · 9 Transformations · 10 Area · 11 Surface Area
and Volume · 12 Circles · 13 Probability. Chapter 2 (logic) and chapter 13 (probability) define no
geometric objects.

## The objects

"Where" is the page of "Geometry 2" that builds the object: `geometry-from-vectors` is
`book/docs/geometry-from-vectors.rst`, right after `vector-addition`; `product-from-projection`'s
section "Angle, area and perpendicular" adds the objects that need the dot and the wedge. In the
vector column, lowercase letters are position vectors (points) and `s`, `t` are real numbers.

### Chapter 1, Tools of Geometry (the undefined terms and the first definitions)

| Object (lesson, exercises p.) | Textbook definition, paraphrased | Vector construction | gacalc | Where |
| --- | --- | --- | --- | --- |
| point (1-2, p. 16) | undefined; a location, no size | a position vector `p` | `Scalar(p_1) * e_1 + Scalar(p_2) * e_2` | geometry-from-vectors |
| line (1-2) | undefined; a straight path of points extending without end both ways | `{a + t * (b − a) : t real}` | `a + t * (b - a)` | geometry-from-vectors |
| plane (1-2) | undefined; a flat surface extending without end | 3D: `{p + s * u + t * v}`, `u ∧ v ≠ 0` | `p + s * u + t * v` (𝒢₃) | Part II; `tasks/affine-flats-lines-planes-from-points.md` |
| collinear / coplanar points (1-2) | points that lie on one line / one plane | `c = a + t * (b − a)` for some `t`; equivalently `(b − a) ∧ (c − a) = 0` | `(b - a).is_parallel_to(c - a)` | geometry-from-vectors (the `t` form); the wedge test after `product-from-projection` |
| segment (1-2) | the two endpoints and every point of the line between them | `{a + t * (b − a) : 0 ≤ t ≤ 1}` | `translate(b=b - a).at(t)(a)` | geometry-from-vectors |
| ray (1-2) | an endpoint and every point of the line on one side of it | `{a + t * (b − a) : t ≥ 0}` | as the segment, `t ≥ 0` | geometry-from-vectors |
| opposite rays (1-2) | two rays with one endpoint that together form a line | `t ≥ 0` and `t ≤ 0` from the same `a` | | geometry-from-vectors |
| intersection (1-2) | the points two figures share | the parameters where two constructions are equal | | (not built: needs solving, the subject of `tasks/affine-flats-lines-planes-from-points.md`) |
| length of a segment / distance (1-3, p. 23) | the distance between the endpoints, by the Ruler Postulate | `\|b − a\|` | `abs(b - a)` | geometry-from-vectors |
| congruent segments (1-3) | segments of equal length | `\|b − a\| = \|d − c\|` | | geometry-from-vectors |
| midpoint (1-3) | the point that divides a segment into two congruent segments | `(a + b) / 2`, the segment at `t = 1/2` | `(a + b) / 2` | geometry-from-vectors (`:eq:` `eq-midpoint`) |
| segment bisector (1-3) | a line, ray or segment through the midpoint | any line through `(a + b) / 2` | | geometry-from-vectors |
| angle, vertex, sides (1-4, p. 31) | two rays with a common endpoint, the vertex | the rays `b + s * (a − b)`, `b + t * (c − b)`, `s, t ≥ 0` | | geometry-from-vectors (the rays); product-from-projection (its measure) |
| measure of an angle (1-4) | a number of degrees, by the Protractor Postulate | `cos(θ) = u · v / (\|u\| * \|v\|)`, `sin(θ)` from `u ∧ v`, with `u = a − b`, `v = c − b` | `u.dot(v).scalar_part() / (abs(u) * abs(v))` | product-from-projection |
| acute, right, obtuse, straight angle (1-4) | measure below 90°, 90°, between 90° and 180°, 180° | the sign of `u · v` (positive, zero, negative); straight: `u ∧ v = 0` with `u · v < 0` | | product-from-projection |
| congruent angles, angle bisector (1-4) | equal measures; a ray that cuts an angle into two congruent angles | bisector direction `û + v̂` | `u.normalize() + v.normalize()` | product-from-projection (named; not computed) |
| adjacent, vertical, complementary, supplementary angles, linear pair (1-5, p. 38) | angle pairs by position or by measures summing to 90° / 180° | from the rays: a linear pair shares `u` and uses `−u` | | (not built separately: each is a pair of the angles above) |
| construction (1-6, p. 46) | a figure drawn with compass and straightedge only | (a method, not an object) | | not covered |
| distance and midpoint formulas (1-7, p. 53) | `d = sqrt((x₂ − x₁)² + (y₂ − y₁)²)`; `M = ((x₁ + x₂)/2, (y₁ + y₂)/2)` | the coordinates of `\|b − a\|` and `(a + b) / 2` | `abs(b - a)`, `(a + b) / 2` | geometry-from-vectors |
| perimeter (1-8, p. 64) | the sum of the side lengths | `\|b − a\| + \|c − b\| + \|a − c\|` | | geometry-from-vectors |
| area (1-8) | the number of square units a figure encloses | parallelogram `\|u ∧ v\|`, triangle `\|u ∧ v\| / 2` | `measure.area(u, v)` | product-from-projection |
| circle, circumference (1-8) | see chapter 12 | | | |

### Chapter 3, Parallel and Perpendicular Lines

| Object (lesson, exercises p.) | Textbook definition, paraphrased | Vector construction | gacalc | Where |
| --- | --- | --- | --- | --- |
| parallel lines (3-1, p. 144) | coplanar lines that do not meet | direction vectors with `u ∧ v = 0` (the sine of the angle between them is 0) | `u.is_parallel_to(v)` | product-from-projection |
| skew lines, parallel planes (3-1) | non-coplanar lines that do not meet; planes that do not meet | 3D: `(u ∧ v) ∧ (b − a) ≠ 0` with `u ∧ v ≠ 0` | | Part II (not built) |
| transversal, corresponding / alternate / same-side angles (3-1) | a line crossing two others, and the angle pairs it makes | angles between the transversal's direction and each line's | | (not built separately) |
| perpendicular lines (3-4, p. 167) | lines that meet at right angles | `u · v = 0` (the cosine of the angle is 0) | `u.is_orthogonal_to(v)` | product-from-projection; `orthogonal` |
| perpendicular bisector (5-2, p. 296) | the line perpendicular to a segment at its midpoint | `(a + b) / 2 + t * r(b − a; π/2)` | `(a + b) / 2 + t * (b - a).rotate_90_degrees()` | product-from-projection |
| slope, equations of lines (3-7, 3-8, pp. 194, 201) | rise over run; `y = m * x + b`, point-slope form | a line `p + t * d` with `d = 1 * e₁ + m * e₂`; parallel slopes equal, perpendicular slopes multiply to −1 (`d · d′ = 0`) | | geometry-from-vectors (the line); product-from-projection (perpendicular) |

### Chapters 4–7, triangles, polygons, similarity

| Object (lesson, exercises p.) | Textbook definition, paraphrased | Vector construction | gacalc | Where |
| --- | --- | --- | --- | --- |
| polygon, triangle, quadrilateral (1-8; 6-1, p. 356) | a closed plane figure of three or more segments meeting only at their endpoints | vertices `a, b, c, …`; sides `b − a, c − b, …`, which sum to zero going around | | geometry-from-vectors |
| congruent figures (4-1, p. 222) | same size and shape; corresponding sides and angles congruent | one figure is the other moved by translations, rotations, reflections | `translate`, `Vector.rotate`, `Vector.reflect` | vector-addition (translate), rotate, reflection |
| isosceles / equilateral / right triangle (4-5, 4-6) | two sides equal / three sides equal / one right angle | side lengths `\|b − a\|` equal; a right angle `u · v = 0` | | geometry-from-vectors (lengths); product-from-projection (right angle) |
| midsegment of a triangle (5-1, p. 288) | the segment joining the midpoints of two sides | `(a + c)/2 − (a + b)/2 = (c − b)/2`: parallel to the third side, half as long | | geometry-from-vectors |
| median (5-4, p. 312) | the segment from a vertex to the midpoint of the opposite side | from `a` to `(b + c) / 2`; the medians meet at the centroid `(a + b + c) / 3` | | geometry-from-vectors (the median; the centroid is named only) |
| altitude (5-4) | the perpendicular segment from a vertex to the line of the opposite side | `rej_{c − b}(a − b)`, the rejection | `(a - b).reject(c - b)` | `projection` (named there by its parts) |
| angle bisector, incenter, circumcenter (5-2, 5-3) | concurrency points of the bisectors | | | not built |
| parallelogram (6-2, p. 364) | a quadrilateral with both pairs of opposite sides parallel | `b − a = c − d`; its diagonals bisect each other exactly then | | geometry-from-vectors |
| rhombus, rectangle, square (6-4, p. 379) | a parallelogram with four equal sides / four right angles / both | parallelogram plus `\|b − a\| = \|c − b\|` / `(b − a) · (c − b) = 0` / both | | product-from-projection (named) |
| trapezoid, kite (6-6, p. 394) | one pair of parallel sides / two pairs of equal adjacent sides | `(b − a) ∧ (c − d) = 0` / two length equalities | | (not built separately) |
| ratio, similar polygons (7-1, 7-2, pp. 436, 444) | same shape: angles congruent, sides in proportion | one is the other uniformly scaled (and moved) | `uniform_scale(m=…)` | `one-dimension` (the `m * x` scaling), rotate |

### Chapters 8–12, trigonometry, transformations, area, solids, circles

| Object (lesson, exercises p.) | Textbook definition, paraphrased | Vector construction | gacalc | Where |
| --- | --- | --- | --- | --- |
| sine, cosine, tangent of an acute angle (8-3, p. 510) | ratios of the sides of a right triangle | `cos(θ) = u · v / (\|u\| * \|v\|)`; `sin(θ) * \|u\| * \|v\|` is the `e₁₂` part of `u ∧ v` | | `trigonometry`; product-from-projection |
| translation (9-1, p. 550) | every point moved the same distance in the same direction | `v ↦ v + b` | `translate(b=b)` | vector-addition |
| reflection (9-2, p. 557) | each point mapped to its mirror image across a line | `v ↦ 2 * proj_n(v) − v` | `Vector.reflect(across=n)` | reflection |
| rotation (9-3, p. 564) | each point turned through an angle about a center | `r(v; θ) = cos(θ) * v + sin(θ) * r(v; π/2)` | `v.rotate(θ)` | rotate |
| composition of isometries, congruence transformation (9-4, 9-5) | one transformation after another; a composition that preserves size and shape | composition of functions | `@`, `compose([...])` | relative-graph-paper |
| dilation (9-6, p. 590) | each point scaled by a factor from a center | `v ↦ c + k * (v − c)` | `uniform_scale(m=k)` conjugated by `translate` | (not built separately) |
| area of a parallelogram, triangle (10-1, p. 619) | base times height; half that | `\|u ∧ v\|`, `\|u ∧ v\| / 2`; from the corners, the surveyor's formula | `measure.area(u, v)` | product-from-projection |
| regular polygon (10-3, p. 632) | equal sides and equal angles | vertices `c + r(p − c; 2 * π * k / n)` | `v.rotate(2 * sympy.pi * k / n)` | (not built) |
| circle, center, radius, arc, central angle (10-6, p. 654) | the set of points in a plane at one distance from a center | `{c + r(r_0; θ)}`: a radius vector `r_0` rotated by every `θ` | `c + r_0.rotate(θ)` | rotate (named only) |
| sector, arc length (10-7, p. 663) | the region between two radii and an arc; the arc's length | `θ * \|r_0\|` (radians) | | (not built) |
| space figures, prism, cylinder, pyramid, cone, sphere (11-1 to 11-6) | solids bounded by polygons or curved surfaces | 3D; volume of the box on three edges `\|u ∧ v ∧ w\|` | `measure.volume(u, v, w)` | Part II (`three-dimensions`) |
| tangent line, chord, inscribed angle (12-1 to 12-3, pp. 767–784) | a line meeting a circle once; a segment with both ends on it; an angle with vertex on it | tangent at `p`: direction `r(p − c; π/2)`, perpendicular to the radius | | (not built) |
| circle in the coordinate plane (12-5, p. 801) | `(x − h)² + (y − k)² = r²` | `\|v − c\| = r` | `abs(v - c)` | (not built) |
| locus (12-6) | the set of points meeting a condition | a set of vectors satisfying an equation | | (not built) |

## What the book builds, and in what order

Every construction on `geometry-from-vectors` uses only what the book has taught by the end of
`vector-addition`: vectors as arrows from the origin, adding and subtracting them, a number times a
vector (`vectors-as-number-lines`), and `translate(b=…).at(t)`. Length is the Pythagorean theorem
on a vector's coordinates (`trigonometry`), introduced there as the textbook's distance formula.
The objects that need more wait for it (`tasks/reference/teaching-order-and-dependencies.md`):

- **dot and wedge** (`product-from-projection`): angle measure, right angle, perpendicular,
  parallel (the wedge test), area, the rectangle / rhombus / square tests;
- **rotation** (`rotate`): circles, regular polygons, rotation as a congruence;
- **3D** (Part II): the plane, skew lines, solids and their volumes.

The machine-checked statements are in `proofs/GacalcProofs/GeometryObjects2D.lean`: the midpoint
as the segment at `t = 1/2` and as two equal halves, a triangle's sides summing to zero, the
parallelogram iff its diagonals bisect each other, the midsegment, and the surveyor's area formula.
Each carries a `twin:` tag matching the cell of `notebooks/geometry-from-vectors.py` or
`notebooks/product-from-projection.py` that checks it.
