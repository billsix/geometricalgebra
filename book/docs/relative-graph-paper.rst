..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Relative Graph Paper
====================

..
   TODO prose (maintainer's voice): two vectors make relative graph paper (kept at 90° for most of
   the book): coordinates, the natural basis, and why a ruler only means something relative to
   something else. Only the coordinates subsection below is drafted.

How we write coordinates
------------------------

.. note::

   Draft. This passage is agent-drafted; maintainer's voice pass pending (the rest of the page is
   still to be written).

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

Graph paper that moves
----------------------

.. note::

   Draft. This section and the next are agent-drafted; maintainer's voice pass pending.

A function of the plane carries every point somewhere, so it carries the whole sheet of graph
paper too: its grid lines, its origin and its two unit arrows. The carried sheet is graph paper
again. A point keeps its coordinates *on the carried sheet*, so many steps of the carried first
arrow and so many of the second, from the carried origin, while its coordinates on the standard
sheet change. The translate :math:`T_b` slides the sheet so that its origin lands on
:math:`\vec{\mathbf{b}}`; the uniform scale :math:`S_m` stretches it about the origin by :math:`m`.
A ruler works the same way: a length means nothing until you say what it is laid against.

Two ways to read a composition
------------------------------

Compose them: :math:`f = T_b \circ S_m`, scale then slide. There are two ways to watch it.

- **Right to left**, the inner function first, the way you evaluate :math:`\sin(\cos(x))`. The
  sheet is stretched about the standard origin, then slid by :math:`\vec{\mathbf{b}}` measured with
  the standard arrows. Every step is measured on the **standard** sheet.
- **Left to right**, the outer function first. The sheet is slid by :math:`\vec{\mathbf{b}}`, then
  stretched about *its own* origin, in *its own* units. Every step is measured on the
  **relative** sheet that the earlier steps left behind.

The middle pictures differ, but both readings end on the same sheet, because they describe the
same function. Reading direction is a choice of story. The order of the functions is not:
:math:`S_m \circ T_b` scales the slide too, and puts the sheet somewhere else. This is how
*Model View Projection* (github.com/billsix/modelviewprojection) reads its sequences of
transformations, top to bottom or bottom to top. Rotation joins translate and scale in
:doc:`rotation-graph-paper`.

The companion notebook draws both sequences and checks that they end on the same function.

.. toctree::
   :maxdepth: 1

   notebooks/relative-graph-paper
