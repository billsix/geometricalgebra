..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Points, Segments, Lines and Polygons from Vectors
=================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending. The companion
   notebook is runnable, and the Lean theorems cited are machine-checked.

A high-school geometry course starts with three words it does not define: **point**, **line** and
**plane**. Everything else, the segment, the ray, the midpoint, the triangle, is defined from
those three (Charles et al., *Geometry: Common Core*, Pearson, 2012, chapter 1, "Tools of
Geometry").

This book has one object, the vector, and so far two things to do with it: add two vectors, and
multiply a vector by a number. That is already enough to build the first chapter of a geometry
course. Each object keeps its name. The name now means a set of vectors, and the set is written
down, so a computer can draw it and check facts about it.

..
   covers: pearson-geo/tools/points-lines-planes/point

Points
------

A geometry textbook says a point marks a location and has no size. A location in the plane is
where an arrow from the origin ends, so a **point is a vector** from the origin, its *position
vector*. The point :math:`A` is the head of :math:`\vec{\mathbf{a}}`, and its coordinates are the
arrow's:

.. math::
   :label: eq-point

   \vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2.

From here on this page names a point by its vector, and says "the point :math:`\vec{\mathbf{a}}`".

..
   covers: pearson-geo/tools/points-lines-planes/segment

Segments
--------

A textbook defines the segment :math:`AB` as the two endpoints and every point of the line between
them. With vectors, "between" becomes a recipe. The trip from :math:`\vec{\mathbf{a}}` to
:math:`\vec{\mathbf{b}}` is :math:`\vec{\mathbf{b}} - \vec{\mathbf{a}}`, the vector you add to
:math:`\vec{\mathbf{a}}` to get :math:`\vec{\mathbf{b}}` (:doc:`vector-addition`). Start at
:math:`\vec{\mathbf{a}}` and go the fraction :math:`t` of that trip:

.. math::
   :label: eq-segment

   \vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}}), \qquad 0 \le t \le 1.

At :math:`t = 0` you have not moved, and you are at :math:`\vec{\mathbf{a}}`. At :math:`t = 1` you
have made the whole trip, and you are at :math:`\vec{\mathbf{b}}`. Every :math:`t` in between
gives a point between them, and the set of all of them is the segment.

.. figure:: _static/epix/geom-segment.*
   :align: center
   :alt: the points a and b as arrows from the origin, the trip b minus a between their heads, and the segment with the points at t equal to 0, one half and 1

This is the slide of :doc:`vector-addition`, stopped part way:
``translate(b=b - a).at(t)`` slides :math:`\vec{\mathbf{a}}` the fraction :math:`t` of the way
along :math:`\vec{\mathbf{b}} - \vec{\mathbf{a}}`.

..
   covers: pearson-geo/tools/segments/midpoint
   covers: pearson-geo/tools/coordinate-plane/midpoint-formula

The midpoint
^^^^^^^^^^^^

The textbook's midpoint is the point that cuts a segment into two equal pieces. Half way along the
trip is :math:`t = \frac{1}{2}` in :eq:`eq-segment`. Simplify it, one rule per line:

.. math::
   :label: eq-midpoint

   \begin{aligned}
   \vec{\mathbf{a}} + \tfrac{1}{2} * (\vec{\mathbf{b}} - \vec{\mathbf{a}})
     &= \vec{\mathbf{a}} + \tfrac{1}{2} * \vec{\mathbf{b}} - \tfrac{1}{2} * \vec{\mathbf{a}}
     && \text{distribute the } \tfrac{1}{2} \\
     &= \tfrac{1}{2} * \vec{\mathbf{a}} + \tfrac{1}{2} * \vec{\mathbf{b}}
     && \text{collect the } \vec{\mathbf{a}} \text{ terms} \\
     &= \tfrac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{b}})
     && \text{factor out the } \tfrac{1}{2}.
   \end{aligned}

