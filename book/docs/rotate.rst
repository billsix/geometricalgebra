..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Rotate
======

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Rotation is the operation this whole book is built on. We will define it the way
*Model View Projection* does: **not by an angle, but from the direction of one vector
to another**. Rotate so that the direction of :math:`\vec{a}` is carried onto the
direction of :math:`\vec{b}`.

.. figure:: _static/epix/rotate-ab-goal.*
   :align: center
   :alt: a and b, and the angle theta from a to b

Why not just say "rotate by 30 degrees"? Because an angle on its own doesn't say much.
Thirty degrees from where, and turning which way? When you turn your head to look at
something, you don't think "turn 30 degrees". You think "turn from where I'm looking now to
where that thing is". Both of those are directions, and directions are what vectors are good
at. So the two vectors *are* the description of the rotation. The angle between them is still
there, and we will draw it, but it is a property of the rotation, not the thing we start from.

The **magnitudes don't matter**; only the directions set the rotation. Rotating from
:math:`\vec{a}` toward :math:`\vec{b}` is the same rotation as rotating from
:math:`2 * \vec{a}` toward :math:`5 * \vec{b}`, because the directions are the same.

That leaves two questions, and the two pages below answer them in order.

#. **What is a rotation, in coordinates?** :doc:`proof-rotate` builds the rotation by an angle
   :math:`\theta` out of the high-school unit circle. Everything else stands on it, so read it
   first.

   .. figure:: _static/epix/rotate-goal.*
      :align: center
      :alt: the goal — rotate a-vector by an angle

#. **How do we get the rotation from two vectors, without ever finding the angle?**
   :doc:`proof-rotate-from-a-to-b` does it with three of those rotations: swing :math:`\vec{a}`
   onto the x-axis, turn up to where :math:`\vec{b}` went, and swing back.

Later, once we have the **geometric product**, rotation gets a coordinate-free definition: the
product of the two vectors *is* the rotation (:doc:`geometric-product`,
:doc:`rotation-from-vectors`). The companion notebook already runs the from-to rotation in gacalc,
as ``versor_rotation(from_vector=a, to_vector=b)``.

.. toctree::
   :maxdepth: 1

   proof-rotate
   proof-rotate-from-a-to-b
   notebooks/rotate
   notebooks/proof-rotate-from-a-to-b
