..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Squaring a Blade: The Sign, by Counting Flips
=============================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`geometric-product` you met the full-angle rotor :math:`R = \cos(\theta) + \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`,
and along the way a small surprise: the object :math:`\mathbf{e}_{12} = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` **squares to**
:math:`-1`, exactly like the imaginary unit :math:`i` from precalculus. Why :math:`-1`,
and not :math:`+1`? And what happens if we square :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3`, or the product of
*all* the basis directions at once?

The answer is not mysterious, and you do not need any new machinery to find it. It comes
out of **counting** — the same kind of counting as "how many swaps to sort a short list."
By the end of this chapter you will be able to square any blade in your head and know the
sign before you finish writing it down.

The two rules we are allowed to use
-----------------------------------

Everything here rests on two rules you have already seen for the geometric product. A
**blade** is just a product of distinct basis directions, like :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3`.

- **Rule 1 — a direction squared is one.** :math:`\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1`. A basis direction times
  *itself* collapses to the plain number :math:`1`. *(This is where "flat, ordinary space"
  lives; it is the one place the number* :math:`+1` *comes from.)*
- **Rule 2 — swapping two different directions flips the sign.**
  :math:`\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\,\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i` when :math:`i \neq j`. Trading the places of two
  neighbours that are *not* the same costs one minus sign.

That is the whole toolkit: **swap neighbours (Rule 2), and cancel a repeated pair
(Rule 1).** We will call one use of Rule 2 a **flip**, and keep a running :math:`\pm` on
the right as we go.

The trick: line up two copies, slide, and cancel
------------------------------------------------

To square a blade, write it down **twice**, side by side. Then take the **first direction
of the second copy** and slide it leftward, one flip at a time, until it bumps into its
twin in the first copy — at which point Rule 1 cancels the pair to :math:`1`. What is left
is *the same problem, one direction shorter*. Repeat until nothing is left but a sign.

Watch it happen, grade by grade. Each line says which rule it used. When Rule 1 cancels a
pair, both directions of the pair carry the same number under a bracket, so you can match them
up, and on paper cross them off one pair at a time.

By hand, grades 1 through 5
---------------------------

Write :math:`I_r = \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \cdots * \vec{\mathbf{e}}_r` for the product of the first :math:`r` basis
directions. We want :math:`I_r{}^2`.

**Grade 1.** Nothing to slide:

.. math::

   \begin{aligned}
   I_1{}^2 &= \underbrace{\vec{\mathbf{e}}_1}_{1} * \underbrace{\vec{\mathbf{e}}_1}_{1} && \text{pair 1 cancels to } 1 \text{ (Rule 1)} \\
           &= +1
   \end{aligned}

**Grade 2.** One flip:

.. math::

   \begin{aligned}
   I_2{}^2 &= \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 \\
           &= -\,\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2
             && \text{slide the second } \vec{\mathbf{e}}_1 \text{ past } \vec{\mathbf{e}}_2\text{: one flip (Rule 2)} \\
           &= -\,\underbrace{\vec{\mathbf{e}}_1}_{1} * \underbrace{\vec{\mathbf{e}}_1}_{1} * \underbrace{\vec{\mathbf{e}}_2}_{2} * \underbrace{\vec{\mathbf{e}}_2}_{2}
             && \text{pairs 1 and 2 cancel to } 1 \text{ (Rule 1)} \\
           &= -1
   \end{aligned}

That is the :math:`(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2){}^2 = -1` you already saw — now you can see *where the minus
came from*: exactly one flip.

**Grade 3.** Slide, cancel, then repeat on what is left:

