Vector Addition
===============

..
   TODO prose (maintainer's voice): introduce vector addition in 2D. The figures below
   are drafted and render via `make docs`; the narrative around them is still to be written.

Adding vectors
--------------

..
   TODO prose: two vectors, drawn from the origin, before we add them.

.. figure:: _static/epix/add1.*
   :align: center
   :alt: two vectors a and b drawn from the origin

..
   TODO prose: tip-to-tail — slide b so its tail sits on the head of a; the sum runs from
   the origin to where the slid copy ends.

.. figure:: _static/epix/add2.*
   :align: center
   :alt: a plus b drawn tip-to-tail, with b slid onto the head of a

.. note::

   Draft. The paragraph below is agent-drafted; maintainer's voice pass pending (the rest of
   this page's prose is still to be written).

Slide :math:`\vec{b}` onto the head of :math:`\vec{a}`, or slide :math:`\vec{a}` onto the head of
:math:`\vec{b}` — either order lands on the same corner of the parallelogram the two vectors span,
so **addition commutes**: :math:`\vec{a} + \vec{b} = \vec{b} + \vec{a}`.

.. figure:: _static/epix/add3.*
   :align: center
   :alt: the parallelogram spanned by a and b, showing a plus b equals b plus a

The picture says it; the coordinates confirm it. Adding two vectors adds their coordinates, and
adding two ordinary numbers gives the same answer in either order:

.. math::

   \vec{a} + \vec{b}
     = \begin{bmatrix} a_1 + b_1 \\ a_2 + b_2 \end{bmatrix}
     = \begin{bmatrix} b_1 + a_1 \\ b_2 + a_2 \end{bmatrix}
     = \vec{b} + \vec{a}.

This is the first of many times this book will read a fact off a picture and then check it in
coordinates. The companion notebook runs the same check with the coordinates left as symbols, so
it holds for every pair of vectors at once.

Translate: adding the same vector to everything
-----------------------------------------------

.. note::

   Draft. This subsection is agent-drafted; maintainer's voice pass pending.

So far :math:`\vec{a} + \vec{b}` has been a **one-off**: hand it two vectors, get one back. But
watch what happens if we hold one of them still. Fix :math:`\vec{b}`, and let the *other* input
vary over every point of the plane. What used to be a two-input operation, :math:`\Box + \Box`, is
now a **one-input machine**, :math:`\Box + \vec{b}` — feed it any point :math:`\vec{v}` and it hands
back :math:`\vec{v} + \vec{b}`. That machine is a function. gacalc calls it ``translate(b)``:

.. math::

   \text{translate}(\vec{b})(\vec{v}) = \vec{v} + \vec{b}.

Filling in one of the two blanks of a formula to turn it into a smaller function has a name:
**partial binding**. Addition takes two arguments; bind the second to :math:`\vec{b}` and one blank
is left. (In Python the same idea is ``functools.partial(operator.add, b)``; in this book it is the
transform ``translate(b=...)``, called by keyword because the ``b`` is the intercept of
:math:`f(x) = m*x + b` — the ``+ b`` half of that line, in two dimensions.)

Here is the point worth the picture. ``translate(b)`` does not move one arrow — it moves **every
point at once**. Apply it to the whole plane and the entire sheet of graph paper slides by
:math:`\vec{b}`: every point, the origin, the grid lines, all shifted together, their spacing and
directions unchanged.

.. figure:: _static/epix/trans1.*
   :align: center
   :alt: the original graph paper, with the vector b and two sample points P and Q

.. figure:: _static/epix/trans2.*
   :align: center
   :alt: the whole graph paper slid by b; the origin moves to b and every point follows the same displacement

The faint grid is where the paper started; the solid grid is where ``translate(b)`` put it. The
origin has moved to :math:`\vec{b}`, and :math:`P` and :math:`Q` have each followed the *same*
displacement :math:`\vec{b}` to :math:`P + \vec{b}` and :math:`Q + \vec{b}` — one function, applied
to everything.

Sliding the paper the other way just binds the opposite vector: the inverse of ``translate(b)`` is
``translate(-b)``, which undoes the slide by moving every point back by :math:`\vec{b}`. That is
exactly subtraction — the subject of the next section.

Subtracting vectors
-------------------

..
   TODO prose: a minus b is the vector from the head of b to the head of a — what you add
   to b to get a.

.. figure:: _static/epix/sub1.*
   :align: center
   :alt: a minus b as the connecting vector from the head of b to the head of a

..
   TODO prose: the same difference as adding the opposite — flip b to minus b, then add
   tip-to-tail; it lands on the same point.

.. figure:: _static/epix/sub2.*
   :align: center
   :alt: a plus negative b drawn tip-to-tail, landing on the same point as a minus b

.. toctree::
   :maxdepth: 1

   notebooks/vector-addition
