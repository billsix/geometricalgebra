..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

The Geometric Product from Projection and Rejection
===================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending. The companion
   notebook is runnable, and the Lean theorem cited is machine-checked.

We have now met the geometric product once already. In :doc:`geometric-product`, the 90° turn of a
vector turned out to be a multiplication by :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`, and we followed the multiplication rules
from there. This chapter finds the same product a second way, starting from nothing but the
projection and rejection of :doc:`proof-projection`. The two routes agree, and seeing why they agree
says what the product of two vectors *means*.

Where :math:`\vec{\mathbf{a}}` lands
------------------------------------

In :doc:`proof-projection` we rotated the whole picture until :math:`\vec{\mathbf{b}}` lay flat on the
x-axis, and :math:`\vec{\mathbf{a}}` rode along to a new spot. Call that spot :math:`(x, y)`.

.. figure:: _static/epix/sp4.*
   :align: center
   :alt: in standard position, the projection is a-prime's x-coordinate and the rejection its y-coordinate

The x-coordinate is how far :math:`\vec{\mathbf{a}}` reaches *along* :math:`\vec{\mathbf{b}}`: the projection. The
y-coordinate is how far it reaches *across* :math:`\vec{\mathbf{b}}`: the rejection. Nothing new so far.

Now let's write those two numbers out. The rotation that lays :math:`\vec{\mathbf{b}}` on the x-axis has
:math:`\cos(-\theta) = b_1 / |\vec{\mathbf{b}}|` and :math:`\sin(-\theta) = -b_2 / |\vec{\mathbf{b}}|`, read off
:math:`\vec{\mathbf{b}}` as before. Put them into the rotation formula :eq:`eq-rotate-formula` of
:doc:`proof-rotate`, applied to :math:`\vec{\mathbf{a}}`:

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{b}}|},
   \qquad
   y = \frac{b_1 * a_2 - b_2 * a_1}{|\vec{\mathbf{b}}|}.

Both have :math:`|\vec{\mathbf{b}}|` underneath. So multiply through by :math:`|\vec{\mathbf{b}}|` and look at what
is left on top:

.. math::

   |\vec{\mathbf{b}}| * x = a_1 * b_1 + a_2 * b_2,
   \qquad
   |\vec{\mathbf{b}}| * y = b_1 * a_2 - b_2 * a_1.

The first is the dot product of :math:`\vec{\mathbf{b}}` and :math:`\vec{\mathbf{a}}`: the length of :math:`\vec{\mathbf{b}}`
times the length of :math:`\vec{\mathbf{a}}`'s shadow on it. The second is the signed area of the
parallelogram the two vectors span: the length of :math:`\vec{\mathbf{b}}` times the height of
:math:`\vec{\mathbf{a}}` above it. We met both numerators at the end of :doc:`proof-rotate-from-a-to-b`, as
the tops of the cosine and the sine of the angle between the vectors. (The area's sign is flipped
there, because that chapter turned from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`, and this one measures
:math:`\vec{\mathbf{a}}` from :math:`\vec{\mathbf{b}}`.)

Two numbers, one object
-----------------------

Here is the step. Instead of keeping those two numbers apart, put them into one object. The along
part goes in as a plain number. The across part needs a label that says "this one is measured
across, in the plane", and we already have one: :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`, the unit of area in the plane.
Define

