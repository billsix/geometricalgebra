..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Proof: The Reciprocal Frame
===========================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In the standard basis a coordinate is one dot product: the :math:`x`-coordinate of
:math:`\vec{\mathbf{y}}` is :math:`\vec{\mathbf{y}} \cdot \vec{\mathbf{e}}_1`. That works only because :math:`\vec{\mathbf{e}}_1` and
:math:`\vec{\mathbf{e}}_2` are perpendicular and of unit length. In an **oblique** frame it fails. Take
:math:`\vec{\mathbf{a}}_1 = 2 * \vec{\mathbf{e}}_1`, :math:`\vec{\mathbf{a}}_2 = 1 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2` and
:math:`\vec{\mathbf{y}} = x_1 * \vec{\mathbf{a}}_1 + x_2 * \vec{\mathbf{a}}_2`. Dotting with :math:`\vec{\mathbf{a}}_1` mixes the
two coordinates:

.. math::

   \vec{\mathbf{y}} \cdot \vec{\mathbf{a}}_1 = x_1 * (\vec{\mathbf{a}}_1 \cdot \vec{\mathbf{a}}_1) + x_2 * (\vec{\mathbf{a}}_2 \cdot \vec{\mathbf{a}}_1).

This chapter builds, for any frame, a second set of vectors :math:`\vec{a}^1, \dots,
\vec{a}^n`, the **reciprocal frame**, that makes every coordinate one dot product again:
:math:`x_k = \vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}}`. The upper index names the reciprocal vector; it is not
an exponent. This is Hestenes and Sobczyk's construction (*Clifford Algebra to Geometric
Calculus*, p. 28, equations 3.4 to 3.7).

Every theorem below is machine-checked in Lean, in
``proofs/GacalcProofs/ReciprocalFrame2D.lean`` (the plane) and
``proofs/GacalcProofs/ReciprocalFrame3D.lean`` (space), and checked symbolically in the
companion notebook. The only hypothesis is that the vectors form a frame: their wedge
:math:`\vec{\mathbf{a}}_1 \wedge \dots \wedge \vec{\mathbf{a}}_n` is not zero.

Theorem 1: the definition (eq 3.7)
----------------------------------

Let :math:`A_n = \vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2 \wedge \dots \wedge \vec{\mathbf{a}}_n`, the frame's volume
(an area in the plane). For each :math:`k`,

.. math::

   \vec{\mathbf{a}}^k = (-1)^{k-1} * (\vec{\mathbf{a}}_1 \wedge \dots \wedge \check{\vec{\mathbf{a}}}_k \wedge \dots \wedge
   \vec{\mathbf{a}}_n) * A_n^{-1},

where the check mark means "leave :math:`\vec{\mathbf{a}}_k` out". The wedge of the other vectors is
the **face** of the parallelogram (or parallelepiped) opposite :math:`\vec{\mathbf{a}}_k`. In the
plane the face of :math:`\vec{\mathbf{a}}_1` is :math:`\vec{\mathbf{a}}_2` and the face of :math:`\vec{\mathbf{a}}_2`
is :math:`\vec{\mathbf{a}}_1`, so

.. math::

   \vec{\mathbf{a}}^1 = \vec{\mathbf{a}}_2 * (\vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2)^{-1}, \qquad
   \vec{\mathbf{a}}^2 = -1 * \vec{\mathbf{a}}_1 * (\vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2)^{-1}.

These are the Lean definitions ``recip1`` and ``recip2`` in the plane, and ``recip1``,
``recip2``, ``recip3`` (with the volume ``vol3``) in space. gacalc builds the same vectors with
``gacalc.frame.reciprocal_frame``.

Theorem 2: each reciprocal vector is a vector
---------------------------------------------

A face times the inverse volume is a product of blades, which could in general have several
grades. Here it has only grade 1. The face lies inside the space the volume spans, so the
product is the face's dual inside that space: a vector perpendicular to the face. Lean:
``isVector_recip1`` and ``isVector_recip2`` (plane), ``isVector_recip`` (space).

Theorem 3: the Kronecker delta (eq 3.5)
---------------------------------------

.. math::

   \vec{\mathbf{a}}^k \cdot \vec{\mathbf{a}}_j =
   \begin{cases} 1 & j = k, \\ 0 & j \neq k. \end{cases}

