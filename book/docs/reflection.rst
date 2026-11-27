..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

..
   covers: pearson-geo/transformations/reflections

Reflection
==========

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

A mirror keeps what lies along it and flips what sticks out of it. In the plane the mirror is
a line, the line through a nonzero vector :math:`\vec{\mathbf{b}}`, and the reflection of
:math:`\vec{\mathbf{a}}` keeps the part of :math:`\vec{\mathbf{a}}` along :math:`\vec{\mathbf{b}}` and
flips the part across it.

This chapter gives the same treatment as :doc:`projection`: one easy case, then every other case
reduced to it by a rotation, then a check that the geometric product does the same job in one
multiplication.

The easy case
-------------

Across the x-axis, a vector keeps its x-coordinate and its y-coordinate changes sign:

.. math::
   :label: eq-reflect-e1

   x * \vec{\mathbf{e}}_1 + y * \vec{\mathbf{e}}_2 \;\mapsto\; x * \vec{\mathbf{e}}_1 - y * \vec{\mathbf{e}}_2.

Any other line, by rotating to it
---------------------------------

To reflect across the line through :math:`\vec{\mathbf{b}}`, rotate so that :math:`\vec{\mathbf{b}}` lies
on the x-axis (the rotation :math:`R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}` of
:doc:`proof-rotate-from-a-to-b`), reflect there by :eq:`eq-reflect-e1`, and rotate back. On the
x-axis, :math:`x * \vec{\mathbf{e}}_1` is the projection and :math:`y * \vec{\mathbf{e}}_2` the rejection,
so "keep :math:`x`, flip :math:`y`" is the projection minus the rejection, and rotating back keeps
that true:

.. math::
   :label: eq-reflect-vector

   \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
     = \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) - \operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}).

The same reflection, as a product
---------------------------------

The geometric product gives the reflection with no rotation at all:

.. math::
   :label: eq-reflect-sandwich

   \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
     = \vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1}.

The part of :math:`\vec{\mathbf{a}}` along :math:`\vec{\mathbf{b}}` commutes with :math:`\vec{\mathbf{b}}`, so
:math:`\vec{\mathbf{b}}` and :math:`\vec{\mathbf{b}}^{-1}` (the pair numbered alike) cancel around it and it stays:

.. math::

   \underbrace{\vec{\mathbf{b}}}_{1} * \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) * \underbrace{\vec{\mathbf{b}}^{-1}}_{1}
   = \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) * \underbrace{\vec{\mathbf{b}}}_{1} * \underbrace{\vec{\mathbf{b}}^{-1}}_{1}
   = \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}).

The part across anticommutes with :math:`\vec{\mathbf{b}}` (swapping two perpendicular vectors flips
the sign), so it comes out negated. Along kept, across flipped: :eq:`eq-reflect-vector` again. In the easy case
:math:`\vec{\mathbf{b}} = \vec{\mathbf{e}}_1` the product is
:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{a}} * \vec{\mathbf{e}}_1`, and multiplying it out gives
:eq:`eq-reflect-e1`.

A reflection keeps every length, and reflecting twice across the same line gives back the vector
you started with. The Lean proofs state the product form as ``reflectVec_eq_sandwich``, the length as
``normSq_reflectVec`` and the double reflection as ``reflectVec_twice``, for a line in the plane and in
space, in ``proofs/GacalcProofs/Reflect.lean``. The companion notebook computes all three forms with symbolic
coordinates and shows that they agree. Reflection in space, across a line and in a plane, is
:doc:`reflection-3d`.

.. toctree::
   :maxdepth: 1

   notebooks/reflection
