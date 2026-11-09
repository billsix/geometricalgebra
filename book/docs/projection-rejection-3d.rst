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

In three dimensions a vector :math:`\vec{a}` can be projected onto any of the three coordinate
planes :math:`e_{12}` (the xy-plane), :math:`e_{23}` (yz) and :math:`e_{31}` (zx).

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

   The third plane is written :math:`e_{31}` (cyclically, like :math:`e_{12}` and
   :math:`e_{23}`); gacalc spells the same blade :math:`e_{13} = -e_{31}`.

.. toctree::
   :maxdepth: 1

   proof-projection-3d
   proof-cross
   notebooks/projection-rejection-3d
