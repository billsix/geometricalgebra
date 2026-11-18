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

Step 3 defined the rotation from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`, a map on every vector
:math:`\vec{\mathbf{v}}` in the plane, out of projection. With the product of Step 4 it can be
written two ways: as a product on one side, which works only in the plane, and as a
sandwich, which is the form that carries over to three dimensions.

The one-sided form
------------------

The quarter turn is a product, :math:`\vec{\mathbf{v}} * \mathbf{e}_{12} = \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)`
(Step 4, :eq:`eq-bootstrap-quarter-turn-product`). Now multiply :math:`\vec{\mathbf{v}}` on the right by the product of the two unit vectors,
:eq:`eq-bootstrap-unit-product`:

.. math::
   :label: eq-bootstrap-rotation-one-sided

   \vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})
     = \vec{\mathbf{v}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12})
     = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2),

with :math:`\cos(\theta)` and :math:`\sin(\theta)` those of the angle from :math:`\vec{\mathbf{a}}`
to :math:`\vec{\mathbf{b}}`, :eq:`eq-bootstrap-from-projection-cos-sin`. That is Step 3's second
triangle, the definition :eq:`eq-bootstrap-rotation-from-to`, so

.. math::

   \vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}}) = R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})

for every :math:`\vec{\mathbf{v}}`. **The product of two unit vectors is the rotation from the first
to the second**: multiplying any :math:`\vec{\mathbf{v}}` by it on the right turns :math:`\vec{\mathbf{v}}`
through the angle from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`, whatever the lengths of
:math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`.

.. figure:: _static/epix/boot-rotate-onesided.*
   :align: center
   :alt: a and b with the angle theta between them, and v turned by the same theta to v times (a-hat times b-hat), in purple

The order matters: :math:`(\hat{\mathbf{a}} * \hat{\mathbf{b}}) * \vec{\mathbf{v}}` turns the other way, by
:math:`-\theta`, because :math:`\mathbf{e}_{12} * \vec{\mathbf{v}} = -\vec{\mathbf{v}} * \mathbf{e}_{12}`. And the form is a
plane fact: in three dimensions a vector off the plane of :math:`\vec{\mathbf{a}}` and
:math:`\vec{\mathbf{b}}` does not come out a vector.

The sandwich
------------

Let :math:`\vec{\mathbf{h}} = |\vec{\mathbf{b}}| * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * \vec{\mathbf{b}}`, the sum of the two vectors
scaled to a common length, which bisects the angle from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`.
The versor

.. math::

   R = \vec{\mathbf{b}} * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|

satisfies :math:`R * \vec{\mathbf{a}} = |\vec{\mathbf{a}}| * \vec{\mathbf{h}}` (multiply it out, using
:math:`\vec{\mathbf{a}} * \vec{\mathbf{a}} = |\vec{\mathbf{a}}|^2`), so it turns :math:`\vec{\mathbf{a}}` halfway to
:math:`\vec{\mathbf{b}}`, by :math:`\theta / 2`. Applied from both sides, the two halves make the
whole turn:

.. math::
   :label: eq-bootstrap-rotation-sandwich

   \vec{\mathbf{v}} \mapsto R * \vec{\mathbf{v}} * R^{-1}.

.. figure:: _static/epix/boot-rotate-sandwich.*
   :align: center
   :alt: a and b with the bisector h dashed between them, each half of the angle marked theta over 2

The two forms agree
-------------------

Write :math:`U = \hat{\mathbf{a}} * \hat{\mathbf{b}} = \cos(\theta) + \sin(\theta) * \mathbf{e}_{12}` and
:math:`\tilde{U} = \hat{\mathbf{b}} * \hat{\mathbf{a}} = \cos(\theta) - \sin(\theta) * \mathbf{e}_{12}`, its reverse.
Two facts, each from multiplying out:

#. :math:`U * \tilde{U} = \cos(\theta)^2 + \sin(\theta)^2 = 1`.
#. An element :math:`c + s * \mathbf{e}_{12}` passes through a vector with its sign of
   :math:`\mathbf{e}_{12}` flipped: :math:`R * \vec{\mathbf{v}} = \vec{\mathbf{v}} * \tilde{R}`, because
   :math:`\mathbf{e}_{12} * \vec{\mathbf{v}} = -\vec{\mathbf{v}} * \mathbf{e}_{12}`.

Here :math:`R = |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| * (1 + \tilde{U})` and
:math:`\tilde{R} = |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| * (1 + U)`. By fact 2,
:math:`R * \vec{\mathbf{v}} * R^{-1} = \vec{\mathbf{v}} * \tilde{R} * R^{-1}`, and since
:math:`R^{-1} = \tilde{R} / (R * \tilde{R})`,

.. math::

   \tilde{R} * R^{-1} = \frac{\tilde{R} * \tilde{R}}{R * \tilde{R}}
     = \frac{(1 + U)^2}{(1 + \tilde{U}) * (1 + U)}
     = \frac{1 + 2 * U + U^2}{2 + U + \tilde{U}}.

By fact 1, :math:`U * (2 + U + \tilde{U}) = 2 * U + U^2 + 1`, the numerator. So
:math:`\tilde{R} * R^{-1} = U` and

.. math::

   R * \vec{\mathbf{v}} * R^{-1} = \vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}}).

The sandwich, the one-sided product, and Step 3's rotation built from projection are one
rotation, defined for every vector in the plane. The arc is closed: rotation gave
projection, projection gave the product, and the product gives back both.

The companion notebook works these steps for a set of vectors and draws each one; a
reader running it can change the vectors and rerun. It checks
:eq:`eq-bootstrap-rotation-one-sided` and :eq:`eq-bootstrap-rotation-sandwich` against
Step 3's rotation and gacalc's ``versor_rotation``, for those vectors and with symbolic
coordinates.

Lean: ``rotPlane_fromTo_eq_vec_mul`` (Step 3's rotation, the blend with the cosine and sine
from projection, equals :math:`\vec{\mathbf{v}} * (\hat{\mathbf{a}} * \hat{\mathbf{b}})`) and
``rotateFromToProj_eq_vec_mul`` in ``proofs/GacalcProofs/Bootstrap2D.lean``;
``vec_mul_fullAngleRotor``
(:math:`\vec{\mathbf{v}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12})` is the rotation by :math:`\theta`)
in ``proofs/GacalcProofs/Rotation2D.lean``; ``versor_mul_from_eq_bisector``
(:math:`R * \vec{\mathbf{a}} = |\vec{\mathbf{a}}| * \vec{\mathbf{h}}`) in ``proofs/GacalcProofs/Versor2D.lean``;
``projRotation_eq_vec_mul``, ``versorFromVectors_mul_vec_eq`` (fact 2),
``fhat_that_eq_reverse_mul_inverse`` (:math:`\hat{\mathbf{a}} * \hat{\mathbf{b}} = \tilde{R} * R^{-1}`) and
``projRotation_eq_sandwich`` (the two forms agree) in
``proofs/GacalcProofs/ProjectionRotation2D.lean``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-rotation-from-product
