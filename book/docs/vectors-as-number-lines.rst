..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Vectors as Relative Number Lines
================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`one-dimension` the input :math:`x * \vec{\mathbf{e}}_1` was a number on a number line:
:math:`\vec{\mathbf{e}}_1` gave the direction and the length of one step, and :math:`x` counted the
steps. Nothing about :math:`\vec{\mathbf{e}}_1` was special. Any arrow :math:`\vec{\mathbf{v}}` that is
not zero lays down a number line of its own, the multiples :math:`t * \vec{\mathbf{v}}`, with
:math:`\vec{\mathbf{v}}` as the step: :math:`t = 1` is the tip of :math:`\vec{\mathbf{v}}`,
:math:`t = 2` is twice as far, :math:`t = -1` is one step backward.

A vector is a **relative** number line, because a point's number depends on the line you read it
from. The point :math:`3 * \vec{\mathbf{v}}` reads :math:`3` on :math:`\vec{\mathbf{v}}`'s line,
:math:`3/2` on the line of :math:`2 * \vec{\mathbf{v}}` (whose steps are twice as long), and
:math:`-3` on the line of :math:`-\vec{\mathbf{v}}` (which counts the other way). In general, the
point :math:`t * \vec{\mathbf{v}}` reads :math:`t / s` on the line of :math:`s * \vec{\mathbf{v}}`.

A point has no number of its own, only a number relative to some vector. A ruler works the same
way: a length of 3 means nothing until you say what the ruler is laid against. Two arrows,
:math:`\vec{\mathbf{e}}_1` across and :math:`\vec{\mathbf{e}}_2` up, give two number lines, and two
number lines make graph paper. :doc:`relative-graph-paper`, after rotation, moves that graph
paper.

The companion notebook draws these number lines and reads the numbers with gacalc.

How we write coordinates
------------------------

.. note::

   Draft. This passage is agent-drafted; maintainer's voice pass pending.

You have written coordinates two ways already. In algebra a point was an **ordered pair**
:math:`(x, y)` — the first number its :math:`x`-coordinate, the second its :math:`y`-coordinate
(OpenStax *Algebra 1*, Unit 1, "Find Coordinates"). In precalculus a vector was written in
**component form**, :math:`\langle a, b \rangle`, or as :math:`a\,\mathbf{i} + b\,\mathbf{j}`, with
:math:`\mathbf{i}` and :math:`\mathbf{j}` the unit vectors along the two axes (OpenStax
*Precalculus 2e*, §8.8 "Vectors"). Those are the same idea: a point or a vector is *so many steps
along the first axis, then so many along the second*.

This book writes that idea one way, everywhere. The two axis directions are the basis vectors
:math:`\vec{\mathbf{e}}_1` and :math:`\vec{\mathbf{e}}_2` — your :math:`\mathbf{i}` and :math:`\mathbf{j}` — and a vector is

.. math::

   \vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2,

where the plain numbers :math:`a_1` and :math:`a_2` are the **coordinates** of :math:`\vec{\mathbf{a}}`.
Compare :math:`a\,\mathbf{i} + b\,\mathbf{j}`: same thing, but the subscript now *names the axis
the number belongs to*. We write :math:`a_1`, never :math:`a_{x}`, for two reasons. The subscript
matches the basis vector it multiplies (:math:`a_1` goes with :math:`\vec{\mathbf{e}}_1`), and it keeps working
when there is a third axis (:math:`a_3 * \vec{\mathbf{e}}_3`) or, later, :math:`n` of them — there is no fourth
letter after :math:`z`. A vector is written bold with an arrow, the way gacalc prints it in the
notebooks; a coordinate is an ordinary number, so it is written plain: :math:`\vec{\mathbf{a}}`
is the vector, :math:`a_1` is one of its numbers.

One wrinkle you will see in the companion notebooks: in *code*, gacalc reads the first coordinate
as ``a.x`` and the second as ``a.y``. The math says :math:`a_1`; the code says ``.x``. They are the
same number.

.. toctree::
   :maxdepth: 1

   notebooks/vectors-as-number-lines
