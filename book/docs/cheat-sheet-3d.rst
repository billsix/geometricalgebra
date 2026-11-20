..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Reference Card: Space
=====================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

This card collects the formulas of space in one place, the way :doc:`cheat-sheet-2d` does for
the plane. It is for looking things up, not for learning them: each formula links to the page that
teaches it, and most of those pages come later in the book.

Each operation is a chain. The first line holds for every multivector in any dimension
:math:`\mathcal{G}_n`. Each following line fills in a little more: first the kinds of things
multiplied (vectors, a bivector, a versor), then their named components, and last the
coordinates. The number of lines differs from operation to operation.

The names used throughout:

.. math::

   \vec{\mathbf{a}} &= a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2
   + a_3 * \vec{\mathbf{e}}_3, \quad \text{and the same for } \vec{\mathbf{b}},
   \vec{\mathbf{c}}, \vec{\mathbf{v}}, \\
   B &= B_{12} * \mathbf{e}_{12} + B_{13} * \mathbf{e}_{13} + B_{23} * \mathbf{e}_{23}
   \quad \text{(a bivector)}, \qquad T = t * \mathbf{e}_{123} \quad \text{(a trivector)}, \\
   R &= r_0 + r_{12} * \mathbf{e}_{12} + r_{13} * \mathbf{e}_{13} + r_{23} * \mathbf{e}_{23}
   \quad \text{(a versor)}, \\
   A &= A_0 + \vec{\mathbf{a}} + B + T \quad \text{(any multivector: one part of each grade)},
   \qquad I = \mathbf{e}_{123}.

The geometric product
---------------------

.. math::

   \text{in } \mathcal{G}_n: &\quad \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_i = 1, \qquad
   \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = -\vec{\mathbf{e}}_j * \vec{\mathbf{e}}_i
   \ (i \neq j), \qquad \text{distributive and associative} \\
   \text{basis of } \mathcal{G}_3: &\quad
   \vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j = \mathbf{e}_{ij} \ (i < j), \qquad
   \mathbf{e}_{12} * \vec{\mathbf{e}}_3 = \mathbf{e}_{123} = I \\
   &\quad \mathbf{e}_{ij} * \mathbf{e}_{ij} = -1, \qquad I * I = -1, \qquad
   I \text{ commutes with every multivector} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = (a_1 * b_1 + a_2 * b_2 + a_3 * b_3) + (a_1 * b_2 - a_2 * b_1) * \mathbf{e}_{12} \\
   &\quad \qquad + (a_1 * b_3 - a_3 * b_1) * \mathbf{e}_{13}
   + (a_2 * b_3 - a_3 * b_2) * \mathbf{e}_{23}

Taught in :doc:`three-dimensions` and :doc:`blade-square-sign`.

Grade projection
----------------

.. math::

   \text{in } \mathcal{G}_n: &\quad \langle A \rangle_r = \text{the terms of } A
   \text{ of grade } r \\
   \text{by type}: &\quad \langle A \rangle_0 = A_0, \qquad
   \langle A \rangle_1 = \vec{\mathbf{a}}, \qquad
   \langle A \rangle_2 = B, \qquad \langle A \rangle_3 = T

Taught in :doc:`blade-square-sign` and :doc:`levels-of-abstraction`.

The reverse
-----------

.. math::

   \text{in } \mathcal{G}_n: &\quad
   (\vec{\mathbf{a}}_1 * \cdots * \vec{\mathbf{a}}_r)^{\sim}
   = \vec{\mathbf{a}}_r * \cdots * \vec{\mathbf{a}}_1, \qquad
   \langle \tilde{A} \rangle_r = (-1)^{r * (r - 1) / 2} * \langle A \rangle_r \\
   \text{by type}: &\quad \tilde{\vec{\mathbf{a}}} = \vec{\mathbf{a}}, \qquad
   \tilde{B} = -B, \qquad \tilde{T} = -T, \qquad \tilde{A} = A_0 + \vec{\mathbf{a}} - B - T \\
   \text{coordinates}: &\quad \tilde{R} = r_0 - r_{12} * \mathbf{e}_{12}
   - r_{13} * \mathbf{e}_{13} - r_{23} * \mathbf{e}_{23}

Taught in :doc:`blade-square-sign` and :doc:`bootstrap-rotation-from-product`.

Magnitude
---------