.. math::

   \begin{aligned}
   I_3{}^2 &= \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
           &= -\,\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3
             && \text{slide the second } \vec{\mathbf{e}}_1 \text{ past } \vec{\mathbf{e}}_3\text{: flip (Rule 2)} \\
           &= +\,\underbrace{\vec{\mathbf{e}}_1}_{1} * \underbrace{\vec{\mathbf{e}}_1}_{1} * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3
             && \text{past } \vec{\mathbf{e}}_2\text{: flip; pair 1 cancels (Rule 1)} \\
           &= +\,\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3
             && \text{the same shape, one direction shorter} \\
           &= -\,\underbrace{\vec{\mathbf{e}}_2}_{2} * \underbrace{\vec{\mathbf{e}}_2}_{2} * \underbrace{\vec{\mathbf{e}}_3}_{3} * \underbrace{\vec{\mathbf{e}}_3}_{3}
             && \text{slide } \vec{\mathbf{e}}_2 \text{ past } \vec{\mathbf{e}}_3\text{: flip; pairs 2 and 3 cancel} \\
           &= -1
   \end{aligned}

Count the flips: :math:`2 + 1 + 0 = 3`, so the sign is :math:`(-1)^3 = -1`.

**Grades 4 and 5.** By now the rhythm is clear, so instead of every single flip we count
**per peel**: sliding the lead direction of the second copy into its twin costs *(current
grade* :math:`-1)` flips, and then the problem drops one grade. Each line below is one peel.

::

   I_4^2:  peel e1 out of {1,2,3,4}   ->  3 flips,  leaves {2,3,4}
           peel e2 out of {2,3,4}     ->  2 flips,  leaves {3,4}
           peel e3 out of {3,4}       ->  1 flip,   leaves {4}
           peel e4 out of {4}         ->  0 flips,  done
           total flips = 3 + 2 + 1 + 0 = 6   ->   (-1)^6 = +1

::

   I_5^2:  peel e1 -> 4 flips   (leaves {2,3,4,5})
           peel e2 -> 3 flips
           peel e3 -> 2 flips
           peel e4 -> 1 flip
           peel e5 -> 0 flips
           total flips = 4 + 3 + 2 + 1 + 0 = 10   ->   (-1)^10 = +1

The pattern
-----------

Line up what we found:

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - grade
     - flips to cancel
     - :math:`I_r{}^2`
   * - 1
     - :math:`0`
     - :math:`+1`
   * - 2
     - :math:`1`
     - :math:`-1`
   * - 3
     - :math:`2+1+0 = 3`
     - :math:`-1`
   * - 4
     - :math:`3+2+1+0 = 6`
     - :math:`+1`
   * - 5
     - :math:`4+3+2+1+0 = 10`
     - :math:`+1`

Two things jump out.

**The flip totals are triangular numbers.** Peeling a grade-:math:`r` blade costs
:math:`(r-1) + (r-2) + \cdots + 1 + 0`, and that sum is the number of ways to pick two of
the :math:`r` directions:

.. math::

   0,\ 1,\ 3,\ 6,\ 10,\ 15,\ \ldots \;=\; \frac{r * (r-1)}{2}.

So the sign is always :math:`(-1)` raised to that triangular number:

.. math::

   I_r{}^2 \;=\; (-1)^{\,r * (r-1)/2}.

**The signs run in a wave of period four:** :math:`+,\,-,\,-,\,+,\,+,\,-,\,-,\,+,\ldots`.
That is because the triangular number is even, then odd twice, then even twice, forever —
it is :math:`+1` when :math:`r` leaves remainder :math:`0` or :math:`1` on division by
:math:`4`, and :math:`-1` when it leaves :math:`2` or :math:`3`.

Why it is *always* that (the one-sentence proof)
------------------------------------------------

The "slide and cancel" picture already *is* the proof — it just repeats itself. Peeling one
pair off a grade-:math:`r` blade costs :math:`r-1` flips and hands you the very same
question for grade :math:`r-1`. So the sign for grade :math:`r` is :math:`(-1)^{r-1}` times
the sign for grade :math:`r-1`, starting from :math:`+1` at grade :math:`0` (or :math:`1`).
Multiplying those together stacks up the exponents :math:`(r-1) + (r-2) + \cdots + 0`,
which is the triangular number again. Nothing else can happen, so the formula holds for
*every* grade, not just the five we drew.

.. note::

   There is an even shorter way to see it. The **reverse** of :math:`I_r` writes its
   directions back-to-front, :math:`\tilde{I}_r = \vec{\mathbf{e}}_r * \cdots * \vec{\mathbf{e}}_1`; untangling that ordering
   takes :math:`r * (r-1)/2` flips, so :math:`\tilde{I}_r = (-1)^{\,r * (r-1)/2} * I_r`. And
   :math:`I_r * \tilde{I}_r = 1`, because the two copies cancel neatly from the middle out.
   Put those together and :math:`I_r{}^2 = (-1)^{\,r * (r-1)/2}`. This is why the same sign
   shows up whenever you *reverse* a blade — it is one and the same count of flips.

Numbers and symbols come along for the ride
-------------------------------------------

Real products are not bare blades — the directions come with numbers, or with unknown
symbols like :math:`a`, :math:`b`, :math:`c`, out in front. That changes **nothing** about
the flipping, because a plain number commutes with everything: it slides past any direction
for free, no sign, no fuss. So resolving a messy product is three tidy steps.

Take :math:`(a * \vec{\mathbf{e}}_1) * (b * \vec{\mathbf{e}}_2) * (c * \vec{\mathbf{e}}_1)` as our worked example.

**Step 1 — send the numbers to the front, multiplied together.** Every coefficient slides
out to the left and collects into one product:

.. math::

   (a * \vec{\mathbf{e}}_1) * (b * \vec{\mathbf{e}}_2) * (c * \vec{\mathbf{e}}_1) \;=\; a * b * c * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1.

**Step 2 — resolve the directions with the two rules, tracking the sign on the right.**
This is the exact same flip-and-cancel game, on :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1`:

.. math::

   \begin{aligned}
   \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1
     &= -\,\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2
       && \text{slide the second } \vec{\mathbf{e}}_1 \text{ past } \vec{\mathbf{e}}_2\text{: flip (Rule 2)} \\
     &= -\,\underbrace{\vec{\mathbf{e}}_1}_{1} * \underbrace{\vec{\mathbf{e}}_1}_{1} * \vec{\mathbf{e}}_2
       && \text{pair 1 cancels to } 1 \text{ (Rule 1)} \\
     &= -\,\vec{\mathbf{e}}_2
       && \text{the direction that survives}
   \end{aligned}

So the direction part resolves to :math:`\vec{\mathbf{e}}_2`, carrying a :math:`-` sign.

**Step 3 — put the sign back in front of the numbers.** The minus we counted multiplies the
collected coefficients:

.. math::

   (a * \vec{\mathbf{e}}_1) * (b * \vec{\mathbf{e}}_2) * (c * \vec{\mathbf{e}}_1) \;=\; -\,(a * b * c) * \vec{\mathbf{e}}_2 \;=\; -\,a * b * c * \vec{\mathbf{e}}_2.

Notice we never had to know *what* :math:`a`, :math:`b`, :math:`c` are. A coefficient is
just a number that commutes, so the very same three steps work whether they are whole
numbers, fractions kept in exact form (see :doc:`canonical-form`), or symbols standing in
for numbers we have not chosen yet. **The directions decide the sign; the numbers just come
along for the ride.**

Where this shows up
-------------------

This one sign is not a curiosity — the library leans on it constantly. Reversing a
multivector gives its grade-:math:`r` part exactly the sign :math:`(-1)^{\,r * (r-1)/2}`, and
the exponential map that builds rotors uses it to tell a "turning" plane
(:math:`(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2){}^2 = -1`) apart from a plain stretch. In gacalc it is the little function
``pseudoscalar_squared_sign(r)``. It returns the sign itself, :math:`+1` or :math:`-1`: the
count of flips you just learned to do by hand is the exponent.

The Lean proofs state the sign for the unit blade of the plane, of the line and of space as
``I_sq_eq_sign`` in each of ``proofs/GacalcProofs/G1.lean``, ``G2.lean`` and ``G3.lean``
(:math:`I^2 = (-1)^{\,r * (r-1)/2}` for :math:`r = 1, 2, 3`), and the squares themselves as ``I_sq``.
