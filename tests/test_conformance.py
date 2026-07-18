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

"""Conformance suite: every concrete representation must agree with the general
reference `Gn` on every operation.

Inputs are built in `Gn`, converted to the implementation under test via the
blade-dict interchange, and the result is compared back to the `Gn` result.
Equality goes through the (simplify-aware) `__eq__`, so it is exact even though
the specialized classes do not eagerly simplify.
"""

from itertools import chain, combinations

import pytest
import sympy

import gacalc.g1 as g1mod
import gacalc.g2 as g2mod
import gacalc.g3 as g3mod
import gacalc.gn as gn
from gacalc.base import Coef, MultiVectorBase
from gacalc.g1 import G1
from gacalc.g2 import G2
from gacalc.g3 import G3
from gacalc.gn import Gn
from gacalc.transforms import projection_rotation

SPECIALIZED = {1: G1, 2: G2, 3: G3}
MODULES = {1: g1mod, 2: g2mod, 3: g3mod}

# Every (dimension, implementation) pair, including Gn itself as a sanity check.
CASES = [(n, cls) for n in (1, 2, 3) for cls in (Gn, SPECIALIZED[n])]


def to(cls: type[MultiVectorBase], g: Gn):
    """Convert a Gn multivector into representation ``cls``.

    Deliberately unannotated return: callers invoke dimension-defaulting methods
    like ``dual()`` / ``unit_pseudoscalar()`` on the result, which only the
    concrete specialized classes provide (the abstract ``MultiVectorBase`` requires
    an explicit ``n``).  Leaving the return inferred keeps that gradual, matching
    the parametrized ``cls`` params these tests also leave unannotated.
    """
    return cls.from_blade_dict(g.to_blade_dict())


def blades(n: int) -> list[tuple[int, ...]]:
    idx = range(1, n + 1)
    return list(chain.from_iterable(combinations(idx, r) for r in range(n + 1)))


def field_name(b: tuple[int, ...]) -> str:
    return "scalar" if b == () else "e_" + "".join(str(i) for i in b)


def full(n: int, base: int) -> Gn:
    """A dense multivector with distinct nonzero integer coefficients on every blade."""
    return Gn.from_blade_dict({b: base + i + 1 for i, b in enumerate(blades(n))})


def vec(n: int, base: int) -> Gn:
    """A grade-1 vector with distinct nonzero integer coefficients."""
    return Gn.from_blade_dict({(i,): base + i for i in range(1, n + 1)})


def scalar_eq(a: Coef, b: Coef) -> bool:
    return sympy.simplify(sympy.sympify(a) - sympy.sympify(b)) == 0


# --------------------------------------------------------------------------
# the geometric product, derived directly from the symbolic Gn product
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", [(1, G1), (2, G2)])
def test_symbolic_product_matches_gn(n: int, cls) -> None:
    a = Gn.symbolic_multivector(n, "a")
    b = Gn.symbolic_multivector(n, "b")
    assert to(cls, a) * to(cls, b) == a * b


def test_symbolic_vector_product_3d() -> None:
    # full symbolic 𝒢₃ product is intentionally slow on Gn; vectors stay cheap
    a = Gn.symbolic_multivector(3, "a").r_vector_part(1)
    b = Gn.symbolic_multivector(3, "b").r_vector_part(1)
    assert to(G3, a) * to(G3, b) == a * b


@pytest.mark.parametrize("n,cls", CASES)
def test_geometric_product(n: int, cls) -> None:
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a) * to(cls, b) == a * b


# --------------------------------------------------------------------------
# linear structure
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_add_sub_neg(n: int, cls) -> None:
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a) + to(cls, b) == a + b
    assert to(cls, a) - to(cls, b) == a - b
    assert -to(cls, a) == -a


@pytest.mark.parametrize("n,cls", CASES)
def test_scalar_multiplication(n: int, cls) -> None:
    a = full(n, 0)
    assert 3 * to(cls, a) == 3 * a
    assert to(cls, a) * 3 == a * 3


# --------------------------------------------------------------------------
# grade operations
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_r_vector_part_and_scalar_part(n: int, cls) -> None:
    a = full(n, 0)
    for r in range(n + 1):
        assert to(cls, a).r_vector_part(r) == a.r_vector_part(r)
    assert scalar_eq(to(cls, a).scalar_part(), a.scalar_part())
    assert sorted(to(cls, a).grades()) == sorted(a.grades())


@pytest.mark.parametrize("n,cls", CASES)
def test_even_odd_part(n: int, cls) -> None:
    a = full(n, 0)
    assert to(cls, a).even_part() == a.even_part()
    assert to(cls, a).odd_part() == a.odd_part()


@pytest.mark.parametrize("n,cls", CASES)
def test_reverse(n: int, cls) -> None:
    a = full(n, 0)
    assert to(cls, a).reverse() == a.reverse()


@pytest.mark.parametrize("n,cls", CASES)
def test_dual(n: int, cls) -> None:
    a = full(n, 0)
    assert to(cls, a).dual(n) == a.dual(n)


