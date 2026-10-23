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

In :doc:`projection-rejection-3d` we reduced one vector to the :math:`\vec{e}_1` axis to
project in space. The **cross product** :math:`\vec{a} \times \vec{b}` yields to the same
move, done to *both* vectors at once — and this is the last step of the reduce-to-standard-position
story, the one the rest of the book promised but had not yet assembled.

(The change-of-frame idea is adapted from William Emerison Six's *Multivariate Math*,
"Cross Product", which this chapter mirrors.)

The goal
--------

Given two vectors :math:`\vec{a}` and :math:`\vec{b}` in space, we want their cross product
:math:`\vec{a} \times \vec{b}` — the vector perpendicular to both, with length
:math:`\lvert\vec{a}\rvert\,\lvert\vec{b}\rvert\sin(\theta)`. As with projection, a general cross
product is annoying, but a cross product **in standard position** is trivial: if
:math:`\vec{a} = (m, 0, 0)` lies on the x-axis and :math:`\vec{b} = (b_1', b_2', 0)` lies in the
:math:`\vec{e}_1\vec{e}_2` plane, then

.. math::

   \vec{a} \times \vec{b} = (0,\ 0,\ m \, b_2'),

a pure :math:`\vec{e}_3` vector — the x-axis length times :math:`\vec{b}`'s height in the plane.

The idea: move *both* vectors into the plane
---------------------------------------------

So we cheat exactly as before. We **rotate the whole picture** until :math:`\vec{a}` lies on the
x-axis and :math:`\vec{b}` lies flat in the :math:`\vec{e}_1\vec{e}_2` plane, take the trivial
cross product there, and rotate back. Whatever we do to one vector we do to both — we are turning
the graph paper, and they ride along.

One rotation no longer suffices in space, so we go **one plane at a time**, each a plain 2D rotation
that leaves the third coordinate alone:

#. **Swing** :math:`\vec{a}`\ **'s** :math:`xy` **shadow onto the x-axis**, then **swing its**
   :math:`z` **part down** — the two rotations of :doc:`projection-rejection-3d`, read off
   :math:`\vec{a}`'s coordinates, which land :math:`\vec{a}` on :math:`\lvert\vec{a}\rvert\,\vec{e}_1`.
   Both vectors are rotated.
#. **Swing** :math:`\vec{b}` **into the plane** with a third rotation, this time about the fixed
   :math:`\vec{e}_1` axis (in the :math:`\vec{e}_2\vec{e}_3` plane), read off :math:`\vec{b}`'s
   image — zeroing its :math:`\vec{e}_3` component. Now :math:`\vec{b}` lies in the plane and
   :math:`\vec{a}` is untouched (a rotation about :math:`\vec{e}_1` fixes a vector already on it).

In that frame the cross product is the pure :math:`\vec{e}_3` vector above. Rotate it back by the
three rotations undone, and it lands on the true :math:`\vec{a} \times \vec{b}`.

Why we are allowed to do this
-----------------------------

A rotation carries a cross product to the cross product of the rotated vectors:
:math:`R(\vec{a}) \times R(\vec{b}) = R(\vec{a} \times \vec{b})` — the cross product is
*equivariant* under each elementary plane rotation (for :math:`\cos^2 + \sin^2 = 1`). So
crossing in the rotated frame and rotating back is the **same map** as crossing in place. Writing
:math:`\mathcal{R}` for the whole three-rotation reduction,

.. math::

   \vec{a} \times \vec{b}
     = \mathcal{R}^{-1}\!\big(\, \mathcal{R}(\vec{a}) \times \mathcal{R}(\vec{b}) \,\big),

read right to left: reduce both vectors, cross in standard position, rotate back. This is the cross
analogue of the projection capstone :math:`P_{\vec{b}} = R^{-1}\circ P_{\vec{e}_1}\circ R`.

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
   :hidden:

   notebooks/proof-cross
