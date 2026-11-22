..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Projection
==========

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

..
   TODO prose (maintainer's voice): introduce projection and rejection in 2D. The figures
   below are drafted and render via `make docs`; the narrative around them is still to be
   written. The companion page :doc:`proof-projection` derives the same result by rotating to
   standard position.

The projection of :math:`\vec{\mathbf{a}}` onto :math:`\vec{\mathbf{b}}` is the part of :math:`\vec{\mathbf{a}}` that
points along :math:`\vec{\mathbf{b}}` — its shadow on the line through :math:`\vec{\mathbf{b}}`.

.. figure:: _static/epix/proj1.*
   :align: center
   :alt: a and b, the line through b, and the foot of the perpendicular from a

The projection runs along :math:`\vec{\mathbf{b}}`; the **rejection** is what is left over,
perpendicular to :math:`\vec{\mathbf{b}}`.

.. figure:: _static/epix/proj2.*
   :align: center
   :alt: the projection of a along b and the rejection perpendicular to b, meeting at a right angle

Together they add back up to :math:`\vec{\mathbf{a}}`.

.. figure:: _static/epix/proj3.*
   :align: center
   :alt: projection plus rejection, tip-to-tail, equal to a

What the two parts do to the product
------------------------------------

Multiply each part by :math:`\vec{\mathbf{a}}`. The part along :math:`\vec{\mathbf{a}}` is a number
times :math:`\vec{\mathbf{a}}`, so its product with :math:`\vec{\mathbf{a}}` is a plain number. The
part across is perpendicular to :math:`\vec{\mathbf{a}}`, and the product of perpendicular vectors
is a pure piece of plane, a multiple of :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`. Since
:math:`\vec{\mathbf{b}}` is the sum of its parts, the two pieces add up to the whole product:

.. math::

   \vec{\mathbf{a}} * \vec{\mathbf{b}}
     = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
     + \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}).

The next chapter, :doc:`product-from-projection`, names the two pieces. The companion notebook
computes each one with symbolic coordinates; the Lean proofs are ``mul_proj_eq_dot`` and
``mul_reject_eq_wedge`` in ``proofs/GacalcProofs/Bootstrap2D.lean``.

.. toctree::
   :maxdepth: 1

   proof-projection
   notebooks/projection
   notebooks/proof-projection
