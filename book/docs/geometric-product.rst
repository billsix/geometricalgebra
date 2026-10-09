..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

The Geometric Product
=====================

In :doc:`proof-rotate` we derived, from high-school trigonometry, that rotating a point
:math:`\vec{a}` by an angle :math:`\theta` about the origin gives

.. math::

   \vec{r}(\vec{a}; \theta) = \cos\theta\,\vec{a} + \sin\theta\,\vec{r}(\vec{a}; \pi/2),
   \qquad \vec{r}(\vec{a}; \pi/2) = \begin{bmatrix} -a_2 \\ a_1 \end{bmatrix}.

The 90° rotation :math:`(-a_2, a_1)` is the key. **It is a product.** Write
the two basis directions as :math:`e_1` and :math:`e_2`, and define their *geometric
product* :math:`e_1 e_2` — call it :math:`e_{12}`. Multiplying :math:`\vec{a}` by
:math:`e_{12}` on the right turns it 90°:

.. math::

   \vec{a}\,e_{12} = (a_1 e_1 + a_2 e_2)\,e_{12}
                   = -a_2\,e_1 + a_1\,e_2.

(The two facts used, :math:`e_1 e_{12} = e_2` and :math:`e_2 e_{12} = -e_1`, are the
multiplication rules of the algebra, spelled out in :doc:`defining-g2`.) So the whole rotation is
a single multiplication:

.. math::

   \vec{r}(\vec{a}; \theta) = \cos\theta\,\vec{a} + \sin\theta\,(\vec{a}\,e_{12})
                            = \vec{a}\,(\cos\theta + \sin\theta\,e_{12}).

Check it in coordinates. Multiply the right-hand side out, component by component, and compare
with the formula we started from:

.. math::

   \vec{a}\,(\cos\theta + \sin\theta\,e_{12})
     = \cos\theta\,(a_1 e_1 + a_2 e_2) + \sin\theta\,(-a_2 e_1 + a_1 e_2)
     = (a_1\cos\theta - a_2\sin\theta)\,e_1
       + (a_1\sin\theta + a_2\cos\theta)\,e_2,

exactly the two coordinates of :math:`\vec{r}(\vec{a}; \theta)` in :doc:`proof-rotate`. (The Lean
proofs state this as ``vec_mul_fullAngleRotor`` in ``proofs/GacalcProofs/Rotation2D.lean``.)

The object :math:`R = \cos\theta + \sin\theta\,e_{12}` is a **full-angle rotor**: to
rotate is simply to *multiply by* :math:`R`, on one side, by the whole angle. This is what
we mean when we say the geometric product produces a rotation — an **action**, not just a
number. The one-sided, full-angle form works because in two dimensions nothing lies outside
the plane of rotation. The form that survives into three dimensions is the *half-angle*
rotor :math:`\cos(\theta/2) - \sin(\theta/2)\,e_{12}` applied as a sandwich
:math:`R\,\vec{v}\,\tilde{R}`; gacalc's ``plane_rotation`` uses it under the hood, and the
companion notebook checks that the two give the same answer. (gacalc's Lean proofs name the two
objects ``fullAngleRotor`` and ``rotor``, and prove them equal in effect.)

Keep everything exact
---------------------

Notice we never turned :math:`\cos\theta` or :math:`\sin\theta` into a decimal, and
:math:`e_{12}` is an exact unit bivector. This is the same discipline as buying 12
crackers from a 6-for-5¢ pack: you keep :math:`6` and :math:`5` whole and compute
:math:`12 \cdot 6^{-1} \cdot 5 = 10`, and the fraction :math:`5/6` never appears (see
:doc:`canonical-form`). We order the operations so the answer stays in exact, canonical
form — a full-angle rotor built from :math:`\cos\theta`, :math:`\sin\theta`, and :math:`e_{12}`,
not a table of rounded numbers.

The companion notebook builds :math:`R` in gacalc and checks — symbolically — that
:math:`\vec{a}\,(\cos\theta + \sin\theta\,e_{12})` equals both the coordinate formula
above and gacalc's own rotation.

.. toctree::
   :maxdepth: 1

   notebooks/geometric-product
