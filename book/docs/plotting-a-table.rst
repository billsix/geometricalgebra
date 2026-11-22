..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.


Plotting a Table
================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Long before this book you plotted functions from a table. You wrote the inputs :math:`x` in one
row, worked out each output :math:`f(x)` beneath it, and marked the point (:math:`x`,
:math:`f(x)`) on graph paper. :doc:`one-dimension` drew each column of that table on one line:
the input :math:`x * \vec{\mathbf{e}}_1` and the output :math:`f(x) * \vec{\mathbf{e}}_1`, both
pointing the same way, and ended by asking you to tilt your head to see the graph. This chapter
replaces the tilt with a multiplication.

The table
---------

Take :math:`f(x) = m * x + b`, the function of :doc:`one-dimension`, at :math:`m = 1` and
:math:`b = 2`. The table a child fills in, for :math:`x = -5, \ldots, 5`:

.. list-table::
   :header-rows: 1

   * - :math:`x`
     - :math:`-5`
     - :math:`-4`
     - :math:`\ldots`
     - :math:`0`
     - :math:`1`
     - :math:`2`
     - :math:`\ldots`
     - :math:`5`
   * - :math:`f(x)`
     - :math:`-3`
     - :math:`-2`
     - :math:`\ldots`
     - :math:`2`
     - :math:`3`
     - :math:`4`
     - :math:`\ldots`
     - :math:`7`

Each column is two arrows on one line. The input is :math:`x * \vec{\mathbf{e}}_1`. The output is
:math:`f(x) * \vec{\mathbf{e}}_1`. Nothing so far points up.

Turn the output
---------------

:doc:`geometric-product` found that multiplying a vector on the right by
:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` turns it a quarter turn. Multiply the output by it:

.. math::
   :label: eq-turned-output

   \bigl(f(x) * \vec{\mathbf{e}}_1\bigr) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
   = f(x) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1) * \vec{\mathbf{e}}_2
   = f(x) * \vec{\mathbf{e}}_2.

The two equal unit vectors side by side multiply to :math:`1`, and what is left is
:math:`\vec{\mathbf{e}}_2`. The output has the same number :math:`f(x)` and the same length, but
it now points along :math:`\vec{\mathbf{e}}_2`, a quarter turn counterclockwise from where it was.

Plot
----

Vector addition puts one arrow at the tip of another. Put the turned output at the tip of its
input:

.. math::
   :label: eq-plotted-point

   p(x) = x * \vec{\mathbf{e}}_1 + \bigl(f(x) * \vec{\mathbf{e}}_1\bigr) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
        = x * \vec{\mathbf{e}}_1 + f(x) * \vec{\mathbf{e}}_2.

That is the point you marked on graph paper: :math:`x` steps along :math:`\vec{\mathbf{e}}_1`,
then :math:`f(x)` steps along :math:`\vec{\mathbf{e}}_2`. Do it for every column of the table and
the dots fall on the line :math:`y = m * x + b`, the same line :doc:`one-dimension` asked you to
find by tilting your head. The product did the tilt. (The Lean proofs state equation
:eq:`eq-plotted-point` as ``plotted_point_eq`` in ``proofs/GacalcProofs/StandardPosition2D.lean``.)

Why it turns 90°
----------------

Three facts, each checked in the companion notebook.

**An arrow along** :math:`\vec{\mathbf{e}}_1` **leaves along** :math:`\vec{\mathbf{e}}_2`. This is
equation :eq:`eq-turned-output` read for a single unit arrow:
:math:`\vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = \vec{\mathbf{e}}_2`.

**An arrow along** :math:`\vec{\mathbf{e}}_2` **leaves along** :math:`-\vec{\mathbf{e}}_1`.
Swapping :math:`\vec{\mathbf{e}}_2` past :math:`\vec{\mathbf{e}}_1` costs one sign, and then the two
:math:`\vec{\mathbf{e}}_2` cancel:

.. math::

   \vec{\mathbf{e}}_2 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
   = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2
   = -\vec{\mathbf{e}}_1.

So every arrow :math:`v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2` goes to
:math:`-v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2`. It has the same length, and it is
perpendicular to the arrow it came from, because their dot product,
:math:`v_1 * (-v_2) + v_2 * v_1`, is :math:`0`. This is the quarter turn
:math:`\vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)` of :doc:`geometric-product`, the same operation
under the same name.

**Doing it twice gives** :math:`-\vec{\mathbf{v}}`. Two quarter turns are a half turn, which is why
:math:`(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -1`.

The other side
--------------

The side matters. Multiplying the output on the *left*, by
:math:`(\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * \bigl(f(x) * \vec{\mathbf{e}}_1\bigr)`, turns
it the other way, to :math:`-f(x) * \vec{\mathbf{e}}_2`. Every dot lands below the axis and the
graph comes out upside down. The book multiplies on the right.

A table that is not a line
--------------------------

Nothing above used :math:`m * x + b`. Take :math:`f(x) = x * x`, the parabola you plotted next. The
output :math:`x * x * \vec{\mathbf{e}}_1` turns to :math:`x * x * \vec{\mathbf{e}}_2`, and the
point :math:`p(x) = x * \vec{\mathbf{e}}_1 + x * x * \vec{\mathbf{e}}_2` traces the curve. Any
function whose outputs point along :math:`\vec{\mathbf{e}}_1` can be plotted this way.

The companion notebook computes each step with symbols, checks :eq:`eq-plotted-point` against the
point written out directly, and draws the table, the turn and the plot.

.. toctree::
   :maxdepth: 1

   notebooks/plotting-a-table
