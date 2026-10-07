Projection
==========

..
   TODO prose (maintainer's voice): introduce projection and rejection in 2D. The figures
   below are drafted and render via `make docs`; the narrative around them is still to be
   written. The companion page :doc:`proof-projection` derives the same result by rotating to
   standard position.

The projection of :math:`\vec{a}` onto :math:`\vec{b}` is the part of :math:`\vec{a}` that
points along :math:`\vec{b}` — its shadow on the line through :math:`\vec{b}`.

.. figure:: _static/epix/proj1.*
   :align: center
   :alt: a and b, the line through b, and the foot of the perpendicular from a

The projection runs along :math:`\vec{b}`; the **rejection** is what is left over,
perpendicular to :math:`\vec{b}`.

.. figure:: _static/epix/proj2.*
   :align: center
   :alt: the projection of a along b and the rejection perpendicular to b, meeting at a right angle

Together they add back up to :math:`\vec{a}`.

.. figure:: _static/epix/proj3.*
   :align: center
   :alt: projection plus rejection, tip-to-tail, equal to a

.. toctree::
   :maxdepth: 1

   proof-projection
   notebooks/projection
   notebooks/proof-projection
