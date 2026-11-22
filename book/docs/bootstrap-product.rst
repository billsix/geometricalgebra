..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Step 4: The Geometric Product, from Projection
==============================================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

Measure :math:`\vec{\mathbf{b}}` against :math:`\vec{\mathbf{a}}` with Step 2: rotate :math:`\vec{\mathbf{a}}` onto the
x-axis and read off where :math:`\vec{\mathbf{b}}` lands. By
:eq:`eq-bootstrap-projection-coordinates`, that is

.. math::

   x = \frac{a_1 * b_1 + a_2 * b_2}{|\vec{\mathbf{a}}|}, \qquad
   y = \frac{a_1 * b_2 - a_2 * b_1}{|\vec{\mathbf{a}}|},

the signed lengths of :math:`\vec{\mathbf{b}}`'s projection onto :math:`\vec{\mathbf{a}}` (along) and of its
rejection (across). Both have :math:`|\vec{\mathbf{a}}|` underneath. Multiply it back in:

.. math::

   |\vec{\mathbf{a}}| * x = a_1 * b_1 + a_2 * b_2, \qquad |\vec{\mathbf{a}}| * y = a_1 * b_2 - a_2 * b_1.

The first is :math:`|\vec{\mathbf{a}}|` times the length of :math:`\vec{\mathbf{b}}`'s shadow on
:math:`\vec{\mathbf{a}}`. The second is :math:`|\vec{\mathbf{a}}|` times :math:`\vec{\mathbf{b}}`'s height above
:math:`\vec{\mathbf{a}}`: the signed area of the parallelogram the two vectors span.

.. figure:: _static/epix/boot-product.*
   :align: center
   :alt: a and b spanning a parallelogram; x along a in green, y across a in blue

The definition
--------------

Keep both numbers in one object. The along-part goes in as a plain number; the
across-part is an area in the plane, so it carries the unit of area :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`:

.. math::
   :label: eq-bootstrap-product

   \vec{\mathbf{a}} * \vec{\mathbf{b}} = |\vec{\mathbf{a}}| * (x + y * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
     = (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2.

The plain-number part is the **dot product** :math:`\vec{\mathbf{a}} \cdot \vec{\mathbf{b}}` and the
:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` part is the **wedge** :math:`\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}`, so

.. math::

   \vec{\mathbf{a}} * \vec{\mathbf{b}} = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} + \vec{\mathbf{a}} \wedge \vec{\mathbf{b}}.

It is the product of the multiplication rules
----------------------------------------------

Multiply :math:`(a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2) * (b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2)` out term by term with
:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 = \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 = 1`, :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = \mathbf{e}_{12}` and
:math:`\vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 = -\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`:

.. math::

   \begin{aligned}
   (a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2) * (b_1 * \vec{\mathbf{e}}_1 + b_2 * \vec{\mathbf{e}}_2)
     &= a_1 * b_1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 + a_1 * b_2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 + a_2 * b_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_1 + a_2 * b_2 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_2 \\
     &= (a_1 * b_1 + a_2 * b_2) + (a_1 * b_2 - a_2 * b_1) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2,
   \end{aligned}

which is :eq:`eq-bootstrap-product`. The product defined from projection and the product
of the multiplication rules are the same product. Two consequences the next steps use:

- **A vector times itself is its length squared:**
  :math:`\vec{\mathbf{b}} * \vec{\mathbf{b}} = b_1^2 + b_2^2 = |\vec{\mathbf{b}}|^2`, a plain number (the area part
  is :math:`b_1 * b_2 - b_2 * b_1 = 0`).
- **The product of two unit vectors is the cosine and sine of the angle between them.**
  Dividing :eq:`eq-bootstrap-product` by :math:`|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|` and reading off
  :eq:`eq-bootstrap-from-projection-cos-sin`,

  .. math::
     :label: eq-bootstrap-unit-product

     \hat{\mathbf{a}} * \hat{\mathbf{b}} = \cos(\theta) + \sin(\theta) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2,
     \qquad \hat{\mathbf{a}} = \frac{\vec{\mathbf{a}}}{|\vec{\mathbf{a}}|}, \quad \hat{\mathbf{b}} = \frac{\vec{\mathbf{b}}}{|\vec{\mathbf{b}}|},

  with :math:`\theta` the angle from :math:`\vec{\mathbf{a}}` to :math:`\vec{\mathbf{b}}`.

The quarter turn is a product
-----------------------------

Step 1's base case :eq:`eq-bootstrap-quarter-turn` has a second form. Multiply out, with
:math:`\vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = \vec{\mathbf{e}}_2` and :math:`\vec{\mathbf{e}}_2 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -\vec{\mathbf{e}}_1`:

.. math::
   :label: eq-bootstrap-quarter-turn-product

   \vec{\mathbf{r}}(\vec{\mathbf{v}}; \pi/2) = \vec{\mathbf{v}} * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)
     = (v_1 * \vec{\mathbf{e}}_1 + v_2 * \vec{\mathbf{e}}_2) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 = -v_2 * \vec{\mathbf{e}}_1 + v_1 * \vec{\mathbf{e}}_2.

Multiplying by :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` on the right turns a vector a quarter turn. :math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` is
the unit bivector, also called :math:`i`.

