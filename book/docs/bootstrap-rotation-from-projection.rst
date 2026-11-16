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
:math:`\vec{a}` and :math:`\vec{b}`, of any lengths, and we define **the rotation from**
:math:`\vec{a}` **to** :math:`\vec{b}`: a map that turns *every* vector :math:`\vec{v}` in the
plane by the amount it takes to turn :math:`\vec{a}`'s direction onto :math:`\vec{b}`'s. It
is built from projection, and the angle is never named. The picture is one right triangle,
drawn twice.

.. figure:: _static/epix/boot-rotate-from-projection.*
   :align: center
   :alt: on the right, b measured against a, with legs x along a and y across, and the angle theta; on the left, the same triangle on v, with legs cos(theta) times v and sin(theta) times the quarter turn of v, the rotated v-prime, and the same theta between v and v-prime

The first triangle: from :math:`\vec{a}` to :math:`\vec{b}`
-----------------------------------------------------------

Measure :math:`\vec{b}` against :math:`\vec{a}` with Step 2. By
:eq:`eq-bootstrap-projection-coordinates`, the signed length of :math:`\vec{b}`'s projection
onto :math:`\vec{a}` and the signed length of its rejection are

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{a}|}, \qquad
   y = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{a}|}.

They are the legs of a right triangle whose hypotenuse is :math:`\vec{b}`, at the angle
:math:`\theta` from :math:`\vec{a}` to :math:`\vec{b}`. So the projection gives the cosine and
sine of that angle without naming it:

.. math::
   :label: eq-bootstrap-from-projection-cos-sin

   \cos(\theta) = \frac{x}{|\vec{b}|} = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{a}| * |\vec{b}|},
   \qquad
   \sin(\theta) = \frac{y}{|\vec{b}|} = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{a}| * |\vec{b}|}.

The second triangle: from :math:`\vec{v}` to :math:`\vec{v}'`
-------------------------------------------------------------

Now build the same triangle on any :math:`\vec{v}`: walk :math:`\cos(\theta)` of the way
along :math:`\vec{v}`, then :math:`\sin(\theta)` of the way along its quarter turn. That is
Step 1's rotation by :math:`\theta`, and it is the definition:

.. math::
   :label: eq-bootstrap-rotation-from-to

   R_{\vec{a}}^{\vec{b}}(\vec{v}) = \vec{v}'
     = \cos(\theta) * \vec{v} + \sin(\theta) * \vec{r}(\vec{v}; \pi/2).

The legs are :math:`|\vec{v}| * \cos(\theta)` and :math:`|\vec{v}| * \sin(\theta)`, the first
triangle's legs times :math:`|\vec{v}| / |\vec{b}|`: the same angles, so the same triangle at
another size, with :math:`\vec{v}'` as its hypotenuse and :math:`\theta` between :math:`\vec{v}`
and :math:`\vec{v}'`.

**Only directions matter.** :math:`\cos(\theta)` and :math:`\sin(\theta)` divide by
:math:`|\vec{a}| * |\vec{b}|`, so replacing :math:`\vec{a}` by :math:`k * \vec{a}` or
:math:`\vec{b}` by :math:`k * \vec{b}`, for any :math:`k > 0`, gives the same map.

The same map, as two rotations
------------------------------

Step 2's rotation :math:`R_{\vec{a}}^{e_1}` turns by :math:`-\alpha`, where :math:`\alpha` is
:math:`\vec{a}`'s angle; :math:`\big(R_{\vec{b}}^{e_1}\big)^{-1}` turns by :math:`\beta`,
:math:`\vec{b}`'s angle. Rotations add their angles (Step 1), so their composition turns by
:math:`\beta - \alpha = \theta`:

.. math::
   :label: eq-bootstrap-rotation-from-to-composition

   R_{\vec{a}}^{\vec{b}} = \big(R_{\vec{b}}^{e_1}\big)^{-1} \circ R_{\vec{a}}^{e_1}.

Turn :math:`\vec{a}`'s frame onto the x-axis, then turn the x-axis onto :math:`\vec{b}`'s
frame.

What follows
------------

- **It is a rotation:** it keeps every length and every angle (Step 1), because
  :math:`\cos(\theta)^2 + \sin(\theta)^2 = (x^2 + y^2) / |\vec{b}|^2 = 1`.
- **It is linear** (Step 1).
- **It carries** :math:`\vec{a}`'s **direction onto** :math:`\vec{b}`'s. For
  :math:`\vec{v} = \hat{a} = \vec{a} / |\vec{a}|`, the first coordinate of
  :eq:`eq-bootstrap-rotation-from-to` is

  .. math::

     \frac{(a_1 * b_1 + a_2 * b_2) * a_1 - (a_1 * b_2 - a_2 * b_1) * a_2}{|\vec{a}|^2 * |\vec{b}|}
     = \frac{(a_1^2 + a_2^2) * b_1}{|\vec{a}|^2 * |\vec{b}|} = \frac{b_1}{|\vec{b}|},

  and the second works the same way, so :math:`R_{\vec{a}}^{\vec{b}}(\hat{a}) = \hat{b}`.

The companion notebook works these steps for a set of vectors and draws both
triangles; a reader running it can change the vectors and rerun. It checks, for those
vectors and with every coordinate symbolic, that the two triangles have the same cosine
and sine, that the definition equals the composition, keeps lengths, is
linear, ignores the lengths of :math:`\vec{a}` and :math:`\vec{b}`, carries :math:`\hat{a}` to
:math:`\hat{b}`, and equals gacalc's ``projection_rotation``.

Lean, in ``proofs/GacalcProofs/Bootstrap2D.lean``: the definition
:eq:`eq-bootstrap-rotation-from-to` is the ``rotPlane`` of ``rotPlane_fromTo_eq_vec_mul``,
and ``rotPlane_fromTo_eq_rotateFromToProj`` identifies it with ``rotateFromToProj``, whose
theorems give the rest: ``rotateFromToProj_eq_unalign_align`` (the composition),
``rotateFromToProj_preserves_dot`` (lengths and angles), ``rotateFromToProj_smul_smul`` (only
directions matter) and ``rotateFromToProj_normalize`` (:math:`\hat{a} \mapsto \hat{b}`). The
coordinate counterparts are in ``proofs/GacalcProofs/RotateFromTo2D.lean``:
``bprime_coords`` (the first triangle), ``rotPlane_comp`` / ``rotPlane_comm`` (plane
rotations add angles, so they commute), ``rotateFromTo_collapse`` and
``rotateFromTo_carries``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-rotation-from-projection