.. math::
   :label: eq-product-from-projection

   \vec{\mathbf{b}} * \vec{\mathbf{a}} = |\vec{\mathbf{b}}| * (x + y * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
     = (a_1 * b_1 + a_2 * b_2) + (b_1 * a_2 - b_2 * a_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2.

Is this the same product as in :doc:`geometric-product`? Multiply
:math:`(b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2) * (a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2)` out with the rules from that chapter
(:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 = \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 = 1`, :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = \mathbf{e}_{12}`, :math:`\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`):

.. math::

   \begin{aligned}
   (b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2) * (a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2)
     &= b_1 * a_1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 + b_1 * a_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 + b_2 * a_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 + b_2 * a_2 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 \\
     &= (a_1 * b_1 + a_2 * b_2) + (b_1 * a_2 - b_2 * a_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2.
   \end{aligned}

It is. The rules we got from turning by 90° and the numbers we got from projecting and rejecting
give the same object. The Lean proofs state :eq:`eq-product-from-projection` as
``mul_eq_magnitude_smul_alignSP`` in ``proofs/GacalcProofs/StandardPosition2D.lean``, with
``alignSP`` the rotation onto the x-axis.

What the product of two vectors is
----------------------------------

So the product of two vectors carries two facts about them at once:

- its plain-number part is the **dot product** :math:`\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}`, which is
  :math:`|\vec{\mathbf{b}}|` times how far :math:`\vec{\mathbf{a}}` reaches along :math:`\vec{\mathbf{b}}`;
- its :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` part is the **wedge** :math:`\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}`, which is
  :math:`|\vec{\mathbf{b}}|` times how far :math:`\vec{\mathbf{a}}` reaches across :math:`\vec{\mathbf{b}}`.

That is

.. math::

   \vec{\mathbf{b}} * \vec{\mathbf{a}} = \vec{\mathbf{b}} \cdot \vec{\mathbf{a}} + \vec{\mathbf{b}} \wedge \vec{\mathbf{a}},

the identity the rest of the book leans on. (In Lean it is ``mul_eq_dot_add_wedge`` in
``proofs/GacalcProofs/G2.lean``.) The projection and the rejection were in the product all along;
the product just keeps them together, one as a number and one as an area.

..
   covers: pearson-geo/tools/angles/angle
   covers: pearson-geo/tools/angles/measure
   covers: pearson-geo/tools/angles/kinds
   covers: pearson-geo/parallel/perpendicular-lines/perpendicular
   covers: pearson-geo/within-triangles/bisectors/perpendicular-bisector
   covers: pearson-geo/parallel/lines-and-angles/parallel-lines
   covers: pearson-geo/tools/perimeter-area/area
   covers: pearson-geo/area/parallelograms-triangles
   covers: pearson-geo/quadrilaterals/rhombuses-rectangles-squares

Angle, area and perpendicular
-----------------------------

.. note::

   Draft. This section is agent-drafted; the maintainer's voice pass is pending.

:doc:`geometry-from-vectors` built a geometry textbook's points, segments, lines and polygons
from adding vectors and stretching them. It left the objects that need a measurement of turning or
of area for later. The dot and the wedge are those measurements.

**An angle** is two rays from one point, its vertex (Charles et al., *Geometry: Common Core*,
lesson 1-4). With the vertex :math:`\vec{\mathbf{b}}` and the rays toward :math:`\vec{\mathbf{a}}`
and :math:`\vec{\mathbf{c}}`, the rays are :math:`\vec{\mathbf{b}} + s * \vec{\mathbf{u}}` and
:math:`\vec{\mathbf{b}} + t * \vec{\mathbf{v}}` for :math:`s, t \ge 0`, the rays of
:eq:`eq-line`, with :math:`\vec{\mathbf{u}} = \vec{\mathbf{a}} - \vec{\mathbf{b}}` and
:math:`\vec{\mathbf{v}} = \vec{\mathbf{c}} - \vec{\mathbf{b}}`.

.. figure:: _static/epix/geom-angle.*
   :align: center
   :alt: an angle at the vertex b between the sides u and v, its measure theta, and the triangle they close, shaded, with area one half of the magnitude of u wedge v

**Its measure** :math:`\theta`, turning from :math:`\vec{\mathbf{u}}` to :math:`\vec{\mathbf{v}}`,
is in the two parts of the product. Above, the dot product was the length of one vector times how
far the other reaches along it, and the wedge the length times how far it reaches across. For
:math:`\vec{\mathbf{u}}` and :math:`\vec{\mathbf{v}}` those reaches are
:math:`|\vec{\mathbf{v}}| * \cos(\theta)` and :math:`|\vec{\mathbf{v}}| * \sin(\theta)`, the
cosine and sine of :doc:`proof-rotate-from-a-to-b`:

.. math::
   :label: eq-angle-measure

   \vec{\mathbf{u}} \cdot \vec{\mathbf{v}} = |\vec{\mathbf{u}}| * |\vec{\mathbf{v}}| * \cos(\theta),
   \qquad
   \vec{\mathbf{u}} \wedge \vec{\mathbf{v}} = |\vec{\mathbf{u}}| * |\vec{\mathbf{v}}| * \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2.

The textbook's kinds of angle are read off the cosine: an **acute** angle has
:math:`\cos(\theta) > 0`, a **right** angle :math:`\cos(\theta) = 0`, an **obtuse** angle
:math:`\cos(\theta) < 0`, and a **straight** angle :math:`\cos(\theta) = -1`.

**Perpendicular** lines (lesson 3-4) meet at a right angle: their directions have
:math:`\cos(\theta) = 0`, which by :eq:`eq-angle-measure` is :math:`\vec{\mathbf{u}} \cdot \vec{\mathbf{v}} = 0`.
The quarter turn of :doc:`proof-rotate` gives a perpendicular direction for free, so the
**perpendicular bisector** of the segment from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`
is the line through its midpoint :eq:`eq-midpoint` along the quarter turn of the segment:

.. math::

   \tfrac{1}{2} * (\vec{\mathbf{a}} + \vec{\mathbf{b}}) + t * r(\vec{\mathbf{b}} - \vec{\mathbf{a}}; \pi/2).

**Parallel** lines (lesson 3-1) point the same way or opposite ways: :math:`\sin(\theta) = 0`, which
is :math:`\vec{\mathbf{u}} \wedge \vec{\mathbf{v}} = 0`. That happens exactly when one direction is
a number times the other, the "same way" of :doc:`geometry-from-vectors`'s midsegment (Lean:
``wedge_eq_zero_iff_parallel`` in ``proofs/GacalcProofs/Predicates2D.lean``).

**Area** (lessons 1-8 and 10-1) is base times height for a parallelogram. With base
:math:`|\vec{\mathbf{u}}|` and height :math:`|\vec{\mathbf{v}}| * \sin(\theta)`, that is the size of
the wedge, and a triangle is half of it:

.. math::
   :label: eq-triangle-area

   \text{area of the parallelogram} = |\vec{\mathbf{u}} \wedge \vec{\mathbf{v}}|,
   \qquad
   \text{area of the triangle} = \tfrac{1}{2} * |\vec{\mathbf{u}} \wedge \vec{\mathbf{v}}|.

From the corners themselves, the sides from :math:`\vec{\mathbf{a}}` give the surveyor's formula,
each corner wedged with the next:

.. math::

   (\vec{\mathbf{b}} - \vec{\mathbf{a}}) \wedge (\vec{\mathbf{c}} - \vec{\mathbf{a}})
     = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} + \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}
       + \vec{\mathbf{c}} \wedge \vec{\mathbf{a}}

(Lean: ``wedge_sides_eq_surveyor`` in ``proofs/GacalcProofs/GeometryObjects2D.lean``). With the
dot and the wedge the textbook's special quadrilaterals become tests too: a parallelogram
:eq:`eq-parallelogram` is a **rectangle** when
:math:`(\vec{\mathbf{b}} - \vec{\mathbf{a}}) \cdot (\vec{\mathbf{c}} - \vec{\mathbf{b}}) = 0`, a
**rhombus** when :math:`|\vec{\mathbf{b}} - \vec{\mathbf{a}}| = |\vec{\mathbf{c}} - \vec{\mathbf{b}}|`,
and a **square** when it is both.

The companion notebook checks all of this with every coordinate left as a symbol, against gacalc's
own product.

.. toctree::
   :maxdepth: 1

   rotation-from-vectors
   notebooks/product-from-projection