Dot and wedge through projection and rejection
----------------------------------------------

The numbers :math:`x` and :math:`y` were the signed lengths of :math:`\vec{\mathbf{b}}`'s projection
onto :math:`\vec{\mathbf{a}}` and of its rejection. So the two parts of the product are
:math:`\vec{\mathbf{a}}` times each of those pieces. With Step 2's formula
:eq:`eq-bootstrap-projection`, :math:`\operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) = x * \vec{\mathbf{a}} / |\vec{\mathbf{a}}|`,
and :math:`\vec{\mathbf{a}} * \vec{\mathbf{a}} = |\vec{\mathbf{a}}|^2`:

.. math::

   \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
     = \frac{x}{|\vec{\mathbf{a}}|} * \vec{\mathbf{a}} * \vec{\mathbf{a}} = |\vec{\mathbf{a}}| * x.

With Step 2's formula :eq:`eq-bootstrap-rejection`,
:math:`\operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}) = y * \vec{\mathbf{r}}(\vec{\mathbf{a}}; \pi/2) / |\vec{\mathbf{a}}|`, and
:math:`\vec{\mathbf{a}} * \vec{\mathbf{r}}(\vec{\mathbf{a}}; \pi/2) = \vec{\mathbf{a}} * \vec{\mathbf{a}} * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = |\vec{\mathbf{a}}|^2 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`
by :eq:`eq-bootstrap-quarter-turn-product`:

.. math::

   \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
     = \frac{y}{|\vec{\mathbf{a}}|} * \vec{\mathbf{a}} * \vec{\mathbf{r}}(\vec{\mathbf{a}}; \pi/2) = |\vec{\mathbf{a}}| * y * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2.

These are the two parts of :eq:`eq-bootstrap-product`, so

.. math::
   :label: eq-bootstrap-dot-wedge-proj-rej

   \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}), \qquad
   \vec{\mathbf{a}} \wedge \vec{\mathbf{b}} = \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}), \qquad
   \vec{\mathbf{a}} * \vec{\mathbf{b}} = \vec{\mathbf{a}} * \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}})
     + \vec{\mathbf{a}} * \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{b}}).

A vector times a vector along it is a plain number; times a vector across it, a pure area.
These are facts about the product, shown here for vectors. Projection and rejection apply to
more than vectors, and later chapters replace these simple forms with general ones.

Measuring the other way, :math:`\vec{\mathbf{a}}` against :math:`\vec{\mathbf{b}}`, exchanges the names. The
dot part keeps its value and the wedge part changes sign, because
:math:`a_1 * b_1 + a_2 * b_2` is unchanged by the swap and :math:`a_1 * b_2 - a_2 * b_1` is negated:

.. math::
   :label: eq-bootstrap-dot-wedge-mirror

   \vec{\mathbf{b}} * \operatorname{proj}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}}, \qquad
   \vec{\mathbf{b}} * \operatorname{rej}_{\vec{\mathbf{b}}}(\vec{\mathbf{a}}) = \vec{\mathbf{b}} \wedge \vec{\mathbf{a}}
     = -(\vec{\mathbf{a}} \wedge \vec{\mathbf{b}}).

The companion notebook works these steps for a set of vectors and draws each one; a
reader running it can change the vectors and rerun. It checks :eq:`eq-bootstrap-product`
against gacalc's product, the split into dot and wedge,
:eq:`eq-bootstrap-quarter-turn-product`, :eq:`eq-bootstrap-unit-product`,
:eq:`eq-bootstrap-dot-wedge-proj-rej` and :eq:`eq-bootstrap-dot-wedge-mirror`, for those
vectors and with symbolic coordinates.

Lean: ``mul_eq_magnitude_smul_alignSP`` (:eq:`eq-bootstrap-product`, stated as
:math:`\vec{\mathbf{b}} * \vec{\mathbf{a}} = |\vec{\mathbf{b}}| * (x + y * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2)` with :math:`\vec{\mathbf{a}}` measured in
:math:`\vec{\mathbf{b}}`'s standard position; swap the names for the form above) in
``proofs/GacalcProofs/StandardPosition2D.lean``; ``mul_eq_dot_add_wedge`` in
``proofs/GacalcProofs/G2.lean``; ``uvec_mul_uvec`` (two unit vectors at angles
:math:`\alpha`, :math:`\beta` multiply to :math:`\cos(\beta - \alpha) + \sin(\beta - \alpha) * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`)
in ``proofs/GacalcProofs/Rotation2D.lean``; ``mul_proj_eq_dot``, ``mul_reject_eq_wedge`` and
``mul_eq_mul_proj_add_mul_reject`` (:eq:`eq-bootstrap-dot-wedge-proj-rej`) and
``mul_proj_symm``, ``mul_reject_antisymm`` (:eq:`eq-bootstrap-dot-wedge-mirror`) in
``proofs/GacalcProofs/Bootstrap2D.lean``; ``rot90_eq_mul_e12``
(:eq:`eq-bootstrap-quarter-turn-product`) in ``proofs/GacalcProofs/StandardPosition2D.lean``.

.. toctree::
   :maxdepth: 1

   notebooks/bootstrap-product