**Proof.** For :math:`j \neq k`, :math:`\vec{\mathbf{a}}_j` lies in the face of :math:`\vec{\mathbf{a}}_k`,
and :math:`\vec{\mathbf{a}}^k` is perpendicular to that face (theorem 2), so the dot product is 0. For
:math:`j = k`, the dot product of :math:`\vec{\mathbf{a}}_k` with the face's dual is the volume
divided by itself: a parallelotope's volume is its face times the height of the remaining
vector above it. The sign :math:`(-1)^{k-1}` is the one that makes this :math:`+1` rather
than :math:`-1`. Lean proves all four cases in the plane and all nine in space, each as
``dot_recip_kronecker``.

Theorem 4: reconstruction (eq 3.4)
----------------------------------

Every vector :math:`\vec{\mathbf{y}}` in the frame's space is the sum of its reciprocal-frame
coordinates times the frame:

.. math::

   \vec{\mathbf{y}} = \sum_k (\vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}}) * \vec{\mathbf{a}}_k.

**Proof.** Write :math:`\vec{\mathbf{y}} = \sum_j x_j * \vec{\mathbf{a}}_j`. The dot product is linear, so
:math:`\vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}} = \sum_j x_j * (\vec{\mathbf{a}}^k \cdot \vec{\mathbf{a}}_j)`, and by theorem 3
every term but :math:`j = k` is zero. So :math:`\vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}} = x_k`, and putting
those coordinates back in rebuilds :math:`\vec{\mathbf{y}}`. Lean: ``reconstruct`` (plane and space),
and in space also ``reconstruct_dual``, the same sum with the two frames' roles swapped.

Theorem 5: similar right triangles
----------------------------------

*Why* does one dot product read off an oblique coordinate? Fix the coordinate :math:`x_k`, and
let :math:`\vec{\mathbf{m}}` be any vector perpendicular to the face of :math:`\vec{\mathbf{a}}_k` (to
:math:`\vec{\mathbf{a}}_2` when :math:`k = 1` in the plane). Then

.. math::

   x_k = \frac{\vec{\mathbf{m}} \cdot \vec{\mathbf{y}}}{\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_k}.

**Proof.** Measure heights above the face, along :math:`\vec{\mathbf{m}}`. Every term
:math:`x_j * \vec{\mathbf{a}}_j` with :math:`j \neq k` lies in the face, so it adds no height, and the
height of :math:`\vec{\mathbf{y}}` is the height of :math:`x_k * \vec{\mathbf{a}}_k` alone:
:math:`\vec{\mathbf{m}} \cdot \vec{\mathbf{y}} = x_k * (\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_k)`. Picture two right triangles,
each with its right angle on the face: one with hypotenuse :math:`\vec{\mathbf{a}}_k`, the other with
hypotenuse :math:`x_k * \vec{\mathbf{a}}_k`. Both hypotenuses lie on one line, so the triangles are
similar with ratio :math:`x_k`, and the coordinate is **the height of** :math:`\vec{\mathbf{y}}`
**above the face, divided by the height of** :math:`\vec{\mathbf{a}}_k`.

Fold that division into the vector and the reciprocal vector appears, whatever the length of
:math:`\vec{\mathbf{m}}`:

.. math::

   \vec{\mathbf{a}}^k = \frac{\vec{\mathbf{m}}}{\vec{\mathbf{m}} \cdot \vec{\mathbf{a}}_k}.

Its length is one over the height of :math:`\vec{\mathbf{a}}_k` above the face, so a long, thin
parallelogram (frame vectors nearly parallel) has long reciprocal vectors. Lean:
``coord1_of_perp`` and ``coord2_of_perp`` with ``recip1_eq_normal_div`` and
``recip2_eq_normal_div`` (plane); ``coord1_of_perp`` to ``coord3_of_perp`` with
``recip1_eq_normal_div`` to ``recip3_eq_normal_div`` (space).

