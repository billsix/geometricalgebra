# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

"""Dedicated tests for the blade coefficient dictionary — THE interchange format.

Every representation (``Gn``, ``g1.G``/``g2.G``/``g3.G``, the graded subtypes) converts
to and from ``BladeCoef`` (``dict[Blade, Coef]``), and all shared arithmetic in
``base.py`` routes through it.  Other suites use the interchange incidentally
(conversion helpers); this one pins its *contract*:

- round-trip identity per representation;
- cross-representation conversion preserves coefficients;
- canonical keys (strictly increasing index tuples; ``()`` is the scalar blade);
- readers omit exact-zero coefficients and treat a missing blade as 0 —
  with the eager/lazy split: ``Gn`` simplifies a hidden zero away, the lazy
  classes keep it (structural ``!= 0`` only);
- a graded type's ``from_blade_dict`` keeps ONLY its own blades (foreign keys
  silently dropped — why results must be built via dispatching arithmetic);
- coefficient types survive the round trip (float stays float in the lazy
  classes; ``Gn``'s eager simplify normalizes numbers to sympy).

Non-canonical keys (unsorted or repeated indices) are rejected loudly:
``from_blade_dict`` raises ``ValueError`` in every representation (decision (a)
of the validate-blade-dict-keys task, 2026-07-29 — replacing two divergent
*silent* failure modes: ``Gn`` used to store a ``(2, 1)`` key raw, ``g2.G`` used
to drop it).  ``(2, 1)`` is deliberately NOT read as the signed permutation
``-e1e2``.
"""

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
from gacalc.base import Blade, BladeCoef, MultiVectorBase
from gacalc.gn import Gn

# every concrete representation, with a dense sample value's blade dict
SAMPLES: list[tuple[type[MultiVectorBase], BladeCoef]] = [
    (Gn, {(): 1, (1,): 2, (2,): 3, (1, 2): 4}),
    (g1.G, {(): 1, (1,): 2}),
    (g2.G, {(): 1, (1,): 2, (2,): 3, (1, 2): 4}),
    (
        g3.G,
        {
            (): 1,
            (1,): 2,
            (2,): 3,
            (3,): 4,
            (1, 2): 5,
            (1, 3): 6,
            (2, 3): 7,
            (1, 2, 3): 8,
        },
    ),
    (g2.Scalar, {(): 5}),
    (g2.Vector, {(1,): 2, (2,): 3}),
    (g2.Bivector, {(1, 2): 4}),
    (g2.Rotor, {(): 1, (1, 2): 4}),
    (g3.Vector, {(1,): 2, (2,): 3, (3,): 4}),
    (g3.Bivector, {(1, 2): 5, (1, 3): 6, (2, 3): 7}),
    (g3.Trivector, {(1, 2, 3): 8}),
    (g3.Rotor, {(): 1, (1, 2): 5, (1, 3): 6, (2, 3): 7}),
]


def test_roundtrip_identity() -> None:
    # from_blade_dict(x.to_blade_dict()) == x, and the dict itself round-trips
    # verbatim, for every representation.
    for cls, d in SAMPLES:
        x: MultiVectorBase = cls.from_blade_dict(d)
        assert cls.from_blade_dict(x.to_blade_dict()) == x
        assert x.to_blade_dict() == d


def test_cross_representation_preserves_coefficients() -> None:
    # Gn -> dict -> specialized -> dict -> Gn is the identity on the dict.
    d: BladeCoef = {(): 1, (1,): 2, (2,): 3, (1, 2): 4}
    g: Gn = Gn.from_blade_dict(d)
    specialized: g2.G = g2.G.from_blade_dict(g.to_blade_dict())
    assert specialized.to_blade_dict() == d
    assert Gn.from_blade_dict(specialized.to_blade_dict()) == g


def test_arithmetic_through_interchange_agrees() -> None:
    # the same addition done in Gn and in g3.G produces the same blade dict
    a: BladeCoef = {(1,): 1, (1, 2): 2}
    b: BladeCoef = {(): 5, (1,): 10}
    gn_sum: BladeCoef = (Gn.from_blade_dict(a) + Gn.from_blade_dict(b)).to_blade_dict()
    g3_sum: BladeCoef = (
        g3.G.from_blade_dict(a) + g3.G.from_blade_dict(b)
    ).to_blade_dict()
    assert gn_sum == g3_sum == {(): 5, (1,): 11, (1, 2): 2}


