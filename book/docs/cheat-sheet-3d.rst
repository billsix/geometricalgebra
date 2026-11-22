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
teaches it, and most of those pages come later in the book. The formulas that hold in every
dimension :math:`\mathcal{G}_n` are on :doc:`cheat-sheet-gn`; each chain below starts from that
line and fills in a little more: first the kinds of things multiplied (vectors, a bivector, a
trivector, a versor), then their coordinates. The number of lines differs from operation to
operation.

The names used throughout, by kind. Every name is defined here, even those a formula below does
not use:

.. math::

   \text{scalars}: &\quad m, \ \theta, \ \text{and the coordinates } a_1, a_2, a_3, b_1, b_2,
   b_3, c_1, c_2, c_3, v_1, v_2, v_3 \quad \text{(plain numbers)} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2 + a_3 * \vec{\mathbf{e}}_3, \quad
   \text{and the same for } \vec{\mathbf{b}}, \vec{\mathbf{c}}, \vec{\mathbf{v}} \\
   \text{the unit of volume}: &\quad I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   \text{a bivector}: &\quad B = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}), \\
   &\quad \qquad = (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2
   + (a_1 * b_3 - a_3 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 \\
   &\quad \qquad \quad + (a_2 * b_3 - a_3 * b_2) * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   \text{a trivector}: &\quad V = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}
   = \det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   \text{a versor}: &\quad R = \vec{\mathbf{a}} * \vec{\mathbf{b}} = \langle R \rangle_0 + \langle R \rangle_2,
   \qquad \langle R \rangle_0 = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}, \qquad \langle R \rangle_2 = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{any multivector}: &\quad A = \langle A \rangle_0 + \langle A \rangle_1
   + \langle A \rangle_2 + \langle A \rangle_3

The geometric product
---------------------

.. math::

   \text{basis of } \mathcal{G}_3: &\quad
   (\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j) * (\vec{\mathbf{e}}_i * \vec{\mathbf{e}}_j) = -1 \ (i \neq j), \qquad I * I = -1, \qquad
   I \text{ commutes with every multivector} \\
   \text{vectors}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} * \vec{\mathbf{b}}
   = (a_1 * b_1 + a_2 * b_2 + a_3 * b_3) + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 \\
   &\quad \qquad + (a_1 * b_3 - a_3 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3
   + (a_2 * b_3 - a_3 * b_2) * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3

Taught in :doc:`three-dimensions` and :doc:`blade-square-sign`.

Grade projection
----------------

.. math::

   \text{by kind}: &\quad \langle \vec{\mathbf{a}} \rangle_1 = \vec{\mathbf{a}}, \qquad
   \langle B \rangle_2 = B, \qquad \langle V \rangle_3 = V \\
   \text{a product of vectors}: &\quad \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0 = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}},
   \qquad \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2 = \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} = B

Taught in :doc:`blade-square-sign` and :doc:`levels-of-abstraction`.

The reverse
-----------

.. math::

   \text{by kind}: &\quad \tilde{\vec{\mathbf{a}}} = \vec{\mathbf{a}}, \qquad
   \tilde{B} = -B, \qquad \tilde{V} = -V, \qquad
   \tilde{R} = \langle R \rangle_0 - \langle R \rangle_2 \\
   \text{any multivector}: &\quad \tilde{A} = \langle A \rangle_0 + \langle A \rangle_1
   - \langle A \rangle_2 - \langle A \rangle_3

Taught in :doc:`blade-square-sign` and :doc:`bootstrap-rotation-from-product`.

Magnitude
---------

.. math::

   \text{by kind}: &\quad |\vec{\mathbf{a}}| = \sqrt{a_1^2 + a_2^2 + a_3^2}, \qquad
   |V| = |\det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})| \\
   &\quad |B| = \sqrt{(a_1 * b_2 - a_2 * b_1)^2 + (a_1 * b_3 - a_3 * b_1)^2
   + (a_2 * b_3 - a_3 * b_2)^2} \\
   &\quad |R| = \sqrt{\langle R \rangle_0^2 + |\langle R \rangle_2|^2}

Taught in :doc:`three-dimensions` and :doc:`dual-3d`.

The inverse
-----------

Each kind of value has its own inverse; there is no formula here for every multivector of
:math:`\mathcal{G}_3`.

.. math::

   \text{by kind}: &\quad \vec{\mathbf{a}}^{-1}
   = \frac{\vec{\mathbf{a}}}{|\vec{\mathbf{a}}|^2}, \qquad
   B^{-1} = -\frac{B}{|B|^2}, \qquad V^{-1} = -\frac{V}{|V|^2}, \qquad
   R^{-1} = \frac{\tilde{R}}{|R|^2}

Taught in :doc:`bootstrap-projection-from-product`, :doc:`dual-3d`, and :doc:`frames-qr`.

The dot product
---------------

