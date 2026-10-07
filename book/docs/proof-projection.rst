..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

..
   DRAFT (agent-drafted 2026-09-30, for the maintainer to refine into his own voice).
   Structure and cadence follow proof-rotate.rst. Figure placeholders are marked with
   ".. TODO figure"; no SVGs were invented. The math is machine-checked in
   proofs/GacalcProofs/StandardPosition.lean and runnable via gacalc.standardposition.

Proof: Projection by Rotating to Standard Position
==================================================

In :doc:`projection` we met the **projection** of one vector onto another — the part of
:math:`\vec{a}` that points along :math:`\vec{b}`. Here is the precalculus-level
derivation of how to *compute* it, using nothing more than the 2D rotation we already
built in :doc:`proof-rotate`. As in that chapter, we reduce to coordinates on purpose;
later, once we have the geometric product, we throw the coordinates away.

(The change-of-frame idea is adapted from William Emerison Six's *Multivariate Math*,
"Cross Product".)

The goal
--------

We are handed two vectors :math:`\vec{a}` and :math:`\vec{b}` in 3D, and we want the
piece of :math:`\vec{a}` that lies along :math:`\vec{b}` — its shadow on the line
through :math:`\vec{b}`.

.. figure:: _static/epix/sp1.*
   :align: center
   :alt: a and b, the line through b, and the shadow of a on it

..
   TODO prose (2D vs 3D): the figures in this chapter are drawn for the **2D** case — a single
   rotation carries b onto the x-axis. The prose below is still written for 3D (two plane
   rotations, xy then xz). The maintainer will restructure the page as 2D-first-then-3D; until
   then the 2D figures illustrate the idea and the 3D pictures are a step-3 follow-on.

If you already read :doc:`projection`, you know the slick geometric-algebra formula for
this. Forget it for a moment. We are going to earn the answer a different way — one that
uses **only rotations you already trust** — because that will let us, much later, turn
everything around and *build* the geometric product out of projection.

The idea: make it easy by moving the problem
--------------------------------------------

Here is the one trick in this whole chapter. Projecting onto a general vector
:math:`\vec{b}` is annoying. But projecting onto the **x-axis** is trivial: the shadow
of :math:`\vec{a}` on the x-axis is just its x-coordinate — throw away :math:`\vec{a}_y`
and :math:`\vec{a}_z`, keep :math:`\vec{a}_x`. Nothing to it.

So we cheat. We **rotate the whole picture** until :math:`\vec{b}` lies flat along the
x-axis, do the trivial projection there, and then rotate back. And whatever rotation we
do to :math:`\vec{b}`, we do to :math:`\vec{a}` as well — we are turning the graph paper,
and both vectors ride along with it.

In 2D the angle to undo is just the angle :math:`\varphi` that :math:`\vec{b}` makes with the
x-axis:

.. figure:: _static/epix/sp2.*
   :align: center
   :alt: the angle phi that b makes with the x-axis, the amount to rotate back by

Rotate the whole picture by :math:`-\varphi` and :math:`\vec{b}` lands flat on the x-axis,
carrying :math:`\vec{a}` along with it:

.. figure:: _static/epix/sp3.*
   :align: center
   :alt: a and b rotated so b lies on the x-axis, with the faint originals shown dashed

Rotating :math:`\vec{b}` onto the x-axis, one plane at a time
------------------------------------------------------------------

How do we rotate :math:`\vec{b}` onto the x-axis? We never need a fancy 3D rotation. We
do it with the plain 2D rotation from :doc:`proof-rotate`, applied to one coordinate
plane at a time — leaving the third coordinate completely alone.

**Step 1 — swing the** :math:`xy` **shadow onto the x-axis.** Ignore :math:`\vec{b}`'s
z-coordinate for a second and look at its shadow on the :math:`xy`-plane, the point
:math:`(\vec{b}_x, \vec{b}_y)`. That shadow has some length

.. math::

   k = \sqrt{\vec{b}_x^{\,2} + \vec{b}_y^{\,2}}

— it is just :math:`\lvert\vec{b}\text{'s } xy\text{-part}\rvert`. Rotate the
:math:`xy`-plane by the angle that carries that shadow onto the x-axis. From
:doc:`proof-rotate`, a 2D rotation is built from a cosine and a sine, and the ones that
do the job we can read straight off the shadow: :math:`\cos = \vec{b}_x / k` and
:math:`\sin = -\vec{b}_y / k`. Applied to any vector :math:`\vec{v}` this is

