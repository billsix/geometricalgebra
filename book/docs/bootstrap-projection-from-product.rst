..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 5: Projection, through the Product
=======================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Step 2 defined the projection of :math:`\vec{b}` onto :math:`\vec{a}` by rotating,
:eq:`eq-bootstrap-projection-definition`. With the product of Step 4, the same projection has
a second formula that needs no rotation at all.

The inverse of a vector
-----------------------

By Step 4, :math:`\vec{a} * \vec{a} = |\vec{a}|^2`, a plain number. So for
:math:`\vec{a} \neq 0`

.. math::

   \vec{a}^{-1} = \frac{\vec{a}}{|\vec{a}|^2}

satisfies :math:`\vec{a} * \vec{a}^{-1} = \vec{a}^{-1} * \vec{a} = 1`. It points along
:math:`\vec{a}`, at length :math:`1 / |\vec{a}|`.

The projection through the product
-----------------------------------

The dot product :math:`\vec{b} \cdot \vec{a}` is the plain-number part of
:math:`\vec{b} * \vec{a}`. The projection of :math:`\vec{b}` onto :math:`\vec{a}` is

.. math::
   :label: eq-bootstrap-projection-product

   \operatorname{proj}_{\vec{a}}(\vec{b}) = (\vec{b} \cdot \vec{a}) * \vec{a}^{-1}.

.. figure:: _static/epix/boot-project-product.*
   :align: center
   :alt: a, b, and the shorter a-inverse along a in purple; the number b dot a times a-inverse lands on the projection of b, in green

It is Step 2's projection
-------------------------

By :eq:`eq-bootstrap-product` (with the names exchanged; the plain-number part is the same
either way), :math:`\vec{b} \cdot \vec{a} = a_1 * b_1 + a_2 * b_2`, so

.. math::

   (\vec{b} \cdot \vec{a}) * \vec{a}^{-1}
     = (a_1 * b_1 + a_2 * b_2) * \frac{\vec{a}}{a_1^2 + a_2^2},

which is Step 2's formula :eq:`eq-bootstrap-projection`. The rotation to the x-axis and back
has disappeared into the product.

The rejection, the same way
---------------------------

Replace the dot product by the wedge:

.. math::
   :label: eq-bootstrap-rejection-product

   \operatorname{rej}_{\vec{a}}(\vec{b}) = (\vec{b} \wedge \vec{a}) * \vec{a}^{-1}.

With :math:`\vec{b} \wedge \vec{a} = (b_1 * a_2 - b_2 * a_1) * e_{12}` and
:math:`e_{12} * \vec{a} = -\vec{r}(\vec{a}; \pi/2)` (multiply it out),

.. math::

   (\vec{b} \wedge \vec{a}) * \vec{a}^{-1}
     = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{a}|^2} * \vec{r}(\vec{a}; \pi/2),

which is Step 2's formula :eq:`eq-bootstrap-rejection`. Adding
:eq:`eq-bootstrap-projection-product` and :eq:`eq-bootstrap-rejection-product` gives back
:math:`\vec{b}`:
:math:`(\vec{b} \cdot \vec{a} + \vec{b} \wedge \vec{a}) * \vec{a}^{-1} = \vec{b} * \vec{a} * \vec{a}^{-1} = \vec{b}`.

The companion notebook checks both forms against Step 2's construction and against
gacalc's ``projected_onto`` and ``rejected_away_from``, with symbolic coordinates.

Lean: ``proj_eq_dot_mul_inverse`` (:eq:`eq-bootstrap-projection-product`) in
``proofs/GacalcProofs/Bootstrap2D.lean``; ``projectSP_eq_proj`` and ``rejectSP_eq_reject``
(Step 2's construction equals ``proj`` and the Hestenes rejection; stated there as
:math:`\vec{a}` onto :math:`\vec{b}`, so read them with the names exchanged) in
``proofs/GacalcProofs/StandardPosition2D.lean``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-projection-from-product