.. math::

   \text{in } \mathcal{G}_n: &\quad |A| = \sqrt{\langle \tilde{A} * A \rangle_0} \\
   \text{coordinates}: &\quad |\vec{\mathbf{a}}| = \sqrt{a_1^2 + a_2^2 + a_3^2}, \qquad
   |B| = \sqrt{B_{12}^2 + B_{13}^2 + B_{23}^2}, \qquad |T| = |t| \\
   &\quad |R| = \sqrt{r_0^2 + r_{12}^2 + r_{13}^2 + r_{23}^2}

Taught in :doc:`three-dimensions` and :doc:`dual-3d`.

The inverse
-----------

There is no inverse formula for every multivector of :math:`\mathcal{G}_3` here; each kind of
value has its own.

.. math::

   \text{a vector, a blade, a versor}: &\quad A^{-1} = \frac{\tilde{A}}{|A|^2} \\
   \text{by type}: &\quad \vec{\mathbf{a}}^{-1}
   = \frac{\vec{\mathbf{a}}}{|\vec{\mathbf{a}}|^2}, \qquad
   B^{-1} = -\frac{B}{|B|^2}, \qquad T^{-1} = -\frac{1}{t} * \mathbf{e}_{123}, \qquad
   R^{-1} = \frac{\tilde{R}}{|R|^2}

Taught in :doc:`bootstrap-projection-from-product`, :doc:`dual-3d`, and :doc:`frames-qr`.

The dot product
---------------

.. math::

   \text{in } \mathcal{G}_n: &\quad A \cdot B = \sum_{r, s \geq 1}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{|r - s|}
   \quad \text{(a scalar part contributes } 0\text{)} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0
   = a_1 * b_1 + a_2 * b_2 + a_3 * b_3 \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{a}} \cdot B
   = \langle \vec{\mathbf{a}} * B \rangle_1 \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \cdot B
   = (-a_2 * B_{12} - a_3 * B_{13}) * \vec{\mathbf{e}}_1
   + (a_1 * B_{12} - a_3 * B_{23}) * \vec{\mathbf{e}}_2 \\
   &\quad \qquad + (a_1 * B_{13} + a_2 * B_{23}) * \vec{\mathbf{e}}_3

Taught in :doc:`projection-rejection-3d` and :doc:`dual-3d`.

The wedge product
-----------------

.. math::

   \text{in } \mathcal{G}_n: &\quad A \wedge B = \sum_{r, s}
   \langle \langle A \rangle_r * \langle B \rangle_s \rangle_{r + s} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2
   = (a_1 * b_2 - a_2 * b_1) * \mathbf{e}_{12} + (a_1 * b_3 - a_3 * b_1) * \mathbf{e}_{13} \\
   &\quad \qquad + (a_2 * b_3 - a_3 * b_2) * \mathbf{e}_{23} \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{a}} \wedge B
   = \langle \vec{\mathbf{a}} * B \rangle_3
   = (a_1 * B_{23} - a_2 * B_{13} + a_3 * B_{12}) * \mathbf{e}_{123} \\
   \text{three vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}
   = \det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}) * \mathbf{e}_{123}

Taught in :doc:`projection-rejection-3d`, :doc:`dual-3d`, and :doc:`proof-reciprocal-frame`.

The cross product
-----------------

.. math::

   \text{vectors}: &\quad \vec{\mathbf{a}} \times \vec{\mathbf{b}}
   = (\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) * I^{-1} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \times \vec{\mathbf{b}}
   = (a_2 * b_3 - a_3 * b_2) * \vec{\mathbf{e}}_1
   - (a_1 * b_3 - a_3 * b_1) * \vec{\mathbf{e}}_2
   + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_3

Taught in :doc:`dual-3d`, equation :eq:`eq-dual-of-plane` and :doc:`proof-cross`.

Angle, area, volume and the unit bivector
-----------------------------------------

.. math::

   \text{vectors}: &\quad \cos(\theta)
   = \frac{\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad |\sin(\theta)|
   = \frac{|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|}{|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|},
   \qquad \text{area} = |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}| \\
   \text{coordinates}: &\quad \text{area}
   = \sqrt{(a_1 * b_2 - a_2 * b_1)^2 + (a_1 * b_3 - a_3 * b_1)^2 + (a_2 * b_3 - a_3 * b_2)^2} \\
   \text{three vectors}: &\quad \text{volume}
   = |\vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}|
   = |\det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})| \\
   \text{coordinates}: &\quad \det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})
   = c_1 * (a_2 * b_3 - a_3 * b_2) - c_2 * (a_1 * b_3 - a_3 * b_1) \\
   &\quad \qquad + c_3 * (a_1 * b_2 - a_2 * b_1) \\
   \text{the unit bivector}: &\quad i(\vec{\mathbf{a}}, \vec{\mathbf{b}})
   = \frac{\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}}{|\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}|},
   \qquad i * i = -1