Call it :math:`\vec{\mathbf{m}} = \frac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{b}})`. In
coordinates it is :math:`\left(\frac{a_1 + b_1}{2}, \frac{a_2 + b_2}{2}\right)`, the textbook's
midpoint formula (its lesson 1-7, "Midpoint and Distance in the Coordinate Plane"). Does it cut the
segment into two equal pieces? The trip from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{m}}`
and the trip from :math:`\vec{\mathbf{m}}` to :math:`\vec{\mathbf{b}}` are

.. math::

   \vec{\mathbf{m}} - \vec{\mathbf{a}} = \tfrac{1}{2} * (\vec{\mathbf{b}} - \vec{\mathbf{a}})
     = \vec{\mathbf{b}} - \vec{\mathbf{m}},

the same vector, so the two halves have the same length and point the same way. The Lean proofs
state both facts as ``segmentMidpoint_eq_segment_half`` and ``segmentMidpoint_halves`` in
``proofs/GacalcProofs/GeometryObjects2D.lean``.

..
   covers: pearson-geo/tools/segments/length
   covers: pearson-geo/tools/segments/congruent-segments
   covers: pearson-geo/tools/coordinate-plane/distance-formula

Length and distance
^^^^^^^^^^^^^^^^^^^

The length of the segment is the length of the trip :math:`\vec{\mathbf{b}} - \vec{\mathbf{a}}`. Its
coordinates are the legs of a right triangle, so the Pythagorean theorem gives

.. math::
   :label: eq-distance

   |\vec{\mathbf{b}} - \vec{\mathbf{a}}| = \sqrt{(b_1 - a_1)^2 + (b_2 - a_2)^2},

the textbook's distance formula. Two segments are **congruent** when they have the same length.

..
   covers: pearson-geo/tools/points-lines-planes/ray
   covers: pearson-geo/tools/points-lines-planes/opposite-rays
   covers: pearson-geo/tools/points-lines-planes/line
   covers: pearson-geo/tools/points-lines-planes/collinear

Rays and lines
--------------

Let :math:`t` in :eq:`eq-segment` run past :math:`0` and :math:`1`. With :math:`t \ge 0` you start
at :math:`\vec{\mathbf{a}}` and keep going through :math:`\vec{\mathbf{b}}` and on forever: that
is the **ray** from :math:`\vec{\mathbf{a}}` through :math:`\vec{\mathbf{b}}`. With :math:`t \le 0`
you go the other way, the **opposite ray**. With every :math:`t` you get both, the **line**
through :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`:

.. math::
   :label: eq-line

   \vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}}), \qquad t \text{ any number}.

.. figure:: _static/epix/geom-line.*
   :align: center
   :alt: the ray from a through b for t at least 0, and the opposite ray for t at most 0, together making the line

The textbook leaves "line" undefined; here it is a formula. Three points are **collinear** when the
third is on the line through the first two, that is, when
:math:`\vec{\mathbf{c}} = \vec{\mathbf{a}} + t * (\vec{\mathbf{b}} - \vec{\mathbf{a}})` for some
number :math:`t`.

..
   covers: pearson-geo/quadrilaterals/angle-sums/polygon
   covers: pearson-geo/tools/perimeter-area/perimeter

Triangles and polygons
----------------------

A textbook polygon is a closed figure made of segments that meet only at their ends; a triangle
has three. With vectors a triangle is its three corners :math:`\vec{\mathbf{a}}`,
:math:`\vec{\mathbf{b}}`, :math:`\vec{\mathbf{c}}`, and its sides are the trips between them.
Walk around it and you are back where you started, so the sides add up to nothing:

.. math::
   :label: eq-triangle-closed

   \begin{aligned}
   (\vec{\mathbf{b}} - \vec{\mathbf{a}}) + (\vec{\mathbf{c}} - \vec{\mathbf{b}})
     + (\vec{\mathbf{a}} - \vec{\mathbf{c}})
     &= (\vec{\mathbf{a}} - \vec{\mathbf{a}}) + (\vec{\mathbf{b}} - \vec{\mathbf{b}})
       + (\vec{\mathbf{c}} - \vec{\mathbf{c}})
     && \text{regroup the six terms} \\
     &= 0.
   \end{aligned}

The same holds for any polygon: its sides are a chain of vectors, tip to tail, that ends where it
began. Its **perimeter** is the sum of the side lengths; for a triangle,

.. math::

   |\vec{\mathbf{b}} - \vec{\mathbf{a}}| + |\vec{\mathbf{c}} - \vec{\mathbf{b}}|
     + |\vec{\mathbf{a}} - \vec{\mathbf{c}}|.

