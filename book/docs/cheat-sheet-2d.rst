..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Reference Card: The Plane
=========================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

This card collects the plane's formulas in one place. It is for looking things up, not for
learning them: each formula links to the page that teaches it, and most of those pages come later
in the book. The formulas that hold in every dimension :math:`\mathcal{G}_n` are on
:doc:`cheat-sheet-gn`; each chain below starts from that line and fills in a little more: first
the kinds of things multiplied (vectors, a bivector, a versor), then their coordinates. The number
of lines differs from operation to operation.

The names used throughout, by kind. Every name is defined here, even those a formula below does
not use:

.. math::

   \text{scalars}: &\quad m, \ \theta, \ \text{and the coordinates } a_1, a_2, b_1, b_2, v_1,
   v_2 \quad \text{(plain numbers)} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2, \qquad
   \vec{\mathbf{b}} = b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2, \qquad
   \vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2 \\
   \text{the unit of area}: &\quad I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 \\
   \text{a bivector}: &\quad B = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 \\
   \text{a versor}: &\quad R = \vec{\mathbf{a}} * \vec{\mathbf{b}} = \langle R \rangle_0 + \langle R \rangle_2,
   \qquad \langle R \rangle_0 = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}, \qquad \langle R \rangle_2 = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{any multivector}: &\quad A = \langle A \rangle_0 + \langle A \rangle_1
   + \langle A \rangle_2

The geometric product
---------------------

.. math::

   \text{basis of } \mathcal{G}_2: &\quad
   (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -1, \qquad
   \vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = \vec{\mathbf{e}}_2, \qquad
   \vec{\mathbf{e}}_2 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -\vec{\mathbf{e}}_1 \\
   \text{vectors}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2

Taught in :doc:`geometric-product`, :doc:`defining-g2`, and :doc:`bootstrap-product`, equation
:eq:`eq-bootstrap-product`.

Grade projection
----------------

.. math::

   \text{a vector}: &\quad \langle \vec{\mathbf{a}} \rangle_0 = 0, \qquad
   \langle \vec{\mathbf{a}} \rangle_1 = \vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2, \qquad \langle \vec{\mathbf{a}} \rangle_2 = 0 \\
   \text{a product of vectors}: &\quad \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0 = a_1 * b_1 + a_2 * b_2,
   \qquad \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_1 = 0, \\
   &\quad \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2 = (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2

Taught in :doc:`defining-g2` and :doc:`levels-of-abstraction`.

The reverse
-----------

.. math::

   \text{by kind}: &\quad \tilde{\vec{\mathbf{a}}} = \vec{\mathbf{a}}, \qquad
   \tilde{B} = -B, \qquad \tilde{R} = \langle R \rangle_0 - \langle R \rangle_2 \\
   \text{any multivector}: &\quad \tilde{A} = \langle A \rangle_0 + \langle A \rangle_1
   - \langle A \rangle_2

Taught in :doc:`bootstrap-rotation-from-product` and :doc:`blade-square-sign`.

Magnitude
---------

.. math::

   \text{by kind}: &\quad |\vec{\mathbf{a}}| = \sqrt{a_1^2 + a_2^2}, \qquad
   |B| = |a_1 * b_2 - a_2 * b_1|, \\
   &\quad |R| = \sqrt{\langle R \rangle_0^2 + |\langle R \rangle_2|^2}

Taught in :doc:`vectors-as-number-lines` and :doc:`bootstrap-product`.

The inverse
-----------

Each kind of value has its own inverse; there is no formula here for every multivector of
:math:`\mathcal{G}_2`.

.. math::

   \text{by kind}: &\quad \vec{\mathbf{a}}^{-1} = \frac{\vec{\mathbf{a}}}{|\vec{\mathbf{a}}|^2}, \qquad
   B^{-1} = -\frac{B}{|B|^2}, \qquad
   R^{-1} = \frac{\langle R \rangle_0 - \langle R \rangle_2}
   {\langle R \rangle_0^2 + |\langle R \rangle_2|^2} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}}^{-1}
   = \frac{a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2}{a_1^2 + a_2^2}

Taught in :doc:`bootstrap-projection-from-product` and :doc:`dual`.

The dot product
---------------

