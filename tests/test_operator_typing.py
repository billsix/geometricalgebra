"""Operators on the generated graded types type *precisely* (added 2026-07-21).

The geometric/outer/inner products and their operators used to be declared
``-> typing.Self`` and cast, so ``v2 * v2`` mistyped as ``g2.Vector`` though it is a
``g2.Rotor`` at runtime.  ``@typing.overload`` signatures now give the true type.

``typing.assert_type`` guards the STATIC types (checked by ``ty`` -- a regression
makes ``ty check tests`` fail); the runtime block guards values/runtime types under
pytest.  See ``tasks/typed-product-helper-functions.md``.
"""

import typing

import pytest
import sympy

import gacalc.g1 as g1
import gacalc.g2 as g2
import gacalc.g3 as g3


def test_operator_static_types() -> None:
    a: g2.Vector = g2.Vector.e_1
    b: g2.Vector = g2.Vector.e_2
    typing.assert_type(a * b, g2.Rotor)  # geometric: was g2.Vector, now honest
    typing.assert_type(a ^ b, g2.Bivector)  # wedge operator
    typing.assert_type(a.outer_product(b), g2.Bivector)
    typing.assert_type(a.inner_product(b), g2.Scalar)
    typing.assert_type(a * 3, g2.Vector)  # scalar scaling preserves the type
    u: g3.Vector = g3.Vector.e_1
    v: g3.Vector = g3.Vector.e_2
    typing.assert_type(u * v, g3.Rotor)
    typing.assert_type(u ^ v, g3.Bivector)


def test_scalar_lhs_static_types() -> None:
    # ScalarN as a product/sum lhs is now precise too (was cast to ScalarN): the
    # products scale, so they stay in the rhs's type; +/- narrow by grade.
    s: g2.Scalar = g2.Scalar(coeff_scalar=3.0)
    v: g2.Vector = g2.Vector.e_1
    typing.assert_type(s * v, g2.Vector)  # scalar * vector -> vector (scaling)
    typing.assert_type(s * g2.Bivector.e_12, g2.Bivector)
    typing.assert_type(s.outer_product(v), g2.Vector)
    typing.assert_type(s.inner_product(v), g2.Scalar)  # scalar . X == 0 (grade 0)
    typing.assert_type(s * 3, g2.Scalar)  # scalar * number -> scalar
    typing.assert_type(s * s, g2.Scalar)
    typing.assert_type(s + v, g2.G)  # {0} + {1} -> full g2.G
    typing.assert_type(s + g2.Bivector.e_12, g2.Rotor)  # {0} + {2} -> g2.Rotor
    typing.assert_type(s - v, g2.G)
    typing.assert_type(s + s, g2.Scalar)  # same grade stays g2.Scalar
    typing.assert_type(s + 2, g2.Scalar)  # scalar + number -> scalar
    s3: g3.Scalar = g3.Scalar(coeff_scalar=2.0)
    typing.assert_type(s3 * g3.Trivector.e_123, g3.Trivector)


