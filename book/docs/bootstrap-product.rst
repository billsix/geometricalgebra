..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 4: The Geometric Product, from Projection
==============================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Measure :math:`\vec{b}` against :math:`\vec{a}` with Step 2: rotate :math:`\vec{a}` onto the
x-axis and read off where :math:`\vec{b}` lands. By
:eq:`eq-bootstrap-projection-coordinates`, that is

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{a}|}, \qquad
   y = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{a}|},

the signed lengths of :math:`\vec{b}`'s projection onto :math:`\vec{a}` (along) and of its
rejection (across). Both have :math:`|\vec{a}|` underneath. Multiply it back in:

.. math::

   |\vec{a}| * x = a_1 * b_1 + a_2 * b_2, \qquad |\vec{a}| * y = a_1 * b_2 - a_2 * b_1.

The first is :math:`|\vec{a}|` times the length of :math:`\vec{b}`'s shadow on
:math:`\vec{a}`. The second is :math:`|\vec{a}|` times :math:`\vec{b}`'s height above
:math:`\vec{a}`: the signed area of the parallelogram the two vectors span.

.. figure:: _static/epix/boot-product.*
   :align: center
   :alt: a and b spanning a parallelogram; x along a in green, y across a in blue

The definition
--------------

Keep both numbers in one object. The along-part goes in as a plain number; the
across-part is an area in the plane, so it carries the unit of area :math:`e_{12}`:

.. math::
   :label: eq-bootstrap-product

   \vec{a} * \vec{b} = |\vec{a}| * (x + y * e_{12})
     = (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * e_{12}.

The plain-number part is the **dot product** :math:`\vec{a} \cdot \vec{b}` and the
:math:`e_{12}` part is the **wedge** :math:`\vec{a} \wedge \vec{b}`, so

.. math::

   \vec{a} * \vec{b} = \vec{a} \cdot \vec{b} + \vec{a} \wedge \vec{b}.

It is the product of the multiplication rules
----------------------------------------------

Multiply :math:`(a_1 * e_1 + a_2 * e_2) * (b_1 * e_1 + b_2 * e_2)` out term by term with
:math:`e_1 * e_1 = e_2 * e_2 = 1`, :math:`e_1 * e_2 = e_{12}` and
:math:`e_2 * e_1 = -e_{12}`:

.. math::

   \begin{aligned}
   (a_1 * e_1 + a_2 * e_2) * (b_1 * e_1 + b_2 * e_2)
     &= a_1 * b_1 * e_1 * e_1 + a_1 * b_2 * e_1 * e_2 + a_2 * b_1 * e_2 * e_1 + a_2 * b_2 * e_2 * e_2 \\
     &= (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * e_{12},
   \end{aligned}

which is :eq:`eq-bootstrap-product`. The product defined from projection and the product
of the multiplication rules are the same product. Two consequences the next steps use:

- **A vector times itself is its length squared:**
  :math:`\vec{b} * \vec{b} = b_1^2 + b_2^2 = |\vec{b}|^2`, a plain number (the area part
  is :math:`b_1 * b_2 - b_2 * b_1 = 0`).
- **The product of two unit vectors is the cosine and sine of the angle between them.**
  Dividing :eq:`eq-bootstrap-product` by :math:`|\vec{a}| * |\vec{b}|` and reading off
  :eq:`eq-bootstrap-from-projection-cos-sin`,

  .. math::
     :label: eq-bootstrap-unit-product

     \hat{a} * \hat{b} = \cos(\theta) + \sin(\theta) * e_{12},
     \qquad \hat{a} = \frac{\vec{a}}{|\vec{a}|}, \quad \hat{b} = \frac{\vec{b}}{|\vec{b}|},

  with :math:`\theta` the angle from :math:`\vec{a}` to :math:`\vec{b}`.

The companion notebook checks :eq:`eq-bootstrap-product` against gacalc's product, the
split into dot and wedge, and :eq:`eq-bootstrap-unit-product`, all with symbolic
coordinates.

Lean: ``mul_eq_magnitude_smul_alignSP`` (:eq:`eq-bootstrap-product`, stated as
:math:`\vec{b} * \vec{a} = |\vec{b}| * (x + y * e_{12})` with :math:`\vec{a}` measured in
:math:`\vec{b}`'s standard position; swap the names for the form above) in
``proofs/GacalcProofs/StandardPosition2D.lean``; ``mul_eq_dot_add_wedge`` in
``proofs/GacalcProofs/G2.lean``; ``uvec_mul_uvec`` (two unit vectors at angles
:math:`\alpha`, :math:`\beta` multiply to :math:`\cos(\beta - \alpha) + \sin(\beta - \alpha) * e_{12}`)
in ``proofs/GacalcProofs/Rotation2D.lean``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-product
