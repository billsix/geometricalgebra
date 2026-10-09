Relative Graph Paper
====================

Placeholder — content to come. Two vectors make relative graph paper (kept at 90° for most of the book): coordinates, the natural basis, and why a ruler only means something relative to something else.

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
:math:`e_1` and :math:`e_2` — your :math:`\mathbf{i}` and :math:`\mathbf{j}` — and a vector is

.. math::

   \vec{a} = a_1\,e_1 + a_2\,e_2,

where the plain numbers :math:`a_1` and :math:`a_2` are the **coordinates** of :math:`\vec{a}`.
Compare :math:`a\,\mathbf{i} + b\,\mathbf{j}`: same thing, but the subscript now *names the axis
the number belongs to*. We write :math:`a_1`, never :math:`a_{x}`, for two reasons. The subscript
matches the basis vector it multiplies (:math:`a_1` goes with :math:`e_1`), and it keeps working
when there is a third axis (:math:`a_3 e_3`) or, later, :math:`n` of them — there is no fourth
letter after :math:`z`. A coordinate is an ordinary number, so it carries no arrow: :math:`\vec{a}`
is the vector, :math:`a_1` is one of its numbers.

One wrinkle you will see in the companion notebooks: in *code*, gacalc reads the first coordinate
as ``a.x`` and the second as ``a.y``. The math says :math:`a_1`; the code says ``.x``. They are the
same number.

.. toctree::
   :maxdepth: 1

   notebooks/relative-graph-paper
