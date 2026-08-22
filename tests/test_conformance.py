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

import importlib
from itertools import chain, combinations
from types import ModuleType

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3
import gacalc.gn as gn
from gacalc.base import Blade, BladeCoef, Coef, MultiVectorBase
from gacalc.gn import Gn
from gacalc.transforms import projection_rotation

# g1--g3 are always generated (the dev default); g4/g5 are release-only and exist
# only when generated with GACALC_DIMS=1,2,3,4,5 (make generate-all / dist / the
# full-dim gate).  Include whichever specialized modules are present, so the
# default suite covers g1--g3 and the full-dim gate additionally covers g4/g5.
MODULES: dict[int, ModuleType] = {1: g1, 2: g2, 3: g3}
for _n in (4, 5):
    try:
        MODULES[_n] = importlib.import_module(f"gacalc.g{_n}")
    except ModuleNotFoundError:
        pass

SPECIALIZED = {n: mod.G for n, mod in MODULES.items()}

# Every (dimension, implementation) pair, including Gn itself as a sanity check.
CASES = [(n, cls) for n in sorted(MODULES) for cls in (Gn, SPECIALIZED[n])]


def to(cls: type[MultiVectorBase], g: Gn):
    """Convert a Gn multivector into representation ``cls``.

    Deliberately unannotated return: callers invoke dimension-defaulting methods
    like ``dual()`` / ``unit_pseudoscalar()`` on the result, which only the
    concrete specialized classes provide (the abstract ``MultiVectorBase`` requires
    an explicit ``n``).  Leaving the return inferred keeps that gradual, matching
    the parametrized ``cls`` params these tests also leave unannotated.
    """
    return cls.from_blade_dict(g.to_blade_dict())


def blades(n: int) -> list[Blade]:
    idx: range = range(1, n + 1)
    return list(chain.from_iterable(combinations(idx, r) for r in range(n + 1)))


def field_name(b: Blade) -> str:
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
@pytest.mark.parametrize("n,cls", [(1, g1.G), (2, g2.G)])
def test_symbolic_product_matches_gn(n: int, cls) -> None:
    a: Gn = Gn.symbolic_multivector(n, "a")
    b: Gn = Gn.symbolic_multivector(n, "b")
    assert to(cls, a) * to(cls, b) == a * b


def test_symbolic_vector_product_3d() -> None:
    # full symbolic 𝒢₃ product is intentionally slow on Gn; vectors stay cheap
    a: Gn = Gn.symbolic_multivector(3, "a").r_vector_part(1)
    b: Gn = Gn.symbolic_multivector(3, "b").r_vector_part(1)
    assert to(g3.G, a) * to(g3.G, b) == a * b


@pytest.mark.parametrize("n,cls", CASES)
def test_geometric_product(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a) * to(cls, b) == a * b


# --------------------------------------------------------------------------
# linear structure
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_add_sub_neg(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a) + to(cls, b) == a + b
    assert to(cls, a) - to(cls, b) == a - b
    assert -to(cls, a) == -a


@pytest.mark.parametrize("n,cls", CASES)
def test_scalar_multiplication(n: int, cls) -> None:
    a: Gn = full(n, 0)
    assert 3 * to(cls, a) == 3 * a
    assert to(cls, a) * 3 == a * 3


# --------------------------------------------------------------------------
# grade operations
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_r_vector_part_and_scalar_part(n: int, cls) -> None:
    a: Gn = full(n, 0)
    r: int
    for r in range(n + 1):
        assert to(cls, a).r_vector_part(r) == a.r_vector_part(r)
    assert scalar_eq(to(cls, a).scalar_part(), a.scalar_part())
    assert sorted(to(cls, a).grades()) == sorted(a.grades())


@pytest.mark.parametrize("n,cls", CASES)
def test_even_odd_part(n: int, cls) -> None:
    a: Gn = full(n, 0)
    assert to(cls, a).even_part() == a.even_part()
    assert to(cls, a).odd_part() == a.odd_part()


@pytest.mark.parametrize("n,cls", CASES)
def test_reverse(n: int, cls) -> None:
    a: Gn = full(n, 0)
    assert to(cls, a).reverse() == a.reverse()


@pytest.mark.parametrize("n,cls", CASES)
def test_dual(n: int, cls) -> None:
    a: Gn = full(n, 0)
    assert to(cls, a).dual(n) == a.dual(n)