.. math::

   \text{vectors}: &\quad \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_0
   = a_1 * b_1 + a_2 * b_2 + a_3 * b_3 \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{v}} \cdot B
   = \langle \vec{\mathbf{v}} * B \rangle_1
   = (\vec{\mathbf{v}} \cdot \vec{\mathbf{a}}) * \vec{\mathbf{b}} - (\vec{\mathbf{v}} \cdot \vec{\mathbf{b}}) * \vec{\mathbf{a}}

Taught in :doc:`projection-rejection-3d` and :doc:`dual-3d`.

The wedge product
-----------------

.. math::

   \text{vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = \langle \vec{\mathbf{a}} * \vec{\mathbf{b}} \rangle_2 \\
   \text{coordinates}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}
   = (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 + (a_1 * b_3 - a_3 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 \\
   &\quad \qquad + (a_2 * b_3 - a_3 * b_2) * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   \text{a vector and a bivector}: &\quad \vec{\mathbf{v}} \wedge B
   = \langle \vec{\mathbf{v}} * B \rangle_3
   = \vec{\mathbf{v}} \wedge \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} = \det(\vec{\mathbf{v}}, \vec{\mathbf{a}}, \vec{\mathbf{b}}) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   \text{three vectors}: &\quad \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} \wedge \vec{\mathbf{c}}
   = \det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}}) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3

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

   \text{onto a vector}: &\quad \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \frac{\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}}{|\vec{\mathbf{a}}|^2} * \vec{\mathbf{a}},
   \qquad \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
   = \vec{\mathbf{b}} - \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) \\
   \text{onto a plane}: &\quad \operatorname{proj}_{B}(\vec{\mathbf{v}})
   = (\vec{\mathbf{v}} \cdot B) * B^{-1}, \qquad
   \operatorname{rej}_{B}(\vec{\mathbf{v}}) = (\vec{\mathbf{v}} \wedge B) * B^{-1} \\
   \text{onto the plane of } \vec{\mathbf{e}}_1 \text{ and } \vec{\mathbf{e}}_2: &\quad
   \operatorname{proj}_{\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2}(\vec{\mathbf{v}})
   = v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2, \qquad
   \operatorname{rej}_{\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2}(\vec{\mathbf{v}}) = v_3 * \vec{\mathbf{e}}_3

Taught in :doc:`projection-rejection-3d` and :doc:`proof-projection-3d`.

Reflection
----------

.. math::

   \text{in a line}: &\quad \operatorname{ref}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}})
   = \vec{\mathbf{b}} * \vec{\mathbf{a}} * \vec{\mathbf{b}}^{-1}
   = \frac{2 * (\vec{\mathbf{a}} \cdot \vec{\mathbf{b}})}{|\vec{\mathbf{b}}|^2}
   * \vec{\mathbf{b}} - \vec{\mathbf{a}} \\
   \text{in a plane}: &\quad \operatorname{ref}_{B}(\vec{\mathbf{v}})
   = -B * \vec{\mathbf{v}} * B^{-1} \\
   \text{in the plane of } \vec{\mathbf{e}}_1 \text{ and } \vec{\mathbf{e}}_2: &\quad
   \operatorname{ref}_{\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2}(\vec{\mathbf{v}})
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
   \text{in the plane of } \vec{\mathbf{e}}_1 \text{ and } \vec{\mathbf{e}}_2: &\quad \vec{\mathbf{v}} \mapsto
   (v_1 * \cos(\theta) - v_2 * \sin(\theta)) * \vec{\mathbf{e}}_1 \\
   &\quad \qquad + (v_1 * \sin(\theta) + v_2 * \cos(\theta)) * \vec{\mathbf{e}}_2 + v_3 * \vec{\mathbf{e}}_3

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

   \text{the unit of volume}: &\quad I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3, \qquad I^{-1} = -I \\
   \text{by kind}: &\quad \vec{\mathbf{a}}^{*} = -a_3 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2
   + a_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_3 - a_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3 \\
   &\quad B^{*} = \vec{\mathbf{a}} \times \vec{\mathbf{b}}, \qquad V^{*} = \det(\vec{\mathbf{a}}, \vec{\mathbf{b}}, \vec{\mathbf{c}})

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
   \vec{\mathbf{c}}^1 = (\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}) * V^{-1} \\
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

These are in the library but not taught in the book; each links to its reference entry. The
scalar product and the contractions are on :doc:`cheat-sheet-gn`.

.. math::

   \text{even and odd parts}: &\quad A^{+} = \langle A \rangle_0 + \langle A \rangle_2, \qquad
   A^{-} = \langle A \rangle_1 + \langle A \rangle_3 \\
   \text{the exponential}: &\quad e^{-i * \theta / 2}
   = \cos(\theta / 2) - \sin(\theta / 2) * i \quad \text{(the rotor above)}

See :py:meth:`~gacalc.base.MultiVectorBase.even_part`,
:py:meth:`~gacalc.base.MultiVectorBase.odd_part`, and
:py:meth:`~gacalc.base.MultiVectorBase.exp`.
