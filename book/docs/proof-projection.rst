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

In :doc:`projection` we met the **projection** of one vector onto another — the part of
:math:`\vec{a}` that points along :math:`\vec{b}`. Here is the precalculus-level
derivation of how to *compute* it, using nothing more than the 2D rotation we already
built in :doc:`proof-rotate`. As in that chapter, we reduce to coordinates on purpose;
later, once we have the geometric product, we throw the coordinates away.

As promised in the outline, we stay in **two dimensions** here — one picture, one
rotation. (The three-dimensional version is the same idea done one plane at a time; it
gets its own short section at the end, and its own chapter, :doc:`projection-rejection-3d`,
in the second half of the book.)

(The change-of-frame idea is adapted from William Emerison Six's *Multivariate Math*,
"Cross Product".)

The goal
--------

We are handed two vectors :math:`\vec{a}` and :math:`\vec{b}` in the plane, and we want
the piece of :math:`\vec{a}` that lies along :math:`\vec{b}` — its shadow on the line
through :math:`\vec{b}`.

.. figure:: _static/epix/sp1.*
   :align: center
   :alt: a and b, the line through b, and the shadow of a on it

If you already read :doc:`projection`, you know the slick geometric-algebra formula for
this. Forget it for a moment. We are going to earn the answer a different way — one that
uses **only rotations you already trust** — because that will let us, much later, turn
everything around and *build* the geometric product out of projection.

The idea: make it easy by moving the problem
--------------------------------------------

Here is the one trick in this whole chapter. Projecting onto a general vector
:math:`\vec{b}` is annoying. But projecting onto the **x-axis** is trivial: the shadow
of :math:`\vec{a}` on the x-axis is just its x-coordinate — throw away :math:`a_2`,
keep :math:`a_1`. Nothing to it.

So we cheat. We **rotate the whole picture** until :math:`\vec{b}` lies flat along the
x-axis, do the trivial projection there, and then rotate back. And whatever rotation we
do to :math:`\vec{b}`, we do to :math:`\vec{a}` as well — we are turning the graph paper,
and both vectors ride along with it.

The angle to undo is just the angle :math:`\theta` that :math:`\vec{b}` makes with the
x-axis:

.. figure:: _static/epix/sp2.*
   :align: center
   :alt: the angle phi that b makes with the x-axis, the amount to rotate back by

Rotate the whole picture by :math:`-\theta` and :math:`\vec{b}` lands flat on the x-axis,
carrying :math:`\vec{a}` along with it:

.. figure:: _static/epix/sp3.*
   :align: center
   :alt: a and b rotated so b lies on the x-axis, with the faint originals shown dashed

Rotating :math:`\vec{b}` onto the x-axis
----------------------------------------

We already built this move, in :doc:`proof-rotate-from-a-to-b` — rotating a vector onto the
x-axis is its **step 1**. Applied to :math:`\vec{b}`, it is the rotation
:math:`R_{\vec{b}}^{\vec{e}_1}` (read "from :math:`\vec{b}`, to :math:`\vec{e}_1`"), whose
cosine and sine we read straight off :math:`\vec{b}` —

.. math::

   \cos(-\theta) = \frac{b_1}{|\vec{b}|}, \qquad \sin(-\theta) = -\frac{b_2}{|\vec{b}|}

— without ever having to find the angle :math:`\theta`. It lays :math:`\vec{b}` flat on the
x-axis, exactly its own length out:

.. math::

   R_{\vec{b}}^{\vec{e}_1}(\vec{b}) = \lvert\vec{b}\rvert\,\vec{e}_1.

Undoing it just swaps the labels:
:math:`R_{\vec{e}_1}^{\vec{b}} = \big(R_{\vec{b}}^{\vec{e}_1}\big)^{-1}` rotates back, from
:math:`\vec{e}_1` to :math:`\vec{b}`.

Why we are allowed to do this
-----------------------------

We just moved the problem. Why is the answer we get back the *real* projection of
:math:`\vec{a}` onto :math:`\vec{b}`, and not some distortion?

Because a rotation does not change any length or any angle — and the projection of one
vector onto another depends on **nothing but** their lengths and the angle between them.
So rotating into standard position, projecting there, and rotating back is the *same map*
as projecting in place. Write :math:`P_{\vec{b}}` for "project onto :math:`\vec{b}`" — and,
since projecting onto :math:`R_{\vec{b}}^{\vec{e}_1}(\vec{b}) = \lvert\vec{b}\rvert\,\vec{e}_1`
is just projecting onto the :math:`\vec{e}_1` axis, that middle step is :math:`P_{\vec{e}_1}`.
**Compose** the three steps rather than nesting them, and write the last rotation as the
**inverse of the first**, so it is unmistakable that we simply undo the rotation we did:

.. math::

   P_{\vec{b}} = \big(R_{\vec{b}}^{\vec{e}_1}\big)^{-1} \circ P_{\vec{e}_1} \circ R_{\vec{b}}^{\vec{e}_1}.