.. math::

   R_{xy}(\vec{v}) =
     \begin{bmatrix}
       \tfrac{\vec{b}_x}{k}\,\vec{v}_x - \big(\tfrac{-\vec{b}_y}{k}\big)\,\vec{v}_y \\[4pt]
       \tfrac{-\vec{b}_y}{k}\,\vec{v}_x + \tfrac{\vec{b}_x}{k}\,\vec{v}_y \\[4pt]
       \vec{v}_z
     \end{bmatrix}

— rotate the :math:`x` and :math:`y` parts, and **copy the** :math:`z` **part straight
down.** Do the arithmetic on :math:`\vec{b}` itself and its :math:`y`-coordinate lands
exactly on zero, its :math:`x`-coordinate becomes :math:`k`:

.. math::

   R_{xy}(\vec{b}) = (k,\ 0,\ \vec{b}_z).

**Step 2 — swing the** :math:`z` **part down.** Now :math:`\vec{b}` sits at
:math:`(k, 0, \vec{b}_z)` — flat in the :math:`xz`-plane. Do the same trick again, this
time in the :math:`xz`-plane, to fold :math:`\vec{b}_z` down to zero. Its full length is

.. math::

   m = \lvert\vec{b}\rvert = \sqrt{k^2 + \vec{b}_z^{\,2}}
     = \sqrt{\vec{b}_x^{\,2} + \vec{b}_y^{\,2} + \vec{b}_z^{\,2}},

and the rotation that finishes the job uses :math:`\cos = k / m` and
:math:`\sin = -\vec{b}_z / m`, leaving the :math:`y` part alone:

.. math::

   R_{xz}(k,\ 0,\ \vec{b}_z) = (m,\ 0,\ 0) = \lvert\vec{b}\rvert\,\vec{e}_1.

Compose the two and :math:`\vec{b}` is standing straight up on the x-axis, exactly
:math:`\lvert\vec{b}\rvert` long. Call the whole rotation :math:`R`, so
:math:`R(\vec{b}) = \lvert\vec{b}\rvert\,\vec{e}_1`.

Why we are allowed to do this
-----------------------------

We just moved the problem. Why is the answer we get back the *real* projection of
:math:`\vec{a}` onto :math:`\vec{b}`, and not some distortion?

Because a rotation does not change any length or any angle — and the projection of one
vector onto another depends on **nothing but** their lengths and the angle between them.
So projecting and then un-rotating gives the identical result to un-rotating and then
projecting. In symbols, with :math:`P` for "project onto",

.. math::

   R^{-1}\big(P_{R(\vec{b})}(R(\vec{a}))\big) = P_{\vec{b}}(\vec{a}).

(That is the one fact doing the real work; it is proved once and for all in the library —
``proj_rotXY_equivariant`` / ``proj_rotXZ_equivariant`` in
``proofs/GacalcProofs/StandardPosition.lean`` — and the whole rotate / keep-the-x-coordinate /
rotate-back procedure is proved equal to the geometric-algebra projection there, as the single
theorem ``projectSP_eq_proj``.)

Now the algebra
---------------

Stop thinking about geometry — the rest is bookkeeping. Putting the three steps together:

#. **Rotate** both vectors: :math:`\vec{a}' = R(\vec{a})`,
   :math:`\vec{b}' = R(\vec{b}) = \lvert\vec{b}\rvert\,\vec{e}_1`.
#. **Project in standard position** — onto the x-axis, which is trivial: keep the
   x-coordinate of :math:`\vec{a}'`, drop the rest, giving :math:`\vec{a}'_x\,\vec{e}_1`.
#. **Rotate back** by :math:`R^{-1}` (each 2D rotation undone by rotating the same plane
   through the negative angle, in the reverse order).

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
lands on the same answer as the geometric-algebra formula from :doc:`projection` — with
``gacalc.standardposition.project_sp`` (see the companion calculation notebook).

The payoff
----------

Look at what we did **not** use: no dot product, no geometric product, nothing from later
in the book. We defined projection using only rotations a precalculus student already
owns. That is not an accident — it is the point. Later, once we have projection and its
partner **rejection** in hand this way, we can turn the whole thing around and *build* the
geometric product out of them: the part of :math:`\vec{a}` along :math:`\vec{b}` gives the
dot product, the part across gives the wedge, and together they are :math:`\vec{a}\vec{b}`.
Bootstrapping the hard thing out of the easy things — that is worth staring at.
