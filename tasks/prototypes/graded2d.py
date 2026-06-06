# Copyright (c) 2026 William Emerison Six -- GPL v2+ (see repo COPYING).
"""PHASE 0 THROWAWAY PROTOTYPE -- graded subtypes for 𝒢₂.

Not production code, not wired into the package, not tested by the suite. Its
only jobs are to (1) show how a structural ``match`` dispatch reads as the grade
product table, (2) confirm the operation determines the return type (so floating
point never decides a type), (3) confirm cross-type ``==`` against G2/Gn works,
and (4) benchmark a typed ``Vector2 * Vector2`` against the full ``G2`` and the
general ``Gn``.

Run from the repo root:  python tasks/prototypes/graded2d.py

Types: Vector2 {e_1,e_2}, Bivector2 {e_12}, Rotor2 {scalar,e_12} (even ≅ ℂ).
Scalars are plain Python numbers. Anything that widens out of these lands in G2.

Return-type table (geometric product *), all derived by hand from the 𝒢₂ rules
(e₁²=e₂²=1, e₁₂=e₁e₂, e₁₂²=−1):

    Vector2  * Vector2  -> Rotor2     (scalar = dot, e_12 = wedge)
    Vector2  * Bivector2-> Vector2
    Vector2  * Rotor2   -> Vector2
    Bivector2* Vector2  -> Vector2
    Bivector2* Bivector2-> Rotor2     (a pure scalar; Rotor2 is its smallest home)
    Bivector2* Rotor2   -> Rotor2
    Rotor2   * Vector2  -> Vector2
    Rotor2   * Bivector2-> Rotor2
    Rotor2   * Rotor2   -> Rotor2     (closed -- this is ℂ multiplication)
    <any>    * number   -> <same type>
    <any>    * G2/Gn    -> G2         (widen and defer)
"""

import sys
import time
from dataclasses import dataclass

sys.path.insert(0, "src")

import sympy  # noqa: E402

from geometricalgebra.g2 import G2  # noqa: E402
from geometricalgebra.gn import Gn  # noqa: E402


def _simplify_eq(a_dict, b_dict) -> bool:
    keys = set(a_dict) | set(b_dict)
    return all(
        sympy.simplify(sympy.sympify(a_dict.get(k, 0)) - sympy.sympify(b_dict.get(k, 0)))
        == 0
        for k in keys
    )


@dataclass(eq=False)
class Vector2:
    e_1: object = 0
    e_2: object = 0

    def to_blade_dict(self):
        return {b: c for b, c in (((1,), self.e_1), ((2,), self.e_2)) if c != 0}

    def widen(self) -> G2:
        return G2(e_1=self.e_1, e_2=self.e_2)

    def __mul__(self, rhs):
        match rhs:
            case Vector2():  # vector * vector -> rotor (scalar + bivector)
                return Rotor2(
                    scalar=self.e_1 * rhs.e_1 + self.e_2 * rhs.e_2,  # dot
                    e_12=self.e_1 * rhs.e_2 - self.e_2 * rhs.e_1,  # wedge
                )
            case Bivector2():  # vector * bivector -> vector
                return Vector2(e_1=-self.e_2 * rhs.e_12, e_2=self.e_1 * rhs.e_12)
            case Rotor2():  # vector * rotor -> vector
                return Vector2(
                    e_1=self.e_1 * rhs.scalar - self.e_2 * rhs.e_12,
                    e_2=self.e_2 * rhs.scalar + self.e_1 * rhs.e_12,
                )
            case _ if hasattr(rhs, "to_blade_dict"):  # G2 / Gn -> widen
                return self.widen() * rhs
            case _:  # scalar
                return Vector2(self.e_1 * rhs, self.e_2 * rhs)

    def __rmul__(self, lhs):
        return Vector2(lhs * self.e_1, lhs * self.e_2)

    def __xor__(self, rhs):  # wedge
        match rhs:
            case Vector2():  # vector ^ vector -> bivector (always, by construction)
                return Bivector2(e_12=self.e_1 * rhs.e_2 - self.e_2 * rhs.e_1)
            case _ if hasattr(rhs, "to_blade_dict"):
                return self.widen() ^ rhs
            case _:
                return Vector2(self.e_1 * rhs, self.e_2 * rhs)

    def __add__(self, rhs):
        match rhs:
            case Vector2():
                return Vector2(self.e_1 + rhs.e_1, self.e_2 + rhs.e_2)
            case _ if hasattr(rhs, "to_blade_dict"):  # cross-grade -> widen to G2
                other = rhs.widen() if hasattr(rhs, "widen") else rhs
                return self.widen() + other
            case _:
                return NotImplemented

    def __eq__(self, other):
        if not hasattr(other, "to_blade_dict"):
            return NotImplemented
        return _simplify_eq(self.to_blade_dict(), other.to_blade_dict())


