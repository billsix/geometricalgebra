..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

The Dual
========

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

The plane has a unit of area, :math:`I = 1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`, the piece of plane spanned by
:math:`\vec{\mathbf{e}}_1` and :math:`\vec{\mathbf{e}}_2`. It squares to :math:`-1`, so it has an
inverse, :math:`I^{-1} = -1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`. The **dual** of a vector :math:`\vec{\mathbf{a}}` is
the vector times that inverse:

.. math::
   :label: eq-dual

   \vec{\mathbf{a}}^{*} = \vec{\mathbf{a}} * I^{-1}.

For :math:`\vec{\mathbf{a}} = a_1 * \vec{\mathbf{e}}_1 + a_2 * \vec{\mathbf{e}}_2`, multiplying out gives
:math:`\vec{\mathbf{a}}^{*} = a_2 * \vec{\mathbf{e}}_1 - a_1 * \vec{\mathbf{e}}_2`: the same length,
turned a quarter turn clockwise. This chapter proves, by algebra alone, that a vector and its
dual always meet at a right angle.

First, the dual is a vector
---------------------------

The cosine of the angle between two vectors,
:math:`\cos(\theta) = \vec{\mathbf{a}} \cdot \vec{\mathbf{b}} / (|\vec{\mathbf{a}}| * |\vec{\mathbf{b}}|)`, is
defined only for two vectors, neither of length zero. So before asking for an angle, check
that the dual qualifies. Each term of :math:`\vec{\mathbf{a}} * I^{-1}` is a basis vector times
:math:`\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`, and :math:`\vec{\mathbf{e}}_1 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = \vec{\mathbf{e}}_2`,
:math:`\vec{\mathbf{e}}_2 * (\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2) = -\vec{\mathbf{e}}_1`: the result is a vector. Its
length is :math:`|\vec{\mathbf{a}}|`, so it is zero only when :math:`\vec{\mathbf{a}}` is.

The proof
---------

In :doc:`product-from-projection` the dot product of two vectors turned out to be the
plain-number part of their product. Write :math:`\langle X \rangle_0` for the plain-number part
of :math:`X`. Then

.. math::

   \begin{aligned}
   \vec{\mathbf{a}} \cdot (\vec{\mathbf{a}} * I^{-1})
     &= \langle \vec{\mathbf{a}} * (\vec{\mathbf{a}} * I^{-1}) \rangle_0
       && \text{the dot product is the plain-number part} \\
     &= \langle (\vec{\mathbf{a}} * \vec{\mathbf{a}}) * I^{-1} \rangle_0
       && \text{regroup (associativity)} \\
     &= \langle |\vec{\mathbf{a}}|^2 * I^{-1} \rangle_0
       && \text{a vector times itself is its squared length} \\
     &= 0
       && \text{a number times } I^{-1} \text{ is all area.}
   \end{aligned}

The dot product is zero and neither length is, so :math:`\cos(\theta) = 0` and
:math:`\theta = 90°`. Nothing in the argument used coordinates: only associativity, the square of
a vector, and which part of a product is the plain number. That is why it carries over to space
(:doc:`dual-3d`), where the quarter-turn picture does not.

The Lean proofs state the dot-product form as ``dual_perp_dot`` in
``proofs/GacalcProofs/Predicates2D.lean`` and the cosine form as ``dual_perp`` in
``proofs/GacalcProofs/StudentTrigForms.lean``. The companion notebook computes each line of the
proof with symbolic coordinates.

.. toctree::
   :maxdepth: 1

   notebooks/dual
