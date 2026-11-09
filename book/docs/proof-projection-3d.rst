..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Proof: Projection in Space, One Plane at a Time
================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`proof-projection` we projected one vector onto another in the plane by rotating
:math:`\vec{b}` flat onto the x-axis, keeping the x-coordinate, and rotating back. The same idea
works for vectors in space. The only new wrinkle is that **one rotation is no longer enough**: a
single turn can bring :math:`\vec{b}` into a coordinate plane, but not all the way onto the x-axis.
So we do it **one plane at a time**, each a plain 2D rotation that leaves the third coordinate alone.

**First, swing the** :math:`xy` **shadow onto the x-axis.** Look at :math:`\vec{b}`'s shadow on the
:math:`xy`-plane, the point :math:`(b_1, b_2)`, of length :math:`k = \sqrt{b_1^{2} + b_2^{2}}`.
Rotate the :math:`xy`-plane by an angle :math:`\theta_1` with :math:`\cos(\theta_1) = b_1 / k` and
:math:`\sin(\theta_1) = -b_2 / k`, **copying the** :math:`z` **part straight down**, and
:math:`\vec{b}` moves to :math:`(k,\ 0,\ b_3)`.

**Then swing the** :math:`z` **part down.** Now :math:`\vec{b}` is flat in the :math:`xz`-plane.
Rotate *that* plane by an angle :math:`\theta_2` with :math:`\cos(\theta_2) = k / m` and
:math:`\sin(\theta_2) = -b_3 / m`, where :math:`m = |\vec{b}|`, leaving :math:`y` alone, and
:math:`\vec{b}` lands on :math:`(m,\ 0,\ 0) = |\vec{b}| * e_1`. Compose the two rotations and we
are back in standard position, where projection is again "keep the x-coordinate".

Everything else is the same as in the plane. Each plane rotation preserves lengths and angles, so
projection commutes with it, and the rotate / keep-x / rotate-back answer is the true projection.
This 3D construction is machine-checked in ``proofs/GacalcProofs/StandardPosition.lean``
(``proj_rotXY_equivariant`` and ``proj_rotXZ_equivariant``, and the single theorem
``projectSP_eq_proj``), and you can run it with ``gacalc.standardposition.project_sp``; the last
section of the companion notebook of :doc:`proof-projection` does so symbolically.

.. toctree::
   :maxdepth: 1

   notebooks/proof-projection-3d
