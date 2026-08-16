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

In :doc:`geometric-product` you met the rotor :math:`R = \cos\theta + \sin\theta\,e_{12}`,
and along the way a small surprise: the object :math:`e_{12} = e_1 e_2` **squares to**
:math:`-1`, exactly like the imaginary unit :math:`i` from precalculus. Why :math:`-1`,
and not :math:`+1`? And what happens if we square :math:`e_1 e_2 e_3`, or the product of
*all* the basis directions at once?

The answer is not mysterious, and you do not need any new machinery to find it. It comes
out of **counting** — the same kind of counting as "how many swaps to sort a short list."
By the end of this chapter you will be able to square any blade in your head and know the
sign before you finish writing it down.

The two rules we are allowed to use
-----------------------------------

Everything here rests on two rules you have already seen for the geometric product. A
**blade** is just a product of distinct basis directions, like :math:`e_1 e_2 e_3`.

- **Rule 1 — a direction squared is one.** :math:`e_i\, e_i = 1`. A basis direction times
  *itself* collapses to the plain number :math:`1`. *(This is where "flat, ordinary space"
  lives; it is the one place the number* :math:`+1` *comes from.)*
- **Rule 2 — swapping two different directions flips the sign.**
  :math:`e_i\, e_j = -\,e_j\, e_i` when :math:`i \neq j`. Trading the places of two
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

Watch it happen, grade by grade.

By hand, grades 1 through 5
---------------------------

Write :math:`I_r = e_1 e_2 \cdots e_r` for the product of the first :math:`r` basis
directions. We want :math:`I_r{}^2`.

**Grade 1.** Nothing to slide:

::

   I_1^2 =  e1 e1                      sign = +1
            \__/  e1 e1 = 1  (cancel, Rule 1)
         =  +1

**Grade 2.** One flip:

::

   I_2^2 =  e1 e2 | e1 e2              sign = +1
                    ^^ slide this e1 left
            e1 e1 e2 e2   (past e2)    flip  ->  sign = -1
            \__/  \__/    cancel both  (Rule 1)
         =  -1

That is the :math:`e_{12}{}^2 = -1` you already saw — now you can see *where the minus
came from*: exactly one flip.

**Grade 3.** Slide, cancel, then repeat on what is left:

::

   I_3^2 =  e1 e2 e3 | e1 e2 e3               sign = +1
                       ^^ slide this e1 left
            e1 e2 e1 e3 e2 e3   (past e3)     flip  ->  sign = -1
            e1 e1 e2 e3 e2 e3   (past e2)     flip  ->  sign = +1
            \__/  e1 e1 = 1     cancel
                  e2 e3 | e2 e3          <-- same shape, one direction shorter
                          ^^ slide this e2 left
                  e2 e2 e3 e3   (past e3)     flip  ->  sign = -1
                  \__/  \__/    cancel both
         =  -1

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

   0,\ 1,\ 3,\ 6,\ 10,\ 15,\ \ldots \;=\; \frac{r(r-1)}{2}.

So the sign is always :math:`(-1)` raised to that triangular number:

.. math::

   I_r{}^2 \;=\; (-1)^{\,r(r-1)/2}.

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
   directions back-to-front, :math:`\tilde{I}_r = e_r \cdots e_1`; untangling that ordering
   takes :math:`r(r-1)/2` flips, so :math:`\tilde{I}_r = (-1)^{\,r(r-1)/2}\, I_r`. And
   :math:`I_r\,\tilde{I}_r = 1`, because the two copies cancel neatly from the middle out.
   Put those together and :math:`I_r{}^2 = (-1)^{\,r(r-1)/2}`. This is why the same sign
   shows up whenever you *reverse* a blade — it is one and the same count of flips.

Numbers and symbols come along for the ride
-------------------------------------------

Real products are not bare blades — the directions come with numbers, or with unknown
symbols like :math:`a`, :math:`b`, :math:`c`, out in front. That changes **nothing** about
the flipping, because a plain number commutes with everything: it slides past any direction
for free, no sign, no fuss. So resolving a messy product is three tidy steps.

Take :math:`(a\,e_1)(b\,e_2)(c\,e_1)` as our worked example.

**Step 1 — send the numbers to the front, multiplied together.** Every coefficient slides
out to the left and collects into one product:

.. math::

   (a\,e_1)(b\,e_2)(c\,e_1) \;=\; a\,b\,c \,\cdot\, e_1 e_2 e_1.

**Step 2 — resolve the directions with the two rules, tracking the sign on the right.**
This is the exact same flip-and-cancel game, on :math:`e_1 e_2 e_1`:

::

   e1 e2 e1                    sign = +1
         ^^ slide this e1 left
   e1 e1 e2   (past e2)        flip  ->  sign = -1
   \__/  e1 e1 = 1  (cancel)
         e2                    the direction that survives

So the direction part resolves to :math:`e_2`, carrying a :math:`-` sign.

**Step 3 — put the sign back in front of the numbers.** The minus we counted multiplies the
collected coefficients:

.. math::

   (a\,e_1)(b\,e_2)(c\,e_1) \;=\; -\,(a\,b\,c)\,e_2 \;=\; -\,a b c\, e_2.

Notice we never had to know *what* :math:`a`, :math:`b`, :math:`c` are. A coefficient is
just a number that commutes, so the very same three steps work whether they are whole
numbers, fractions kept in exact form (see :doc:`canonical-form`), or symbols standing in
for numbers we have not chosen yet. **The directions decide the sign; the numbers just come
along for the ride.**

Where this shows up
-------------------

This one sign is not a curiosity — the library leans on it constantly. Reversing a
multivector gives its grade-:math:`r` part exactly the sign :math:`(-1)^{\,r(r-1)/2}`, and
the exponential map that builds rotors uses it to tell a "turning" plane
(:math:`e_{12}{}^2 = -1`) apart from a plain stretch. In gacalc it is the little function
``pseudoscalar_squared_sign(r)``, and it returns precisely the count of flips you just
learned to do by hand.