# --------------------------------------------------------------------------
# products / norms
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_inner_outer_product(n: int, cls) -> None:
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a).inner_product(to(cls, b)) == a.inner_product(b)
    assert to(cls, a).outer_product(to(cls, b)) == a.outer_product(b)


@pytest.mark.parametrize("n,cls", CASES)
def test_dot_wedge_vectors(n: int, cls) -> None:
    a, b = vec(n, 0), vec(n, 10)
    assert to(cls, a).dot(to(cls, b)) == a.dot(b)
    assert to(cls, a).wedge(to(cls, b)) == a.wedge(b)
    assert (to(cls, a) ^ to(cls, b)) == (a ^ b)


@pytest.mark.parametrize("n,cls", CASES)
def test_magnitude_squared_and_inverse(n: int, cls) -> None:
    a = vec(n, 0)
    assert scalar_eq(to(cls, a).magnitude_squared(), a.magnitude_squared())
    assert to(cls, a).inverse() == a.inverse()


# --------------------------------------------------------------------------
# geometric transformations (defined on vectors)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_project_reject(n: int, cls) -> None:
    a, b = vec(n, 0), vec(n, 10)
    assert cls.project(to(cls, b))(to(cls, a)) == Gn.project(b)(a)
    assert cls.reject(to(cls, b))(to(cls, a)) == Gn.reject(b)(a)
    # the parts reconstruct the original vector
    parallel: MultiVectorBase = cls.project(to(cls, b))(to(cls, a))
    perp: MultiVectorBase = cls.reject(to(cls, b))(to(cls, a))
    assert parallel + perp == to(cls, a)


@pytest.mark.parametrize("n,cls", CASES)
def test_reflect(n: int, cls) -> None:
    a, b = vec(n, 0), vec(n, 10)
    assert cls.reflect(to(cls, b))(to(cls, a)) == Gn.reflect(b)(a)


@pytest.mark.parametrize("n,cls", [(n, cls) for (n, cls) in CASES if n >= 2])
def test_rotate(n: int, cls) -> None:
    a = vec(n, 0)
    got = projection_rotation(from_vector=to(cls, gn.e_1), to_vector=to(cls, gn.e_2))(
        to(cls, a)
    )
    assert got == projection_rotation(from_vector=gn.e_1, to_vector=gn.e_2)(a)


@pytest.mark.parametrize("n,cls", CASES)
def test_coefficient_readback(n: int, cls) -> None:
    # coefficient(blade) reads each blade's stored coefficient, and summing
    # coefficient * blade over the basis reconstructs the value (decomposition)
    g = full(n, 0)
    x: MultiVectorBase = to(cls, g)
    coefs = g.to_blade_dict()
    recon: MultiVectorBase = cls.zero()
    for b in blades(n):
        unit: MultiVectorBase = cls.from_blade_dict({b: 1})
        assert scalar_eq(x.coefficient(unit), coefs.get(b, 0))
        recon = recon + x.coefficient(unit) * unit
    assert recon == x


# --------------------------------------------------------------------------
# representation invariants
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_result_type_is_preserved(n: int, cls) -> None:
    a, b = full(n, 0), full(n, 10)
    assert type(to(cls, a) * to(cls, b)) is cls
    assert type(to(cls, a).reverse()) is cls
    assert type(to(cls, a).dual(n)) is cls
    assert type(to(cls, a) + to(cls, b)) is cls


@pytest.mark.parametrize("n,cls", [(1, G1), (2, G2), (3, G3)])
def test_mixing_with_gn_coerces_to_gn(n: int, cls) -> None:
    a, b = full(n, 0), full(n, 10)
    mixed = to(cls, a) * b  # specialized * Gn
    assert isinstance(mixed, Gn)
    assert mixed == a * b


@pytest.mark.parametrize("n,cls", [(1, G1), (2, G2), (3, G3)])
def test_basis_constants(n: int, cls) -> None:
    mod = MODULES[n]
    assert type(mod.zero) is cls
    assert type(mod.one) is cls
    for b in blades(n):
        if b == ():
            continue
        const = getattr(mod, field_name(b))
        assert type(const) is cls
        assert const == Gn.from_blade_dict({b: 1})
    # building from the module's own constants stays in the specialized type
    built = 3 * mod.one
    for i, b in enumerate([x for x in blades(n) if len(x) == 1]):
        built = built + (i + 2) * getattr(mod, field_name(b))
    assert type(built) is cls


@pytest.mark.parametrize("n,cls", [(1, G1), (2, G2), (3, G3)])
def test_implicit_dimension_methods(n: int, cls) -> None:
    a = full(n, 0)
    # n defaults to the algebra's own dimension
    assert to(cls, a).dual() == a.dual(n)
    assert to(cls, a).dual() == to(cls, a).dual(n)
    assert cls.unit_pseudoscalar() == Gn.unit_pseudoscalar(n)
    assert cls.unit_pseudoscalar_squared() == Gn.unit_pseudoscalar_squared(n)
    assert len(list(cls.bases())) == 2**n
    assert type(cls.symbolic_multivector(prefix="z")) is cls


