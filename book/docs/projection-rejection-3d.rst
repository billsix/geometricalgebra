..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Projection and Rejection in 3D
==============================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

..
   TODO prose (maintainer's voice): projection and rejection in three dimensions. The figures
   below are drafted and render via `make docs`; the narrative is still to be written. The
   one-plane-at-a-time derivation is :doc:`proof-projection-3d`.

In three dimensions a vector :math:`\vec{\mathbf{a}}` can be projected onto any of the three coordinate
planes :math:`\mathbf{e}_{12}` (the xy-plane), :math:`\mathbf{e}_{23}` (yz) and :math:`\mathbf{e}_{31}` (zx).

.. figure:: _static/epix/proj3d-overview.*
   :align: center
   :alt: a vector a and the three coordinate planes

Onto each plane, the projection lies in the plane and the rejection is the perpendicular
remainder.

.. figure:: _static/epix/proj3d-e12.*
   :align: center
   :alt: projection of a onto the e12 (xy) plane and the perpendicular rejection

.. figure:: _static/epix/proj3d-e23.*
   :align: center
   :alt: projection of a onto the e23 (yz) plane and the perpendicular rejection

.. figure:: _static/epix/proj3d-e31.*
   :align: center
   :alt: projection of a onto the e31 (zx) plane and the perpendicular rejection

.. note::

   The third plane is written :math:`\mathbf{e}_{31}` (cyclically, like :math:`\mathbf{e}_{12}` and
   :math:`\mathbf{e}_{23}`); gacalc spells the same blade :math:`\mathbf{e}_{13} = -\mathbf{e}_{31}`.

Onto any plane, and the product split
-------------------------------------

The same split works for any plane through the origin, :math:`B = \vec{\mathbf{p}} \wedge
\vec{\mathbf{q}}`: the projection lies in the plane, the rejection is perpendicular to both
:math:`\vec{\mathbf{p}}` and :math:`\vec{\mathbf{q}}`, and the two add back up to
:math:`\vec{\mathbf{a}}`. Onto a line, the split of the product from :doc:`projection` carries over
to space unchanged: :math:`\vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})`
is the dot product :math:`\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}`, and
:math:`\vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})` is the wedge
:math:`\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}`, now with a part in each of the three coordinate
planes. The companion notebook computes each step with symbolic coordinates; the Lean proofs are
``project_add_reject`` (``proofs/GacalcProofs/Projection3D.lean``) and ``mul_proj_eq_dot`` and
``mul_eq_proj_dot_add_reject_wedge`` (``proofs/GacalcProofs/StandardPosition.lean``).

.. toctree::
   :maxdepth: 1

   proof-projection-3d
   proof-cross
   notebooks/projection-rejection-3d