@dataclass(eq=False)
class Bivector2:
    e_12: object = 0

    def to_blade_dict(self):
        return {(1, 2): self.e_12} if self.e_12 != 0 else {}

    def widen(self) -> G2:
        return G2(e_12=self.e_12)

    def __mul__(self, rhs):
        match rhs:
            case Vector2():  # bivector * vector -> vector
                return Vector2(e_1=rhs.e_2 * self.e_12, e_2=-rhs.e_1 * self.e_12)
            case Bivector2():  # bivector * bivector -> scalar (lives in Rotor2)
                return Rotor2(scalar=-self.e_12 * rhs.e_12, e_12=0)
            case Rotor2():  # bivector * rotor -> rotor
                return Rotor2(
                    scalar=-self.e_12 * rhs.e_12, e_12=self.e_12 * rhs.scalar
                )
            case _ if hasattr(rhs, "to_blade_dict"):
                return self.widen() * rhs
            case _:
                return Bivector2(self.e_12 * rhs)

    def __rmul__(self, lhs):
        return Bivector2(lhs * self.e_12)

    def __add__(self, rhs):
        match rhs:
            case Bivector2():
                return Bivector2(self.e_12 + rhs.e_12)
            case _ if hasattr(rhs, "to_blade_dict"):
                other = rhs.widen() if hasattr(rhs, "widen") else rhs
                return self.widen() + other
            case _:
                return NotImplemented

    def __eq__(self, other):
        if not hasattr(other, "to_blade_dict"):
            return NotImplemented
        return _simplify_eq(self.to_blade_dict(), other.to_blade_dict())


@dataclass(eq=False)
class Rotor2:
    scalar: object = 0
    e_12: object = 0

    def to_blade_dict(self):
        return {
            b: c for b, c in (((), self.scalar), ((1, 2), self.e_12)) if c != 0
        }

    def widen(self) -> G2:
        return G2(scalar=self.scalar, e_12=self.e_12)

    def __mul__(self, rhs):
        match rhs:
            case Rotor2():  # rotor * rotor -> rotor  (this is ℂ multiplication)
                return Rotor2(
                    scalar=self.scalar * rhs.scalar - self.e_12 * rhs.e_12,
                    e_12=self.scalar * rhs.e_12 + self.e_12 * rhs.scalar,
                )
            case Vector2():  # rotor * vector -> vector (rotation/scaling)
                return Vector2(
                    e_1=self.scalar * rhs.e_1 + self.e_12 * rhs.e_2,
                    e_2=self.scalar * rhs.e_2 - self.e_12 * rhs.e_1,
                )
            case Bivector2():  # rotor * bivector -> rotor
                return Rotor2(
                    scalar=-self.e_12 * rhs.e_12, e_12=self.scalar * rhs.e_12
                )
            case _ if hasattr(rhs, "to_blade_dict"):
                return self.widen() * rhs
            case _:
                return Rotor2(self.scalar * rhs, self.e_12 * rhs)

    def __rmul__(self, lhs):
        return Rotor2(lhs * self.scalar, lhs * self.e_12)

    def __add__(self, rhs):
        match rhs:
            case Rotor2():
                return Rotor2(self.scalar + rhs.scalar, self.e_12 + rhs.e_12)
            case _ if hasattr(rhs, "to_blade_dict"):
                other = rhs.widen() if hasattr(rhs, "widen") else rhs
                return self.widen() + other
            case _:
                return NotImplemented

    def __eq__(self, other):
        if not hasattr(other, "to_blade_dict"):
            return NotImplemented
        return _simplify_eq(self.to_blade_dict(), other.to_blade_dict())