def test_scalar_blade_is_the_empty_tuple() -> None:
    for cls in (Gn, g1.G, g2.G, g3.G):
        assert cls.from_scalar(7).to_blade_dict() == {(): 7}
        assert cls.from_blade_dict({(): 7}).scalar_part() == 7


def test_canonical_keys_are_sorted_index_tuples() -> None:
    # every key any representation ever EMITS is a strictly increasing tuple of
    # basis-vector indices (the writer-side precondition, held by construction)
    for cls in (Gn, g2.G, g3.G):
        n: int = 3 if cls in (Gn, g3.G) else 2
        dense: MultiVectorBase = sum(
            ((i + 1) * b for i, b in enumerate(cls.bases(n))), start=cls.zero()
        )
        blade: Blade
        for blade in (dense * dense).to_blade_dict():
            assert list(blade) == sorted(set(blade))


def test_zero_coefficients_omitted_missing_reads_zero() -> None:
    # readers omit exact zeros; a missing blade reads as 0
    for cls in (Gn, g2.G):
        x: MultiVectorBase = cls.from_blade_dict({(1,): 0, (2,): 3})
        assert x.to_blade_dict() == {(2,): 3}
        assert x.coefficient(cls.basis_vector(1)) == 0


def test_hidden_zero_eager_vs_lazy() -> None:
    # the eager/lazy split, visible through the interchange: Gn simplifies
    # cos^2 + sin^2 - 1 to zero and omits the blade; the lazy g2.G keeps the
    # un-reduced coefficient (only structural != 0 is pruned).  Equality still
    # holds (it is simplify-aware).
    t: sympy.Symbol = sympy.Symbol("t")
    hidden_zero: sympy.Expr = sympy.cos(t) ** 2 + sympy.sin(t) ** 2 - 1
    assert Gn.from_blade_dict({(1,): hidden_zero}).to_blade_dict() == {}
    lazy: g2.G = g2.G.from_blade_dict({(1,): hidden_zero})
    assert lazy.to_blade_dict() == {(1,): hidden_zero}
    assert lazy == g2.G.zero()


def test_graded_from_blade_dict_keeps_only_own_blades() -> None:
    # A graded type's from_blade_dict reads ONLY its own blade keys; anything
    # else is silently dropped.  This is why results carrying a new grade must
    # be built via dispatching arithmetic (e.g. Bivector + scalar -> Rotor),
    # never by from_blade_dict on the operand's type -- the trap exp() documents.
    assert g2.Bivector.from_blade_dict({(): 7, (1, 2): 3}).to_blade_dict() == {
        (1, 2): 3
    }
    assert g3.Vector.from_blade_dict({(1,): 1, (1, 2): 9}).to_blade_dict() == {(1,): 1}
    # the Rotor spans scalar + bivectors, so both survive there
    assert g2.Rotor.from_blade_dict({(): 7, (1, 2): 3}).to_blade_dict() == {
        (): 7,
        (1, 2): 3,
    }


def test_non_canonical_keys_raise() -> None:
    # every representation rejects an unsorted or repeated-index key loudly;
    # (2, 1) is NOT read as the signed permutation -e1e2
    for cls in (Gn, g2.G, g2.Bivector):
        with pytest.raises(ValueError, match="not canonical"):
            cls.from_blade_dict({(2, 1): 5})
        with pytest.raises(ValueError, match="not canonical"):
            cls.from_blade_dict({(1, 1): 5})


def test_coef_types_survive_lazy_roundtrip() -> None:
    # lazy classes hand back exactly what was put in: float stays float, int
    # stays int, sympy stays sympy
    d: BladeCoef = g2.Vector.from_blade_dict({(1,): 1.5, (2,): 2}).to_blade_dict()
    assert type(d[(1,)]) is float and type(d[(2,)]) is int
    sym: BladeCoef = g2.Vector.from_blade_dict(
        {(1,): sympy.Symbol("x")}
    ).to_blade_dict()
    assert isinstance(sym[(1,)], sympy.Expr)
    # Gn eager-simplifies, which normalizes numbers to sympy objects -- value
    # equality holds even though the coefficient TYPE changes
    assert Gn.from_blade_dict({(1,): 1.5}).to_blade_dict()[(1,)] == 1.5
