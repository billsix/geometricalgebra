..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Reference Card: Every Dimension
===============================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

This card collects the formulas that hold in every dimension :math:`\mathcal{G}_n`, in one
place. It is for looking things up, not for learning them: each formula links to the page that
teaches it, and most of those pages come later in the book. :doc:`cheat-sheet-2d` and
:doc:`cheat-sheet-3d` start each chain from the line here and fill it in for the plane and for
space.

The names used throughout:

.. math::

   A, B &: \text{any multivectors}, \qquad \langle A \rangle_r = \text{the part of } A
   \text{ of grade } r, \\
   A &= \langle A \rangle_0 + \langle A \rangle_1 + \cdots + \langle A \rangle_n, \\
   \text{a blade} &: \text{a wedge of vectors, } \vec{\mathbf{a}}_1 \wedge \vec{\mathbf{a}}_2 \wedge \cdots \wedge \vec{\mathbf{a}}_r,
   \qquad I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \cdots * \vec{\mathbf{e}}_n \quad \text{(the unit pseudoscalar)}.

The geometric product
---------------------

.. math::

   \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1, \qquad
   \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i
   \ (i \neq j), \qquad \text{distributive and associative}

Taught in :doc:`geometric-product`, :doc:`defining-g2`, :doc:`three-dimensions`, and
:doc:`bootstrap-product`, equation :eq:`eq-bootstrap-product`.

Grade projection
----------------

.. math::

   \langle A \rangle_r = \text{the terms of } A \text{ of grade } r

Taught in :doc:`defining-g2`, :doc:`blade-square-sign`, and :doc:`levels-of-abstraction`.

The reverse
-----------

.. math::

   (\vec{\mathbf{a}}_1 * \cdots * \vec{\mathbf{a}}_r)^{\sim}
   = \vec{\mathbf{a}}_r * \cdots * \vec{\mathbf{a}}_1, \qquad
   \langle \tilde{A} \rangle_r = (-1)^{r * (r - 1) / 2} * \langle A \rangle_r

Taught in :doc:`bootstrap-rotation-from-product` and :doc:`blade-square-sign`.

Magnitude
---------

.. math::

   |A| = \sqrt{\langle \tilde{A} * A \rangle_0}

Taught in :doc:`vectors-as-number-lines`, :doc:`three-dimensions`, and :doc:`bootstrap-product`.

The inverse
-----------

There is no inverse formula for every multivector; a vector, a blade and a versor have one.

.. math::

   A^{-1} = \frac{\tilde{A}}{|A|^2}

Taught in :doc:`bootstrap-projection-from-product`, :doc:`dual`, and :doc:`frames-qr`.

The dot product
---------------

.. math::

   A \cdot B = \sum_{r, s \geq 1}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{|r - s|}
   \quad \text{(a scalar part contributes } 0\text{)}

Taught in :doc:`product-from-projection`, equation :eq:`eq-product-from-projection`,
:doc:`bootstrap-product`, equation :eq:`eq-bootstrap-dot-wedge-proj-rej`, and
:doc:`projection-rejection-3d`.

The wedge product
-----------------

.. math::

   A \wedge B = \sum_{r, s}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{r + s}

Taught in :doc:`product-from-projection`, :doc:`bootstrap-product`, equation
:eq:`eq-bootstrap-dot-wedge-proj-rej`, and :doc:`projection-rejection-3d`.

Projection and rejection
------------------------

For a blade :math:`B`:

.. math::

   \operatorname{proj}_{B}(A) = (A \cdot B) * B^{-1}, \qquad
   \operatorname{rej}_{B}(A) = (A \wedge B) * B^{-1}

Taught in :doc:`projection`, :doc:`bootstrap-projection`, :doc:`bootstrap-projection-from-product`,
and :doc:`projection-rejection-3d`.

Reflection
----------

.. math::

   \operatorname{ref}_{B}(A)
   = \operatorname{proj}_{B}(A) - \operatorname{rej}_{B}(A)

Taught in :doc:`reflection` and :doc:`reflection-3d`.

The dual
--------

.. math::

   A^{*} = A * I^{-1}

Taught in :doc:`dual` and :doc:`dual-3d`.

The scalar product and the contractions
---------------------------------------

These are in the library but not taught in the book; each links to its reference entry.

.. math::

   \text{the scalar product}: &\quad \langle A * B \rangle_0 \\
   \text{contractions}: &\quad A \rfloor B
   = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{m - k}, \qquad
   A \lfloor B = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{k - m}

See :py:meth:`~gacalc.base.MultiVectorBase.scalar_product`,
:py:meth:`~gacalc.base.MultiVectorBase.left_contraction`, and
:py:meth:`~gacalc.base.MultiVectorBase.right_contraction`.
