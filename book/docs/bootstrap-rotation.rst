..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 1: Rotation, from Precalculus
==================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

This part runs the whole two-dimensional bootstrap in six short steps, with the proofs and
little else. Each step uses only what the steps before it built:

#. rotation, from precalculus;
#. projection, defined from rotation;
#. rotation from one vector to another, defined from projection;
#. the geometric product, defined from projection;
#. projection again, through the product;
#. rotation again, through the product.

Nothing is circular: the first step rests only on sine, cosine and the angle-addition
identities. The earlier chapters cover the same ground slowly; this part is the short
version.

The rotation
------------

Rotate a vector :math:`\vec{v} = v_1 * e_1 + v_2 * e_2` about the origin by the angle
:math:`\theta`. Write :math:`\vec{v}` by its length :math:`r` and its own angle
:math:`\beta`: :math:`v_1 = r * \cos(\beta)`, :math:`v_2 = r * \sin(\beta)`. Rotating adds
:math:`\theta` to :math:`\beta` and keeps :math:`r`. The angle-addition identities do the
rest:

.. math::

   \begin{aligned}
   \vec{r}(\vec{v}; \theta)
     &= r * \begin{bmatrix} \cos(\beta + \theta) \\ \sin(\beta + \theta) \end{bmatrix}
      = r * \begin{bmatrix} \cos(\beta) * \cos(\theta) - \sin(\beta) * \sin(\theta) \\
                            \sin(\beta) * \cos(\theta) + \cos(\beta) * \sin(\theta)
            \end{bmatrix} \\
     &= \cos(\theta) * \begin{bmatrix} v_1 \\ v_2 \end{bmatrix}
      + \sin(\theta) * \begin{bmatrix} -v_2 \\ v_1 \end{bmatrix}.
   \end{aligned}

The second vector is :math:`\vec{v}` turned by :math:`\pi/2` (the same formula with
:math:`\cos(\pi/2) = 0`, :math:`\sin(\pi/2) = 1`), so

.. math::
   :label: eq-bootstrap-rotation

   \vec{r}(\vec{v}; \theta) = \cos(\theta) * \vec{v} + \sin(\theta) * \vec{r}(\vec{v}; \pi/2),
   \qquad \vec{r}(\vec{v}; \pi/2) = \begin{bmatrix} -v_2 \\ v_1 \end{bmatrix}.

A rotation is a blend of the vector and its quarter turn. The formula never uses
:math:`\beta`, only :math:`\cos(\theta)` and :math:`\sin(\theta)`, so it holds for every
vector, the zero vector included.

.. figure:: _static/epix/boot-rotate.*
   :align: center
   :alt: v, its quarter turn dashed, cos(theta) times v in blue, sin(theta) times the quarter turn in green, and the rotated vector in purple

What the later steps use
------------------------

- **Only the cosine and sine are needed, never the angle.** Any pair :math:`(c, s)` with
  :math:`c^2 + s^2 = 1` is the cosine and sine of some angle, and
  :math:`c * \vec{v} + s * \vec{r}(\vec{v}; \pi/2)` rotates by it.
- **A rotation keeps length:**
  :math:`(c * v_1 - s * v_2)^2 + (s * v_1 + c * v_2)^2 = (c^2 + s^2) * (v_1^2 + v_2^2)`.
- **Rotations add their angles**, so the rotation by :math:`-\theta` (the sine negated)
  undoes the rotation by :math:`\theta`.
- **A rotation is linear:** it carries sums to sums and scalar multiples to scalar
  multiples.

The companion notebook checks the formula and these four facts with every coordinate and
angle left as a symbol.

Lean: ``rot_vec`` (the formula), ``rot_normSq`` (length), ``rot_add`` (angles add) and
``rot_add_vec`` / ``rot_smul`` (linearity) in ``proofs/GacalcProofs/Rotation2D.lean``; the
cosine-and-sine form as the blend is ``rotPlane_vec_eq_blend`` in
``proofs/GacalcProofs/StandardPosition2D.lean``, with ``rotPlane_preserves_dot`` and
``rotPlane_inv``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-rotation