In the example from the start, the face of :math:`\vec{\mathbf{a}}_1` is the line of
:math:`\vec{\mathbf{a}}_2 = 1 * \vec{\mathbf{e}}_1 + 3 * \vec{\mathbf{e}}_2`, and :math:`\vec{\mathbf{m}} = 3 * \vec{\mathbf{e}}_1 - 1 * \vec{\mathbf{e}}_2` is
perpendicular to it. The height of :math:`\vec{\mathbf{a}}_1 = 2 * \vec{\mathbf{e}}_1` is 6, so
:math:`\vec{\mathbf{a}}^1 = (3 * \vec{\mathbf{e}}_1 - 1 * \vec{\mathbf{e}}_2) / 6 = \tfrac{1}{2} * \vec{\mathbf{e}}_1 - \tfrac{1}{6} * \vec{\mathbf{e}}_2`.

Theorem 6: the last reciprocal vector is the last rejection
-----------------------------------------------------------

Orthogonalize the frame by rejection, as :doc:`frames-qr` does: :math:`\vec{\mathbf{w}}_n` is
:math:`\vec{\mathbf{a}}_n` with the span of :math:`\vec{\mathbf{a}}_1, \dots, \vec{\mathbf{a}}_{n-1}` rejected out of
it. Then

.. math::

   \vec{\mathbf{a}}^n = \frac{\vec{\mathbf{w}}_n}{|\vec{\mathbf{w}}_n|^2}.

**Proof.** :math:`\vec{\mathbf{w}}_n` is perpendicular to every earlier frame vector, which is the
face of :math:`\vec{\mathbf{a}}_n`, so it is an :math:`\vec{\mathbf{m}}` for theorem 5. Its height:
:math:`\vec{\mathbf{a}}_n` is :math:`\vec{\mathbf{w}}_n` plus a part inside the face, so
:math:`\vec{\mathbf{w}}_n \cdot \vec{\mathbf{a}}_n = \vec{\mathbf{w}}_n \cdot \vec{\mathbf{w}}_n = |\vec{\mathbf{w}}_n|^2`. Lean:
``dot_reject_self`` and ``recip2_eq_reject_div`` (plane); ``reject_plane_facts``,
``reject_line_facts`` and ``recip3_eq_reject_div`` (space).

Theorem 7: two inverses of the frame's map
------------------------------------------

The frame's map :math:`f` sends :math:`\vec{\mathbf{e}}_i \mapsto \vec{\mathbf{a}}_i`, so
:math:`f(x_1 * \vec{\mathbf{e}}_1 + \dots + x_n * \vec{\mathbf{e}}_n) = x_1 * \vec{\mathbf{a}}_1 + \dots + x_n * \vec{\mathbf{a}}_n`. Two
maps undo it:

* the **reciprocal** inverse reads every coordinate at once,
  :math:`g(\vec{\mathbf{y}}) = \sum_k (\vec{\mathbf{a}}^k \cdot \vec{\mathbf{y}}) * \vec{\mathbf{e}}_k`;
* the **peel** inverse reads the last coordinate with theorem 6,
  :math:`x_n = (\vec{\mathbf{w}}_n \cdot \vec{\mathbf{y}}) / |\vec{\mathbf{w}}_n|^2`, removes :math:`x_n * \vec{\mathbf{a}}_n`,
  and repeats on the smaller frame.

Each is a two-sided inverse: :math:`g \circ f` and :math:`f \circ g` are both the identity.
For the reciprocal inverse this is theorem 4. For the peel, each step's dot product sees only
the vector being solved, because :math:`\vec{\mathbf{w}}_k` is perpendicular to every earlier one.
Lean: ``invReciprocal_frameMap``, ``frameMap_invReciprocal``, ``invPeel_frameMap`` and
``frameMap_invPeel`` (plane and space; in space the peel is proved through ``invPeel_comb``).
gacalc builds both with ``Frame.to_invertible_function(inverse_method=...)``, choosing
``InverseMethod.RECIPROCAL`` or ``InverseMethod.PEEL``.

Theorem 8: the two inverses agree
---------------------------------

On every vector, the reciprocal and peel inverses give the same coordinates.

**Proof.** A frame's coordinates are unique, and both inverses recover them (theorem 7).
Lean: ``invReciprocal_eq_invPeel`` (plane and space; in space it goes through
``invPeel_eq_reciprocal_coords``).

Check it yourself
-----------------

The companion notebook checks all eight theorems: in the plane for a fully general frame,
with every coordinate its own symbol, and in space for an oblique frame and a general vector.

.. toctree::
   :maxdepth: 1

   notebooks/proof-reciprocal-frame