.. math::

   \text{vectors}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0
   = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = a_1 * b_1 + a_2 * b_2 \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{v}} \cdot B
   = \langle \vec{\mathbf{v}} * B \rangle_1
   = (a_1 * b_2 - a_2 * b_1) * (-v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2)

Taught in :doc:`product-from-projection`, equation :eq:`eq-product-from-projection` and
:doc:`bootstrap-product`, equation :eq:`eq-bootstrap-dot-wedge-proj-rej`.

The wedge product
-----------------

.. math::

   \text{vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2
   = \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2

Taught in :doc:`product-from-projection` and :doc:`bootstrap-product`, equation
:eq:`eq-bootstrap-dot-wedge-proj-rej`.

Angle, area and the unit bivector
---------------------------------

.. math::

   \text{vectors}: &\quad \cos(\theta)
   = \frac{\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad |\sin(\theta)|
   = \frac{|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad \text{area} = |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}| \\
   \text{coordinates}: &\quad \cos(\theta)
   = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|}, \qquad
   \text{signed area} = a_1 * b_2 - a_2 * b_1 \\
   \text{the unit bivector}: &\quad i(\vec{\mathbf{a}}, \vec{\mathbf{b}})
   = \frac{\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}}{|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|}
   = \pm (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) \quad \text{(the sign of } a_1 * b_2 - a_2 * b_1\text{)}

Taught in :doc:`bootstrap-product`, equation :eq:`eq-bootstrap-unit-product`,
:doc:`bootstrap-rotation-from-projection`, equation :eq:`eq-bootstrap-from-projection-cos-sin`,
and :doc:`product-from-projection`.

Projection and rejection
------------------------

.. math::

   \text{vectors}: &\quad \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = (\vec{\mathbf{b}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1}, \qquad
   \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = (\vec{\mathbf{b}} \wedge \vec{\mathbf{a}}) * \vec{\mathbf{a}}^{-1} \\
   \text{coordinates}: &\quad \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \frac{a_1 * b_1 + a_2 * b_2}{a_1^2 + a_2^2} * \vec{\mathbf{a}} \\
   &\quad \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \frac{a_1 * b_2 - a_2 * b_1}{a_1^2 + a_2^2}
   * (-a_2 * \vec{\mathbf{e}}_1 + a_1 * \vec{\mathbf{e}}_2)

Taught in :doc:`projection`, :doc:`bootstrap-projection`, equations :eq:`eq-bootstrap-projection`
and :eq:`eq-bootstrap-rejection`, and :doc:`bootstrap-projection-from-product`, equations
:eq:`eq-bootstrap-projection-product` and :eq:`eq-bootstrap-rejection-product`.

Reflection
----------

.. math::

   \text{vectors}: &\quad \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
   = \vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1} \\
   \text{coordinates}: &\quad \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
   = \frac{2 * (a_1 * b_1 + a_2 * b_2)}{b_1^2 + b_2^2} * \vec{\mathbf{b}} - \vec{\mathbf{a}}

Taught in :doc:`reflection`, equations :eq:`eq-reflect-vector` and :eq:`eq-reflect-sandwich`.

Rotation
--------

By an angle:

.. math::

   \text{the quarter turn}: &\quad \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)
   = \vec{\mathbf{v}} * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
   = -v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2 \\
   \text{any angle}: &\quad \vec{\mathbf{r}}(\vec{\mathbf{v}}; \theta)
   = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)
   = \vec{\mathbf{v}} * (\cos(\theta) + \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) \\
   \text{coordinates}: &\quad \vec{\mathbf{r}}(\vec{\mathbf{v}}; \theta)
   = (v_1 * \cos(\theta) - v_2 * \sin(\theta)) * \vec{\mathbf{e}}_1
   + (v_1 * \sin(\theta) + v_2 * \cos(\theta)) * \vec{\mathbf{e}}_2