# --------------------------------------------------------------------------
# products / norms
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_inner_outer_product(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a).inner_product(to(cls, b)) == a.inner_product(b)
    assert to(cls, a).outer_product(to(cls, b)) == a.outer_product(b)


@pytest.mark.parametrize("n,cls", CASES)
def test_left_right_contraction(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    assert to(cls, a).left_contraction(to(cls, b)) == a.left_contraction(b)
    assert to(cls, a).right_contraction(to(cls, b)) == a.right_contraction(b)
    # the ``<`` / ``>`` operators delegate to the named methods
    assert (to(cls, a) < to(cls, b)) == a.left_contraction(b)
    assert (to(cls, a) > to(cls, b)) == a.right_contraction(b)


@pytest.mark.parametrize("n,cls", CASES)
def test_dot_wedge_vectors(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = vec(n, 0), vec(n, 10)
    assert to(cls, a).dot(to(cls, b)) == a.dot(b)
    assert to(cls, a).wedge(to(cls, b)) == a.wedge(b)
    assert (to(cls, a) ^ to(cls, b)) == (a ^ b)


@pytest.mark.parametrize("n,cls", CASES)
def test_magnitude_squared_and_inverse(n: int, cls) -> None:
    a: Gn = vec(n, 0)
    assert scalar_eq(to(cls, a).magnitude_squared(), a.magnitude_squared())
    assert to(cls, a).inverse() == a.inverse()


# --------------------------------------------------------------------------
# geometric transformations (defined on vectors)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,cls", CASES)
def test_project_reject(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = vec(n, 0), vec(n, 10)
    assert cls.project(to(cls, b))(to(cls, a)) == Gn.project(b)(a)
    assert cls.reject(to(cls, b))(to(cls, a)) == Gn.reject(b)(a)
    # the parts reconstruct the original vector
    parallel: MultiVectorBase = cls.project(to(cls, b))(to(cls, a))
    perp: MultiVectorBase = cls.reject(to(cls, b))(to(cls, a))
    assert parallel + perp == to(cls, a)


@pytest.mark.parametrize("n,cls", CASES)
def test_reflect(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = vec(n, 0), vec(n, 10)
    assert cls.reflect(to(cls, b))(to(cls, a)) == Gn.reflect(b)(a)


@pytest.mark.parametrize("n,cls", [(n, cls) for (n, cls) in CASES if n >= 2])
def test_rotate(n: int, cls) -> None:
    a: Gn = vec(n, 0)
    got: MultiVectorBase = projection_rotation(
        from_vector=to(cls, gn.e_1), to_vector=to(cls, gn.e_2)
    )(to(cls, a))
    assert got == projection_rotation(from_vector=gn.e_1, to_vector=gn.e_2)(a)


@pytest.mark.parametrize("n,cls", CASES)
def test_exp(n: int, cls) -> None:
    # exp is defined for a scalar and any negative-square blade (bivector /
    # pseudoscalar); every representation must agree with Gn on each kind it can
    # hold, and reject a vector (A**2 > 0) the same way.
    s: Gn = Gn.from_scalar(2)
    assert to(cls, s).exp() == s.exp()
    v: Gn = vec(n, 0)
    with pytest.raises(ValueError):
        v.exp()
    with pytest.raises(ValueError):
        to(cls, v).exp()
    if n >= 2:
        b: Gn = vec(n, 0) ^ vec(n, 10)
        assert to(cls, b).exp() == b.exp()


@pytest.mark.parametrize("n,cls", CASES)
def test_coefficient_readback(n: int, cls) -> None:
    # coefficient(blade) reads each blade's stored coefficient, and summing
    # coefficient * blade over the basis reconstructs the value (decomposition)
    g: Gn = full(n, 0)
    x: MultiVectorBase = to(cls, g)
    coefs: BladeCoef = g.to_blade_dict()
    recon: MultiVectorBase = cls.zero()
    b: Blade
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
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    assert type(to(cls, a) * to(cls, b)) is cls
    assert type(to(cls, a).reverse()) is cls
    assert type(to(cls, a).dual(n)) is cls
    assert type(to(cls, a) + to(cls, b)) is cls


@pytest.mark.parametrize("n,cls", [(1, g1.G), (2, g2.G), (3, g3.G)])
def test_mixing_with_gn_coerces_to_gn(n: int, cls) -> None:
    a: Gn
    b: Gn
    a, b = full(n, 0), full(n, 10)
    mixed: MultiVectorBase = to(cls, a) * b  # specialized * Gn
    assert isinstance(mixed, Gn)
    assert mixed == a * b


@pytest.mark.parametrize("n,cls", [(1, g1.G), (2, g2.G), (3, g3.G)])
def test_basis_constants(n: int, cls) -> None:
    # Module constants carry the GRADED type of their blade (reversed 2026-08-04:
    # they used to be the full class cls) -- zero/one -> Scalar_n, a vector blade
    # -> Vector_n, e_12 -> Bivector_n, e_123 -> g3.Trivector.  See
    # tasks/graded-typed-module-basis-constants.md.
    mod: ModuleType = MODULES[n]
    grade_prefix: dict[int, str] = {
        0: "Scalar",
        1: "Vector",
        2: "Bivector",
        3: "Trivector",
    }

    def graded_type(grade: int) -> type:
        return getattr(mod, grade_prefix[grade])

    assert type(mod.zero) is graded_type(0)
    assert type(mod.one) is graded_type(0)
    b: Blade
    for b in blades(n):
        if b == ():
            continue
        const: MultiVectorBase = getattr(mod, field_name(b))
        assert type(const) is graded_type(len(b))
        assert const == Gn.from_blade_dict({b: 1})
    # Summing same-grade module constants stays in that grade's graded type;
    # adding a scalar spans grades (no covering graded type) so it widens to the
    # algebra's full class cls.
    grade1: list[Blade] = [x for x in blades(n) if len(x) == 1]
    coeffs: dict[Blade, int] = {b: i + 2 for i, b in enumerate(grade1)}
    first: Blade = grade1[0]
    vector_sum: MultiVectorBase = coeffs[first] * getattr(mod, field_name(first))
    for b in grade1[1:]:
        vector_sum = vector_sum + coeffs[b] * getattr(mod, field_name(b))
    assert type(vector_sum) is graded_type(1)
    assert vector_sum == Gn.from_blade_dict(coeffs)
    assert type(3 * mod.one + vector_sum) is cls


@pytest.mark.parametrize("n,cls", [(1, g1.G), (2, g2.G), (3, g3.G)])
def test_implicit_dimension_methods(n: int, cls) -> None:
    a: Gn = full(n, 0)
    # n defaults to the algebra's own dimension
    assert to(cls, a).dual() == a.dual(n)
    assert to(cls, a).dual() == to(cls, a).dual(n)
    assert cls.unit_pseudoscalar() == Gn.unit_pseudoscalar(n)
    assert cls.unit_pseudoscalar_squared() == Gn.unit_pseudoscalar_squared(n)
    assert len(list(cls.bases())) == 2**n
    assert type(cls.symbolic_multivector(prefix="z")) is cls


def test_is_close_numeric() -> None:
    a: g2.G = g2.G.from_blade_dict({(1,): 3.0, (2,): 4.0})
    b: g2.G = g2.G.from_blade_dict({(1,): 3.0 + 1e-9, (2,): 4.0})
    assert a.isclose(b, rel_tol=1e-5, abs_tol=1e-5)
    assert not a.isclose(
        g2.G.from_blade_dict({(1,): 3.5, (2,): 4.0}), rel_tol=1e-5, abs_tol=1e-5
    )


@pytest.mark.parametrize("cls", [g1.G, g2.G, g3.G])
def test_simplified_and_expanded_form(cls) -> None:
    # On the lazy (specialized/graded) classes, expanded()/simplified() change the
    # coefficient *form*: distribute, and collapse to lowest terms.  (Gn eager-
    # simplifies in __post_init__, so it re-canonicalizes -- value test below.)
    a: sympy.Symbol
    b: sympy.Symbol
    t: sympy.Symbol
    a, b, t = sympy.symbols("a b t")
    v: MultiVectorBase = cls.from_blade_dict({(1,): (a + b) ** 2})
    assert v.expanded().to_blade_dict()[(1,)] == a**2 + 2 * a * b + b**2
    w: MultiVectorBase = cls.from_blade_dict(
        {(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2}
    )
    assert w.simplified().to_blade_dict()[(1,)] == 1


def test_expand_numerators_dict_for_display() -> None:
    # nbplotutils._expand_numerators_dict (used by show_mult): expand each
    # coefficient's NUMERATOR, keep its denominator factored, and do NOT
    # rebuild the multivector, so the distributed form survives Gn's eager
    # __post_init__ simplify (which would otherwise re-factor it, e.g. back to
    # a0*(b0 + c0) -- the regression this fixed).
    from gacalc.nbplotutils import _expand_numerators_dict

    a: sympy.Symbol
    b: sympy.Symbol
    c: sympy.Symbol
    a, b, c = sympy.symbols("a b c")
    # survives Gn eager-simplify: a factored product is distributed for display
    v: Gn = Gn.from_blade_dict({(1,): a * (b + c)})
    assert _expand_numerators_dict(v)[(1,)] == a * b + a * c
    # numerator expanded, radical denominator left factored (not rationalized)
    den: Coef = sympy.sqrt(a**2 + b**2)
    w: Gn = Gn.from_blade_dict({(1,): (a + b) ** 2 / den})
    num: Coef
    d: Coef
    num, d = sympy.fraction(sympy.together(_expand_numerators_dict(w)[(1,)]))
    assert num == a**2 + 2 * a * b + b**2
    assert d == den


def _same_value(x: MultiVectorBase, y: MultiVectorBase) -> bool:
    # Value equality independent of coefficient *form* (Gn's __eq__ is structural,
    # so (a+b)**2 vs a**2+2ab+b**2 would compare unequal there).
    dx: BladeCoef
    dy: BladeCoef
    dx, dy = x.to_blade_dict(), y.to_blade_dict()
    return all(
        sympy.simplify(sympy.sympify(dx.get(k, 0)) - sympy.sympify(dy.get(k, 0))) == 0
        for k in set(dx) | set(dy)
    )


@pytest.mark.parametrize("n,cls", CASES)
def test_simplified_and_expanded_preserve_value(n: int, cls) -> None:
    # Same value on every representation -- only the coefficient form may change.
    a: sympy.Symbol
    b: sympy.Symbol
    t: sympy.Symbol
    a, b, t = sympy.symbols("a b t")
    v: MultiVectorBase = cls.from_blade_dict({(1,): (a + b) ** 2})
    assert _same_value(v.expanded(), v)
    assert _same_value(v.simplified(), v)
    w: MultiVectorBase = cls.from_blade_dict(
        {(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2}
    )
    assert _same_value(w.simplified(), w)
    assert w.simplified().to_blade_dict()[(1,)] == 1


def test_project_vector_onto_bivector_2d() -> None:
    # the bivector e_12 spans the whole plane, so any 2D vector projects to itself
    v: g2.G = 3 * g2.G.basis_vector(1) + 4 * g2.G.basis_vector(2)
    assert g2.G.project(onto=g2.G.e_12)(v) == v
    # Gn reference: same result onto the e_1 e_2 bivector
    gv: Gn = 3 * gn.e_1 + 4 * gn.e_2
    assert Gn.project(onto=gn.e_1 * gn.e_2)(gv) == gv


def test_project_vector_onto_bivector_and_trivector_3d() -> None:
    e1: g3.G
    e2: g3.G
    e3: g3.G
    e1, e2, e3 = (g3.G.basis_vector(i) for i in (1, 2, 3))
    # onto the e_12 plane: keep the in-plane part, drop the perpendicular e_3
    assert g3.G.project(onto=g3.G.e_12)(e1 + e3) == e1
    assert g3.G.project(onto=g3.G.e_12)(e3) == g3.G.zero()
    # onto the trivector e_123 (all of 3-space): a vector projects to itself
    assert g3.G.project(onto=g3.G.e_123)(e1 + e3) == e1 + e3


def test_repr_latex_shows_simplified() -> None:
    # the lazy classes don't eager-simplify, but the display (_repr_latex_) renders
    # the simplified coefficient (sin^2 + cos^2 -> 1), not the raw stored form
    t: sympy.Symbol = sympy.symbols("t")
    v: g2.G = g2.G.from_blade_dict({(1,): sympy.sin(t) ** 2 + sympy.cos(t) ** 2})
    assert "sin" in str(v.to_blade_dict()[(1,)])  # stored coefficient is still raw
    latex: str = v._repr_latex_()
    assert "sin" not in latex and "cos" not in latex  # displayed form is simplified