Taught in :doc:`three-dimensions`, :doc:`dual-3d`, and :doc:`blade-square-sign`.

Projection and rejection
------------------------

.. math::

   \text{in } \mathcal{G}_n \text{, onto a blade } B: &\quad
   \operatorname{proj}_{B}(A) = (A \cdot B) * B^{-1}, \qquad
   \operatorname{rej}_{B}(A) = (A \wedge B) * B^{-1} \\
   \text{onto a vector}: &\quad \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \frac{\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}}{|\vec{\mathbf{a}}|^2} * \vec{\mathbf{a}},
   \qquad \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \vec{\mathbf{b}} - \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{onto a plane}: &\quad \operatorname{proj}_{B}(\vec{\mathbf{v}})
   = (\vec{\mathbf{v}} \cdot B) * B^{-1}, \qquad
   \operatorname{rej}_{B}(\vec{\mathbf{v}}) = (\vec{\mathbf{v}} \wedge B) * B^{-1} \\
   \text{onto } \mathbf{e}_{12}: &\quad \operatorname{proj}_{\mathbf{e}_{12}}(\vec{\mathbf{v}})
   = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2, \qquad
   \operatorname{rej}_{\mathbf{e}_{12}}(\vec{\mathbf{v}}) = v_3 * \vec{\mathbf{e}}_3

Taught in :doc:`projection-rejection-3d` and :doc:`proof-projection-3d`.

Reflection
----------

.. math::

   \text{in } \mathcal{G}_n: &\quad \operatorname{ref}_{B}(A)
   = \operatorname{proj}_{B}(A) - \operatorname{rej}_{B}(A) \\
   \text{in a line}: &\quad \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
   = \vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1}
   = \frac{2 * (\vec{\mathbf{a}} \cdot \vec{\mathbf{b}})}{|\vec{\mathbf{b}}|^2}
   * \vec{\mathbf{b}} - \vec{\mathbf{a}} \\
   \text{in a plane}: &\quad \operatorname{ref}_{B}(\vec{\mathbf{v}})
   = -B * \vec{\mathbf{v}} * B^{-1} \\
   \text{in } \mathbf{e}_{12}: &\quad \operatorname{ref}_{\mathbf{e}_{12}}(\vec{\mathbf{v}})
   = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2 - v_3 * \vec{\mathbf{e}}_3

Taught in :doc:`reflection-3d`, equation :eq:`eq-reflect-plane` and :doc:`reflection`, equation
:eq:`eq-reflect-sandwich`.

Rotation
--------

By an angle :math:`\theta` in the plane of a unit bivector :math:`i`, turning
:math:`\vec{\mathbf{a}}` toward :math:`\vec{\mathbf{b}}` when
:math:`i = i(\vec{\mathbf{a}}, \vec{\mathbf{b}})`:

.. math::

   \text{a rotor}: &\quad \vec{\mathbf{v}} \mapsto R * \vec{\mathbf{v}} * \tilde{R}, \qquad
   R = \cos(\theta / 2) - \sin(\theta / 2) * i \\
   \text{in } \mathbf{e}_{12}: &\quad \vec{\mathbf{v}} \mapsto
   (v_1 * \cos(\theta) - v_2 * \sin(\theta)) * \vec{\mathbf{e}}_1
   + (v_1 * \sin(\theta) + v_2 * \cos(\theta)) * \vec{\mathbf{e}}_2 + v_3 * \vec{\mathbf{e}}_3

