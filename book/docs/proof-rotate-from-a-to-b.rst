..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Proof: Rotate from the Direction of a to the Direction of b
===========================================================

In :doc:`proof-rotate` we learned to rotate a vector **by an angle** :math:`\theta`. But the
definition this book is built on (:doc:`rotate`) is different: rotate so that the direction of
:math:`\vec{a}` is carried onto the direction of :math:`\vec{b}`. Here we earn that — in 2D, using
nothing but the rotation we already have — and, as a bonus, **without ever computing an angle**.

The trick is **reduction to standard position**: rotating onto a general vector is annoying, but
rotating onto the x-axis is easy. So we move the problem to the x-axis, solve it there, and move it
back. (The same move does the work later in :doc:`projection`.)

The goal
--------

We are handed two vectors :math:`\vec{a}` and :math:`\vec{b}` — **not** unit length; magnitudes don't
matter, only directions set the rotation — and we want the rotation that swings :math:`\vec{a}`'s
direction onto :math:`\vec{b}`'s, through the angle :math:`\theta` between them.

.. figure:: _static/epix/rotate-ab-goal.*
   :align: center
   :alt: a and b, and the angle theta from a to b

The plan: three rotations
-------------------------

We never find :math:`\theta`. Instead we build the rotation out of three turns, each one a rotation of
:doc:`proof-rotate` whose cosine and sine we read straight off a vector's coordinates. Written in the
order they are applied — **right to left**, the way a composition reads —

