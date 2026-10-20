..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

A Rotation from Two Vectors — No Angle
======================================

.. note::

   Draft. The companion notebook is runnable and the Lean proofs cited are machine-checked;
   the prose is agent-drafted, maintainer's voice pass pending.

In :doc:`proof-rotate-from-a-to-b` we built the rotation that carries :math:`\vec{a}`'s direction
onto :math:`\vec{b}`'s — and we got there without ever *computing* an angle, reading every cosine
and sine straight off the coordinates. But we still told the story in terms of an angle
:math:`\theta`: three turns, a middle rotation "by the angle from :math:`\vec{a}` to :math:`\vec{b}`."

Now that we have the **geometric product** (:doc:`geometric-product`), we can do better. The product
of two vectors *is* the rotation from one to the other. The angle never enters — not in the
computation, and not in the story.

The product of two unit vectors is the rotor
--------------------------------------------

Take two **unit** vectors :math:`\hat{a}` and :math:`\hat{b}`, with :math:`\theta` the angle between
them. Multiply them. From :doc:`geometric-product`, a vector times a vector in 𝒢₂ is a scalar plus a
bivector, and the two pieces are exactly the dot and the wedge:

.. math::

   \hat{a} * \hat{b} = \hat{a} \cdot \hat{b} + \hat{a} \wedge \hat{b}
                     = \cos(\theta) + \sin(\theta) * e_{12}.

That is the **full-angle rotor** of :doc:`geometric-product` — :math:`R = \cos(\theta) + \sin(\theta)
* e_{12}` — but we did not have to know :math:`\theta` to write it. We *multiplied the two vectors*,
and the cosine and sine appeared on their own as :math:`\hat{a} \cdot \hat{b}` and :math:`\hat{a}
\wedge \hat{b}`. (The Lean proofs state this as ``uvec_mul_uvec`` in
``proofs/GacalcProofs/Rotation2D.lean`` — the product of the unit vectors at angles :math:`\alpha`
and :math:`\beta` is the full-angle rotor for :math:`\beta - \alpha` — with the scalar and bivector
parts named ``uvec_dot`` and ``uvec_wedge``.)

And this rotor carries :math:`\hat{a}` to :math:`\hat{b}` by a single multiplication. Right-multiply
:math:`\hat{a}` by it, and use associativity together with the one fact that a unit vector squares to
one, :math:`\hat{a} * \hat{a} = \hat{a} \cdot \hat{a} = 1`:

.. math::

   \hat{a} * (\hat{a} * \hat{b}) = (\hat{a} * \hat{a}) * \hat{b} = 1 * \hat{b} = \hat{b}.

No angle was named anywhere. (This is ``fullAngleRotorFromTo_carry`` in the same file:
``uvec α`` times the rotor from :math:`\alpha` to :math:`\beta` is ``uvec β``.)

Vectors of any length
---------------------

The unit case is the whole idea; the only loose end is that :math:`\vec{a}` and :math:`\vec{b}` are
usually not unit length. gacalc's :meth:`~gacalc.base.MultiVectorBase.versor_from_vectors` handles the
general case by building the rotor from the **angle bisector** :math:`\vec{h} = |\vec{b}| * \vec{a} +
|\vec{a}| * \vec{b}`, so the magnitudes cancel and only the directions set the rotation;
:meth:`~gacalc.base.MultiVectorBase.rotor_from_vectors` is that versor normalized to unit length, the
half-angle rotor that drives the sandwich :math:`R * \vec{v} * \tilde{R}`. The transform factories
:func:`~gacalc.transforms.versor_rotation` and :func:`~gacalc.transforms.projection_rotation` package
the same rotation as an :class:`~gacalc.functions.InvertibleFunction` keyed by the two vectors — again,
no angle argument.

The same rotation, from projection and rejection
------------------------------------------------

There is a second route to the identical rotation, and it names no angle either. Split the vector
being rotated into its part **in** the :math:`\vec{a} \wedge \vec{b}` plane and its part perpendicular
to that plane; turn the in-plane part from :math:`\vec{a}`'s direction toward :math:`\vec{b}`'s, and
leave the perpendicular part fixed. In 𝒢₂ nothing is perpendicular to the only plane, so this collapses
to the rotor action :math:`\vec{v} * \hat{a} * \hat{b}` — the very product above.

gacalc builds this as :func:`~gacalc.transforms.projection_rotation`, and the Lean proofs
(``proofs/GacalcProofs/ProjectionRotation2D.lean``) prove it is the same map three ways: it **carries**
:math:`\vec{a}` to :math:`\vec{b}`'s direction (``projRotation_carries_from_to``: the image is
:math:`(|\vec{a}|/|\vec{b}|) * \vec{b}`, same direction, :math:`\vec{a}`'s length), it is an
**isometry** (``projRotation_isometry``), and it **equals the versor sandwich**
(``projRotation_eq_sandwich``). The projection route and the product route are one rotation.

The angle was scaffolding
-------------------------

Hold this page next to :doc:`proof-rotate-from-a-to-b`. There, rotating onto a general vector was
"annoying," so we reduced to standard position, rotated by the angle :math:`\theta`, and rotated back;
the angle was the organizing idea even though we never evaluated it, and the payoff was watching
:math:`\cos(\theta)` and :math:`\sin(\theta)` come out as the dot product and the signed area,

.. math::

   \cos(\theta) = \frac{\vec{a} \cdot \vec{b}}{|\vec{a}| * |\vec{b}|},
   \qquad
   \sin(\theta) = \frac{\vec{a} \wedge \vec{b}}{|\vec{a}| * |\vec{b}|}.

Here those same two quantities are not the *answer* to a calculation about an angle — they *are* the
rotation, handed to us as the single object :math:`\vec{a} * \vec{b}`. The angle was scaffolding we
can now take down: two vectors are enough to say "rotate from here to there," and the geometric product
turns that sentence into one multiplication.

The companion notebook, :doc:`notebooks/rotation-from-vectors`, checks all of this symbolically in
gacalc — the product of two unit vectors is the full-angle rotor, right-multiplication carries
:math:`\hat{a}` to :math:`\hat{b}`, and the versor, projection, and angle-based routes agree.

.. toctree::
   :maxdepth: 1

   notebooks/rotation-from-vectors