# --------------------------------------------------------------------------
# checks + benchmark
# --------------------------------------------------------------------------
def _checks() -> None:
    from geometricalgebra.g2 import e_1 as g2_e1
    from geometricalgebra.g2 import e_2 as g2_e2

    a, b = Vector2(3, 4), Vector2(1, 2)

    # return types are operation-driven
    assert isinstance(a * b, Rotor2), "vector*vector must be a Rotor2"
    assert isinstance(a ^ b, Bivector2), "vector^vector must be a Bivector2"
    assert isinstance(Rotor2(0, 1) * a, Vector2), "rotor*vector must be a Vector2"

    # values agree with the full G2 product (cross-type ==)
    assert (a * b) == (g2_e1 * 3 + g2_e2 * 4) * (g2_e1 * 1 + g2_e2 * 2)
    assert (a * b) == G2(scalar=11, e_12=2)  # 3*1+4*2=11 ; 3*2-4*1=2
    assert (a ^ b) == G2(e_12=2)

    # orthogonal vectors: product is a pure bivector *by value*, but the TYPE is
    # still Rotor2 -- we never narrowed based on the scalar being 0 (FP-proof).
    o = Vector2(1, 0) * Vector2(0, 1)
    assert isinstance(o, Rotor2) and o == G2(e_12=1)

    # rotor is ℂ: (e_12)^2 == -1
    assert Rotor2(0, 1) * Rotor2(0, 1) == G2(scalar=-1)

    # cross-grade add widens to G2
    assert isinstance(a + Bivector2(5), G2)

    # symbolic works (lazy, no eager simplify)
    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    sym = Vector2(a1, a2) * Vector2(b1, b2)
    assert sym == Gn.from_blade_dict(
        {(): a1 * b1 + a2 * b2, (1, 2): a1 * b2 - a2 * b1}
    )
    print("all checks passed")


def _time(fn, reps: int) -> float:
    start = time.perf_counter()
    for _ in range(reps):
        fn()
    return (time.perf_counter() - start) / reps * 1e6  # microseconds/op


def _bench() -> None:
    reps = 20000
    v, w = Vector2(3.0, 4.0), Vector2(1.0, 2.0)
    g2a, g2b = G2(e_1=3.0, e_2=4.0), G2(e_1=1.0, e_2=2.0)
    gna = Gn.from_blade_dict({(1,): 3.0, (2,): 4.0})
    gnb = Gn.from_blade_dict({(1,): 1.0, (2,): 2.0})

    tv = _time(lambda: v * w, reps)
    tg = _time(lambda: g2a * g2b, reps)
    tn = _time(lambda: gna * gnb, max(reps // 20, 200))  # Gn is slow; fewer reps

    print("\nnumeric vector*vector (microseconds/op, lower is better):")
    print(f"  Vector2 (typed) : {tv:8.2f}")
    print(f"  G2 (full)       : {tg:8.2f}   ({tg / tv:5.1f}x the typed cost)")
    print(f"  Gn (general)    : {tn:8.2f}   ({tn / tv:5.1f}x the typed cost)")

    a1, a2, b1, b2 = sympy.symbols("a1 a2 b1 b2")
    vs, ws = Vector2(a1, a2), Vector2(b1, b2)
    g2sa, g2sb = G2(e_1=a1, e_2=a2), G2(e_1=b1, e_2=b2)
    tvs = _time(lambda: vs * ws, 2000)
    tgs = _time(lambda: g2sa * g2sb, 2000)
    print("\nsymbolic vector*vector (microseconds/op):")
    print(f"  Vector2 (typed) : {tvs:8.2f}")
    print(f"  G2 (full)       : {tgs:8.2f}")
    print("  (Gn symbolic omitted -- its eager simplify makes it orders slower)")


if __name__ == "__main__":
    _checks()
    _bench()