.. math::

   R_{\vec{a}}^{\vec{b}} = \big(R_{\vec{a}}^{\vec{e}_1}\big)^{-1}
     \circ R_{\vec{e}_1}^{\vec{b}'} \circ R_{\vec{a}}^{\vec{e}_1}.

Read it right to left: swing :math:`\vec{a}` onto :math:`\vec{e}_1`, rotate up to :math:`\vec{b}'` there,
then undo the first swing.

**Step 1 — swing :math:`\vec{a}` onto the x-axis.** This is the single plane rotation of
:doc:`proof-rotate`. Call the angle :math:`\vec{a}` makes with the x-axis :math:`\beta`; its cosine and
sine are read straight off :math:`\vec{a}`, so — as in that chapter — we never have to compute
:math:`\beta` itself:

.. math::

   \cos\beta = \frac{a_1}{|\vec{a}|}, \qquad \sin\beta = \frac{a_2}{|\vec{a}|}.

To swing :math:`\vec{a}` down onto the axis we rotate by :math:`-\beta`, and since cosine is even while
sine is odd that rotation uses :math:`\cos = a_1/|\vec{a}|`, :math:`\sin = -a_2/|\vec{a}|`.
Substitute those into :math:`\vec{r}(\,\cdot\,;\theta)` and call the result
:math:`R_{\vec{a}}^{\vec{e}_1}` — read "from :math:`\vec{a}`, to :math:`\vec{e}_1`". Applied to
:math:`\vec{a}` itself, its :math:`y`-coordinate cancels and its :math:`x`-coordinate becomes
:math:`(a_1^2 + a_2^2)/|\vec{a}| = |\vec{a}|`:

.. math::

   R_{\vec{a}}^{\vec{e}_1}(\vec{a}) = |\vec{a}|\,\vec{e}_1.

And it carries :math:`\vec{b}` along to a new vector :math:`\vec{b}' = R_{\vec{a}}^{\vec{e}_1}(\vec{b})`.

.. figure:: _static/epix/rotate-ab-step1.*
   :align: center
   :alt: a swung onto the x-axis; b carried to b-prime; faint dashed originals

**Step 2 — in standard position, rotate :math:`\vec{e}_1` onto :math:`\vec{b}'`.** Now the problem is
easy: swing the x-axis up onto :math:`\vec{b}'` by the angle :math:`\theta` between them — and, again,
we read its cosine and sine straight off :math:`\vec{b}'`'s coordinates
(:math:`\cos = b'_1/|\vec{b}'|`, :math:`\sin = b'_2/|\vec{b}'|`). Call it
:math:`R_{\vec{e}_1}^{\vec{b}'}`.

.. figure:: _static/epix/rotate-ab-step2.*
   :align: center
   :alt: in standard position, rotate e1 onto b-prime by theta

**Step 3 — undo step 1.** Rotate back by :math:`\big(R_{\vec{a}}^{\vec{e}_1}\big)^{-1}`, the same
rotation as step 1 run backwards. Whatever was on the x-axis swings up to where :math:`\vec{a}`
started, carrying our standard-position answer with it — so the image of :math:`\vec{a}` lands exactly
on :math:`\vec{b}`'s direction, with :math:`\vec{a}`'s own length: :math:`(|\vec{a}|/|\vec{b}|)\,\vec{b}`.

.. figure:: _static/epix/rotate-ab-step3.*
   :align: center
   :alt: undo step 1; a's image lands on b's direction

The collapse
------------

Now the payoff. In 2D, **rotations commute** — turning by one angle and then another is the same in
either order. That is easy to believe, and we can *check it in coordinates* with the formula of
:doc:`proof-rotate`. Rotate :math:`\vec{v}` by :math:`\theta_1`, then rotate the result by
:math:`\theta_2`, and multiply out:

.. math::

   \begin{aligned}
   \vec{r}\big(\vec{r}(\vec{v};\theta_1);\theta_2\big)
     &= \begin{bmatrix}
          \cos\theta_2\,(v_1\cos\theta_1 - v_2\sin\theta_1)
            - \sin\theta_2\,(v_1\sin\theta_1 + v_2\cos\theta_1) \\
          \sin\theta_2\,(v_1\cos\theta_1 - v_2\sin\theta_1)
            + \cos\theta_2\,(v_1\sin\theta_1 + v_2\cos\theta_1)
        \end{bmatrix} \\
     &= \begin{bmatrix}
          v_1\,(\cos\theta_1\cos\theta_2 - \sin\theta_1\sin\theta_2)
            - v_2\,(\sin\theta_1\cos\theta_2 + \cos\theta_1\sin\theta_2) \\
          v_1\,(\sin\theta_1\cos\theta_2 + \cos\theta_1\sin\theta_2)
            + v_2\,(\cos\theta_1\cos\theta_2 - \sin\theta_1\sin\theta_2)
        \end{bmatrix} \\
     &= \begin{bmatrix}
          v_1\cos(\theta_1 + \theta_2) - v_2\sin(\theta_1 + \theta_2) \\
          v_1\sin(\theta_1 + \theta_2) + v_2\cos(\theta_1 + \theta_2)
        \end{bmatrix}
      = \vec{r}(\vec{v};\ \theta_1 + \theta_2),
   \end{aligned}

by the angle-addition identities. The last line is the single rotation by :math:`\theta_1 + \theta_2`
— and :math:`\theta_1 + \theta_2 = \theta_2 + \theta_1`, so the two turns in the other order land
on exactly the same vector. (The companion notebook, :doc:`notebooks/proof-rotate-from-a-to-b`, runs
the same check with symbolic coordinates, and the Lean proofs state it twice: ``rot_comm`` in
``proofs/GacalcProofs/Rotation2D.lean`` for this angle form, and ``rotPlane_comm`` in
``proofs/GacalcProofs/RotateFromTo2D.lean`` for the cosine-and-sine form the three turns above are
written in.)

So in :math:`\big(R_{\vec{a}}^{\vec{e}_1}\big)^{-1} \circ R_{\vec{e}_1}^{\vec{b}'} \circ
R_{\vec{a}}^{\vec{e}_1}`, the outer rotation and the inner rotation — step 3 and step 1, which are
inverses — slide past the middle one and **cancel**. The whole sandwich collapses to its middle turn:

.. math::

   R_{\vec{a}}^{\vec{b}} = R_{\vec{e}_1}^{\vec{b}'}
   \quad\text{— a single rotation, by the angle from } \vec{a} \text{ to } \vec{b}.

And its cosine and sine are a tidy formula in the coordinates of :math:`\vec{a}` and :math:`\vec{b}`,
**with no angle named** (the :math:`|\vec{a}|`'s from aligning :math:`\vec{a}` combine with the
:math:`\vec{b}'` coordinates):

.. math::

   \cos\theta = \frac{a_1b_1 + a_2b_2}{|\vec{a}|\,|\vec{b}|},
   \qquad
   \sin\theta = \frac{a_1b_2 - a_2b_1}{|\vec{a}|\,|\vec{b}|}.

So the rotation that carries :math:`\vec{a}`'s direction to :math:`\vec{b}`'s, applied to any vector
:math:`\vec{v}`, is just the rotation of :doc:`proof-rotate` with that cosine and sine:

.. math::

   R_{\vec{a}}^{\vec{b}}(\vec{v}) = \cos\theta\,\vec{v} + \sin\theta\,\vec{r}(\vec{v};\ \pi/2).

(Both facts are machine-checked in ``proofs/GacalcProofs/RotateFromTo2D.lean``: the sandwich collapses
to the middle rotation — ``rotateFromTo_collapse``, built on ``rotPlane_conj_collapse``, which rests on
``rotPlane_comm`` above — and the whole construction carries :math:`\vec{a}` to :math:`(|\vec{a}|/|\vec{b}|)\,\vec{b}` — ``rotateFromTo_carries``.)

Look again at those two numerators. The top one, :math:`a_1b_1 + a_2b_2`, is the
**dot product** of :math:`\vec{a}` and :math:`\vec{b}`; the bottom one,
:math:`a_1b_2 - a_2b_1`, is the **signed area** of the parallelogram they span.
We built the rotation from nothing but turns we already trusted, and the answer handed us the two
quantities the rest of the book is about. That is worth staring at.
