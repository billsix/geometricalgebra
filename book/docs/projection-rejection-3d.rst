Projection and Rejection in 3D
==============================

..
   TODO prose (maintainer's voice): projection and rejection in three dimensions. The figures
   below are drafted and render via `make docs`; the narrative is still to be written. (The
   rotate-to-standard-position derivation pictures for 3D — one plane at a time — are a
   follow-on, after :doc:`proof-projection` is restructured as 2D-then-3D.)

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

   notebooks/projection-rejection-3d
