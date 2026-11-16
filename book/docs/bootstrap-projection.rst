..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 2: Projection, from Rotation
=================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

The projection of :math:`\vec{b}` onto :math:`\vec{a}` is the part of :math:`\vec{b}` along
the line through :math:`\vec{a}`; the rejection is the part across it. Onto the x-axis both
are trivial: keep the x-coordinate for the projection, the y-coordinate for the rejection.
So rotate :math:`\vec{a}` onto the x-axis, carrying :math:`\vec{b}` along, read off the two
coordinates there, and rotate back.

.. figure:: _static/epix/boot-sp2.*
   :align: center
   :alt: the angle theta that a makes with the x-axis

The rotation onto the x-axis
----------------------------

Let :math:`\theta` be the angle of :math:`\vec{a}` from the x-axis. Rotating by
:math:`-\theta` lays :math:`\vec{a}` on the x-axis, and its cosine and sine are read off
:math:`\vec{a}` itself:

.. math::

   \cos(-\theta) = \frac{a_1}{|\vec{a}|}, \qquad \sin(-\theta) = -\frac{a_2}{|\vec{a}|}.

Call that rotation :math:`R_{\vec{a}}^{e_1}` ("from :math:`\vec{a}`, to :math:`e_1`"). By
:eq:`eq-bootstrap-rotation` it sends :math:`\vec{a}` to :math:`|\vec{a}| * e_1`, and its
inverse, the same rotation with the sine negated, sends it back.

.. figure:: _static/epix/boot-sp3.*
   :align: center
   :alt: a and b rotated so a lies on the x-axis

The base case: onto the x-axis
------------------------------

Projecting onto :math:`e_1` keeps the x-coordinate, and rejecting from :math:`e_1` keeps the
y-coordinate:

.. math::
   :label: eq-bootstrap-projection-base

   \operatorname{proj}_{e_1}(\vec{b}) = b_1 * e_1, \qquad
   \operatorname{rej}_{e_1}(\vec{b}) = b_2 * e_2.

These are the base cases: the general projection below is built from them, the way Step 1
builds the rotation by :math:`\theta` from the quarter turn.

The definition
--------------

The projection of :math:`\vec{b}` onto :math:`\vec{a}` and its rejection from
:math:`\vec{a}` are the base cases :eq:`eq-bootstrap-projection-base`, done in
:math:`\vec{a}`'s standard position:

.. math::
   :label: eq-bootstrap-projection-definition

   \operatorname{proj}_{\vec{a}}
     = \big(R_{\vec{a}}^{e_1}\big)^{-1} \circ \operatorname{proj}_{e_1} \circ R_{\vec{a}}^{e_1},
   \qquad
   \operatorname{rej}_{\vec{a}}
     = \big(R_{\vec{a}}^{e_1}\big)^{-1} \circ \operatorname{rej}_{e_1} \circ R_{\vec{a}}^{e_1}.

This is a fair definition because a rotation keeps lengths and angles (Step 1), and the part
of :math:`\vec{b}` along :math:`\vec{a}` depends on nothing else. When :math:`\vec{a}` already
lies along :math:`e_1` the rotation does nothing, and
:eq:`eq-bootstrap-projection-definition` gives back the base cases.

.. figure:: _static/epix/boot-sp4.*
   :align: center
   :alt: in standard position, the projection is the x-coordinate of b-prime and the rejection its y-coordinate

The formula
-----------

Apply :eq:`eq-bootstrap-rotation` to :math:`\vec{b}` with the cosine and sine above. The
rotated :math:`\vec{b}` has coordinates

.. math::
   :label: eq-bootstrap-projection-coordinates

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{a}|}, \qquad
   y = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{a}|}:

:math:`\vec{b}`'s coordinates in :math:`\vec{a}`'s standard position, the signed lengths of
its projection onto :math:`\vec{a}` and of its rejection. Keep :math:`x * e_1` and rotate
back. :math:`\big(R_{\vec{a}}^{e_1}\big)^{-1}` sends :math:`e_1` to the unit vector
:math:`\vec{a} / |\vec{a}|`, so

.. math::
   :label: eq-bootstrap-projection

   \operatorname{proj}_{\vec{a}}(\vec{b}) = x * \frac{\vec{a}}{|\vec{a}|}
     = \frac{a_1 * b_1 + a_2 * b_2}{a_1^2 + a_2^2} * \vec{a}.

The rejection keeps :math:`y * e_2` and rotates it back.
:math:`\big(R_{\vec{a}}^{e_1}\big)^{-1}` sends :math:`e_2` to the unit vector
:math:`\vec{r}(\vec{a}; \pi/2) / |\vec{a}|`, so

.. math::
   :label: eq-bootstrap-rejection

   \operatorname{rej}_{\vec{a}}(\vec{b}) = y * \frac{\vec{r}(\vec{a}; \pi/2)}{|\vec{a}|}
     = \frac{a_1 * b_2 - a_2 * b_1}{a_1^2 + a_2^2} * \vec{r}(\vec{a}; \pi/2).

The two add back to :math:`\vec{b}`,
:math:`\operatorname{proj}_{\vec{a}}(\vec{b}) + \operatorname{rej}_{\vec{a}}(\vec{b}) = \vec{b}`,
because :math:`x * e_1 + y * e_2` was the whole rotated :math:`\vec{b}`.

.. figure:: _static/epix/boot-sp5.*
   :align: center
   :alt: rotated back, the projection of b along a and the rejection across a

No dot product and no geometric product was used: only the rotation of Step 1. The
numbers :math:`a_1 * b_1 + a_2 * b_2` and :math:`a_1 * b_2 - a_2 * b_1` appearing on top
are where Steps 3 and 4 start.

The companion notebook works the construction for a set of vectors and draws each step;
a reader running it can change the vectors and rerun. It checks the base cases
:eq:`eq-bootstrap-projection-base` and the formulas :eq:`eq-bootstrap-projection` and
:eq:`eq-bootstrap-rejection`, for those vectors and with symbolic coordinates, and that
projecting twice changes nothing, that the rejection has no part along :math:`\vec{a}`, and that the two
parts add back to :math:`\vec{b}`.

Lean, in ``proofs/GacalcProofs/StandardPosition2D.lean``, where the statements project
:math:`\vec{a}` onto :math:`\vec{b}` (read them with the names exchanged):
``projectSP_eq_proj`` and ``rejectSP_eq_reject`` (the construction equals the projection
and rejection), ``proj_onto_x_axis`` and ``reject_onto_x_axis`` (the base cases
:eq:`eq-bootstrap-projection-base`: projecting onto the x-axis keeps the x-coordinate,
rejecting from it keeps the y-coordinate),
``proj_rotPlane_equivariant`` (rotating, then projecting, equals projecting, then rotating)
and ``unalignSP_alignSP`` (the rotation back undoes the rotation).

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-projection
