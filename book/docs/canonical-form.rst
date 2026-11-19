..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Exact Answers, Not Decimals
===========================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

:math:`1 + \sqrt{2}` is the answer. A calculator would say :math:`2.414213562373095`, but that
decimal is a nearby number, not the answer, and its small error rides along through every later
step. Square the calculator's :math:`\sqrt{2}` and you get :math:`2.0000000000000004`, not
:math:`2`; add the decimals :math:`0.1` and :math:`0.2` and you get :math:`0.30000000000000004`.
An answer that is almost right cannot be tested for equality.

So this book keeps answers exact, and writes each one in a single standard way, its **canonical
form**: :math:`\sqrt{8}` and :math:`4 / \sqrt{2}` are both written :math:`2 * \sqrt{2}`, and
:math:`(1 + \sqrt{2})^2` is written :math:`3 + 2 * \sqrt{2}`. Two answers are then equal exactly
when they look the same, and checking a result means checking that a difference is :math:`0`.

Keeping things exact is easier when the multiplications are ordered well. A six-pack of crackers
costs 5 cents, so one cracker costs :math:`5/6` of a cent, which nobody can pay. Buying 12, you
never need to: :math:`12 * 6^{-1} = 2` packs, at :math:`2 * 5 = 10` cents. The geometric product
later in the book works the same way: order the multiplications so that they resolve cleanly, and
nothing awkward ever appears.

A decimal comes last, only when it is truly needed, to measure or to draw, and then with as many
digits as the job requires. The companion notebook shows each of these with sympy, the library the
notebooks use for exact algebra.

.. toctree::
   :maxdepth: 1

   notebooks/canonical-form
