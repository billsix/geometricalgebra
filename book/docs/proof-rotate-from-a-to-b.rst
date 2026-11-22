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

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`proof-rotate` we learned to rotate a vector **by an angle** :math:`\theta`. But the
definition this book is built on (:doc:`rotate`) is different: rotate so that the direction of
:math:`\vec{\mathbf{a}}` is carried onto the direction of :math:`\vec{\mathbf{b}}`. Here we earn that — in 2D, using
nothing but the rotation we already have — and, as a bonus, **without ever computing an angle**.

The trick is **reduction to standard position**: rotating onto a general vector is annoying, but
rotating onto the x-axis is easy. So we move the problem to the x-axis, solve it there, and move it
back. (The same move does the work later, in :doc:`proof-projection`.)

The goal
--------

We are handed two vectors :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}` — **not** unit length; magnitudes don't
matter, only directions set the rotation — and we want the rotation that swings :math:`\vec{\mathbf{a}}`'s
direction onto :math:`\vec{\mathbf{b}}`'s, through the angle :math:`\theta` between them.

.. figure:: _static/epix/rotate-ab-goal.*
   :align: center
   :alt: a and b, and the angle theta from a to b

The plan: three rotations
-------------------------

We never find :math:`\theta`. Instead we build the rotation out of three turns, each one a rotation of
:doc:`proof-rotate` whose cosine and sine we read straight off a vector's coordinates. Written in the
order they are applied — **right to left**, the way a composition reads —

.. math::

   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}} = \big(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}\big)^{-1}
     \circ R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'} \circ R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}.

Read it right to left: swing :math:`\vec{\mathbf{a}}` onto :math:`\vec{\mathbf{e}}_1`, rotate up to :math:`\vec{\mathbf{b}}'` there,
then undo the first swing.

**Step 1 — swing** :math:`\vec{\mathbf{a}}` **onto the x-axis.** This is the single plane rotation of
:doc:`proof-rotate`. Call the angle :math:`\vec{\mathbf{a}}` makes with the x-axis :math:`\beta`; its cosine and
sine are read straight off :math:`\vec{\mathbf{a}}`, so — as in that chapter — we never have to compute
:math:`\beta` itself:

.. math::

   \cos(\beta) = \frac{a_1}{|\vec{\mathbf{a}}|}, \qquad \sin(\beta) = \frac{a_2}{|\vec{\mathbf{a}}|}.

To swing :math:`\vec{\mathbf{a}}` down onto the axis we rotate by :math:`-\beta`, and since cosine is even while
sine is odd that rotation uses :math:`\cos(-\beta) = a_1/|\vec{\mathbf{a}}|`,
:math:`\sin(-\beta) = -a_2/|\vec{\mathbf{a}}|`.
Substitute those into :math:`\vec{\mathbf{r}}(\,\cdot\,;\theta)` and call the result
:math:`R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}` — read "from :math:`\vec{\mathbf{a}}`, to :math:`\vec{\mathbf{e}}_1`". Applied to
:math:`\vec{\mathbf{a}}` itself, the two terms of its second coordinate carry the same number and
cancel, and its first coordinate becomes :math:`(a_1^2 + a_2^2)/|\vec{\mathbf{a}}| = |\vec{\mathbf{a}}|`:

.. math::

   \begin{aligned}
   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{a}})
     &= \frac{a_1}{|\vec{\mathbf{a}}|} * \begin{bmatrix} a_1 \\ a_2 \end{bmatrix}
        - \frac{a_2}{|\vec{\mathbf{a}}|} * \begin{bmatrix} -a_2 \\ a_1 \end{bmatrix}
      = \frac{1}{|\vec{\mathbf{a}}|} * \begin{bmatrix} a_1 * a_1 + a_2 * a_2 \\
          \underbrace{a_1 * a_2}_{1} - \underbrace{a_2 * a_1}_{1} \end{bmatrix} \\
     &= |\vec{\mathbf{a}}| * \vec{\mathbf{e}}_1.
   \end{aligned}

And it carries :math:`\vec{\mathbf{b}}` along to a new vector :math:`\vec{\mathbf{b}}' = R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}(\vec{\mathbf{b}})`.

.. figure:: _static/epix/rotate-ab-step1.*
   :align: center
   :alt: a swung onto the x-axis; b carried to b-prime; faint dashed originals

**Step 2 — in standard position, rotate** :math:`\vec{\mathbf{e}}_1` **onto** :math:`\vec{\mathbf{b}}'`. Now the problem is
easy: swing the x-axis up onto :math:`\vec{\mathbf{b}}'` by the angle :math:`\theta` between them — and, again,
we read its cosine and sine straight off :math:`\vec{\mathbf{b}}'`'s coordinates
(:math:`\cos(\theta) = b'_1/|\vec{\mathbf{b}}'|`, :math:`\sin(\theta) = b'_2/|\vec{\mathbf{b}}'|`). Call it
:math:`R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'}`.

.. figure:: _static/epix/rotate-ab-step2.*
   :align: center
   :alt: in standard position, rotate e1 onto b-prime by theta

**Step 3 — undo step 1.** Rotate back by :math:`\big(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}\big)^{-1}`, the same
rotation as step 1 run backwards. Whatever was on the x-axis swings up to where :math:`\vec{\mathbf{a}}`
started, carrying our standard-position answer with it — so the image of :math:`\vec{\mathbf{a}}` lands exactly
on :math:`\vec{\mathbf{b}}`'s direction, with :math:`\vec{\mathbf{a}}`'s own length: :math:`(|\vec{\mathbf{a}}|/|\vec{\mathbf{b}}|) * \vec{\mathbf{b}}`.

