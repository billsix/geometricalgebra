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

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`proof-rotate` we derived, from high-school trigonometry, that rotating a point
:math:`\vec{\mathbf{a}}` by an angle :math:`\theta` about the origin gives

.. math::

   \vec{\mathbf{r}}(\vec{\mathbf{a}}; \theta) = \cos(\theta) * \vec{\mathbf{a}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{a}}; \pi/2),
   \qquad \vec{\mathbf{r}}(\vec{\mathbf{a}}; \pi/2) = \begin{bmatrix} -a_2 \\ a_1 \end{bmatrix}.

The 90° rotation :math:`(-a_2, a_1)` is the key. **It is a product.** Write
the two basis directions as :math:`\vec{\mathbf{e}}_1` and :math:`\vec{\mathbf{e}}_2`, and define their *geometric
product* :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` — call it :math:`\mathbf{e}_{12}`. Multiplying :math:`\vec{\mathbf{a}}` by
:math:`\mathbf{e}_{12}` on the right turns it 90°:

.. math::

   \vec{\mathbf{a}} * \mathbf{e}_{12} = (a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2) * \mathbf{e}_{12}
                   = -a_2 * \vec{\mathbf{e}}_1 + a_1 * \vec{\mathbf{e}}_2.

(The two facts used, :math:`\vec{\mathbf{e}}_1 * \mathbf{e}_{12} = \vec{\mathbf{e}}_2` and :math:`\vec{\mathbf{e}}_2 * \mathbf{e}_{12} = -\vec{\mathbf{e}}_1`, are the
multiplication rules of the algebra, spelled out in :doc:`defining-g2`.)

Turn by 90° twice and the vector points the other way: :math:`(\vec{\mathbf{a}} * \mathbf{e}_{12}) * \mathbf{e}_{12} = -\vec{\mathbf{a}}`.
So :math:`\mathbf{e}_{12} * \mathbf{e}_{12} = -1`. This object squares to :math:`-1`, just like the imaginary unit
:math:`i` from precalculus. :doc:`blade-square-sign` works out why, by counting.

So the whole rotation is a single multiplication:

.. math::

   \vec{\mathbf{r}}(\vec{\mathbf{a}}; \theta) &= \cos(\theta) * \vec{\mathbf{a}} + \sin(\theta) * (\vec{\mathbf{a}} * \mathbf{e}_{12}) \\
                                              &= \vec{\mathbf{a}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12}).

Check it in coordinates. Multiply the right-hand side out, component by component, and compare
with the formula we started from:

.. math::

   \vec{\mathbf{a}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12})
     &= \cos(\theta) * (a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2) \\
     &\quad + \sin(\theta) * (-a_2 * \vec{\mathbf{e}}_1 + a_1 * \vec{\mathbf{e}}_2) \\
     &= (a_1 * \cos(\theta) - a_2 * \sin(\theta)) * \vec{\mathbf{e}}_1 \\
     &\quad + (a_1 * \sin(\theta) + a_2 * \cos(\theta)) * \vec{\mathbf{e}}_2,

exactly the two coordinates of :math:`\vec{\mathbf{r}}(\vec{\mathbf{a}}; \theta)` in :doc:`proof-rotate`,
equation :eq:`eq-rotate-formula`. (The Lean
proofs state this as ``vec_mul_fullAngleRotor`` in ``proofs/GacalcProofs/Rotation2D.lean``.)

The object :math:`R = \cos(\theta) + \sin(\theta) * \mathbf{e}_{12}` is a **full-angle rotor**: to
rotate is simply to *multiply by* :math:`R`, on one side, by the whole angle. This is what
we mean when we say the geometric product produces a rotation — an **action**, not just a
number. The one-sided, full-angle form works because in two dimensions nothing lies outside
the plane of rotation. The form that survives into three dimensions is the *half-angle*
rotor :math:`\cos(\theta/2) - \sin(\theta/2) * \mathbf{e}_{12}` applied as a sandwich
:math:`R * \vec{\mathbf{v}} * \tilde{R}`; gacalc's ``plane_rotation`` uses it under the hood, and the
companion notebook checks that the two give the same answer. (gacalc's Lean proofs name the two
objects ``fullAngleRotor`` and ``rotor``, and prove them equal in effect.)

Rotation is distributive
------------------------

Because to rotate is to *multiply by* :math:`R`, and the geometric product **distributes over
addition**, rotation distributes too:

.. math::
   :label: eq-rotation-distributive

   (\vec{\mathbf{u}} + \vec{\mathbf{v}}) * R = \vec{\mathbf{u}} * R + \vec{\mathbf{v}} * R.

Rotating a sum is the same as rotating each piece and adding. That one fact is the whole game. Write
any vector in the **natural basis**, :math:`\vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2`, and
distribute:

.. math::

   \vec{\mathbf{v}} * R = (v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2) * R
               = v_1 * (\vec{\mathbf{e}}_1 * R) + v_2 * (\vec{\mathbf{e}}_2 * R).

A rotation is **completely determined by what it does to** :math:`\vec{\mathbf{e}}_1` **and**
:math:`\vec{\mathbf{e}}_2` — rotate those two, and every vector's rotation follows by distributing. (This is
the idea the "rotating the graph paper" picture will rest on: turn the two axes, and everything drawn
on the paper turns with them.) The Lean proofs state this as ``rot_add_vec`` (and ``rot_smul`` for a
scalar multiple), with the basis form ``rot_basis_decomp`` in
``proofs/GacalcProofs/Rotation2D.lean``; the companion notebook checks it symbolically in gacalc.

Keep everything exact
---------------------

Notice we never turned :math:`\cos(\theta)` or :math:`\sin(\theta)` into a decimal, and
:math:`\mathbf{e}_{12}` is an exact unit bivector. This is the same discipline as buying 12
crackers from a 6-for-5¢ pack: you keep :math:`6` and :math:`5` whole and compute
:math:`12 * 6^{-1} * 5 = 10`, and the fraction :math:`5/6` never appears (see
:doc:`canonical-form`). We order the operations so the answer stays in exact, canonical
form — a full-angle rotor built from :math:`\cos(\theta)`, :math:`\sin(\theta)`, and :math:`\mathbf{e}_{12}`,
not a table of rounded numbers.

This is the first of two ways the book meets the geometric product. The second starts from
projection and rejection instead of rotation (:doc:`product-from-projection`), and the two give the
same product.

The companion notebook builds :math:`R` in gacalc and checks — symbolically — that
:math:`\vec{\mathbf{a}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12})` equals both the coordinate formula
above and gacalc's own rotation.

.. toctree::
   :maxdepth: 1

   notebooks/geometric-product