Read right to left, the way :math:`\circ` composes: rotate :math:`\vec{b}` onto
:math:`\vec{e}_1`, project onto :math:`\vec{e}_1` (keep the x-coordinate), then run that very
same rotation **backwards**, :math:`\big(R_{\vec{b}}^{\vec{e}_1}\big)^{-1} = R_{\vec{e}_1}^{\vec{b}}`.
The outer map is literally the inner one inverted.

(That is the one fact doing the real work; it is proved once and for all in the library —
``proj_rotPlane_equivariant`` in ``proofs/GacalcProofs/StandardPosition2D.lean`` — and the
whole rotate / keep-the-x-coordinate / rotate-back procedure is proved equal to the
geometric-algebra projection there, as the single theorem ``projectSP_eq_proj``.)

Now the algebra
---------------

Stop thinking about geometry — the rest is bookkeeping. Putting the three steps together:

#. **Rotate** both vectors by :math:`R_{\vec{b}}^{\vec{e}_1}`:
   :math:`\vec{a}' = R_{\vec{b}}^{\vec{e}_1}(\vec{a})`,
   :math:`\vec{b}' = R_{\vec{b}}^{\vec{e}_1}(\vec{b}) = \lvert\vec{b}\rvert\,\vec{e}_1`.
#. **Project in standard position** — onto the x-axis, which is trivial: keep the
   x-coordinate of :math:`\vec{a}'`, drop the rest, giving :math:`a'_1\,\vec{e}_1`.
#. **Rotate back** by :math:`\big(R_{\vec{b}}^{\vec{e}_1}\big)^{-1}` — the same rotation
   undone (through :math:`+\theta`, i.e. with the sine negated).

In standard position step 2 is the whole point — the projection is simply the x-coordinate,
and the rejection is the y-coordinate:

.. figure:: _static/epix/sp4.*
   :align: center
   :alt: in standard position, the projection is a-prime's x-coordinate and the rejection its y-coordinate

Undo the rotation and those two pieces land exactly on the projection and rejection of the
original :math:`\vec{a}` onto :math:`\vec{b}`:

.. figure:: _static/epix/sp5.*
   :align: center
   :alt: rotated back, the projection along b and the rejection perpendicular to b

That is the entire projection, and it never used anything but the 2D rotation of
:doc:`proof-rotate`. You can run the whole construction — and check, symbolically, that it
lands on the same answer as the geometric-algebra formula from :doc:`projection` — in the
companion calculation notebook.

Stepping up to three dimensions
-------------------------------

The same idea works for vectors in space; the only new wrinkle is that **one rotation no
longer suffices** — a single turn can bring :math:`\vec{b}` into a coordinate plane, but
not all the way onto the x-axis. So we do it **one plane at a time**, each a plain 2D
rotation that leaves the third coordinate alone.

**First, swing the** :math:`xy` **shadow onto the x-axis.** Look at :math:`\vec{b}`'s
shadow on the :math:`xy`-plane, the point :math:`(b_1, b_2)`, of length
:math:`k = \sqrt{b_1^{\,2} + b_2^{\,2}}`. Rotate the :math:`xy`-plane by an angle :math:`\theta_1` with
:math:`\cos(\theta_1) = b_1 / k`, :math:`\sin(\theta_1) = -b_2 / k`, **copying the** :math:`z`
**part straight down**, and :math:`\vec{b}` moves to :math:`(k,\ 0,\ b_3)`.

**Then swing the** :math:`z` **part down.** Now :math:`\vec{b}` is flat in the
:math:`xz`-plane; rotate *that* plane by an angle :math:`\theta_2` with
:math:`\cos(\theta_2) = k / m`, :math:`\sin(\theta_2) = -b_3 / m` (where :math:`m = \lvert\vec{b}\rvert`), leaving :math:`y`
alone, and :math:`\vec{b}` lands on :math:`(m,\ 0,\ 0) = \lvert\vec{b}\rvert\,\vec{e}_1`.
Compose the two rotations and we are back in standard position, where projection is again
"keep the x-coordinate."

Everything else is identical — each plane rotation preserves lengths and angles, so the
projection is equivariant and the rotate / keep-x / rotate-back answer is the true
projection. This 3D construction is machine-checked in
``proofs/GacalcProofs/StandardPosition.lean`` (``proj_rotXY_equivariant`` /
``proj_rotXZ_equivariant`` and the single theorem ``projectSP_eq_proj``), and you can run
it with ``gacalc.standardposition.project_sp``. We return to projection and rejection in
space, with pictures, in :doc:`projection-rejection-3d`.

The payoff
----------

Look at what we did **not** use: no dot product, no geometric product, nothing from later
in the book. We defined projection using only rotations a precalculus student already
owns. That is not an accident — it is the point. Later, once we have projection and its
partner **rejection** in hand this way, we can turn the whole thing around and *build* the
geometric product out of them: the part of :math:`\vec{a}` along :math:`\vec{b}` gives the
dot product, the part across gives the wedge, and together they are :math:`\vec{a}\vec{b}`.
Bootstrapping the hard thing out of the easy things — that is worth staring at.
