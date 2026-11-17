..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 3: Rotation from One Vector to Another, from Projection
============================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Step 1 rotates by an angle we are given. Here we are given two vectors instead,
:math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`, of any lengths, and we define **the rotation from**
:math:`\vec{\mathbf{a}}` **to** :math:`\vec{\mathbf{b}}`: a map that turns *every* vector :math:`\vec{\mathbf{v}}` in the
plane by the amount it takes to turn :math:`\vec{\mathbf{a}}`'s direction onto :math:`\vec{\mathbf{b}}`'s. It
is built from projection, and the angle is never named. The picture is one right triangle,
drawn twice.

.. figure:: _static/epix/boot-rotate-from-projection.*
   :align: center
   :alt: on the right, b measured against a, with legs x along a and y across, and the angle theta; on the left, the same triangle on v, with legs cos(theta) times v and sin(theta) times the quarter turn of v, the rotated v-prime, and the same theta between v and v-prime

The first triangle: from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`
-----------------------------------------------------------

Measure :math:`\vec{\mathbf{b}}` against :math:`\vec{\mathbf{a}}` with Step 2. By
:eq:`eq-bootstrap-projection-coordinates`, the signed length of :math:`\vec{\mathbf{b}}`'s projection
onto :math:`\vec{\mathbf{a}}` and the signed length of its rejection are

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{a}}|}, \qquad
   y = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{\mathbf{a}}|}.

They are the legs of a right triangle whose hypotenuse is :math:`\vec{\mathbf{b}}`, at the angle
:math:`\theta` from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`. So the projection gives the cosine and
sine of that angle without naming it:

.. math::
   :label: eq-bootstrap-from-projection-cos-sin

   \cos(\theta) = \frac{x}{|\vec{\mathbf{b}}|} = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad
   \sin(\theta) = \frac{y}{|\vec{\mathbf{b}}|} = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|}.

The second triangle: from :math:`\vec{\mathbf{v}}` to :math:`\vec{\mathbf{v}}'`
-------------------------------------------------------------

Now build the same triangle on any :math:`\vec{\mathbf{v}}`: walk :math:`\cos(\theta)` of the way
along :math:`\vec{\mathbf{v}}`, then :math:`\sin(\theta)` of the way along its quarter turn. That is
Step 1's rotation by :math:`\theta`, and it is the definition:

.. math::
   :label: eq-bootstrap-rotation-from-to

   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}}) = \vec{\mathbf{v}}'
     = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2).

The legs are :math:`|\vec{\mathbf{v}}| * \cos(\theta)` and :math:`|\vec{\mathbf{v}}| * \sin(\theta)`, the first
triangle's legs times :math:`|\vec{\mathbf{v}}| / |\vec{\mathbf{b}}|`: the same angles, so the same triangle at
another size, with :math:`\vec{\mathbf{v}}'` as its hypotenuse and :math:`\theta` between :math:`\vec{\mathbf{v}}`
and :math:`\vec{\mathbf{v}}'`.

**Only directions matter.** :math:`\cos(\theta)` and :math:`\sin(\theta)` divide by
:math:`|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|`, so replacing :math:`\vec{\mathbf{a}}` by :math:`k * \vec{\mathbf{a}}` or
:math:`\vec{\mathbf{b}}` by :math:`k * \vec{\mathbf{b}}`, for any :math:`k > 0`, gives the same map.

The same map, as two rotations
------------------------------

Step 2's rotation :math:`R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}` turns by :math:`-\alpha`, where :math:`\alpha` is
:math:`\vec{\mathbf{a}}`'s angle; :math:`\big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1}` turns by :math:`\beta`,
:math:`\vec{\mathbf{b}}`'s angle. Rotations add their angles (Step 1), so their composition turns by
:math:`\beta - \alpha = \theta`:

.. math::
   :label: eq-bootstrap-rotation-from-to-composition

   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}} = \big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1} \circ R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}.

Turn :math:`\vec{\mathbf{a}}`'s frame onto the x-axis, then turn the x-axis onto :math:`\vec{\mathbf{b}}`'s
frame.

What follows
------------

- **It is a rotation:** it keeps every length and every angle (Step 1), because
  :math:`\cos(\theta)^2 + \sin(\theta)^2 = (x^2 + y^2) / |\vec{\mathbf{b}}|^2 = 1`.
- **It is linear** (Step 1).
- **It carries** :math:`\vec{\mathbf{a}}`'s **direction onto** :math:`\vec{\mathbf{b}}`'s. For
  :math:`\vec{\mathbf{v}} = \hat{\mathbf{a}} = \vec{\mathbf{a}} / |\vec{\mathbf{a}}|`, the first coordinate of
  :eq:`eq-bootstrap-rotation-from-to` is

  .. math::

     \frac{(a_1 * b_1 + a_2 * b_2) * a_1 - (a_1 * b_2 - a_2 * b_1) * a_2}{|\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|}
     = \frac{(a_1^2 + a_2^2) * b_1}{|\vec{\mathbf{a}}|^2 * |\vec{\mathbf{b}}|} = \frac{b_1}{|\vec{\mathbf{b}}|},

  and the second works the same way, so :math:`R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\hat{\mathbf{a}}) = \hat{\mathbf{b}}`.

The companion notebook works these steps for a set of vectors and draws both
triangles; a reader running it can change the vectors and rerun. It checks, for those
vectors and with every coordinate symbolic, that the two triangles have the same cosine
and sine, that the definition equals the composition, keeps lengths, is
linear, ignores the lengths of :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`, carries :math:`\hat{\mathbf{a}}` to
:math:`\hat{\mathbf{b}}`, and equals gacalc's ``projection_rotation``.

Lean, in ``proofs/GacalcProofs/Bootstrap2D.lean``: the definition
:eq:`eq-bootstrap-rotation-from-to` is the ``rotPlane`` of ``rotPlane_fromTo_eq_vec_mul``,
and ``rotPlane_fromTo_eq_rotateFromToProj`` identifies it with ``rotateFromToProj``, whose
theorems give the rest: ``rotateFromToProj_eq_unalign_align`` (the composition),
``rotateFromToProj_preserves_dot`` (lengths and angles), ``rotateFromToProj_smul_smul`` (only
directions matter) and ``rotateFromToProj_normalize`` (:math:`\hat{\mathbf{a}} \mapsto \hat{\mathbf{b}}`). The
coordinate counterparts are in ``proofs/GacalcProofs/RotateFromTo2D.lean``:
``bprime_coords`` (the first triangle), ``rotPlane_comp`` / ``rotPlane_comm`` (plane
rotations add angles, so they commute), ``rotateFromTo_collapse`` and
``rotateFromTo_carries``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-rotation-from-projection
