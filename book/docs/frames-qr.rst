..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Frames and QR
=============

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

..
   TODO prose (maintainer's voice): frames, their orthogonal set, QR as "orthogonalize, then
   write each vector in the new directions", and the peel inverse. The two notebooks below
   compute with gacalc's ``Frame`` and draw every step live with ePiX; the narrative is still
   to be written. The math is in the repository's
   ``tasks/reference/frames-qr-and-reciprocal-frames.md``.

A frame is a set of linearly independent vectors. gacalc's ``Frame`` keeps the vectors as
given and computes an orthogonal set from them, which turns the frame's linear map into
something that can be undone one coordinate at a time.

.. toctree::
   :maxdepth: 1

   notebooks/frame-qr-2d
   notebooks/frame-qr-3d
