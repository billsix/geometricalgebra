"""Operators on the generated graded types type *precisely* (added 2026-07-21).

The geometric/outer/inner products and their operators used to be declared
``-> typing.Self`` and cast, so ``v2 * v2`` mistyped as ``Vector2`` though it is a
``Rotor2`` at runtime.  ``@typing.overload`` signatures now give the true type.

``typing.assert_type`` guards the STATIC types (checked by ``ty`` -- a regression
makes ``ty check tests`` fail); the runtime block guards values/runtime types under
pytest.  See ``tasks/typed-product-helper-functions.md``.
"""

import typing

import pytest
import sympy

from gacalc.g1 import Scalar1, Vector1
from gacalc.g2 import G2, Bivector2, Rotor2, Scalar2, Vector2
from gacalc.g3 import G3, Bivector3, Rotor3, Scalar3, Trivector3, Vector3


def test_operator_static_types() -> None:
    a: Vector2 = Vector2.e_1
    b: Vector2 = Vector2.e_2
    typing.assert_type(a * b, Rotor2)  # geometric: was Vector2, now honest
    typing.assert_type(a ^ b, Bivector2)  # wedge operator
    typing.assert_type(a.outer_product(b), Bivector2)
    typing.assert_type(a.inner_product(b), Scalar2)
    typing.assert_type(a * 3, Vector2)  # scalar scaling preserves the type
    u: Vector3 = Vector3.e_1
    v: Vector3 = Vector3.e_2
    typing.assert_type(u * v, Rotor3)
    typing.assert_type(u ^ v, Bivector3)


def test_scalar_lhs_static_types() -> None:
    # ScalarN as a product/sum lhs is now precise too (was cast to ScalarN): the
    # products scale, so they stay in the rhs's type; +/- narrow by grade.
    s: Scalar2 = Scalar2(coeff_scalar=3.0)
    v: Vector2 = Vector2.e_1
    typing.assert_type(s * v, Vector2)  # scalar * vector -> vector (scaling)
    typing.assert_type(s * Bivector2.e_12, Bivector2)
    typing.assert_type(s.outer_product(v), Vector2)
    typing.assert_type(s.inner_product(v), Scalar2)  # scalar . X == 0 (grade 0)
    typing.assert_type(s * 3, Scalar2)  # scalar * number -> scalar
    typing.assert_type(s * s, Scalar2)
    typing.assert_type(s + v, G2)  # {0} + {1} -> full G2
    typing.assert_type(s + Bivector2.e_12, Rotor2)  # {0} + {2} -> Rotor2
    typing.assert_type(s - v, G2)
    typing.assert_type(s + s, Scalar2)  # same grade stays Scalar2
    typing.assert_type(s + 2, Scalar2)  # scalar + number -> scalar
    s3: Scalar3 = Scalar3(coeff_scalar=2.0)
    typing.assert_type(s3 * Trivector3.e_123, Trivector3)


