..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Proof: Projection by Rotating to Standard Position
==================================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`projection` we met the **projection** of one vector onto another — the part of
:math:`\vec{\mathbf{a}}` that points along :math:`\vec{\mathbf{b}}`. Here is the precalculus-level
derivation of how to *compute* it, using nothing more than the 2D rotation we already
built in :doc:`proof-rotate`. As in that chapter, we reduce to coordinates on purpose.

We stay in two dimensions here: one picture, one rotation. The three-dimensional version
is the same idea done one plane at a time, and it waits for the second half of the book
(:doc:`proof-projection-3d`).

(The change-of-frame idea is adapted from William Emerison Six's *Multivariate Math*,
"Cross Product".)

The goal
--------

We are handed two vectors :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}` in the plane, and we want
the piece of :math:`\vec{\mathbf{a}}` that lies along :math:`\vec{\mathbf{b}}` — its shadow on the line
through :math:`\vec{\mathbf{b}}`.

.. figure:: _static/epix/sp1.*
   :align: center
   :alt: a and b, the line through b, and the shadow of a on it

There is a slick geometric-algebra formula for this, and we will get to it. For now, let's
earn the answer a different way, one that uses **only rotations you already trust**. That
choice pays off in the very next chapter, where we turn everything around and *build* the
geometric product out of projection.

The idea: make it easy by moving the problem
--------------------------------------------

Here is the one trick in this whole chapter. Projecting onto a general vector
:math:`\vec{\mathbf{b}}` is annoying. But projecting onto the **x-axis** is trivial: the shadow
of :math:`\vec{\mathbf{a}}` on the x-axis is just its x-coordinate — throw away :math:`a_2`,
keep :math:`a_1`. Nothing to it.

So we cheat. We **rotate the whole picture** until :math:`\vec{\mathbf{b}}` lies flat along the
x-axis, do the trivial projection there, and then rotate back. And whatever rotation we
do to :math:`\vec{\mathbf{b}}`, we do to :math:`\vec{\mathbf{a}}` as well — we are turning the graph paper,
and both vectors ride along with it.

The angle to undo is just the angle :math:`\theta` that :math:`\vec{\mathbf{b}}` makes with the
x-axis:

.. figure:: _static/epix/sp2.*
   :align: center
   :alt: the angle theta that b makes with the x-axis, the amount to rotate back by

Rotate the whole picture by :math:`-\theta` and :math:`\vec{\mathbf{b}}` lands flat on the x-axis,
carrying :math:`\vec{\mathbf{a}}` along with it:

.. figure:: _static/epix/sp3.*
   :align: center
   :alt: a and b rotated so b lies on the x-axis, with the faint originals shown dashed

Rotating :math:`\vec{\mathbf{b}}` onto the x-axis
-------------------------------------------------

We already built this move, in :doc:`proof-rotate-from-a-to-b` — rotating a vector onto the
x-axis is its **step 1**. Applied to :math:`\vec{\mathbf{b}}`, it is the rotation
:math:`R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}` (read "from :math:`\vec{\mathbf{b}}`, to :math:`\vec{\mathbf{e}}_1`"), whose
cosine and sine we read straight off :math:`\vec{\mathbf{b}}` —

.. math::

   \cos(-\theta) = \frac{b_1}{|\vec{\mathbf{b}}|}, \qquad \sin(-\theta) = -\frac{b_2}{|\vec{\mathbf{b}}|}

— without ever having to find the angle :math:`\theta`. It lays :math:`\vec{\mathbf{b}}` flat on the
x-axis, exactly its own length out:

.. math::

   R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}) = |\vec{\mathbf{b}}| * \vec{\mathbf{e}}_1.

Undoing it just swaps the labels:
:math:`R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}} = \big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1}` rotates back, from
:math:`\vec{\mathbf{e}}_1` to :math:`\vec{\mathbf{b}}`.

Why we are allowed to do this
-----------------------------

We just moved the problem. Why is the answer we get back the *real* projection of
:math:`\vec{\mathbf{a}}` onto :math:`\vec{\mathbf{b}}`, and not some distortion?

Because a rotation does not change any length or any angle — and the projection of one
vector onto another depends on **nothing but** their lengths and the angle between them.
So rotating into standard position, projecting there, and rotating back is the *same map*
as projecting in place. Write :math:`P_{\vec{\mathbf{b}}}` for "project onto :math:`\vec{\mathbf{b}}`" — and,
since projecting onto :math:`R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}) = |\vec{\mathbf{b}}| * \vec{\mathbf{e}}_1`
is just projecting onto the :math:`\vec{\mathbf{e}}_1` axis, that middle step is :math:`P_{\vec{\mathbf{e}}_1}`.
**Compose** the three steps rather than nesting them, and write the last rotation as the
**inverse of the first**, so it is unmistakable that we simply undo the rotation we did:

.. math::

   P_{\vec{\mathbf{b}}} = \big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1} \circ P_{\vec{\mathbf{e}}_1} \circ R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}.

Read right to left, the way :math:`\circ` composes: rotate :math:`\vec{\mathbf{b}}` onto
:math:`\vec{\mathbf{e}}_1`, project onto :math:`\vec{\mathbf{e}}_1` (keep the x-coordinate), then run that very
same rotation **backwards**, :math:`\big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1} = R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}}`.
The outer map is literally the inner one inverted.

(That is the one fact doing the real work; it is proved once and for all in the library —
``proj_rotPlane_equivariant`` in ``proofs/GacalcProofs/StandardPosition2D.lean`` — and the
whole rotate / keep-the-x-coordinate / rotate-back procedure is proved equal to the
geometric-algebra projection there, as the single theorem ``projectSP_eq_proj``. The rejection
gets the same treatment: ``rejectSP_eq_rotate_keep_rest`` shows that rotate / keep the y-coordinate /
rotate back gives the same vector as the original minus its projection.)

Now the algebra
---------------

Stop thinking about geometry — the rest is bookkeeping. Putting the three steps together:

#. **Rotate** both vectors by :math:`R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}`:
   :math:`\vec{\mathbf{a}}' = R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{a}})`,
   :math:`\vec{\mathbf{b}}' = R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}}) = |\vec{\mathbf{b}}| * \vec{\mathbf{e}}_1`.
