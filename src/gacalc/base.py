# Copyright (c) 2025-2026 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


from __future__ import annotations

import abc
import functools
import itertools
import math
import numbers
import typing
from collections.abc import Callable, Generator, Sequence
from itertools import chain, combinations
from typing import TypeIs

import numpy as np
import sympy

BladeCoef = dict[tuple[int, ...], numbers.Real]
MultiVectorFn = Callable[["AbstractMultiVector"], "AbstractMultiVector"]


class AbstractMultiVector(abc.ABC):
    """Abstract base class for an element (multivector) of a geometric algebra.

    Concrete representations (Gn, and later G2/G3) implement a tiny interchange
    protocol -- ``from_blade_dict`` / ``to_blade_dict`` -- plus the core
    ``_geometric_product``.  Every representation-independent method here is
    written against that protocol, constructing results of the caller's own
    concrete type via ``type(self)``.  This is the abstraction boundary: only
    methods that touch the raw representation are reimplemented per subclass.
    """

    # No instance state of its own; empty slots so slotted subclasses (Gn,
    # G1/G2/G3 with ``slots=True``) don't inherit a __dict__ from the base.
    __slots__ = ()

    # ------------------------------------------------------------------
    # interchange protocol + construction (concrete subclasses implement
    # from_blade_dict / to_blade_dict; the rest is shared)
    # ------------------------------------------------------------------
    @classmethod
    @abc.abstractmethod
    def from_blade_dict(cls, blade_coef) -> typing.Self:
        """Build an instance of this representation from a blade->coef mapping."""

    @abc.abstractmethod
    def to_blade_dict(self) -> BladeCoef:
        """Return this multivector as a canonical blade -> coefficient mapping."""

    @classmethod
    def from_scalar(cls, scalar: int | float) -> typing.Self:
        return cls.from_blade_dict({tuple(): typing.cast(numbers.Real, scalar)})

    @classmethod
    def from_sympy_expr(cls, s: sympy.Expr) -> typing.Self:
        return cls.from_blade_dict({tuple(): typing.cast(numbers.Real, s)})

    @classmethod
    def zero(cls) -> typing.Self:
        return cls.from_scalar(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls.from_scalar(1)

    @classmethod
    def basis_vector(cls, i: int) -> typing.Self:
        """The i-th basis vector e_i of this representation (1-indexed).

        Part of the interchange protocol: lets representation-agnostic code
        (e.g. the transform layer) obtain a basis vector of the *caller's* own
        concrete type, so results stay in that type rather than coercing to Gn.
        """
        return cls.from_blade_dict({(i,): typing.cast(numbers.Real, 1)})

    @classmethod
    def unit_pseudoscalar(cls, n: int) -> typing.Self:
        """Unit pseudoscalar  i  =  e₁ e₂ … e_n  — the highest-grade unit blade of
        the n-dimensional algebra.
        """
        return math.prod(
            [cls.basis_vector(x) for x in range(1, n + 1)],
            start=cls.one(),
        )

    @classmethod
    def bases(cls, n: int) -> Generator[typing.Self]:
        def powerset(iterable: Sequence[int]) -> chain[tuple[int, ...]]:
            s: list[int] = list(iterable)
            # chain.from_iterable flattens the list of combinations
            return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

        yield from (
            math.prod(
                [cls.basis_vector(x) for x in b],
                start=cls.one(),
            )
            for b in powerset(range(1, n + 1))
        )

    @classmethod
    def symbolic_multivector(cls, n: int, prefix: str) -> typing.Self:
        mv: list[AbstractMultiVector] = list(cls.bases(n))
        symbols: list[sympy.Symbol] = sympy.symbols(prefix + ":" + str(len(mv)))
        return sum([s * blade for s, blade in zip(symbols, mv)], start=cls.zero())

    @classmethod
    def unit_pseudoscalar_squared(cls, n: int) -> typing.Self:
        unit_pseudoscalar: AbstractMultiVector = cls.unit_pseudoscalar(n)
        return unit_pseudoscalar * unit_pseudoscalar

    # ------------------------------------------------------------------
    # core product: scalar dispatch is shared, the multivector*multivector
    # case is the representation-specific primitive _geometric_product
    # ------------------------------------------------------------------
    @abc.abstractmethod
    def _geometric_product(self, rhs: AbstractMultiVector) -> typing.Self:
        """Geometric product  A B  (juxtaposition) — the fundamental product of the
        algebra, from which the inner product  A · B  and outer product  A ∧ B  are
        derived.  This is the representation-specific primitive.
        """

    def __mul__(self, rhs) -> typing.Self:
        match rhs:
            case int() | float() as n:
                return self._geometric_product(type(self).from_scalar(n))
            case sympy.Expr() as s:
                return self._geometric_product(type(self).from_sympy_expr(s))
            case _:
                return self._geometric_product(rhs)

    def __rmul__(self, lhs) -> typing.Self:
        match lhs:
            case int() | float() as n:
                return self._geometric_product(type(self).from_scalar(n))
            case sympy.Expr() as s:
                return self._geometric_product(type(self).from_sympy_expr(s))
            case _:
                # multivector*multivector is handled by __mul__; any other left
                # operand is unsupported -- defer so Python raises a clean
                # TypeError (the previous `-self._geometric_product(lhs)` was dead
                # and wrongly negated: the geometric product is not anticommutative).
                return NotImplemented

    # ------------------------------------------------------------------
    # shared arithmetic, all built on the interchange + primitives
    # ------------------------------------------------------------------
    def __add__(self, rhs) -> typing.Self:
        left: BladeCoef = self.to_blade_dict()
        right: BladeCoef = rhs.to_blade_dict()
        return type(self).from_blade_dict(
            {
                blade: (left.get(blade, 0) + right.get(blade, 0))
                for blade in (left.keys() | right.keys())
            }
        )

    def __sub__(self, rhs: typing.Self) -> typing.Self:
        return self + -rhs

    def __neg__(self) -> typing.Self:
        return -1 * self

    def __abs__(self) -> numbers.Real | sympy.Expr:
        return self.magnitude()

    def __iter__(self):
        d: BladeCoef = self.to_blade_dict()
        yield from (
            type(self).from_blade_dict({key: d[key]})
            for key in sorted(d.keys(), key=lambda b: (len(b), str(b)))
        )

    def magnitude(self) -> numbers.Real | sympy.Expr:
        """Magnitude  |A|  =  √(Ã ∗ A)  — the positive square root of the scalar
        product of A with its reverse.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.49
        """
        return sympy.sqrt(self.magnitude_squared())

    def magnitude_squared(self) -> numbers.Real:
        """Squared magnitude  |A|²  =  Ã ∗ A  =  ⟨Ã A⟩  (a scalar)."""
        return self.reverse().scalar_product(self)

    def normalize(self) -> typing.Self:
        """Unit multivector  Â  =  A / |A|  — A rescaled to magnitude 1."""
        return self * (abs(self) ** (-1))

    def component(self, x: typing.Self) -> numbers.Real:
        """Scalar coefficient of this multivector along the unit blade ``x``.

        For an orthonormal basis blade e_J (e.g. ``e_1`` or ``e_12``), the
        coefficient α_J in  A = Σ_J α_J e_J  is the scalar part of  A ẽ_J ,
        i.e. ⟨A x̃⟩₀ (ẽ_J = reverse(e_J) = e_J⁻¹ for a unit Euclidean blade,
        since e_J ẽ_J = 1).  So ``v.component(e_1)`` reads off v's e_1 coefficient
        and ``B.component(e_12)`` its e_12 coefficient (the reverse is what keeps
        the sign right for grade ≥ 2, where e_12 e_12 = −1).

        ``x`` is expected to be a unit basis blade — the named class constants
        (``Vector2.e_1``, ``Bivector2.e_12``, …) or ``gn.e_1`` are exactly these.
        For the blade-valued part instead of the scalar, see ``project``.
        """
        return (self * x.reverse()).scalar_part()

    def inner_product(self, rhs: typing.Self) -> typing.Self:
        """Inner (dot) product  A · B  — the lowest-grade part of the geometric
        product, ⟨A B⟩_|r−s| summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.21a, 1.21b, 1.21c
        """

        def inner_product_of_homogenous_multivectors(
            lhs: AbstractMultiVector, rhs: AbstractMultiVector
        ) -> AbstractMultiVector:
            # # 1.21b
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(abs(left_grade - right_grade))

        inner: AbstractMultiVector = sum(
            [
                inner_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
                if lg > 0 and rg > 0
            ],
            start=type(self).zero(),  # 1.21b
        )
        return typing.cast(typing.Self, inner)

    def dot(self, rhs: typing.Self) -> typing.Self:
        return self.inner_product(rhs)

    def outer_product(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  — the highest-grade part of the geometric
        product, ⟨A B⟩_(r+s) summed over the homogeneous grade-r, grade-s parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 6,
        equation 1.22a, 1.22b, 1.22c
        """

        def outer_product_of_homogenous_multivectors(
            lhs: AbstractMultiVector, rhs: AbstractMultiVector
        ) -> AbstractMultiVector:
            # 1.22a
            left_grade: int = lhs.max_grade()
            right_grade: int = rhs.max_grade()
            assert lhs.is_homogeneous_of_grade_r(left_grade)
            assert rhs.is_homogeneous_of_grade_r(right_grade)
            return (lhs * rhs).r_vector_part(left_grade + right_grade)

        # 1.22b
        # 1.22c, because unlike the inner_product, we keep grade 0s
        outer: AbstractMultiVector = sum(
            [
                outer_product_of_homogenous_multivectors(
                    self.r_vector_part(lg), rhs.r_vector_part(rg)
                )
                for lg, rg in itertools.product(self.grades(), rhs.grades())
            ],
            start=type(self).zero(),
        )
        return typing.cast(typing.Self, outer)

    def scalar_product(self, other: typing.Self) -> numbers.Real:
        """Scalar product  A ∗ B  =  ⟨A B⟩  — the grade-0 (scalar) part of the
        geometric product.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 13,
        equation 1.44
        """
        return (self * other).scalar_part()

    def wedge(self, rhs: typing.Self) -> typing.Self:
        """Outer (wedge) product  A ∧ B  (alias of ``outer_product``)."""
        return self.outer_product(rhs)

    def __xor__(self, other: typing.Self) -> typing.Self:
        """Operator form of the outer product:  a ^ b  ==  a ∧ b  ==  a.wedge(b)."""
        return self.wedge(other)

    @staticmethod
    def outer_product_of_vectors(
        *vectors: AbstractMultiVector,
    ) -> AbstractMultiVector:
        """Outer product of several vectors  a₁ ∧ a₂ ∧ … ∧ a_r  — a simple r-blade."""
        return functools.reduce(lambda a, b: a ^ b, vectors)

    def r_vector_part(self, r: int) -> typing.Self:
        """Grade-r part  ⟨A⟩ᵣ  — the r-vector (grade-r) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        d: BladeCoef = self.to_blade_dict()
        return type(self).from_blade_dict(
            {blade: d[blade] for blade in d.keys() if len(blade) == r}
        )

    def is_homogeneous_of_grade_r(self, r: int) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self.max_grade() == r and self.is_r_vector()

    def is_scalar(self) -> bool:
        """ """
        return self == self.r_vector_part(0)

    def is_r_vector(self) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self == self.r_vector_part(self.max_grade())

    def is_vector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=1)

    def is_bivector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=2)

    def is_trivector(self) -> bool:
        return self.is_homogeneous_of_grade_r(r=3)

    def is_orthogonal_to(
        self, other: typing.Self, float_close_to_zero: bool = False
    ) -> bool:
        """
        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 9,
        between equations 1.32 and 1.33
        """

        # TODO - defined for vectors only right now, it's probably defined more
        # generally later in the book
        assert self.is_vector()
        assert other.is_vector()

        return bool(
            np.isclose(
                float(self.inner_product(other).scalar_part()),
                float(0.0),
                rtol=1e-5,
                atol=1e-5,
            )
            if float_close_to_zero
            else (self.inner_product(other) == type(self).zero())
        )

    def is_parallel_to(
        self, other: typing.Self, float_close_to_zero: bool = False
    ) -> bool:
        """
        not sure if I'm doing this correctly
        """

        # TODO - defined for vectors only right now, it's probably defined more
        # generally later in the book
        assert self.is_vector()
        assert other.is_vector()

        return bool(
            np.isclose(float(self.cosine(other)), float(1.0), rtol=1e-5, atol=1e-5)
            if float_close_to_zero
            else (self.cosine(other) == 1)
        )

    def scalar_part(self) -> numbers.Real:
        """Scalar part  ⟨A⟩  =  ⟨A⟩₀  — the grade-0 (scalar) component of A.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 4
        """
        return self.to_blade_dict().get(tuple(), typing.cast(numbers.Real, 0))

    def grades(self) -> list[int]:
        return list(set(len(blade) for blade in self.to_blade_dict().keys()))

    def max_grade(self) -> int:
        return max(self.grades())

    def reverse(self) -> typing.Self:
        """Reverse  Ã  — reverses the order of the vector factors in each blade,
        giving the grade-r part the sign (−1)^(r(r−1)/2).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 5,
        equation 1.19
        """

        # supposedly, 1.19 works for simple r-vectors, but because of linearity
        # of the grade operator, it works for all multivectors
        return sum(
            [
                ((-1) ** ((r * (r - 1)) // 2)) * self.r_vector_part(r)
                for r in self.grades()
            ],
            start=type(self).zero(),
        )

    def inverse(self) -> typing.Self:
        """Inverse  A⁻¹  =  Ã / |A|²  — defined when |A|² ≠ 0.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18

        Not sure if I'm doing it correctly
        """
        # sympify the magnitude before the reciprocal: for the specialized
        # classes magnitude_squared() is a raw Python int, and ``int ** -1``
        # silently degrades to a float -- sympify keeps it exact (Rational).
        mag_sq = typing.cast(sympy.Expr, sympy.sympify(self.magnitude_squared()))
        return self.reverse() * (mag_sq ** (-1))

    def dual(self, n: int) -> typing.Self:
        """Dual  A*  =  A I⁻¹  — multiplication by the inverse unit pseudoscalar I,
        mapping a grade-r part to grade n−r.
        """
        return self * type(self).unit_pseudoscalar(n).inverse()

    def even_part(self) -> typing.Self:
        """Even part  A⁺  =  ⟨A⟩₀ + ⟨A⟩₂ + …  — the sum of the even-grade parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 0],
            start=type(self).zero(),
        )

    def odd_part(self) -> typing.Self:
        """Odd part  A⁻  =  ⟨A⟩₁ + ⟨A⟩₃ + …  — the sum of the odd-grade parts.

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 8
        """
        return sum(
            [self.r_vector_part(g) for g in self.grades() if g % 2 == 1],
            start=type(self).zero(),
        )

    def cosine(self, other: AbstractMultiVector) -> numbers.Real:
        """Cosine of the angle between A and B  —  cos θ  =  (Ã ∗ B) / (|A| |B|).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 14,
        equation 1.53b
        """
        return typing.cast(
            numbers.Real,
            self.reverse().scalar_product(other)
            * typing.cast(numbers.Real, abs(self) ** (-1))
            * typing.cast(numbers.Real, (abs(other) ** (-1))),
        )

    @classmethod
    def project(
        cls,
        onto: AbstractMultiVector | Sequence[AbstractMultiVector],
    ) -> MultiVectorFn:
        """Projection  P_B(A)  =  (A · B) B⁻¹  — the component of A lying in the
        subspace represented by the blade B (``onto``).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18,
        equations 2.9a, 2.9b, 2.9c
        """
        if isinstance(onto, Sequence):

            def is_multivector_sequence(
                val: Sequence[object],
            ) -> TypeIs[Sequence[AbstractMultiVector]]:
                return all(isinstance(x, AbstractMultiVector) for x in val)

            if is_multivector_sequence(onto):
                return cls.project(cls.outer_product_of_vectors(*onto))

        def fn(value: AbstractMultiVector) -> AbstractMultiVector:
            if value.is_scalar():  # 2.9b
                return value
            elif value.is_r_vector():  # 2.9c
                return (value.dot(onto)) * onto.inverse()
            else:
                return (value.dot(onto)).dot(onto.inverse())  # 2.9a

        return fn

    @classmethod
    def reject(
        cls,
        away_from: AbstractMultiVector | Sequence[AbstractMultiVector],
    ) -> MultiVectorFn:
        """Rejection  P_B^⊥(A)  =  (A ∧ B) B⁻¹  — the component of A orthogonal to
        the subspace represented by the blade B (``away_from``).

        from Hestenes and Sobczyk, Clifford Algebra to Geometric Calculus, page 18
        """

        def r(value: AbstractMultiVector) -> AbstractMultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(
                away_from, AbstractMultiVector
            )  # to satisfy type checking
            return (value.wedge(away_from)) * away_from.inverse()

        match away_from:
            case [*sequence]:
                return cls.reject(cls.outer_product_of_vectors(*sequence))
            case AbstractMultiVector() as away_from_vector if (
                away_from_vector.is_vector()
            ):
                return r
            case AbstractMultiVector() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(away_from))

    @classmethod
    def reflect(
        cls,
        across: AbstractMultiVector | Sequence[AbstractMultiVector],
    ) -> MultiVectorFn:
        """Reflection across the subspace (blade) ``across``  —  the projection
        minus the rejection,  P_B(A) − P_B^⊥(A).
        """
        components_in_plane: MultiVectorFn = cls.project(across)
        components_exterior_to_plane: MultiVectorFn = cls.reject(across)

        def r(value: AbstractMultiVector) -> AbstractMultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            assert isinstance(across, AbstractMultiVector)  # to satisfy type checking

            return components_in_plane(value) - components_exterior_to_plane(value)

        match across:
            case [*sequence]:
                return cls.reflect(cls.outer_product_of_vectors(*sequence))
            case AbstractMultiVector() as away_from_vector if (
                away_from_vector.is_vector()
            ):
                return r
            case AbstractMultiVector() as away_from_bivector if (
                away_from_bivector.is_bivector()
            ):
                return r
            case _:
                raise Exception("TODO - implement project for " + str(across))

    @staticmethod
    def identity() -> MultiVectorFn:
        def i(value: AbstractMultiVector) -> AbstractMultiVector:
            return value

        return i

    @classmethod
    def rotate(
        cls,
        from_vector: AbstractMultiVector,
        to_vector: AbstractMultiVector,
    ) -> MultiVectorFn:
        """Rotate by the angle from ``from_vector`` to ``to_vector``, in their plane.

        ``from_vector``/``to_vector`` are normalized first, so this is a *pure*
        rotation (no scaling): the in-plane part of a value is turned through the
        angle between them (the plane ``from_vector ∧ to_vector`` they span), the
        perpendicular part is left unchanged.  Equivalent to the rotor sandwich
        ``R v R.inverse()`` with ``R = rotor_from_vectors(from_vector, to_vector)``.
        """
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        from_vector = from_vector.normalize()
        to_vector = to_vector.normalize()
        plane: AbstractMultiVector = from_vector ^ to_vector

        components_in_plane: MultiVectorFn = cls.project(plane)
        components_exterior_to_plane: MultiVectorFn = cls.reject(plane)

        def r(value: AbstractMultiVector) -> AbstractMultiVector:
            assert value.is_vector()  # TODO - can this be generalized?
            return (
                components_in_plane(value) * from_vector * to_vector
            ) + components_exterior_to_plane(value)

        return r

    @classmethod
    def rotor_from_vectors(
        cls,
        from_vector: AbstractMultiVector,
        to_vector: AbstractMultiVector,
    ) -> AbstractMultiVector:
        """The rotor ``R = |from||to| + to from`` taking ``from`` toward ``to``.

        An (un-normalized) even multivector whose sandwich rotates: for any
        vector ``v``, ``R v R.inverse()`` equals ``rotate(from, to)(v)``.  ``R``
        is the half-angle rotor; because it is not normalized, ``R v R.reverse()``
        would also *scale* by ``R.magnitude_squared()`` -- using ``R.inverse()``
        (= ``R.reverse() / |R|^2``) divides that out, leaving a pure rotation.

        (Assumes ``from``/``to`` are not antiparallel; the construction
        degenerates only on that measure-zero case.)
        """
        assert from_vector.is_vector()
        assert to_vector.is_vector()
        scale = typing.cast(sympy.Expr, from_vector.magnitude() * to_vector.magnitude())
        # scalar + bivector -- the rotor's grade
        product: AbstractMultiVector = to_vector * from_vector
        return product + type(product).from_sympy_expr(scale)

    def is_close(self, other: typing.Self) -> bool:
        left: BladeCoef = self.to_blade_dict()
        right: BladeCoef = other.to_blade_dict()
        return all(
            [
                np.isclose(
                    float(left.get(blade, 0)),
                    float(right.get(blade, 0)),
                    rtol=1e-5,
                    atol=1e-5,
                )
                for blade in (left.keys() | right.keys())
            ]
        )

    def _repr_latex_(self):
        d: BladeCoef = self.to_blade_dict()

        def add_parens_or_dont(x):
            # Parenthesize a sum so its terms bind to the blade; render the
            # coefficient straight from the sympy/number object (no fragile
            # sympify(str(x)) round-trip).
            if isinstance(x, sympy.Expr) and x.is_Add:
                return "(" + sympy.latex(x) + ")"
            return sympy.latex(x)

        blades = [
            add_parens_or_dont(d[blade])
            + " ".join(map(lambda b: r"\mathbf{\vec{e}}_" + str(b), blade))
            if blade != tuple()
            else add_parens_or_dont(d[blade])
            for blade in sorted(d.keys(), key=lambda b: (len(b), str(b)))
        ]
        # latex_string = r"$\frac{1}{2}$"
        return "$" + ("0" if (self == type(self).zero()) else " +  ".join(blades)) + "$"
