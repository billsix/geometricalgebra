..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Defining the Algebra: G2
========================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

The chapters so far used the plane's product one piece at a time. This one writes the whole
algebra down: what its elements are, how to add and multiply them, and what kinds of element
there are. Geometry textbooks define their objects first and use them after; we did it the other
way round, so that you had seen the product do something before meeting its rules.

The algebra and its pieces
--------------------------

The algebra of the plane, :math:`\mathcal{G}_2`, is every sum

.. math::

   s + v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2 + b * \mathbf{e}_{12}

of plain numbers times the four **basis blades** :math:`1`, :math:`\vec{\mathbf{e}}_1`,
:math:`\vec{\mathbf{e}}_2` and :math:`\mathbf{e}_{12}`. The blades are constants: they never change,
the way the digits of a number system never change. Some elements have only some of the four
parts, and those have names.

.. figure:: _static/epix/g2subsets.*
   :align: center
   :alt: the whole of G2 as a box, containing the vectors, and the versors, which contain the
         scalars and the bivectors

- A **scalar** is a plain number: grade 0.
- A **vector** has only :math:`\vec{\mathbf{e}}_1` and :math:`\vec{\mathbf{e}}_2` parts: grade 1.
- A **bivector** is a multiple of :math:`\mathbf{e}_{12}`, a piece of plane: grade 2.
- A **versor** is a scalar plus a bivector, the kind of element that rotates
  (:doc:`geometric-product`). Every scalar and every bivector is a versor whose other part is zero.

The **grade** of a blade is the number of arrows it is made of. An element such as
:math:`1 + \vec{\mathbf{e}}_1` mixes grades 0 and 1 and is none of the named kinds; it is a general
element of :math:`\mathcal{G}_2`. Zero belongs to every kind. (Some books use "versor" for a product
of vectors. In the plane the two meanings agree: every nonzero scalar-plus-bivector is a product of
two vectors.)

Adding and subtracting
----------------------

Add or subtract the numbers in front of the same blade, as you collect like terms in
:math:`2x + 3y + 5x = 7x + 3y`. Unlike blades stay separate: :math:`1 + \vec{\mathbf{e}}_1` does not
simplify, any more than :math:`x + y` does.

Multiplying
-----------

Multiply everything by everything, as with :math:`(x + 2)(x + 3)`, and clean up with three rules:

1. A unit arrow times itself is one: :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 = \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 = 1`.
2. Swapping two different arrows flips the sign:
   :math:`\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = -\mathbf{e}_{12}`.
3. Plain numbers slide to the front and multiply as usual.

The product is associative: how a product of several elements is grouped does not change the
answer, even though the order of factors does. Two consequences we have already used:
a vector times itself is its squared length (the Pythagorean theorem), and
:math:`\mathbf{e}_{12} * \mathbf{e}_{12} = -1`.

The kind of a product follows from the rules. A vector times a vector is a versor (the dot product
plus the wedge); a vector times :math:`\mathbf{e}_{12}` is a vector, turned a quarter turn; a
bivector times a bivector is a scalar; a versor times a vector is a vector, which is how a versor
rotates.

Resolving the blades to plot
----------------------------

In school, :math:`(3, 2)` meant three to the right and two up, and the directions were hidden in
the notation: the first slot means right, the second means up. Here the directions are part of the
object. :math:`3 * \vec{\mathbf{e}}_1 + 2 * \vec{\mathbf{e}}_2` says three steps of the arrow
:math:`\vec{\mathbf{e}}_1`, then two of :math:`\vec{\mathbf{e}}_2`. To plot it we resolve each blade
to the arrow it names, and :math:`\mathbf{e}_{12}` to the unit square those arrows span. The numbers
say how far; the blades say which way.

The companion notebook works through each rule and each kind of element with gacalc.

.. toctree::
   :maxdepth: 1

   notebooks/defining-g2
