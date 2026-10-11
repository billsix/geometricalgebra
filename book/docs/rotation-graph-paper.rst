..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Rotation is turning the graph paper
===================================

We just saw (:doc:`geometric-product`) that rotation is **distributive**: rotating a sum is
rotating each piece and adding, so a rotation is fixed by what it does to the two basis vectors
:math:`\vec{e_1}` and :math:`\vec{e_2}`. There is a picture that makes this feel obvious — and it
is the picture to keep for the rest of the book.

Start with ordinary graph paper and a grid of points.

.. figure:: _static/epix/graphpaper1.*
   :align: center
   :alt: a 4x4 grid of points on ordinary graph paper

We could rotate the points one at a time about the origin by :math:`30°` — this corner swings to
there, that one to there.

.. figure:: _static/epix/graphpaper2.*
   :align: center
   :alt: a few grid points rotated by 30 degrees, with arrows

Doing it to all sixteen is a lot of bookkeeping, but here is where they land (blue), over where they
started (faint).

.. figure:: _static/epix/graphpaper3.*
   :align: center
   :alt: all sixteen grid points rotated by 30 degrees

Now the easy way to see the whole thing. Draw the grid **lines** rotated too. The points did not each
move on their own — the **whole sheet of graph paper turned** by :math:`30°`, and every point rode
along with it. That is all a rotation is.

.. figure:: _static/epix/graphpaper4.*
   :align: center
   :alt: the whole graph paper rotated by 30 degrees

This is why distributivity was the whole game: once the sheet turns, the two axes
:math:`\vec{e_1}` and :math:`\vec{e_2}` turn, and *everything drawn on the paper* turns with them —
you never rotate points one by one. A rotation is not something you do to a vector; it is something
you do to the plane the vector lives in.

And since the rotated grid is just graph paper — tilted — we can draw on it exactly as we always do.
Here is :math:`y = x^2` plotted on the rotated frame: the same parabola you know from high school, on
paper that has simply been turned by :math:`30°`.

.. figure:: _static/epix/graphpaper5.*
   :align: center
   :alt: y = x squared plotted on the rotated graph paper

That is the picture: a rotation is **deformed graph paper**, and whatever we draw — points, vectors,
a parabola — comes along for the ride.