def test_scalar_lhs_runtime_types_and_values() -> None:
    s: Scalar2 = Scalar2(coeff_scalar=3.0)
    v: Vector2 = Vector2(1.0, 2.0)
    assert type(s * v) is Vector2  # scaling preserves the concrete type
    assert (s * v).isclose(Vector2(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s.inner_product(v)) is Scalar2  # scalar . vector == 0
    assert s.inner_product(v).isclose(
        Scalar2(coeff_scalar=0.0), rel_tol=1e-5, abs_tol=1e-5
    )
    assert type(s + Bivector2.e_12) is Rotor2  # {0} + {2}
    assert (s + Bivector2.e_12).isclose(
        Rotor2(coeff_scalar=3.0, coeff_e_12=1.0), rel_tol=1e-5, abs_tol=1e-5
    )
    assert type(s + v) is G2  # {0} + {1} widens to the full class


def test_alias_and_scalar_contraction_static_types() -> None:
    # wedge / dot are precise aliases of outer_product / inner_product (they were
    # inherited from base as -> Self); now overridden on every graded type.
    a: Vector2 = Vector2.e_1
    b: Vector2 = Vector2.e_2
    typing.assert_type(a.wedge(b), Bivector2)  # was Vector2
    typing.assert_type(a.dot(b), Scalar2)  # was Vector2
    u: Vector3 = Vector3.e_1
    typing.assert_type(u.wedge(Vector3.e_2), Bivector3)
    typing.assert_type(u.dot(Vector3.e_2), Scalar3)
    # ScalarN now overrides ^, wedge, dot, <, >, left/right_contraction too (all
    # were inherited from base as -> Self).
    s: Scalar2 = Scalar2(coeff_scalar=3.0)
    v: Vector2 = Vector2.e_1
    typing.assert_type(s ^ v, Vector2)  # scalar ^ vector -> vector (scaling)
    typing.assert_type(s.wedge(v), Vector2)
    typing.assert_type(s.dot(v), Scalar2)  # scalar . X == 0 (grade 0)
    typing.assert_type(s < v, Vector2)  # left contraction: grade 1 - 0 = 1
    typing.assert_type(s.left_contraction(v), Vector2)
    typing.assert_type(s > v, Scalar2)  # right contraction: grade 0 - 1 < 0 -> 0
    typing.assert_type(s.right_contraction(v), Scalar2)


def test_alias_and_scalar_contraction_runtime() -> None:
    a: Vector2 = Vector2.e_1
    b: Vector2 = Vector2.e_2
    assert type(a.wedge(b)) is Bivector2
    assert a.wedge(b).isclose(a.outer_product(b), rel_tol=1e-5, abs_tol=1e-5)
    assert type(a.dot(b)) is Scalar2
    assert a.dot(b).isclose(a.inner_product(b), rel_tol=1e-5, abs_tol=1e-5)
    s: Scalar2 = Scalar2(coeff_scalar=3.0)
    v: Vector2 = Vector2(1.0, 2.0)
    assert type(s ^ v) is Vector2  # scaling preserves the rhs type
    assert (s ^ v).isclose(Vector2(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s < v) is Vector2  # scalar left-contraction == scaling
    assert (s < v).isclose(Vector2(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s > v) is Scalar2  # scalar right-contraction of a vector == 0
    assert (s > v).isclose(Scalar2(coeff_scalar=0.0), rel_tol=1e-5, abs_tol=1e-5)


def test_add_sub_narrow_by_grade() -> None:
    # scalar + bivector spans grades {0, 2} -> the even/Rotor type, in either
    # order (__add__ / __radd__) and for subtraction (__sub__ / __rsub__).
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(3 * i2 + 2, Rotor2)  # __add__ scalar arm
    typing.assert_type(2 + 3 * i2, Rotor2)  # __radd__ (number on the left)
    typing.assert_type(i2 - 2, Rotor2)  # __add__ (subtract a scalar)
    typing.assert_type(2 - i2, Rotor2)  # __rsub__
    typing.assert_type(i2 + i2, Bivector2)  # same grade stays Bivector2


def test_reflected_operators_are_precise_for_numbers() -> None:
    # __rmul__/__radd__/__rsub__ fire ONLY with a number on the left: every gacalc
    # multivector-on-the-left is handled by that operand's own forward op (never
    # NotImplemented), so a multivector never reaches the reflected op.  For that
    # sole number-left case the single-signature typing is already precise -- no
    # @overload needed.  (See the archived reflected-operator-typing-overloads task.)
    v: Vector2 = Vector2.e_1
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    r2: Rotor2 = Vector2.e_1 * Vector2.e_2
    s2: Scalar2 = Scalar2(coeff_scalar=3.0)
    # __rmul__: number * multivector scales -> the multivector's own type
    typing.assert_type(2 * v, Vector2)
    typing.assert_type(2.0 * i2, Bivector2)
    typing.assert_type(2 * r2, Rotor2)
    typing.assert_type(2 * s2, Scalar2)
    # __radd__/__rsub__: narrow by grade, either operand order
    typing.assert_type(2 + v, G2)  # {0} + {1} -> full G2
    typing.assert_type(2 - v, G2)
    typing.assert_type(2 + s2, Scalar2)  # scalar + number -> scalar
    typing.assert_type(2 - s2, Scalar2)
    v3: Vector3 = Vector3.e_1
    typing.assert_type(2 * v3, Vector3)


def test_reflected_operators_runtime_including_symbolic_left() -> None:
    # Runtime confirms the reflected ops fire (and are correct) with a number left,
    # INCLUDING a sympy symbol -- for which the STATIC type is `Unknown`, not because
    # gacalc's __rmul__ is imprecise but because `sympy.Expr.__mul__` intercepts the
    # dispatch in the checker's view (returning Unknown) so the checker never consults
    # __rmul__.  At runtime sympy returns NotImplemented, so __rmul__ correctly fires.
    # Overloading gacalc's reflected ops cannot fix the static gap; it is a sympy-stub
    # limitation.
    v: Vector2 = Vector2.e_1
    assert type(2 * v) is Vector2
    assert (2 * v).isclose(Vector2(2.0, 0.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(2 + Bivector2.e_12) is Rotor2
    t: sympy.Expr = sympy.Symbol("t")
    assert type(t * v) is Vector2  # runtime is correct though ty infers Unknown
    assert (t * v).to_blade_dict() == {(1,): t}
    assert type(t + Bivector2.e_12) is Rotor2


def test_r_vector_part_narrows_by_grade() -> None:
    # r_vector_part(r) with a literal r types precisely to that grade's part:
    # a present grade -> that grade's type, an absent grade -> Scalar2 (the zero).
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    typing.assert_type(v.r_vector_part(1), Vector2)  # present grade -> itself
    typing.assert_type(v.r_vector_part(0), Scalar2)  # absent grade -> Scalar2(0)
    typing.assert_type(v.r_vector_part(2), Scalar2)
    rotor: Rotor2 = Vector2.e_1 * Vector2.e_2  # grades {0, 2}
    typing.assert_type(rotor.r_vector_part(0), Scalar2)  # scalar part
    typing.assert_type(rotor.r_vector_part(2), Bivector2)  # bivector part
    typing.assert_type(rotor.r_vector_part(1), Scalar2)  # absent grade -> Scalar2(0)


def test_r_vector_part_runtime_types_and_values() -> None:
    rotor: Rotor2 = 5 * Vector2.e_1 * Vector2.e_2 + 7  # 7 + 5 e_12
    assert type(rotor.r_vector_part(2)) is Bivector2
    assert rotor.r_vector_part(2).coeff_e_12 == 5
    assert type(rotor.r_vector_part(0)) is Scalar2
    assert rotor.r_vector_part(0).coeff_scalar == 7
    assert type(rotor.r_vector_part(1)) is Scalar2  # absent grade -> zero Scalar2


def test_even_odd_part_narrow_to_resolved_grade() -> None:
    # even_part/odd_part have no argument to overload on, so the graded override
    # declares its resolved return type directly (base is -> MultiVectorBase).
    v: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    typing.assert_type(v.odd_part(), Vector2)  # a vector is purely odd
    typing.assert_type(v.even_part(), Scalar2)  # its even part is the scalar 0
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(i2.even_part(), Bivector2)  # a bivector is purely even
    typing.assert_type(i2.odd_part(), Scalar2)
    rotor: Rotor2 = Vector2.e_1 * Vector2.e_2
    typing.assert_type(rotor.even_part(), Rotor2)  # grades {0, 2} are both even
    typing.assert_type(rotor.odd_part(), Scalar2)


def test_even_odd_part_runtime_types() -> None:
    i2: Bivector2 = 5 * (Vector2.e_1 ^ Vector2.e_2)
    assert type(i2.even_part()) is Bivector2
    assert i2.even_part().coeff_e_12 == 5
    assert type(i2.odd_part()) is Scalar2
    assert type((3 * Vector2.e_1).even_part()) is Scalar2  # vector has no even part


def test_contraction_static_types() -> None:
    # left/right contraction resolve their grade like the other products:
    # left keeps grade m-k (right-left), right keeps k-m; a negative grade -> Scalar2.
    a: Vector2 = Vector2.e_1
    i2: Bivector2 = Vector2.e_1 ^ Vector2.e_2
    typing.assert_type(a.left_contraction(a), Scalar2)  # vector ⌋ vector = dot
    typing.assert_type(a.left_contraction(i2), Vector2)  # vector ⌋ bivector (grade 1)
    typing.assert_type(i2.left_contraction(a), Scalar2)  # bivector ⌋ vector -> 0
    typing.assert_type(i2.right_contraction(a), Vector2)  # bivector ⌊ vector (grade 1)
    typing.assert_type(a.right_contraction(i2), Scalar2)  # vector ⌊ bivector -> 0
    # the < / > operators carry the same precise overloads
    typing.assert_type(a < a, Scalar2)
    typing.assert_type(a < i2, Vector2)
    typing.assert_type(i2 > a, Vector2)


def test_contraction_runtime_types_and_values() -> None:
    a: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    i2: Bivector2 = 5 * (Vector2.e_1 ^ Vector2.e_2)
    # vector ⌋ vector is the dot product: 3*3 + 4*4 = 25
    assert type(a.left_contraction(a)) is Scalar2
    assert a.left_contraction(a).coeff_scalar == 25
    assert (a < a).coeff_scalar == 25  # operator agrees
    # e_1 ⌋ (5 e_12) = 5 e_2 ;  contraction asymmetry: (5 e_12) ⌋ e_1 == 0
    assert type(Vector2.e_1.left_contraction(i2)) is Vector2
    assert Vector2.e_1.left_contraction(i2).coeff_e_2 == 5
    assert type(i2.left_contraction(Vector2.e_1)) is Scalar2  # grade -1 -> Scalar2(0)
    assert (i2 > Vector2.e_1).coeff_e_2 == -5  # bivector ⌊ vector = -5 e_2


def test_dual_narrows_by_grade() -> None:
    # dual has no argument to overload on (its grade n−r is fixed by the operand
    # grade + dimension), so like even/odd_part the graded override *declares*
    # the resolved grade type -- no unsound Self cast.
    v3: Vector3 = 3.0 * Vector3.e_1
    typing.assert_type(v3.dual(), Bivector3)  # grade 1 -> grade 2 in 3D
    i3: Bivector3 = 5.0 * Bivector3.e_23
    typing.assert_type(i3.dual(), Vector3)  # grade 2 -> grade 1 in 3D
    t3: Trivector3 = 7.0 * Trivector3.e_123
    typing.assert_type(t3.dual(), Scalar3)  # grade 3 -> grade 0
    r3: Rotor3 = 1 + 2.0 * Bivector3.e_12
    typing.assert_type(r3.dual(), G3)  # {0,2} -> {3,1} = odd, no covering type

    # 2D duals: grade n−r with n=2.
    v2: Vector2 = 3 * Vector2.e_1
    typing.assert_type(v2.dual(), Vector2)  # grade 1 -> grade 1
    i2: Bivector2 = 5 * Bivector2.e_12
    typing.assert_type(i2.dual(), Scalar2)  # grade 2 -> grade 0
    rotor2: Rotor2 = 1 + 2 * Bivector2.e_12
    typing.assert_type(rotor2.dual(), Rotor2)  # {0,2} -> {2,0} = {0,2}

    # per-algebra scalar duals: grade 0 -> that algebra's pseudoscalar (the whole
    # point of the per-algebra ScalarN split -- a shared Scalar couldn't type these).
    typing.assert_type(Scalar1(coeff_scalar=1).dual(), Vector1)
    typing.assert_type(Scalar2(coeff_scalar=1).dual(), Bivector2)
    typing.assert_type(Scalar3(coeff_scalar=1).dual(), Trivector3)


def test_dual_runtime_types_and_values() -> None:
    # e_23* = e_1 (Bivector3.dual really returns a Vector3 -- the whole point).
    n: Vector3 = Bivector3.e_23.dual()
    assert type(n) is Vector3
    assert n.coeff_e_1 == 1
    assert type(Trivector3.e_123.dual()) is Scalar3
    assert Trivector3.e_123.dual().coeff_scalar == 1
    assert type(Bivector2.e_12.dual()) is Scalar2
    # a fixed-dimension type's dual is at its own dimension: a mismatched n raises.
    with pytest.raises(ValueError, match="fixed at dimension 3"):
        Bivector3.e_23.dual(2)
    Bivector3.e_23.dual(3)  # the dimension itself is fine


def test_operator_runtime_types_and_values() -> None:
    a: Vector2 = 3 * Vector2.e_1 + 4 * Vector2.e_2
    b: Vector2 = Vector2.e_1 + 2 * Vector2.e_2
    # the runtime type has always been correct; here we pin it next to the static one
    assert type(a * b) is Rotor2
    assert type(a ^ b) is Bivector2
    assert type(a.inner_product(b)) is Scalar2
    assert type(a * 3) is Vector2
    # value equals the wedge coefficient e_1 e_2:  3*2 - 4*1 = 2
    assert (a ^ b).coeff_e_12 == 2
    # and the geometric product carries both scalar and bivector parts
    product: Rotor2 = a * b
    assert product.coeff_scalar == 11  # 3*1 + 4*2
    assert product.coeff_e_12 == 2