.. figure:: _static/epix/rotate-ab-step3.*
   :align: center
   :alt: undo step 1; a's image lands on b's direction

The collapse
------------

Now the payoff. In 2D, **rotations commute** — turning by one angle and then another is the same in
either order. That is easy to believe, and we can *check it in coordinates* with the formula
:eq:`eq-rotate-formula` of :doc:`proof-rotate`. Rotate :math:`\vec{\mathbf{v}}` by :math:`\theta_1`, then rotate the result by
:math:`\theta_2`, and multiply out:

.. math::

   \begin{aligned}
   \vec{\mathbf{r}}\big(\vec{\mathbf{r}}(\vec{\mathbf{v}};\theta_1);\theta_2\big)
     &= \begin{bmatrix}
          \cos(\theta_2) * (v_1 * \cos(\theta_1) - v_2 * \sin(\theta_1))
            - \sin(\theta_2) * (v_1 * \sin(\theta_1) + v_2 * \cos(\theta_1)) \\
          \sin(\theta_2) * (v_1 * \cos(\theta_1) - v_2 * \sin(\theta_1))
            + \cos(\theta_2) * (v_1 * \sin(\theta_1) + v_2 * \cos(\theta_1))
        \end{bmatrix} \\
     &= \begin{bmatrix}
          v_1 * (\cos(\theta_1) * \cos(\theta_2) - \sin(\theta_1) * \sin(\theta_2))
            - v_2 * (\sin(\theta_1) * \cos(\theta_2) + \cos(\theta_1) * \sin(\theta_2)) \\
          v_1 * (\sin(\theta_1) * \cos(\theta_2) + \cos(\theta_1) * \sin(\theta_2))
            + v_2 * (\cos(\theta_1) * \cos(\theta_2) - \sin(\theta_1) * \sin(\theta_2))
        \end{bmatrix} \\
     &= \begin{bmatrix}
          v_1 * \cos(\theta_1 + \theta_2) - v_2 * \sin(\theta_1 + \theta_2) \\
          v_1 * \sin(\theta_1 + \theta_2) + v_2 * \cos(\theta_1 + \theta_2)
        \end{bmatrix}
      = \vec{\mathbf{r}}(\vec{\mathbf{v}};\ \theta_1 + \theta_2),
   \end{aligned}

by the angle-addition identities. The last line is the single rotation by :math:`\theta_1 + \theta_2`
— and :math:`\theta_1 + \theta_2 = \theta_2 + \theta_1`, so the two turns in the other order land
on exactly the same vector. (The companion notebook, :doc:`notebooks/proof-rotate-from-a-to-b`, runs
the same check with symbolic coordinates, and the Lean proofs state it twice: ``rot_comm`` in
``proofs/GacalcProofs/Rotation2D.lean`` for this angle form, and ``rotPlane_comm`` in
``proofs/GacalcProofs/RotateFromTo2D.lean`` for the cosine-and-sine form the three turns above are
written in.)

So in :math:`\big(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}\big)^{-1} \circ R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'} \circ
R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}`, the outer rotation and the inner rotation — step 3 and step 1, which are
inverses — slide past the middle one and **cancel**; the two carrying the same number below are
that pair. The whole sandwich collapses to its middle turn:

.. math::

   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}
   = \underbrace{\big(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}\big)^{-1}}_{1} \circ R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'} \circ
     \underbrace{R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}}_{1}
   = R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'} \circ \underbrace{\big(R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}\big)^{-1}}_{1} \circ
     \underbrace{R_{\vec{\mathbf{a}}}^{\vec{\mathbf{e}}_1}}_{1}
   = R_{\vec{\mathbf{e}}_1}^{\vec{\mathbf{b}}'}
   \quad\text{— a single rotation, by the angle from } \vec{\mathbf{a}} \text{ to } \vec{\mathbf{b}}.

And its cosine and sine are a tidy formula in the coordinates of :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`,
**with no angle named** (the :math:`|\vec{\mathbf{a}}|`'s from aligning :math:`\vec{\mathbf{a}}` combine with the
:math:`\vec{\mathbf{b}}'` coordinates):

.. math::

   \cos(\theta) = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad
   \sin(\theta) = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|}.

So the rotation that carries :math:`\vec{\mathbf{a}}`'s direction to :math:`\vec{\mathbf{b}}`'s, applied to any vector
:math:`\vec{\mathbf{v}}`, is just the rotation :eq:`eq-rotate-formula` of :doc:`proof-rotate` with that cosine and sine:

.. math::

   R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}}) = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}};\ \pi/2).

(Both facts are machine-checked in ``proofs/GacalcProofs/RotateFromTo2D.lean``: the sandwich collapses
to the middle rotation — ``rotateFromTo_collapse``, built on ``rotPlane_conj_collapse`` (the fact
``rotPlane_comm`` above states, for a conjugation) — and the whole construction carries :math:`\vec{\mathbf{a}}` to :math:`(|\vec{\mathbf{a}}|/|\vec{\mathbf{b}}|) * \vec{\mathbf{b}}` — ``rotateFromTo_carries``.)

Look again at those two numerators. The top one, :math:`a_1 * b_1 + a_2 * b_2`, is the
**dot product** of :math:`\vec{\mathbf{a}}` and :math:`\vec{\mathbf{b}}`; the bottom one,
:math:`a_1 * b_2 - a_2 * b_1`, is the **signed area** of the parallelogram they span.
We built the rotation from nothing but turns we already trusted, and the answer handed us the two
quantities the rest of the book is about. That is worth staring at.
