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
in the book.

Each operation is a chain. The first line holds for every multivector in any dimension
:math:`\mathcal{G}_n`. Each following line fills in a little more: first the kinds of things
multiplied (vectors, a bivector, a versor), then their named components, and last the
coordinates. The number of lines differs from operation to operation.

The names used throughout:

.. math::

   \vec{\mathbf{a}} &= a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2,
   \qquad \vec{\mathbf{b}} = b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2,
   \qquad \vec{\mathbf{v}} = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2, \\
   B &= B_{12} * \mathbf{e}_{12} \quad \text{(a bivector)},
   \qquad R = r_0 + r_{12} * \mathbf{e}_{12} \quad \text{(a versor)}, \\
   A &= A_0 + A_1 * \vec{\mathbf{e}}_1 + A_2 * \vec{\mathbf{e}}_2 + A_{12} * \mathbf{e}_{12}
   \quad \text{(any multivector)}, \qquad I = \mathbf{e}_{12}.

The geometric product
---------------------

.. math::

   \text{in } \mathcal{G}_n: &\quad \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1, \qquad
   \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i
   \ (i \neq j), \qquad \text{distributive and associative} \\
   \text{basis of } \mathcal{G}_2: &\quad
   \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = \mathbf{e}_{12}, \quad
   \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 = -\mathbf{e}_{12}, \quad
   \mathbf{e}_{12} * \mathbf{e}_{12} = -1 \\
   &\quad \vec{\mathbf{e}}_1 * \mathbf{e}_{12} = \vec{\mathbf{e}}_2, \quad
   \vec{\mathbf{e}}_2 * \mathbf{e}_{12} = -\vec{\mathbf{e}}_1 \\
   \text{vectors}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * \mathbf{e}_{12}

Taught in :doc:`geometric-product`, :doc:`defining-g2`, and :doc:`bootstrap-product`, equation
:eq:`eq-bootstrap-product`.

Grade projection
----------------

.. math::

   \text{in } \mathcal{G}_n: &\quad \langle A \rangle_r = \text{the terms of } A
   \text{ of grade } r \\
   \text{coordinates}: &\quad \langle A \rangle_0 = A_0, \qquad
   \langle A \rangle_1 = A_1 * \vec{\mathbf{e}}_1 + A_2 * \vec{\mathbf{e}}_2, \qquad
   \langle A \rangle_2 = A_{12} * \mathbf{e}_{12}

Taught in :doc:`defining-g2` and :doc:`levels-of-abstraction`.

The reverse
-----------

.. math::

   \text{in } \mathcal{G}_n: &\quad
   (\vec{\mathbf{a}}_1 * \cdots * \vec{\mathbf{a}}_r)^{\sim}
   = \vec{\mathbf{a}}_r * \cdots * \vec{\mathbf{a}}_1, \qquad
   \langle \tilde{A} \rangle_r = (-1)^{r * (r - 1) / 2} * \langle A \rangle_r \\
   \text{by type}: &\quad \tilde{\vec{\mathbf{a}}} = \vec{\mathbf{a}}, \qquad
   \tilde{B} = -B, \qquad \tilde{R} = r_0 - r_{12} * \mathbf{e}_{12} \\
   \text{coordinates}: &\quad \tilde{A} = A_0 + A_1 * \vec{\mathbf{e}}_1
   + A_2 * \vec{\mathbf{e}}_2 - A_{12} * \mathbf{e}_{12}

Taught in :doc:`bootstrap-rotation-from-product` and :doc:`blade-square-sign`.

Magnitude
---------

.. math::

   \text{in } \mathcal{G}_n: &\quad |A| = \sqrt{\langle \tilde{A} * A \rangle_0} \\
   \text{coordinates}: &\quad |\vec{\mathbf{a}}| = \sqrt{a_1^2 + a_2^2}, \qquad
   |B| = |B_{12}|, \qquad |R| = \sqrt{r_0^2 + r_{12}^2}

Taught in :doc:`vectors-as-number-lines` and :doc:`bootstrap-product`.

The inverse
-----------

There is no inverse formula for every multivector of :math:`\mathcal{G}_2` here; each kind of
value has its own.

.. math::

   \text{a vector, a blade, a versor}: &\quad A^{-1} = \frac{\tilde{A}}{|A|^2} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}}^{-1}
   = \frac{a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2}{a_1^2 + a_2^2}, \qquad
   B^{-1} = -\frac{1}{B_{12}} * \mathbf{e}_{12}, \qquad
   R^{-1} = \frac{r_0 - r_{12} * \mathbf{e}_{12}}{r_0^2 + r_{12}^2}

