..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Orthogonal
==========

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending. The companion
   notebook is runnable, and the Lean theorems cited are machine-checked.

*Orthogonal* is the word this book uses for what a geometry course calls *perpendicular*, and it
goes further than lines: any two vectors can be orthogonal, and so can a vector and a whole
frame. The definition is the right angle of :doc:`product-from-projection`.

..
   covers: pearson-geo/parallel/perpendicular-lines/perpendicular

The definition
--------------

Two vectors :math:`\vec{\mathbf{u}}` and :math:`\vec{\mathbf{v}}` are **orthogonal** when the angle
between them is a right angle, :math:`\cos(\theta) = 0`. By :eq:`eq-angle-measure` that is the same as
their dot product being zero:

.. math::
   :label: eq-orthogonal

   \vec{\mathbf{u}} \perp \vec{\mathbf{v}}
   \quad\Longleftrightarrow\quad
   \vec{\mathbf{u}} \cdot \vec{\mathbf{v}} = 0.

The test needs no angle and no square root, and it also covers the zero vector, which is orthogonal to
every vector. The quarter turn of :doc:`plotting-a-table` is the first example: the vector
:math:`v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2` and its quarter turn
:math:`-v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2` have dot product
:math:`v_1 * (-v_2) + v_2 * v_1 = 0`.

The two parts of a vector
-------------------------

Projection and rejection were built to split a vector along a direction and across it. The pieces
:doc:`projection` drew meet at a right angle, and now that has a name: the rejection of
:math:`\vec{\mathbf{a}}` from :math:`\vec{\mathbf{b}}` is orthogonal to :math:`\vec{\mathbf{b}}`,

.. math::
   :label: eq-rejection-orthogonal

   \operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) \cdot \vec{\mathbf{b}} = 0,

and so is the projection to the rejection, because the projection is a number times
:math:`\vec{\mathbf{b}}`. Machine-checked as ``reject_perp_dot`` (and, as a statement about the
cosine, ``reject_perp``) in ``proofs/GacalcProofs/Projection2D.lean`` and
``proofs/GacalcProofs/StudentTrigForms.lean``, with the roles of the two vectors swapped.

.. figure:: _static/epix/proj2.*
   :align: center
   :alt: the projection of a along b and the rejection perpendicular to b, meeting at a right angle

Two orthogonal parts that add up to :math:`\vec{\mathbf{a}}` are the legs of a right triangle with
:math:`\vec{\mathbf{a}}` as its hypotenuse, so their squared lengths add up to the squared length of
:math:`\vec{\mathbf{a}}`, which is Pythagoras:

.. math::
   :label: eq-pythagoras

   |\vec{\mathbf{a}}|^2
   = |\operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})|^2
   + |\operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})|^2.

Orthogonal frames
-----------------

Two nonzero vectors :math:`\vec{\mathbf{w}}_1` and :math:`\vec{\mathbf{w}}_2` that are orthogonal
(:eq:`eq-orthogonal`) cannot point the same way or opposite ways, so they make a **frame** of the plane:
every vector is a sum of a multiple of each. What makes an *orthogonal* frame pleasant is that the
multiples are projections, with nothing left over to correct:

.. math::
   :label: eq-orthogonal-coordinates

   \vec{\mathbf{c}}
   = \operatorname{proj}_{\vec{\mathbf{w}}_1}(\vec{\mathbf{c}})
   + \operatorname{proj}_{\vec{\mathbf{w}}_2}(\vec{\mathbf{c}}).

Each projection is found by itself, from :math:`\vec{\mathbf{c}}` and one frame vector, the way
:doc:`projection` found it, so a frame that is orthogonal turns a vector into coordinates one
coordinate at a time.

Any two vectors that are not parallel can be made into such a frame: keep the first, and replace the
second by its rejection from the first.

.. math::

   \vec{\mathbf{w}}_1 = \vec{\mathbf{a}},
   \qquad
   \vec{\mathbf{w}}_2 = \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}).

By :eq:`eq-rejection-orthogonal` they are orthogonal, and they span the same plane as
:math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`, because :math:`\vec{\mathbf{b}}` is
:math:`\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})` plus :math:`\vec{\mathbf{w}}_2`. In
gacalc this is ``make_orthogonal_frame``. In space the same step is taken once for each vector, rejecting
every earlier vector: that is :doc:`frames-qr`.

The companion notebook checks the quarter turn, :eq:`eq-rejection-orthogonal`, :eq:`eq-pythagoras` and
:eq:`eq-orthogonal-coordinates`, with every coordinate left as a symbol, and draws the frame.

.. toctree::
   :maxdepth: 1

   notebooks/orthogonal
