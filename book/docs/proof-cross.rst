..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Proof: The Cross Product by Rotating to Standard Position
=========================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`proof-projection-3d` we reduced one vector to the :math:`e_1` axis to project in
space. The **cross product** :math:`\vec{a} \times \vec{b}` yields to the same
move, done to *both* vectors at once — and this is the last step of the reduce-to-standard-position
story, the one the rest of the book promised but had not yet assembled.

(The change-of-frame idea is adapted from William Emerison Six's *Multivariate Math*,
"Cross Product", which this chapter mirrors.)

The goal
--------

Given two vectors :math:`\vec{a}` and :math:`\vec{b}` in space, we want their cross product
:math:`\vec{a} \times \vec{b}` — the vector perpendicular to both, with length
:math:`|\vec{a}| * |\vec{b}| * \sin(\theta)`. As with projection, a general cross
product is annoying, but a cross product **in standard position** is trivial: if
:math:`\vec{a} = (m, 0, 0)` lies on the x-axis and :math:`\vec{b} = (b'_1, b'_2, 0)` lies in the
:math:`e_{12}` plane, then

.. math::

   \vec{a} \times \vec{b} = (0,\ 0,\ m * b'_2),

a pure :math:`e_3` vector — the x-axis length times :math:`\vec{b}`'s height in the plane.

The idea: move *both* vectors into the plane
---------------------------------------------

So we cheat exactly as before. We **rotate the whole picture** until :math:`\vec{a}` lies on the
x-axis and :math:`\vec{b}` lies flat in the :math:`e_{12}` plane, take the trivial
cross product there, and rotate back. Whatever we do to one vector we do to both — we are turning
the graph paper, and they ride along.

One rotation no longer suffices in space, so we go **one plane at a time**, each a plain 2D rotation
that leaves the third coordinate alone:

#. **Swing** :math:`\vec{a}`\ **'s** :math:`xy` **shadow onto the x-axis**, then **swing its**
   :math:`z` **part down** — the two rotations of :doc:`proof-projection-3d`, read off
   :math:`\vec{a}`'s coordinates, which land :math:`\vec{a}` on :math:`|\vec{a}| * e_1`.
   Both vectors are rotated.
#. **Swing** :math:`\vec{b}` **into the plane** with a third rotation, this time about the fixed
   :math:`e_1` axis (in the :math:`e_{23}` plane), read off :math:`\vec{b}`'s
   image — zeroing its :math:`e_3` component. Now :math:`\vec{b}` lies in the plane and
   :math:`\vec{a}` is untouched (a rotation about :math:`e_1` fixes a vector already on it).

In that frame the cross product is the pure :math:`e_3` vector above. Rotate it back by the
three rotations undone, and it lands on the true :math:`\vec{a} \times \vec{b}`.

Why we are allowed to do this
-----------------------------

A rotation carries a cross product to the cross product of the rotated vectors:
:math:`R(\vec{a}) \times R(\vec{b}) = R(\vec{a} \times \vec{b})` — the cross product is
*equivariant* under each elementary plane rotation (for :math:`\cos(\theta)^2 + \sin(\theta)^2 = 1`). So
crossing in the rotated frame and rotating back is the **same map** as crossing in place. Writing
:math:`\mathcal{R}` for the whole three-rotation reduction,

.. math::

   \vec{a} \times \vec{b}
     = \mathcal{R}^{-1}\!\big(\, \mathcal{R}(\vec{a}) \times \mathcal{R}(\vec{b}) \,\big),

read right to left: reduce both vectors, cross in standard position, rotate back. This is the cross
analogue of the projection capstone :math:`P_{\vec{b}} = R^{-1}\circ P_{e_1}\circ R`.

This is all machine-checked in ``proofs/GacalcProofs/CrossStandardPosition.lean``. The equivariance
engine is ``cross_reduceToPlane_equivariant`` (the three elementary equivariances
``cross_rotXY_equivariant`` / ``cross_rotXZ_equivariant`` / ``cross_rotYZ_equivariant`` composed);
the round-trip identity above is ``cross_eq_unreduce_cross_reduce``; and the standard-position
capstone — reduced operands placed by ``reduceToPlane_a_on_e1`` / ``reduceToPlane_b_in_plane`` and
the in-frame cross value ``cross_reduced`` — is ``cross_via_reduction`` (with its explicit-angle
form ``cross_via_reduction_of_vectors``).

The payoff
----------

Look again at what we did **not** use: no cross-product formula, no geometric product, no determinant
— only 2D rotations and the trivial standard-position cross. The same reduction that gave us
projection and rejection gives us the cross product, closing the reduce-to-standard-position arc.
You can run the whole construction — and check, symbolically, that it lands on the same answer as
``gacalc.vectorcalc.cross`` — in the companion calculation notebook.

.. toctree::
   :maxdepth: 1

   notebooks/proof-cross
