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
vector turned out to be a multiplication by :math:`e_{12}`, and we followed the multiplication rules
from there. This chapter finds the same product a second way, starting from nothing but the
projection and rejection of :doc:`proof-projection`. The two routes agree, and seeing why they agree
says what the product of two vectors *means*.

Where :math:`\vec{a}` lands
---------------------------

In :doc:`proof-projection` we rotated the whole picture until :math:`\vec{b}` lay flat on the
x-axis, and :math:`\vec{a}` rode along to a new spot. Call that spot :math:`(x, y)`.

.. figure:: _static/epix/sp4.*
   :align: center
   :alt: in standard position, the projection is a-prime's x-coordinate and the rejection its y-coordinate

The x-coordinate is how far :math:`\vec{a}` reaches *along* :math:`\vec{b}`: the projection. The
y-coordinate is how far it reaches *across* :math:`\vec{b}`: the rejection. Nothing new so far.

Now let's write those two numbers out. The rotation that lays :math:`\vec{b}` on the x-axis has
:math:`\cos(-\theta) = b_1 / |\vec{b}|` and :math:`\sin(-\theta) = -b_2 / |\vec{b}|`, read off
:math:`\vec{b}` as before. Put them into the rotation formula :eq:`eq-rotate-formula` of
:doc:`proof-rotate`, applied to :math:`\vec{a}`:

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{b}|},
   \qquad
   y = \frac{b_1 * a_2 - b_2 * a_1}{|\vec{b}|}.

Both have :math:`|\vec{b}|` underneath. So multiply through by :math:`|\vec{b}|` and look at what
is left on top:

.. math::

   |\vec{b}| * x = a_1 * b_1 + a_2 * b_2,
   \qquad
   |\vec{b}| * y = b_1 * a_2 - b_2 * a_1.

The first is the dot product of :math:`\vec{b}` and :math:`\vec{a}`: the length of :math:`\vec{b}`
times the length of :math:`\vec{a}`'s shadow on it. The second is the signed area of the
parallelogram the two vectors span: the length of :math:`\vec{b}` times the height of
:math:`\vec{a}` above it. We met both numerators at the end of :doc:`proof-rotate-from-a-to-b`, as
the tops of the cosine and the sine of the angle between the vectors. (The area's sign is flipped
there, because that chapter turned from :math:`\vec{a}` to :math:`\vec{b}`, and this one measures
:math:`\vec{a}` from :math:`\vec{b}`.)

Two numbers, one object
-----------------------

Here is the step. Instead of keeping those two numbers apart, put them into one object. The along
part goes in as a plain number. The across part needs a label that says "this one is measured
across, in the plane", and we already have one: :math:`e_{12}`, the unit of area in the plane.
Define

.. math::
   :label: eq-product-from-projection

   \vec{b} * \vec{a} = |\vec{b}| * (x + y * e_{12})
     = (a_1 * b_1 + a_2 * b_2) + (b_1 * a_2 - b_2 * a_1) * e_{12}.

Is this the same product as in :doc:`geometric-product`? Multiply
:math:`(b_1 * e_1 + b_2 * e_2) * (a_1 * e_1 + a_2 * e_2)` out with the rules from that chapter
(:math:`e_1 * e_1 = e_2 * e_2 = 1`, :math:`e_1 * e_2 = e_{12}`, :math:`e_2 * e_1 = -e_{12}`):

.. math::

   \begin{aligned}
   (b_1 * e_1 + b_2 * e_2) * (a_1 * e_1 + a_2 * e_2)
     &= b_1 * a_1 * e_1 * e_1 + b_1 * a_2 * e_1 * e_2 + b_2 * a_1 * e_2 * e_1 + b_2 * a_2 * e_2 * e_2 \\
     &= (a_1 * b_1 + a_2 * b_2) + (b_1 * a_2 - b_2 * a_1) * e_{12}.
   \end{aligned}

It is. The rules we got from turning by 90° and the numbers we got from projecting and rejecting
give the same object. The Lean proofs state :eq:`eq-product-from-projection` as
``mul_eq_magnitude_smul_alignSP`` in ``proofs/GacalcProofs/StandardPosition2D.lean``, with
``alignSP`` the rotation onto the x-axis.

What the product of two vectors is
----------------------------------

So the product of two vectors carries two facts about them at once:

- its plain-number part is the **dot product** :math:`\vec{b} \cdot \vec{a}`, which is
  :math:`|\vec{b}|` times how far :math:`\vec{a}` reaches along :math:`\vec{b}`;
- its :math:`e_{12}` part is the **wedge** :math:`\vec{b} \wedge \vec{a}`, which is
  :math:`|\vec{b}|` times how far :math:`\vec{a}` reaches across :math:`\vec{b}`.

That is

.. math::

   \vec{b} * \vec{a} = \vec{b} \cdot \vec{a} + \vec{b} \wedge \vec{a},

the identity the rest of the book leans on. (In Lean it is ``mul_eq_dot_add_wedge`` in
``proofs/GacalcProofs/G2.lean``.) The projection and the rejection were in the product all along;
the product just keeps them together, one as a number and one as an area.

The companion notebook checks all of this with every coordinate left as a symbol, against gacalc's
own product.

.. toctree::
   :maxdepth: 1

   rotation-from-vectors
   notebooks/product-from-projection