From :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`, in their plane:

.. math::

   \text{a versor}: &\quad R_{\vec{\mathbf{a}}}^{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = R * \vec{\mathbf{v}} * R^{-1}, \qquad
   R = \vec{\mathbf{b}} * \vec{\mathbf{a}} + |\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|

Taught in :doc:`rotation-from-vectors`, :doc:`bootstrap-rotation-from-product`, equation
:eq:`eq-bootstrap-rotation-sandwich`, and :doc:`blade-square-sign`.

The dual
--------

.. math::

   \text{in } \mathcal{G}_n: &\quad A^{*} = A * I^{-1} \\
   \mathcal{G}_3: &\quad I = \mathbf{e}_{123}, \qquad I^{-1} = -\mathbf{e}_{123} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}}^{*} = -a_3 * \mathbf{e}_{12}
   + a_2 * \mathbf{e}_{13} - a_1 * \mathbf{e}_{23} \\
   &\quad B^{*} = B_{23} * \vec{\mathbf{e}}_1 - B_{13} * \vec{\mathbf{e}}_2
   + B_{12} * \vec{\mathbf{e}}_3, \qquad T^{*} = t

Taught in :doc:`dual-3d`, equation :eq:`eq-dual-of-plane`.

Scaling and translation
-----------------------

.. math::

   \text{uniform scale}: &\quad S_m(\vec{\mathbf{v}}) = m * \vec{\mathbf{v}}
   = m * v_1 * \vec{\mathbf{e}}_1 + m * v_2 * \vec{\mathbf{e}}_2 + m * v_3 * \vec{\mathbf{e}}_3 \\
   \text{scale each axis}: &\quad \vec{\mathbf{v}} \mapsto
   m_1 * v_1 * \vec{\mathbf{e}}_1 + m_2 * v_2 * \vec{\mathbf{e}}_2
   + m_3 * v_3 * \vec{\mathbf{e}}_3 \\
   \text{translation}: &\quad T_{\vec{\mathbf{b}}}(\vec{\mathbf{v}})
   = \vec{\mathbf{v}} + \vec{\mathbf{b}}
   = (v_1 + b_1) * \vec{\mathbf{e}}_1 + (v_2 + b_2) * \vec{\mathbf{e}}_2
   + (v_3 + b_3) * \vec{\mathbf{e}}_3

Taught in :doc:`one-dimension`, equation :eq:`eq-mx-plus-b` and :doc:`vector-addition`.

The reciprocal frame
--------------------

For a frame :math:`\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}` (three vectors not in
one plane), the reciprocal frame :math:`\vec{\mathbf{a}}^1, \vec{\mathbf{b}}^1,
\vec{\mathbf{c}}^1` reads coordinates off the frame: each reciprocal vector has dot product
:math:`1` with its own frame vector and :math:`0` with the other two.

.. math::

   \text{the frame}: &\quad \vec{\mathbf{a}}^1
   = (\vec{\mathbf{b}} \wedge \vec{\mathbf{c}}) * V^{-1}, \qquad
   \vec{\mathbf{b}}^1 = -(\vec{\mathbf{a}} \wedge \vec{\mathbf{c}}) * V^{-1}, \qquad
   \vec{\mathbf{c}}^1 = (\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) * V^{-1}, \\
   &\quad V = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}}^1
   = \frac{\vec{\mathbf{b}} \times \vec{\mathbf{c}}}
   {\det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})}, \qquad
   \vec{\mathbf{b}}^1 = \frac{\vec{\mathbf{c}} \times \vec{\mathbf{a}}}
   {\det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})}, \qquad
   \vec{\mathbf{c}}^1 = \frac{\vec{\mathbf{a}} \times \vec{\mathbf{b}}}
   {\det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})}

Taught in :doc:`frames-qr` and :doc:`proof-reciprocal-frame`.

Also in gacalc
--------------

These are in the library but not taught in the book; each links to its reference entry.

.. math::

   \text{even and odd parts}: &\quad A^{+} = A_0 + B, \qquad A^{-} = \vec{\mathbf{a}} + T \\
   \text{the exponential}: &\quad e^{-i * \theta / 2}
   = \cos(\theta / 2) - \sin(\theta / 2) * i \quad \text{(the rotor above)} \\
   \text{the scalar product}: &\quad \langle A * B \rangle_0 \\
   \text{contractions}: &\quad A \rfloor B
   = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{m - k}, \qquad
   A \lfloor B = \langle \langle A \rangle_k * \langle B \rangle_m \rangle_{k - m}

See :py:meth:`~gacalc.base.MultiVectorBase.even_part`,
:py:meth:`~gacalc.base.MultiVectorBase.odd_part`, :py:meth:`~gacalc.base.MultiVectorBase.exp`,
:py:meth:`~gacalc.base.MultiVectorBase.scalar_product`,
:py:meth:`~gacalc.base.MultiVectorBase.left_contraction`, and
:py:meth:`~gacalc.base.MultiVectorBase.right_contraction`.
