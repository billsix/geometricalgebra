..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Reflection in Space
===================

.. note::

   Draft. The prose is agent-drafted; the maintainer's voice pass is pending.

In :doc:`reflection` the reflection across the line through :math:`\vec{\mathbf{a}}` was the
projection minus the rejection. Nothing in that recipe needs the plane, so in space it reads the
same:

.. math::

   \operatorname{ref}_{\vec{\mathbf{a}}}(\vec{\mathbf{v}})
     = \operatorname{proj}_{\vec{\mathbf{a}}}(\vec{\mathbf{v}}) - \operatorname{rej}_{\vec{\mathbf{a}}}(\vec{\mathbf{v}})
     = \vec{\mathbf{a}} * \vec{\mathbf{v}} * \vec{\mathbf{a}}^{-1}.

In space that is a half turn about the line, not a mirror. A mirror is a plane.

A mirror is a plane
-------------------

For a plane :math:`B = \vec{\mathbf{p}} \wedge \vec{\mathbf{q}}` the recipe is the same, with the plane in
place of the line: keep the part of :math:`\vec{\mathbf{v}}` in the plane, flip the part sticking out
of it.

.. math::
   :label: eq-reflect-plane

   \operatorname{ref}_{B}(\vec{\mathbf{v}})
     = \operatorname{proj}_{B}(\vec{\mathbf{v}}) - \operatorname{rej}_{B}(\vec{\mathbf{v}}).

The same mirror, from the normal
--------------------------------

The plane's dual :math:`\vec{\mathbf{n}} = B * I^{-1}` is its normal (:doc:`dual-3d`). The part of
:math:`\vec{\mathbf{v}}` sticking out of the plane is the part along the normal, and the part in the
plane is the part across the normal:
:math:`\operatorname{rej}_{B}(\vec{\mathbf{v}}) = \operatorname{proj}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})` and
:math:`\operatorname{proj}_{B}(\vec{\mathbf{v}}) = \operatorname{rej}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})`. So
working from the normal swaps the two roles, and

.. math::

   \operatorname{ref}_{B}(\vec{\mathbf{v}})
     = \operatorname{rej}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}}) - \operatorname{proj}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}})
     = -\operatorname{ref}_{\vec{\mathbf{n}}}(\vec{\mathbf{v}}).

The two routes give the same mirror once the sign is put in: the mirror in the plane is minus the
reflection across its normal. The product says it too. Since :math:`B = \vec{\mathbf{n}} * I` and
:math:`I` commutes with every vector,
:math:`B * \vec{\mathbf{v}} * B^{-1} = \vec{\mathbf{n}} * \vec{\mathbf{v}} * \vec{\mathbf{n}}^{-1}`, and the mirror
is minus either.

The Lean proofs state the reflection across a vector as ``reflectVec_eq``, the plane-versus-normal
identity as ``reflectPlane_eq_neg_reflectVec_dual`` and the length kept by the mirror as
``normSq_reflectPlane``, all in ``proofs/GacalcProofs/Reflect.lean``. The
companion notebook computes each form with symbolic coordinates.

.. toctree::
   :maxdepth: 1

   notebooks/reflection-3d
