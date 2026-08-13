"""``isclose`` -- floating-point-only approximate equality.

Symmetric (PEP 485 / ``math.isclose``); ``abs_tol`` defaults to ``0.0`` so a
near-zero comparison must opt in; and a symbolic coefficient raises a clear
error instead of crashing inside ``float()``.
"""

import pytest
import sympy

import gacalc.g2 as g2
from gacalc.gn import Gn


def test_symmetric() -> None:
    a: g2.Vector = g2.Vector(1.0, 2.0)
    b: g2.Vector = g2.Vector(1.0 + 1e-7, 2.0)
    assert a.isclose(b, rel_tol=1e-5)
    # order-independent, unlike the old np.isclose (b-as-reference) behaviour
    assert a.isclose(b, rel_tol=1e-5) == b.isclose(a, rel_tol=1e-5)


def test_abs_tol_needed_for_near_zero() -> None:
    # a tiny non-zero component vs exact zero: rejected by default (abs_tol=0.0),
    # accepted once the caller opts into an absolute tolerance.
    v: g2.Vector = g2.Vector(1e-8, 1.0)
    near_zero: g2.Vector = g2.Vector(0.0, 1.0)
    assert not v.isclose(near_zero)  # default abs_tol=0.0
    assert v.isclose(near_zero, abs_tol=1e-5)


def test_symbolic_coefficient_raises() -> None:
    x: sympy.Symbol = sympy.Symbol("x")
    symbolic: g2.Vector = g2.Vector(x, 2.0)
    numeric: g2.Vector = g2.Vector(1.0, 2.0)
    with pytest.raises(TypeError, match="floating-point only"):
        symbolic.isclose(numeric, abs_tol=1e-5)
    # and via the Gn reference path too
    with pytest.raises(TypeError, match="floating-point only"):
        Gn.from_blade_dict({(1,): x}).isclose(
            Gn.from_blade_dict({(1,): 1.0}), abs_tol=1e-5
        )


def test_numeric_sympy_passes() -> None:
    # a pure-*number* sympy coefficient (Rational, sqrt(4)->2) is float-able, so
    # it compares fine -- only free-symbol expressions raise.
    a: g2.Vector = g2.Vector(sympy.Rational(1, 2), sympy.sqrt(sympy.Integer(4)))
    assert a.isclose(g2.Vector(0.5, 2.0), abs_tol=1e-5)


def test_gn_matches_specialized() -> None:
    g: Gn = Gn.from_blade_dict({(1,): 1.0, (2,): 2.0})
    assert g.isclose(Gn.from_blade_dict({(1,): 1.0 + 1e-8, (2,): 2.0}), abs_tol=1e-5)
    v: g2.Vector = g2.Vector(1.0, 2.0)
    assert v.isclose(g2.Vector(1.0 + 1e-8, 2.0), abs_tol=1e-5)