.. figure:: _static/epix/geom-triangle.*
   :align: center
   :alt: a triangle with its three side vectors chained tip to tail, and the midsegment joining the midpoints of two sides

..
   covers: pearson-geo/within-triangles/midsegments/midsegment
   covers: pearson-geo/within-triangles/medians/median

The midsegment
^^^^^^^^^^^^^^

A textbook proves, in its chapter 5, that the segment joining the midpoints of two sides of a
triangle is parallel to the third side and half as long. With :eq:`eq-midpoint` it is a few lines
of algebra:

.. math::

   \begin{aligned}
   \tfrac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{c}}) - \tfrac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{b}})
     &= \tfrac{1}{2} * \vec{\mathbf{a}} + \tfrac{1}{2} * \vec{\mathbf{c}}
       - \tfrac{1}{2} * \vec{\mathbf{a}} - \tfrac{1}{2} * \vec{\mathbf{b}}
     && \text{distribute} \\
     &= \tfrac{1}{2} * (\vec{\mathbf{c}} - \vec{\mathbf{b}})
     && \text{the } \vec{\mathbf{a}} \text{ terms cancel}.
   \end{aligned}

The midsegment is :math:`\frac{1}{2}` times the third side, so it points the same way and is half
as long. (Lean: ``midsegment_eq_half_side``.)

The median from :math:`\vec{\mathbf{a}}` is the segment from :math:`\vec{\mathbf{a}}` to the
midpoint :math:`\frac{1}{2} * (\vec{\mathbf{b}} + \vec{\mathbf{c}})` of the opposite side.

..
   covers: pearson-geo/quadrilaterals/parallelograms/parallelogram

Parallelograms
^^^^^^^^^^^^^^

Take four corners :math:`\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}, \vec{\mathbf{d}}` in
order. The quadrilateral is a **parallelogram** when side :math:`\vec{\mathbf{a}}\vec{\mathbf{b}}`
and the opposite side :math:`\vec{\mathbf{d}}\vec{\mathbf{c}}` are the same trip:

.. math::
   :label: eq-parallelogram

   \vec{\mathbf{b}} - \vec{\mathbf{a}} = \vec{\mathbf{c}} - \vec{\mathbf{d}}.

A textbook proves that the diagonals of a parallelogram cut each other in half, and, separately,
the converse. With vectors both directions are one line. Add :math:`\vec{\mathbf{a}} + \vec{\mathbf{d}}`
to both sides of :eq:`eq-parallelogram`, then halve:

.. math::

   \vec{\mathbf{b}} + \vec{\mathbf{d}} = \vec{\mathbf{c}} + \vec{\mathbf{a}}
   \qquad\Longleftrightarrow\qquad
   \tfrac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{c}}) = \tfrac{1}{2} * (\vec{\mathbf{b}} + \vec{\mathbf{d}}).

The right-hand equation says the diagonal from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{c}}`
and the diagonal from :math:`\vec{\mathbf{b}}` to :math:`\vec{\mathbf{d}}` have the same midpoint
:math:`\vec{\mathbf{m}}`. Each step can be undone, so the sides match exactly when the diagonals
share their midpoint. (Lean: ``parallelogram_iff_diagonals_bisect``.)

.. figure:: _static/epix/geom-parallelogram.*
   :align: center
   :alt: a parallelogram with equal opposite side vectors, and its two diagonals meeting at their shared midpoint m

What has to wait
----------------

Some of a textbook's first objects need more than adding and stretching:

- the **measure of an angle**, a **right angle**, **perpendicular** and **parallel** lines, and
  **area** need the dot and the wedge, and arrive in :doc:`product-from-projection`;
- a **circle** is a radius vector turned through every angle, so it waits for :doc:`rotate`;
- **congruent** figures are one figure moved onto another by a slide (:doc:`vector-addition`),
  a turn (:doc:`rotate`) or a flip (:doc:`reflection`);
- a **plane** in space is a point plus two directions, :math:`\vec{\mathbf{p}} + s * \vec{\mathbf{u}} + t * \vec{\mathbf{v}}`,
  and waits for Part II.

The companion notebook works every step of this page with the coordinates left as symbols.

.. toctree::
   :maxdepth: 1

   notebooks/geometry-from-vectors