def test_scalar_lhs_runtime_types_and_values() -> None:
    s: g2.Scalar = g2.Scalar(coeff_scalar=3.0)
    v: g2.Vector = g2.Vector(1.0, 2.0)
    assert type(s * v) is g2.Vector  # scaling preserves the concrete type
    assert (s * v).isclose(g2.Vector(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s.inner_product(v)) is g2.Scalar  # scalar . vector == 0
    assert s.inner_product(v).isclose(
        g2.Scalar(coeff_scalar=0.0), rel_tol=1e-5, abs_tol=1e-5
    )
    assert type(s + g2.Bivector.e_12) is g2.Rotor  # {0} + {2}
    assert (s + g2.Bivector.e_12).isclose(
        g2.Rotor(coeff_scalar=3.0, coeff_e_12=1.0), rel_tol=1e-5, abs_tol=1e-5
    )
    assert type(s + v) is g2.G  # {0} + {1} widens to the full class


def test_alias_and_scalar_contraction_static_types() -> None:
    # wedge / dot are precise aliases of outer_product / inner_product (they were
    # inherited from base as -> Self); now overridden on every graded type.
    a: g2.Vector = g2.Vector.e_1
    b: g2.Vector = g2.Vector.e_2
    typing.assert_type(a.wedge(b), g2.Bivector)  # was g2.Vector
    typing.assert_type(a.dot(b), g2.Scalar)  # was g2.Vector
    u: g3.Vector = g3.Vector.e_1
    typing.assert_type(u.wedge(g3.Vector.e_2), g3.Bivector)
    typing.assert_type(u.dot(g3.Vector.e_2), g3.Scalar)
    # ScalarN now overrides ^, wedge, dot, <, >, left/right_contraction too (all
    # were inherited from base as -> Self).
    s: g2.Scalar = g2.Scalar(coeff_scalar=3.0)
    v: g2.Vector = g2.Vector.e_1
    typing.assert_type(s ^ v, g2.Vector)  # scalar ^ vector -> vector (scaling)
    typing.assert_type(s.wedge(v), g2.Vector)
    typing.assert_type(s.dot(v), g2.Scalar)  # scalar . X == 0 (grade 0)
    typing.assert_type(s < v, g2.Vector)  # left contraction: grade 1 - 0 = 1
    typing.assert_type(s.left_contraction(v), g2.Vector)
    typing.assert_type(s > v, g2.Scalar)  # right contraction: grade 0 - 1 < 0 -> 0
    typing.assert_type(s.right_contraction(v), g2.Scalar)


def test_alias_and_scalar_contraction_runtime() -> None:
    a: g2.Vector = g2.Vector.e_1
    b: g2.Vector = g2.Vector.e_2
    assert type(a.wedge(b)) is g2.Bivector
    assert a.wedge(b).isclose(a.outer_product(b), rel_tol=1e-5, abs_tol=1e-5)
    assert type(a.dot(b)) is g2.Scalar
    assert a.dot(b).isclose(a.inner_product(b), rel_tol=1e-5, abs_tol=1e-5)
    s: g2.Scalar = g2.Scalar(coeff_scalar=3.0)
    v: g2.Vector = g2.Vector(1.0, 2.0)
    assert type(s ^ v) is g2.Vector  # scaling preserves the rhs type
    assert (s ^ v).isclose(g2.Vector(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s < v) is g2.Vector  # scalar left-contraction == scaling
    assert (s < v).isclose(g2.Vector(3.0, 6.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(s > v) is g2.Scalar  # scalar right-contraction of a vector == 0
    assert (s > v).isclose(g2.Scalar(coeff_scalar=0.0), rel_tol=1e-5, abs_tol=1e-5)


def test_add_sub_narrow_by_grade() -> None:
    # scalar + bivector spans grades {0, 2} -> the even/Rotor type, in either
    # order (__add__ / __radd__) and for subtraction (__sub__ / __rsub__).
    i2: g2.Bivector = g2.Vector.e_1 ^ g2.Vector.e_2
    typing.assert_type(3 * i2 + 2, g2.Rotor)  # __add__ scalar arm
    typing.assert_type(2 + 3 * i2, g2.Rotor)  # __radd__ (number on the left)
    typing.assert_type(i2 - 2, g2.Rotor)  # __add__ (subtract a scalar)
    typing.assert_type(2 - i2, g2.Rotor)  # __rsub__
    typing.assert_type(i2 + i2, g2.Bivector)  # same grade stays g2.Bivector


def test_reflected_operators_are_precise_for_numbers() -> None:
    # __rmul__/__radd__/__rsub__ fire ONLY with a number on the left: every gacalc
    # multivector-on-the-left is handled by that operand's own forward op (never
    # NotImplemented), so a multivector never reaches the reflected op.  For that
    # sole number-left case the single-signature typing is already precise -- no
    # @overload needed.  (See the archived reflected-operator-typing-overloads task.)
    v: g2.Vector = g2.Vector.e_1
    i2: g2.Bivector = g2.Vector.e_1 ^ g2.Vector.e_2
    r2: g2.Rotor = g2.Vector.e_1 * g2.Vector.e_2
    s2: g2.Scalar = g2.Scalar(coeff_scalar=3.0)
    # __rmul__: number * multivector scales -> the multivector's own type
    typing.assert_type(2 * v, g2.Vector)
    typing.assert_type(2.0 * i2, g2.Bivector)
    typing.assert_type(2 * r2, g2.Rotor)
    typing.assert_type(2 * s2, g2.Scalar)
    # __radd__/__rsub__: narrow by grade, either operand order
    typing.assert_type(2 + v, g2.G)  # {0} + {1} -> full g2.G
    typing.assert_type(2 - v, g2.G)
    typing.assert_type(2 + s2, g2.Scalar)  # scalar + number -> scalar
    typing.assert_type(2 - s2, g2.Scalar)
    v3: g3.Vector = g3.Vector.e_1
    typing.assert_type(2 * v3, g3.Vector)


def test_reflected_operators_runtime_including_symbolic_left() -> None:
    # Runtime confirms the reflected ops fire (and are correct) with a number left,
    # INCLUDING a sympy symbol -- for which the STATIC type is `Unknown`, not because
    # gacalc's __rmul__ is imprecise but because `sympy.Expr.__mul__` intercepts the
    # dispatch in the checker's view (returning Unknown) so the checker never consults
    # __rmul__.  At runtime sympy returns NotImplemented, so __rmul__ correctly fires.
    # Overloading gacalc's reflected ops cannot fix the static gap; it is a sympy-stub
    # limitation.
    v: g2.Vector = g2.Vector.e_1
    assert type(2 * v) is g2.Vector
    assert (2 * v).isclose(g2.Vector(2.0, 0.0), rel_tol=1e-5, abs_tol=1e-5)
    assert type(2 + g2.Bivector.e_12) is g2.Rotor
    t: sympy.Expr = sympy.Symbol("t")
    assert type(t * v) is g2.Vector  # runtime is correct though ty infers Unknown
    assert (t * v).to_blade_dict() == {(1,): t}
    assert type(t + g2.Bivector.e_12) is g2.Rotor


def test_r_vector_part_narrows_by_grade() -> None:
    # r_vector_part(r) with a literal r types precisely to that grade's part:
    # a present grade -> that grade's type, an absent grade -> g2.Scalar (the zero).
    v: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    typing.assert_type(v.r_vector_part(1), g2.Vector)  # present grade -> itself
    typing.assert_type(v.r_vector_part(0), g2.Scalar)  # absent grade -> g2.Scalar(0)
    typing.assert_type(v.r_vector_part(2), g2.Scalar)
    rotor: g2.Rotor = g2.Vector.e_1 * g2.Vector.e_2  # grades {0, 2}
    typing.assert_type(rotor.r_vector_part(0), g2.Scalar)  # scalar part
    typing.assert_type(rotor.r_vector_part(2), g2.Bivector)  # bivector part
    typing.assert_type(
        rotor.r_vector_part(1), g2.Scalar
    )  # absent grade -> g2.Scalar(0)


def test_r_vector_part_runtime_types_and_values() -> None:
    rotor: g2.Rotor = 5 * g2.Vector.e_1 * g2.Vector.e_2 + 7  # 7 + 5 e_12
    assert type(rotor.r_vector_part(2)) is g2.Bivector
    assert rotor.r_vector_part(2).coeff_e_12 == 5
    assert type(rotor.r_vector_part(0)) is g2.Scalar
    assert rotor.r_vector_part(0).coeff_scalar == 7
    assert type(rotor.r_vector_part(1)) is g2.Scalar  # absent grade -> zero g2.Scalar


def test_even_odd_part_narrow_to_resolved_grade() -> None:
    # even_part/odd_part have no argument to overload on, so the graded override
    # declares its resolved return type directly (base is -> MultiVectorBase).
    v: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    typing.assert_type(v.odd_part(), g2.Vector)  # a vector is purely odd
    typing.assert_type(v.even_part(), g2.Scalar)  # its even part is the scalar 0
    i2: g2.Bivector = g2.Vector.e_1 ^ g2.Vector.e_2
    typing.assert_type(i2.even_part(), g2.Bivector)  # a bivector is purely even
    typing.assert_type(i2.odd_part(), g2.Scalar)
    rotor: g2.Rotor = g2.Vector.e_1 * g2.Vector.e_2
    typing.assert_type(rotor.even_part(), g2.Rotor)  # grades {0, 2} are both even
    typing.assert_type(rotor.odd_part(), g2.Scalar)


def test_even_odd_part_runtime_types() -> None:
    i2: g2.Bivector = 5 * (g2.Vector.e_1 ^ g2.Vector.e_2)
    assert type(i2.even_part()) is g2.Bivector
    assert i2.even_part().coeff_e_12 == 5
    assert type(i2.odd_part()) is g2.Scalar
    assert type((3 * g2.Vector.e_1).even_part()) is g2.Scalar  # vector has no even part


def test_contraction_static_types() -> None:
    # left/right contraction resolve their grade like the other products:
    # left keeps grade m-k (right-left), right keeps k-m; a negative grade -> g2.Scalar.
    a: g2.Vector = g2.Vector.e_1
    i2: g2.Bivector = g2.Vector.e_1 ^ g2.Vector.e_2
    typing.assert_type(a.left_contraction(a), g2.Scalar)  # vector ⌋ vector = dot
    typing.assert_type(a.left_contraction(i2), g2.Vector)  # vector ⌋ bivector (grade 1)
    typing.assert_type(i2.left_contraction(a), g2.Scalar)  # bivector ⌋ vector -> 0
    typing.assert_type(
        i2.right_contraction(a), g2.Vector
    )  # bivector ⌊ vector (grade 1)
    typing.assert_type(a.right_contraction(i2), g2.Scalar)  # vector ⌊ bivector -> 0
    # the < / > operators carry the same precise overloads
    typing.assert_type(a < a, g2.Scalar)
    typing.assert_type(a < i2, g2.Vector)
    typing.assert_type(i2 > a, g2.Vector)


def test_contraction_runtime_types_and_values() -> None:
    a: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    i2: g2.Bivector = 5 * (g2.Vector.e_1 ^ g2.Vector.e_2)
    # vector ⌋ vector is the dot product: 3*3 + 4*4 = 25
    assert type(a.left_contraction(a)) is g2.Scalar
    assert a.left_contraction(a).coeff_scalar == 25
    assert (a < a).coeff_scalar == 25  # operator agrees
    # e_1 ⌋ (5 e_12) = 5 e_2 ;  contraction asymmetry: (5 e_12) ⌋ e_1 == 0
    assert type(g2.Vector.e_1.left_contraction(i2)) is g2.Vector
    assert g2.Vector.e_1.left_contraction(i2).coeff_e_2 == 5
    assert (
        type(i2.left_contraction(g2.Vector.e_1)) is g2.Scalar
    )  # grade -1 -> g2.Scalar(0)
    assert (i2 > g2.Vector.e_1).coeff_e_2 == -5  # bivector ⌊ vector = -5 e_2


def test_dual_narrows_by_grade() -> None:
    # dual has no argument to overload on (its grade n−r is fixed by the operand
    # grade + dimension), so like even/odd_part the graded override *declares*
    # the resolved grade type -- no unsound Self cast.
    v3: g3.Vector = 3.0 * g3.Vector.e_1
    typing.assert_type(v3.dual(), g3.Bivector)  # grade 1 -> grade 2 in 3D
    i3: g3.Bivector = 5.0 * g3.Bivector.e_23
    typing.assert_type(i3.dual(), g3.Vector)  # grade 2 -> grade 1 in 3D
    t3: g3.Trivector = 7.0 * g3.Trivector.e_123
    typing.assert_type(t3.dual(), g3.Scalar)  # grade 3 -> grade 0
    r3: g3.Rotor = 1 + 2.0 * g3.Bivector.e_12
    typing.assert_type(r3.dual(), g3.G)  # {0,2} -> {3,1} = odd, no covering type

    # 2D duals: grade n−r with n=2.
    v2: g2.Vector = 3 * g2.Vector.e_1
    typing.assert_type(v2.dual(), g2.Vector)  # grade 1 -> grade 1
    i2: g2.Bivector = 5 * g2.Bivector.e_12
    typing.assert_type(i2.dual(), g2.Scalar)  # grade 2 -> grade 0
    rotor2: g2.Rotor = 1 + 2 * g2.Bivector.e_12
    typing.assert_type(rotor2.dual(), g2.Rotor)  # {0,2} -> {2,0} = {0,2}

    # per-algebra scalar duals: grade 0 -> that algebra's pseudoscalar (the whole
    # point of the per-algebra ScalarN split -- a shared Scalar couldn't type these).
    typing.assert_type(g1.Scalar(coeff_scalar=1).dual(), g1.Vector)
    typing.assert_type(g2.Scalar(coeff_scalar=1).dual(), g2.Bivector)
    typing.assert_type(g3.Scalar(coeff_scalar=1).dual(), g3.Trivector)


def test_dual_runtime_types_and_values() -> None:
    # e_23* = e_1 (g3.Bivector.dual really returns a g3.Vector -- the whole point).
    n: g3.Vector = g3.Bivector.e_23.dual()
    assert type(n) is g3.Vector
    assert n.coeff_e_1 == 1
    assert type(g3.Trivector.e_123.dual()) is g3.Scalar
    assert g3.Trivector.e_123.dual().coeff_scalar == 1
    assert type(g2.Bivector.e_12.dual()) is g2.Scalar
    # a fixed-dimension type's dual is at its own dimension: a mismatched n raises.
    with pytest.raises(ValueError, match="fixed at dimension 3"):
        g3.Bivector.e_23.dual(2)
    g3.Bivector.e_23.dual(3)  # the dimension itself is fine


def test_operator_runtime_types_and_values() -> None:
    a: g2.Vector = 3 * g2.Vector.e_1 + 4 * g2.Vector.e_2
    b: g2.Vector = g2.Vector.e_1 + 2 * g2.Vector.e_2
    # the runtime type has always been correct; here we pin it next to the static one
    assert type(a * b) is g2.Rotor
    assert type(a ^ b) is g2.Bivector
    assert type(a.inner_product(b)) is g2.Scalar
    assert type(a * 3) is g2.Vector
    # value equals the wedge coefficient e_1 e_2:  3*2 - 4*1 = 2
    assert (a ^ b).coeff_e_12 == 2
    # and the geometric product carries both scalar and bivector parts
    product: g2.Rotor = a * b
    assert product.coeff_scalar == 11  # 3*1 + 4*2
    assert product.coeff_e_12 == 2
