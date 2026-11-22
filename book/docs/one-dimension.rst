..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

One Dimension: m·x + b
======================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

You have graphed :math:`y = m * x + b` many times: inputs across, outputs up, a straight line
with slope :math:`m` crossing the vertical axis at :math:`b`. This chapter takes that function
apart into two simpler ones and then draws it a second way, the way the rest of the book draws
functions.

Two pieces
----------

Think of the input as a number :math:`x` on a number line, written :math:`x * \vec{\mathbf{e}}_1`:
:math:`x` steps along the line's direction :math:`\vec{\mathbf{e}}_1`. Two functions act on it.

- The **uniform scale** :math:`S_m` stretches it by the factor :math:`m`:
  :math:`S_m(x * \vec{\mathbf{e}}_1) = m * x * \vec{\mathbf{e}}_1`. A negative :math:`m` also flips it.
- The **translate** :math:`T_b` slides it :math:`b` steps along the line:
  :math:`T_b(x * \vec{\mathbf{e}}_1) = x * \vec{\mathbf{e}}_1 + b * \vec{\mathbf{e}}_1`.

Scale first, then translate:

.. math::
   :label: eq-mx-plus-b

   f = T_b \circ S_m, \qquad f(x * \vec{\mathbf{e}}_1) = (m * x + b) * \vec{\mathbf{e}}_1.

On graph paper, changing :math:`m` with :math:`b = 0` swings the line about the origin, and
changing :math:`b` with :math:`m = 1` slides the line :math:`y = x` up and down. The companion
notebook draws both families.

Along one direction
-------------------

The graph paper puts the output on a second axis, but nothing in :eq:`eq-mx-plus-b` points up.
The input points along :math:`\vec{\mathbf{e}}_1` and so does the output. So draw each input on a
number line on the left and its output on a number line on the right, pointing the same way: the
scale step, then the translate step, landing on :math:`m * x + b`.

Stack those pictures for :math:`x = -5, -4, \ldots, 5`, one row each, and tilt your head to the
right. The output dots fall on a straight line, the same line as on the graph paper. The graph
paper spread the outputs out sideways, one column per input, so you could see them all at once;
along one direction, an input and its output share a line.

That is the picture to keep. In the plane the inputs and outputs of a function are arrows in the
same plane, and there is no spare direction to plot an output "up" into, so the book draws a
function as what it does to arrows.

The tilt turns into a multiplication later, in :doc:`plotting-a-table`.

.. toctree::
   :maxdepth: 1

   notebooks/one-dimension
