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
number lines make graph paper, the subject of :doc:`relative-graph-paper`.

The companion notebook draws these number lines and reads the numbers with gacalc.

.. toctree::
   :maxdepth: 1

   notebooks/vectors-as-number-lines
