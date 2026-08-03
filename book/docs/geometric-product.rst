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
   \qquad \vec{r}(\vec{a}; \pi/2) = \begin{bmatrix} -\vec{a}_y \\ \vec{a}_x \end{bmatrix}.

The 90° rotation :math:`(-\vec{a}_y, \vec{a}_x)` is the key. **It is a product.** Write
the two basis directions as :math:`e_1` and :math:`e_2`, and define their *geometric
product* :math:`e_1 e_2` — call it :math:`e_{12}`. Multiplying :math:`\vec{a}` by
:math:`e_{12}` on the right turns it 90°:

.. math::

   \vec{a}\,e_{12} = (\vec{a}_x e_1 + \vec{a}_y e_2)\,e_{12}
                   = -\vec{a}_y\,e_1 + \vec{a}_x\,e_2.

So the whole rotation is a single multiplication:

.. math::

   \vec{r}(\vec{a}; \theta) = \cos\theta\,\vec{a} + \sin\theta\,(\vec{a}\,e_{12})
                            = \vec{a}\,(\cos\theta + \sin\theta\,e_{12}).

The object :math:`R = \cos\theta + \sin\theta\,e_{12}` is a **rotor**: to rotate is
simply to *multiply by* :math:`R`. This is what we mean when we say the geometric
product produces a rotation — an **action**, not just a number.

Keep everything exact
---------------------

Notice we never turned :math:`\cos\theta` or :math:`\sin\theta` into a decimal, and
:math:`e_{12}` is an exact unit bivector. This is the same discipline as buying 12
crackers from a 6-for-5¢ pack: you keep :math:`6` and :math:`5` whole and compute
:math:`12 \cdot 6^{-1} \cdot 5 = 10`, and the fraction :math:`5/6` never appears (see
:doc:`canonical-form`). We order the operations so the answer stays in exact, canonical
form — a rotor built from :math:`\cos\theta`, :math:`\sin\theta`, and :math:`e_{12}`,
not a table of rounded numbers.

The companion notebook builds :math:`R` in gacalc and checks — symbolically — that
:math:`\vec{a}\,(\cos\theta + \sin\theta\,e_{12})` equals both the coordinate formula
above and gacalc's own rotation.

.. toctree::
   :maxdepth: 1

   notebooks/geometric-product
