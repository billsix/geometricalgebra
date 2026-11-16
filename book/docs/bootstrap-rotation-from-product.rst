..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 6: Rotation, through the Product
=====================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Step 3 defined the rotation from :math:`\vec{a}` to :math:`\vec{b}`, a map on every vector
:math:`\vec{v}` in the plane, out of projection. With the product of Step 4 it can be
written two ways: as a product on one side, which works only in the plane, and as a
sandwich, which is the form that carries over to three dimensions.

The one-sided form
------------------

The quarter turn is a product, :math:`\vec{v} * e_{12} = \vec{r}(\vec{v}; \pi/2)`
(Step 4, :eq:`eq-bootstrap-quarter-turn-product`). Now multiply :math:`\vec{v}` on the right by the product of the two unit vectors,
:eq:`eq-bootstrap-unit-product`:

.. math::
   :label: eq-bootstrap-rotation-one-sided

   \vec{v} * (\hat{a} * \hat{b})
     = \vec{v} * (\cos(\theta) + \sin(\theta) * e_{12})
     = \cos(\theta) * \vec{v} + \sin(\theta) * \vec{r}(\vec{v}; \pi/2),

with :math:`\cos(\theta)` and :math:`\sin(\theta)` those of the angle from :math:`\vec{a}`
to :math:`\vec{b}`, :eq:`eq-bootstrap-from-projection-cos-sin`. That is Step 3's second
triangle, the definition :eq:`eq-bootstrap-rotation-from-to`, so

.. math::

   \vec{v} * (\hat{a} * \hat{b}) = R_{\vec{a}}^{\vec{b}}(\vec{v})

for every :math:`\vec{v}`. **The product of two unit vectors is the rotation from the first
to the second**: multiplying any :math:`\vec{v}` by it on the right turns :math:`\vec{v}`
through the angle from :math:`\vec{a}` to :math:`\vec{b}`, whatever the lengths of
:math:`\vec{a}` and :math:`\vec{b}`.

.. figure:: _static/epix/boot-rotate-onesided.*
   :align: center
   :alt: a and b with the angle theta between them, and v turned by the same theta to v times (a-hat times b-hat), in purple

The order matters: :math:`(\hat{a} * \hat{b}) * \vec{v}` turns the other way, by
:math:`-\theta`, because :math:`e_{12} * \vec{v} = -\vec{v} * e_{12}`. And the form is a
plane fact: in three dimensions a vector off the plane of :math:`\vec{a}` and
:math:`\vec{b}` does not come out a vector.

The sandwich
------------

Let :math:`\vec{h} = |\vec{b}| * \vec{a} + |\vec{a}| * \vec{b}`, the sum of the two vectors
scaled to a common length, which bisects the angle from :math:`\vec{a}` to :math:`\vec{b}`.
The versor

.. math::

   R = \vec{b} * \vec{a} + |\vec{a}| * |\vec{b}|

satisfies :math:`R * \vec{a} = |\vec{a}| * \vec{h}` (multiply it out, using
:math:`\vec{a} * \vec{a} = |\vec{a}|^2`), so it turns :math:`\vec{a}` halfway to
:math:`\vec{b}`, by :math:`\theta / 2`. Applied from both sides, the two halves make the
whole turn:

.. math::
   :label: eq-bootstrap-rotation-sandwich

   \vec{v} \mapsto R * \vec{v} * R^{-1}.

.. figure:: _static/epix/boot-rotate-sandwich.*
   :align: center
   :alt: a and b with the bisector h dashed between them, each half of the angle marked theta over 2

The two forms agree
-------------------

Write :math:`U = \hat{a} * \hat{b} = \cos(\theta) + \sin(\theta) * e_{12}` and
:math:`\tilde{U} = \hat{b} * \hat{a} = \cos(\theta) - \sin(\theta) * e_{12}`, its reverse.
Two facts, each from multiplying out:

#. :math:`U * \tilde{U} = \cos(\theta)^2 + \sin(\theta)^2 = 1`.
#. An element :math:`c + s * e_{12}` passes through a vector with its sign of
   :math:`e_{12}` flipped: :math:`R * \vec{v} = \vec{v} * \tilde{R}`, because
   :math:`e_{12} * \vec{v} = -\vec{v} * e_{12}`.

Here :math:`R = |\vec{a}| * |\vec{b}| * (1 + \tilde{U})` and
:math:`\tilde{R} = |\vec{a}| * |\vec{b}| * (1 + U)`. By fact 2,
:math:`R * \vec{v} * R^{-1} = \vec{v} * \tilde{R} * R^{-1}`, and since
:math:`R^{-1} = \tilde{R} / (R * \tilde{R})`,

.. math::

   \tilde{R} * R^{-1} = \frac{\tilde{R} * \tilde{R}}{R * \tilde{R}}
     = \frac{(1 + U)^2}{(1 + \tilde{U}) * (1 + U)}
     = \frac{1 + 2 * U + U^2}{2 + U + \tilde{U}}.

By fact 1, :math:`U * (2 + U + \tilde{U}) = 2 * U + U^2 + 1`, the numerator. So
:math:`\tilde{R} * R^{-1} = U` and

.. math::

   R * \vec{v} * R^{-1} = \vec{v} * (\hat{a} * \hat{b}).

The sandwich, the one-sided product, and Step 3's rotation built from projection are one
rotation, defined for every vector in the plane. The arc is closed: rotation gave
projection, projection gave the product, and the product gives back both.

The companion notebook checks :eq:`eq-bootstrap-rotation-one-sided` and
:eq:`eq-bootstrap-rotation-sandwich` against Step 3's rotation and gacalc's
``versor_rotation``, with symbolic coordinates.

Lean: ``rotPlane_fromTo_eq_vec_mul`` (Step 3's rotation, the blend with the cosine and sine
from projection, equals :math:`\vec{v} * (\hat{a} * \hat{b})`) and
``rotateFromToProj_eq_vec_mul`` in ``proofs/GacalcProofs/Bootstrap2D.lean``;
``vec_mul_fullAngleRotor``
(:math:`\vec{v} * (\cos(\theta) + \sin(\theta) * e_{12})` is the rotation by :math:`\theta`)
in ``proofs/GacalcProofs/Rotation2D.lean``; ``versor_mul_from_eq_bisector``
(:math:`R * \vec{a} = |\vec{a}| * \vec{h}`) in ``proofs/GacalcProofs/Versor2D.lean``;
``projRotation_eq_vec_mul``, ``versorFromVectors_mul_vec_eq`` (fact 2),
``fhat_that_eq_reverse_mul_inverse`` (:math:`\hat{a} * \hat{b} = \tilde{R} * R^{-1}`) and
``projRotation_eq_sandwich`` (the two forms agree) in
``proofs/GacalcProofs/ProjectionRotation2D.lean``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-rotation-from-product