#. **Project in standard position** — onto the x-axis, which is trivial: keep the
   x-coordinate of :math:`\vec{\mathbf{a}}'`, drop the rest, giving :math:`a'_1 * \vec{\mathbf{e}}_1`.
#. **Rotate back** by :math:`\big(R_{\vec{\mathbf{b}}}^{\vec{\mathbf{e}}_1}\big)^{-1}` — the same rotation
   undone (through :math:`+\theta`, i.e. with the sine negated).

In standard position step 2 is the whole point — the projection is simply the x-coordinate,
and the rejection is the y-coordinate:

.. figure:: _static/epix/sp4.*
   :align: center
   :alt: in standard position, the projection is a-prime's x-coordinate and the rejection its y-coordinate

Undo the rotation and those two pieces land exactly on the projection and rejection of the
original :math:`\vec{\mathbf{a}}` onto :math:`\vec{\mathbf{b}}`:

.. figure:: _static/epix/sp5.*
   :align: center
   :alt: rotated back, the projection along b and the rejection perpendicular to b

That is the entire projection, and it never used anything but the 2D rotation of
:doc:`proof-rotate`. You can run the whole construction — and check, symbolically, that it
lands on the same answer as the geometric-algebra formula from :doc:`projection` — in the
companion calculation notebook.

The payoff
----------

Look at what we did **not** use: no dot product, and no geometric product. We defined
projection using only rotations a precalculus student already owns. That is on purpose.
With projection and its partner, **rejection**, in hand this way, the next chapter,
:doc:`product-from-projection`, turns the whole thing around and *builds* the geometric
product out of them: the part of :math:`\vec{\mathbf{a}}` along :math:`\vec{\mathbf{b}}` gives the dot
product, the part across gives the wedge, and together they are :math:`\vec{\mathbf{b}} * \vec{\mathbf{a}}`.