Taught in :doc:`bootstrap-projection-from-product` and :doc:`dual`.

The dot product
---------------

.. math::

   \text{in } \mathcal{G}_n: &\quad A \cdot B = \sum_{r, s \geq 1}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{|r - s|}
   \quad \text{(a scalar part contributes } 0\text{)} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0
   = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = a_1 * b_1 + a_2 * b_2 \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{a}} \cdot B
   = \langle \vec{\mathbf{a}} * B \rangle_1
   = B_{12} * (-a_2 * \vec{\mathbf{e}}_1 + a_1 * \vec{\mathbf{e}}_2)

Taught in :doc:`product-from-projection`, equation :eq:`eq-product-from-projection` and
:doc:`bootstrap-product`, equation :eq:`eq-bootstrap-dot-wedge-proj-rej`.

The wedge product
-----------------

.. math::

   \text{in } \mathcal{G}_n: &\quad A \wedge B = \sum_{r, s}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{r + s} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2
   = \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = (a_1 * b_2 - a_2 * b_1) * \mathbf{e}_{12}

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
   = \pm \mathbf{e}_{12} \quad \text{(the sign of } a_1 * b_2 - a_2 * b_1\text{)}

Taught in :doc:`bootstrap-product`, equation :eq:`eq-bootstrap-unit-product`,
:doc:`bootstrap-rotation-from-projection`, equation :eq:`eq-bootstrap-from-projection-cos-sin`,
and :doc:`product-from-projection`.

Projection and rejection
------------------------

.. math::

   \text{in } \mathcal{G}_n \text{, onto a blade } B: &\quad
   \operatorname{proj}_{B}(A) = (A \cdot B) * B^{-1}, \qquad
   \operatorname{rej}_{B}(A) = (A \wedge B) * B^{-1} \\
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

   \text{in } \mathcal{G}_n: &\quad \operatorname{ref}_{B}(A)
   = \operatorname{proj}_{B}(A) - \operatorname{rej}_{B}(A) \\
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
   = \vec{\mathbf{v}} * \mathbf{e}_{12}
   = -v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2 \\
   \text{any angle}: &\quad \vec{\mathbf{r}}(\vec{\mathbf{v}}; \theta)
   = \cos(\theta) * \vec{\mathbf{v}} + \sin(\theta) * \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2)
   = \vec{\mathbf{v}} * (\cos(\theta) + \sin(\theta) * \mathbf{e}_{12}) \\
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

   \text{in } \mathcal{G}_n: &\quad A^{*} = A * I^{-1} \\
   \mathcal{G}_2: &\quad I = \mathbf{e}_{12}, \qquad I^{-1} = -\mathbf{e}_{12} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}}^{*} = a_2 * \vec{\mathbf{e}}_1
   - a_1 * \vec{\mathbf{e}}_2, \qquad B^{*} = B_{12}, \qquad
   (A_0)^{*} = -A_0 * \mathbf{e}_{12}

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

For a frame :math:`\vec{\mathbf{u}}, \vec{\mathbf{v}}` (two vectors that are not parallel), the
reciprocal frame :math:`\vec{\mathbf{u}}^1, \vec{\mathbf{v}}^1` reads coordinates off the frame:
:math:`\vec{\mathbf{u}}^1 \cdot \vec{\mathbf{u}} = 1`,
:math:`\vec{\mathbf{u}}^1 \cdot \vec{\mathbf{v}} = 0`, and the same for
:math:`\vec{\mathbf{v}}^1`.

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

These are in the library but not taught in the book; each links to its reference entry.

.. math::

   \text{even and odd parts}: &\quad A^{+} = A_0 + A_{12} * \mathbf{e}_{12}, \qquad
   A^{-} = A_1 * \vec{\mathbf{e}}_1 + A_2 * \vec{\mathbf{e}}_2 \\
   \text{the exponential}: &\quad e^{\theta * \mathbf{e}_{12}}
   = \cos(\theta) + \sin(\theta) * \mathbf{e}_{12} \\
   \text{the scalar product}: &\quad \langle A * B \rangle_0 \\
   \text{contractions}: &\quad A \rfloor B
   = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{m - k}, \qquad
   A \lfloor B = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{k - m}

See :py:meth:`~gacalc.base.MultiVectorBase.even_part`,
:py:meth:`~gacalc.base.MultiVectorBase.odd_part`, :py:meth:`~gacalc.base.MultiVectorBase.exp`,
:py:meth:`~gacalc.base.MultiVectorBase.scalar_product`,
:py:meth:`~gacalc.base.MultiVectorBase.left_contraction`, and
:py:meth:`~gacalc.base.MultiVectorBase.right_contraction`.
