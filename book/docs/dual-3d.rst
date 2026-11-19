..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

The Dual in Space
=================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`dual` the dual of a vector was the vector times :math:`I^{-1}`, and an algebraic proof
showed it meets the vector at a right angle. In space the unit is a volume,
:math:`I = \mathbf{e}_{123}`, which also squares to :math:`-1`, and the dual is still
multiplication by :math:`I^{-1} = -\mathbf{e}_{123}`. But now it changes what kind of object it
gets: a vector times :math:`I^{-1}` is a plane, and a plane times :math:`I^{-1}` is a vector. So in
space the right question is about the dual of a **plane**.

Take the plane spanned by :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`. Its dual is the
vector

.. math::
   :label: eq-dual-of-plane

   \vec{\mathbf{d}} = (\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) * I^{-1},

and the claim is that :math:`\vec{\mathbf{d}}` is perpendicular to both :math:`\vec{\mathbf{a}}` and
:math:`\vec{\mathbf{b}}`.

A perpendicular pair in the plane
---------------------------------

Replace :math:`\vec{\mathbf{b}}` by its rejection from :math:`\vec{\mathbf{a}}`,
:math:`\vec{\mathbf{r}} = \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})`. The part of
:math:`\vec{\mathbf{b}}` along :math:`\vec{\mathbf{a}}` adds no area, so
:math:`\vec{\mathbf{a}} \wedge \vec{\mathbf{r}} = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}`. And since
:math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{r}}` are perpendicular, their product has no
plain-number part: :math:`\vec{\mathbf{a}} * \vec{\mathbf{r}} = \vec{\mathbf{a}} \wedge \vec{\mathbf{r}}`,
and :math:`\vec{\mathbf{r}} * \vec{\mathbf{a}} = -\vec{\mathbf{a}} * \vec{\mathbf{r}}`. So

.. math::

   \vec{\mathbf{d}} = \vec{\mathbf{a}} * \vec{\mathbf{r}} * I^{-1}.

The proof
---------

The same three facts as in the plane: the dot product of two vectors is the plain-number part
of their product, grouping does not matter, and a vector times itself is its squared length.
One more fact does the last step each time: a vector times :math:`I^{-1}` is a plane, which has
no plain-number part.

.. math::

   \begin{aligned}
   \vec{\mathbf{a}} \cdot \vec{\mathbf{d}}
     &= \langle (\vec{\mathbf{a}} * \vec{\mathbf{a}}) * (\vec{\mathbf{r}} * I^{-1}) \rangle_0
      = |\vec{\mathbf{a}}|^2 * \langle \vec{\mathbf{r}} * I^{-1} \rangle_0 = 0, \\
   \vec{\mathbf{r}} \cdot \vec{\mathbf{d}}
     &= \langle \vec{\mathbf{r}} * \vec{\mathbf{a}} * \vec{\mathbf{r}} * I^{-1} \rangle_0
      = -\langle \vec{\mathbf{a}} * (\vec{\mathbf{r}} * \vec{\mathbf{r}}) * I^{-1} \rangle_0
      = -|\vec{\mathbf{r}}|^2 * \langle \vec{\mathbf{a}} * I^{-1} \rangle_0 = 0.
   \end{aligned}

Finally :math:`\vec{\mathbf{b}} = \lambda * \vec{\mathbf{a}} + \vec{\mathbf{r}}` for the number
:math:`\lambda` that sizes the projection, and the dot product distributes:
:math:`\vec{\mathbf{b}} \cdot \vec{\mathbf{d}} = \lambda * (\vec{\mathbf{a}} \cdot \vec{\mathbf{d}}) + \vec{\mathbf{r}} \cdot \vec{\mathbf{d}} = 0`.
Both cosines are zero, so :math:`\vec{\mathbf{d}}` meets :math:`\vec{\mathbf{a}}` and
:math:`\vec{\mathbf{b}}` at right angles.

That vector has a familiar name. It is the cross product
:math:`\vec{\mathbf{a}} \times \vec{\mathbf{b}}`, which :doc:`proof-cross` built by rotating to
standard position; here it comes from one multiplication.

The Lean proofs state the two dot products as ``dual_wedge_perp_left_dot`` and
``dual_wedge_perp_right_dot`` in ``proofs/GacalcProofs/Projection3D.lean``. The companion notebook
computes each step with symbolic coordinates.

.. toctree::
   :maxdepth: 1

   notebooks/dual-3d