def test_is_close_numeric() -> None:
    a = G2.from_blade_dict({(1,): 3.0, (2,): 4.0})
    b = G2.from_blade_dict({(1,): 3.0 + 1e-9, (2,): 4.0})
    assert a.is_close(b)
    assert not a.is_close(G2.from_blade_dict({(1,): 3.5, (2,): 4.0}))


@pytest.mark.parametrize("cls", [G1, G2, G3])
def test_simplified_and_expanded_form(cls) -> None:
    # On the lazy (specialized/graded) classes, expanded()/simplified() change the
    # coefficient *form*: distribute, and collapse to lowest terms.  (Gn eager-
    # simplifies in __post_init__, so it re-canonicalizes -- value test below.)
    a, b, t = sympy.symbols("a b t")
    v = cls.from_blade_dict({(1,): (a + b) ** 2})
    assert v.expanded().to_blade_dict()[(1,)] == a**2 + 2 * a * b + b**2
    w = cls.from_blade_dict({(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2})
    assert w.simplified().to_blade_dict()[(1,)] == 1


def test_expand_numerators_dict_for_display() -> None:
    # nbplotutils._expand_numerators_dict (used by show_mult): expand each
    # coefficient's NUMERATOR, keep its denominator factored, and -- crucially --
    # do NOT rebuild the multivector, so the distributed form survives Gn's eager
    # __post_init__ simplify (which would otherwise re-factor it, e.g. back to
    # a0*(b0 + c0) -- the regression this fixed).
    from gacalc.nbplotutils import _expand_numerators_dict

    a, b, c = sympy.symbols("a b c")
    # survives Gn eager-simplify: a factored product is distributed for display
    v = Gn.from_blade_dict({(1,): a * (b + c)})
    assert _expand_numerators_dict(v)[(1,)] == a * b + a * c
    # numerator expanded, radical denominator left factored (not rationalized)
    den = sympy.sqrt(a**2 + b**2)
    w = Gn.from_blade_dict({(1,): (a + b) ** 2 / den})
    num, d = sympy.fraction(sympy.together(_expand_numerators_dict(w)[(1,)]))
    assert num == a**2 + 2 * a * b + b**2
    assert d == den


def _same_value(x: MultiVectorBase, y: MultiVectorBase) -> bool:
    # Value equality independent of coefficient *form* (Gn's __eq__ is structural,
    # so (a+b)**2 vs a**2+2ab+b**2 would compare unequal there).
    dx, dy = x.to_blade_dict(), y.to_blade_dict()
    return all(
        sympy.simplify(sympy.sympify(dx.get(k, 0)) - sympy.sympify(dy.get(k, 0))) == 0
        for k in set(dx) | set(dy)
    )


@pytest.mark.parametrize("n,cls", CASES)
def test_simplified_and_expanded_preserve_value(n: int, cls) -> None:
    # Same value on every representation -- only the coefficient form may change.
    a, b, t = sympy.symbols("a b t")
    v = cls.from_blade_dict({(1,): (a + b) ** 2})
    assert _same_value(v.expanded(), v)
    assert _same_value(v.simplified(), v)
    w = cls.from_blade_dict({(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2})
    assert _same_value(w.simplified(), w)
    assert w.simplified().to_blade_dict()[(1,)] == 1


def test_project_vector_onto_bivector_2d() -> None:
    # the bivector e_12 spans the whole plane, so any 2D vector projects to itself
    v = 3 * G2.basis_vector(1) + 4 * G2.basis_vector(2)
    assert G2.project(onto=G2.e_12)(v) == v
    # Gn reference: same result onto the e_1 e_2 bivector
    gv = 3 * gn.e_1 + 4 * gn.e_2
    assert Gn.project(onto=gn.e_1 * gn.e_2)(gv) == gv


def test_project_vector_onto_bivector_and_trivector_3d() -> None:
    e1, e2, e3 = (G3.basis_vector(i) for i in (1, 2, 3))
    # onto the e_12 plane: keep the in-plane part, drop the perpendicular e_3
    assert G3.project(onto=G3.e_12)(e1 + e3) == e1
    assert G3.project(onto=G3.e_12)(e3) == G3.zero()
    # onto the trivector e_123 (all of 3-space): a vector projects to itself
    assert G3.project(onto=G3.e_123)(e1 + e3) == e1 + e3


def test_repr_latex_shows_simplified() -> None:
    # the lazy classes don't eager-simplify, but the display (_repr_latex_) renders
    # the simplified coefficient (sin^2 + cos^2 -> 1), not the raw stored form
    t = sympy.symbols("t")
    v = G2.from_blade_dict({(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2})
    assert "sin" in str(v.to_blade_dict()[(1,)])  # stored coefficient is still raw
    latex = v._repr_latex_()
    assert "sin" not in latex and "cos" not in latex  # displayed form is simplified
