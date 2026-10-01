..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Levels of Abstraction
=====================

The dot product, the wedge, and the sine and cosine of an angle can each be written at
several *levels of abstraction* — from a fully **coordinate** formula you could compute
by hand, through an intermediate **fixed-grade** form (Hestenes' definition with the grade
bound to a literal), up to a **coordinate-free, dimension-independent** one. The
coordinate-free form is the one we prefer and teach as canonical; the lower rungs are kept
as teaching aids. Showing several forms is safe because we **prove them equal** — the
companion notebook does so symbolically, and the equivalences are pinned by the test suite
(``tests/test_fixed_grade_dot_wedge.py``).

.. note::

   Draft. The companion notebook is runnable; prose and figures are a work in progress
   (maintainer's voice pass pending).

.. toctree::
   :maxdepth: 1

   notebooks/levels-of-abstraction