From :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`:

.. math::

   \text{a versor}: &\quad R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = R * \vec{\mathbf{v}} * R^{-1}, \qquad
   R = \vec{\mathbf{b}} * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}| \\
   \text{the angle}: &\quad R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2),
   \quad \theta \text{ from } \vec{\mathbf{a}} \text{ to } \vec{\mathbf{b}} \\
   \text{coordinates}: &\quad R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = \frac{(a_1 * b_1 + a_2 * b_2) * \vec{\mathbf{v}}
   + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)}
   {|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|}

Taught in :doc:`rotate`, equation :eq:`eq-rotate-formula`, :doc:`bootstrap-rotation`, equation
:eq:`eq-bootstrap-rotation`, :doc:`bootstrap-rotation-from-projection`, equation
:eq:`eq-bootstrap-rotation-from-to`, :doc:`bootstrap-rotation-from-product`, equation
:eq:`eq-bootstrap-rotation-sandwich`, and :doc:`rotation-from-vectors`.

The dual
--------

.. math::

   \text{the unit of area}: &\quad I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2, \qquad I^{-1} = -I \\
   \text{by kind}: &\quad \vec{\mathbf{a}}^{*} = a_2 * \vec{\mathbf{e}}_1 - a_1 * \vec{\mathbf{e}}_2, \qquad
   B^{*} = a_1 * b_2 - a_2 * b_1, \\
   &\quad \langle A \rangle_0^{*} = -\langle A \rangle_0 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2

Taught in :doc:`dual`, equation :eq:`eq-dual`.

Scaling and translation
-----------------------

.. math::

   \text{uniform scale}: &\quad S_m(\vec{\mathbf{v}}) = m * \vec{\mathbf{v}}
   = m * v_1 * \vec{\mathbf{e}}_1 + m * v_2 * \vec{\mathbf{e}}_2 \\
   \text{scale each axis}: &\quad \vec{\mathbf{v}} \mapsto
   m_1 * v_1 * \vec{\mathbf{e}}_1 + m_2 * v_2 * \vec{\mathbf{e}}_2 \\
   \text{translation}: &\quad T_{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = \vec{\mathbf{v}} + \vec{\mathbf{b}}
   = (v_1 + b_1) * \vec{\mathbf{e}}_1 + (v_2 + b_2) * \vec{\mathbf{e}}_2

Taught in :doc:`one-dimension`, equation :eq:`eq-mx-plus-b`, :doc:`vector-addition`, and
:doc:`relative-graph-paper`.

The reciprocal frame
--------------------

For a frame :math:`\vec{\mathbf{u}}, \vec{\mathbf{v}}` (two vectors that are not parallel), the reciprocal frame
:math:`\vec{\mathbf{u}}^1, \vec{\mathbf{v}}^1` reads coordinates off the frame: :math:`\vec{\mathbf{u}}^1 \cdot \vec{\mathbf{u}} = 1`,
:math:`\vec{\mathbf{u}}^1 \cdot \vec{\mathbf{v}} = 0`, and the same for :math:`\vec{\mathbf{v}}^1`.

.. math::

   \text{the frame}: &\quad \vec{\mathbf{u}}^1
   = \vec{\mathbf{v}} * (\vec{\mathbf{u}} \wedge \vec{\mathbf{v}})^{-1}, \qquad
   \vec{\mathbf{v}}^1 = -\vec{\mathbf{u}} * (\vec{\mathbf{u}} \wedge \vec{\mathbf{v}})^{-1} \\
   \text{coordinates}: &\quad \vec{\mathbf{u}}^1
   = \frac{v_2 * \vec{\mathbf{e}}_1 - v_1 * \vec{\mathbf{e}}_2}{u_1 * v_2 - u_2 * v_1}, \qquad
   \vec{\mathbf{v}}^1
   = \frac{-u_2 * \vec{\mathbf{e}}_1 + u_1 * \vec{\mathbf{e}}_2}{u_1 * v_2 - u_2 * v_1}

Taught in :doc:`frames-qr` and :doc:`proof-reciprocal-frame` (in space; the plane is the same with
two vectors).

Also in gacalc
--------------

These are in the library but not taught in the book; each links to its reference entry. The
scalar product and the contractions are on :doc:`cheat-sheet-gn`.

.. math::

   \text{even and odd parts}: &\quad A^{+} = \langle A \rangle_0 + \langle A \rangle_2, \qquad
   A^{-} = \langle A \rangle_1 \\
   \text{the exponential}: &\quad e^{\theta * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)}
   = \cos(\theta) + \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2

See :py:meth:`~gacalc.base.MultiVectorBase.even_part`,
:py:meth:`~gacalc.base.MultiVectorBase.odd_part`, and
:py:meth:`~gacalc.base.MultiVectorBase.exp`.
