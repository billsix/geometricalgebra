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
   the book), the natural basis, and why a ruler only means something relative to something else.

Graph paper that moves
----------------------

.. note::

   Draft. This section and the next are agent-drafted; maintainer's voice pass pending.

A function of the plane carries every point somewhere, so it carries the whole sheet of graph
paper too: its grid lines, its origin and its two unit arrows. The carried sheet is graph paper
again. A point keeps its coordinates *on the carried sheet*, so many steps of the carried first
arrow and so many of the second, from the carried origin, while its coordinates on the standard
sheet change. The translate :math:`T_b` of :doc:`vector-addition` slides the sheet so that its
origin lands on :math:`\vec{\mathbf{b}}`; a rotation :math:`R` from :doc:`rotate` turns it about the
origin. A ruler works the same way: a length means nothing until you say what it is laid against.

Two ways to read a composition
------------------------------

Compose them: :math:`f = T_b \circ R`, turn then slide. There are two ways to watch it.

- **Right to left**, the inner function first, the way you evaluate :math:`\sin(\cos(x))`. The
  sheet turns about the standard origin, then slides by :math:`\vec{\mathbf{b}}` measured with the
  standard arrows. Every step is measured on the **standard** sheet.
- **Left to right**, the outer function first. The sheet slides by :math:`\vec{\mathbf{b}}`, then
  turns about *its own* origin, now at :math:`\vec{\mathbf{b}}`: the drawing turns in place. Every
  step is measured on the **relative** sheet that the earlier steps left behind.

The middle pictures differ, but both readings end on the same sheet, because they describe the
same function. Reading direction is a choice of story. The order of the functions is not:
:math:`R \circ T_b` turns the slide too, and puts the sheet's origin at :math:`R(\vec{\mathbf{b}})`
instead. This is how *Model View Projection* (github.com/billsix/modelviewprojection) reads its
sequences of transformations, top to bottom or bottom to top, and how it places a paddle: turn it
about its own center, then move it into place.

The companion notebook draws both sequences and checks that they end on the same function.

.. toctree::
   :maxdepth: 1

   notebooks/relative-graph-paper
