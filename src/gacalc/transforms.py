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

"""Representation-agnostic transform layer.

``InvertibleFunction`` wraps a function and its inverse (plus LaTeX labels) and
composes via ``compose`` / ``@``.  The transform *factories* (``translate``,
``uniform_scale``, ``scale_non_uniform``, ...) are **representation preserving**:
each derives any basis vectors it needs from the *type of the value it is applied
to* (via the ``MultiVectorBase`` interchange protocol --
``type(vector).basis_vector(i)``), so a ``G2`` in yields a ``G2`` out, a ``Gn``
in yields a ``Gn`` out, and so on.  Nothing here closes over a specific
representation's basis constants.

This module imports only ``base`` (the abstract base), never a concrete
representation, so it stays free of any single algebra.  ``gn.py`` re-exports
these names for backward compatibility.

Rotation is *derived from* the algebra, and packaged here three ways, all
free functions:  :func:`projection_rotation` is the from-vector/to-vector
*projection* formula (split the operand into in-plane + perpendicular parts,
turn the in-plane part), kept for teaching;  :func:`rotor_rotation` wraps the
same from/to rotation as a *rotor* sandwich (one fixed rotation);  and
:func:`plane_rotation` separates the two concerns the from/to form conflates
-- it takes two vectors that *define a plane* (their normalized wedge is the
plane's unit bivector ``i``) and returns a function of the angle, so one plane
established once yields any rotation angle on demand (and interpolation for
free).  The rotor *builder* ``MultiVectorBase.rotor_from_vectors(from, to)``
remains the algebra-level primitive.  (The very old planar 2D
``rotate(angle)`` / ``rotate_90_degrees`` / ``rotate_around`` factories were
removed long before: they acted only in the e_1 e_2 plane and silently
mis-transformed a vector with an e_3+ component -- ``plane_rotation`` is the
plane-explicit replacement.)

This module also carries an *animation* layer (``InvertibleFunction.at`` /
``steps`` plus the ``interpolate`` / ``components`` fields, ported from the
author's *modelviewprojection* book), a linear / affine / non-linear
classification (:class:`Linearity`, joined by ``compose``), and
:func:`to_matrix` (the homogeneous matrix of a linear/affine function).
"""

import math
import typing

import numpy as np
import sympy

from gacalc.base import Coef, MultiVectorBase, MultiVectorFn
from gacalc.functions import (
    ComposableFunction,
    InvertibleFunction,
    Linearity,
    NotInvertibleError,
    compose,
    identity,
    inverse,
)

#: Type variable for the values the GA-specific transform factories produce.
#: Bound to ``MultiVectorBase`` (each derives a basis from the value's own type);
#: the underlying ``functions`` layer uses an unbounded ``V``.
V = typing.TypeVar("V", bound=MultiVectorBase)


def compose_intermediate_fns(
    functions: list[InvertibleFunction[V]], relative_basis: bool = False
) -> typing.Iterable[InvertibleFunction[V]]:
    """Like ``compose``, but returns each of the partial compositions.

    Example:
        >>> from gacalc.transforms import (
        ...     compose_intermediate_fns,
        ...     InvertibleFunction,
        ... )
        >>> add2 = InvertibleFunction(lambda x: x + 2, "", lambda x: x - 2, "")
        >>> scale5 = InvertibleFunction(lambda x: x * 5, "", lambda x: x / 5, "")
        >>> # natural basis: scale5(add2(x))
        >>> fns = compose_intermediate_fns([add2, scale5])
        >>> len(fns)
        3
        >>> [fns[0](1), fns[1](1), fns[2](1)]
        [1, 5, 7]
        >>> # relative basis
        >>> fns = compose_intermediate_fns([add2, scale5], relative_basis=True)
        >>> [fns[0](1), fns[1](1), fns[2](1)]
        [1, 3, 7]
    """
    functions_with_identity_fn: list[InvertibleFunction[V]] = (
        [identity()] + functions if relative_basis else functions + [identity()]
    )

    return [
        compose(fs)
        for fs in (
            [
                functions_with_identity_fn[i:]
                for i in reversed(range(len(functions_with_identity_fn)))
            ]
            if not relative_basis
            else [
                functions_with_identity_fn[:i]
                for i in range(1, len(functions_with_identity_fn) + 1)
            ]
        )
    ]


def compose_intermediate_fns_and_fn(
    functions: list[InvertibleFunction[V]], relative_basis: bool = False
) -> list[tuple[InvertibleFunction[V], InvertibleFunction[V]]]:
    """Like ``compose_intermediate_fns``, paired with the function applied at each step.

    Example:
        >>> from gacalc.transforms import (
        ...     compose_intermediate_fns_and_fn,
        ...     InvertibleFunction,
        ... )
        >>> add2 = InvertibleFunction(lambda x: x + 2, "", lambda x: x - 2, "")
        >>> scale5 = InvertibleFunction(lambda x: x * 5, "", lambda x: x / 5, "")
        >>> for aggregate_fn, current_fn in compose_intermediate_fns_and_fn(
        ...         [add2, scale5]):
        ...     print(aggregate_fn(1), current_fn(1))
        1 5
        5 3
        7 1
    """
    return list(
        zip(
            compose_intermediate_fns(functions, relative_basis=relative_basis),
            [identity()] + functions
            if relative_basis
            else reversed([identity()] + functions),
        )
    )


def translate(b: V) -> InvertibleFunction[V]:
    """Translate by ``b``.  The result has the same representation as ``b``."""

    def f(vector: V) -> V:
        return vector + b

    def f_inv(vector: V) -> V:
        return vector - b

    tex_str: str = f"T_{{{b._repr_latex_()[1:-1]}}}"
    inv_str: str = f"T_{{{(-b)._repr_latex_()[1:-1]}}}"
    return InvertibleFunction(
        func=f,
        latex_repr=tex_str,
        inverse=f_inv,
        latex_repr_inv=inv_str,
        interpolate=lambda t: translate(b * t),
        linearity=Linearity.AFFINE,
    )


def projection_rotation(
    from_vector: V,
    to_vector: V,
) -> MultiVectorFn:
    r"""A rotation built by the **projection** formula: split the operand into its
    part *in* the ``from_vector ^ to_vector`` plane and its part perpendicular to
    it, turn the in-plane part through the angle from ``from_vector`` to
    ``to_vector``, and leave the perpendicular part fixed.

    Each of ``from_vector`` / ``to_vector`` is divided by its own magnitude
    *inside* the turn (not normalized up front), so their lengths cancel and this
    is a *pure* rotation (no scaling) whatever the inputs' magnitudes.  It is the
    projection formulation of the same rotation
    that :func:`rotor_rotation` produces via the rotor sandwich
    ``R v R.inverse()`` (``R = rotor_from_vectors(from_vector, to_vector)``); both
    agree.  This form is kept for teaching -- it makes the in-plane / perpendicular
    split explicit -- while ``rotor_rotation`` is the faster, more general path.
    Like every factory here it is representation-agnostic: the operand's own type
    supplies the basis, so a ``G2`` in yields a ``G2`` out, ``Gn`` yields ``Gn``.

    Example:
        >>> import math
        >>> from gacalc.transforms import projection_rotation
        >>> from gacalc.g3 import Vector3
        >>> to = math.cos(1.0) * Vector3.e_1 + math.sin(1.0) * Vector3.e_2
        >>> f = projection_rotation(Vector3.e_1, to)
        >>> f(Vector3.e_1).is_close(to)              # from -> to
        True
        >>> f(Vector3.e_3).is_close(Vector3.e_3)     # perpendicular fixed
        True
    """
    assert from_vector.is_vector()
    assert to_vector.is_vector()
    plane: MultiVectorBase = from_vector ^ to_vector
    representation = type(from_vector)

    components_in_plane = representation.project(plane)
    components_exterior_to_plane = representation.reject(plane)

    def r(value: MultiVectorBase) -> MultiVectorBase:
        assert value.is_vector()  # TODO - can this be generalized?
        return (
            components_in_plane(value) * from_vector.normalize() * to_vector.normalize()
        ) + components_exterior_to_plane(value)

    return r


def rotor_rotation(
    from_vector: V,
    to_vector: V,
    *,
    interpolate: typing.Optional[
        typing.Callable[[float], "InvertibleFunction[V]"]
    ] = None,
) -> InvertibleFunction[V]:
    r"""A rotation packaged as an :class:`InvertibleFunction`, built from the
    **rotor** ``R = rotor_from_vectors(from, to)``.

    The forward is the versor sandwich ``R v R^-1``; the inverse is ``R^-1 v R``
    (see ``MultiVectorBase.sandwich``).  Both return ``v``'s own type.
    ``linearity`` is ``LINEAR`` (a rotation fixes the origin), and it handles
    ``zero`` for free.  This is the *rotor* formulation of a rotation; the
    *projection* formulation lives at :func:`projection_rotation`.

    Its LaTeX label is fixed as ``R`` / ``R^{-1}`` (the rotor and its inverse).
    ``interpolate`` lets a caller (e.g. an angle-parameterized rotation) supply
    an interpolation law that from/to vectors alone can't express.

    Example:
        >>> import math
        >>> from gacalc.transforms import rotor_rotation
        >>> from gacalc.g3 import Vector3
        >>> to = math.cos(1.0) * Vector3.e_1 + math.sin(1.0) * Vector3.e_2
        >>> R = rotor_rotation(Vector3.e_1, to)
        >>> R.linearity.name
        'LINEAR'
        >>> R(Vector3.zero()).is_close(Vector3.zero())   # no crash on zero
        True
        >>> R.inverse(R(Vector3.e_1)).is_close(Vector3.e_1)
        True
    """
    rotor = type(from_vector).rotor_from_vectors(
        from_vector=from_vector, to_vector=to_vector
    )
    rotor_inv = rotor.inverse()

    def forward(v: V) -> V:
        return rotor.sandwich(v)

    def backward(v: V) -> V:
        return rotor_inv.sandwich(v)

    return InvertibleFunction(
        func=forward,
        latex_repr="R",
        inverse=backward,
        latex_repr_inv="R^{-1}",
        interpolate=interpolate,
        linearity=Linearity.LINEAR,
    )


def plane_rotation(
    a: V,
    b: V,
    *,
    latex_repr: typing.Callable[[Coef], str] | None = None,
    latex_repr_inv: typing.Callable[[Coef], str] | None = None,
) -> typing.Callable[[Coef], InvertibleFunction[V]]:
    r"""Establish a plane of rotation from two vectors; get back *angle ->
    rotation*.

    The from/to rotor form (:func:`rotor_rotation`,
    :func:`projection_rotation`) conflates two concerns: choosing the *plane*
    and choosing the *angle* (locked to the angle between the two vectors).
    This factory separates them.  ``a`` and ``b``'s only job is to define the
    plane: their wedge ``a ^ b`` is a simple bivector, and normalizing it
    gives the plane's unit bivector ``i`` (the "imaginary unit" of that
    plane: ``i * i == -1``).  The returned function takes an angle ``theta``
    and packages the rotation as an :class:`InvertibleFunction` whose forward
    is the half-angle rotor sandwich

    .. math:: R \, v \, \tilde{R}, \qquad
              R = \cos(\theta/2) - \sin(\theta/2)\, i

    and whose inverse is the same with ``-theta``.  Positive ``theta`` turns
    **from a toward b** (the wedge's orientation), so argument order is
    meaningful.  The perpendicular part of the operand is left fixed, in any
    dimension and any representation; the operand keeps its own type.
    Because the angle is a free parameter, interpolation falls out:
    ``rotation(theta).at(t)`` is ``rotation(t * theta)``.

    ``a`` and ``b`` must be (nonzero, non-parallel) *vectors*: a zero wedge
    means the two vectors span no plane -- the wedge-is-zero test IS the
    linear-dependence test.  A symbolic ``theta`` (a sympy expression) stays
    symbolic; a ``float`` theta stays numeric (see the coercion note in the
    body).  ``latex_repr`` / ``latex_repr_inv`` optionally map ``theta`` to
    the label of the returned function (a facade can brand its rotations,
    e.g. mvp's ``RX_{<theta>}``); the default is ``R_{theta}``.

    Example:
        >>> import math
        >>> from gacalc.transforms import plane_rotation
        >>> from gacalc.g3 import Vector3
        >>> turn = plane_rotation(Vector3.e_1, Vector3.e_2)
        >>> f = turn(math.radians(90))
        >>> f(Vector3.e_1).is_close(Vector3.e_2)          # e_1 -> e_2
        True
        >>> f(Vector3.e_3).is_close(Vector3.e_3)          # perpendicular fixed
        True
        >>> f.inverse(f(Vector3.e_1)).is_close(Vector3.e_1)
        True
        >>> f.at(0.5)(Vector3.e_1).is_close(               # interpolation
        ...     turn(math.radians(45))(Vector3.e_1))
        True
    """
    if not (a.is_vector() and b.is_vector()):
        raise TypeError(
            "plane_rotation takes two vectors (grade-1); "
            f"got grades {a.grades()} and {b.grades()}"
        )
    plane = a.outer_product(b)
    if plane == type(plane).zero():
        raise ValueError(
            "the two vectors are parallel (their wedge is zero): "
            "they span no plane of rotation"
        )
    i = plane.normalize()

    # Numeric-preservation guard (base.py's contract: a purely numeric
    # pipeline stays numeric).  Basis constants carry exact ``int``
    # coefficients, and normalize routes an int magnitude through sympy for
    # exactness -- so the unit bivector of e.g. ``e_1 ^ e_2`` comes back
    # with sympy Rational/One coefficients.  Left alone, every rotor built
    # from it mixes float trig with sympy numbers (``float * One`` is a
    # ``sympy.Float``), and the sandwich hands back vectors with sympy
    # coefficients -- silently turning ALL downstream game/demo arithmetic
    # into sympy object math (measured 2026-07-09: ~6x per add, and it
    # spreads to everything the rotated vector later touches).  So keep TWO
    # copies of the unit bivector: the exact one, and -- when every
    # coefficient is a numeric value (no free symbols) -- a float-coerced
    # one.  ``rotation`` picks per theta: numeric theta gets the float
    # plane (float rotors, float results); a symbolic theta keeps the
    # exact plane so notebook output stays ``cos(theta)``, not
    # ``1.0*cos(theta)``.  A genuinely symbolic plane never coerces.
    i_coefs = i.to_blade_dict()
    i_numeric: V | None = None
    if all(
        isinstance(c, (int, float)) or bool(getattr(c, "is_number", False))
        for c in i_coefs.values()
    ):
        i_numeric = type(i).from_blade_dict({b: float(c) for b, c in i_coefs.items()})

    def rotation(theta: Coef) -> InvertibleFunction[V]:
        # sympy trig for a symbolic angle, math trig for a numeric one --
        # keep a purely numeric pipeline numeric (see the magnitude() /
        # inverse() convention in base.py).
        if isinstance(theta, sympy.Expr):
            cos_half = sympy.cos(theta / 2)
            sin_half = sympy.sin(theta / 2)
            plane_i = i
        else:
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)
            # numeric theta: use the float-coerced plane (see above)
            plane_i = i_numeric if i_numeric is not None else i
        rotor = plane_i * (-sin_half) + cos_half

        def forward(v: V) -> V:
            return rotor.sandwich(v)

        def backward(v: V) -> V:
            # the rotor is unit, so the inverse rotor is its reverse
            # (= the -theta rotor).
            return rotor.reverse().sandwich(v)

        return InvertibleFunction(
            func=forward,
            inverse=backward,
            latex_repr=latex_repr(theta) if latex_repr else f"R_{{{theta}}}",
            latex_repr_inv=latex_repr_inv(theta)
            if latex_repr_inv
            else f"R_{{-({theta})}}",
            interpolate=lambda t: rotation(theta * t),
            linearity=Linearity.LINEAR,
        )

    return rotation


def uniform_scale(m: float) -> InvertibleFunction:
    """Scale uniformly by ``m`` (representation preserving -- just ``vector * m``)."""

    def f(vector: MultiVectorBase) -> MultiVectorBase:
        return vector * m

    def f_inv(vector: MultiVectorBase) -> MultiVectorBase:
        if m == 0.0:
            raise ValueError("Not invertible.  Scaling factor cannot be zero.")

        return vector * (1.0 / m)

    tex_str: str = f"S_{{{m}}}"
    inv_str: str = f"S_{{{-m}}}"
    # linear interpolation 1 -> m, so at(0) is the identity scale
    return InvertibleFunction(
        func=f,
        latex_repr=tex_str,
        inverse=f_inv,
        latex_repr_inv=inv_str,
        interpolate=lambda t: uniform_scale(1.0 + (m - 1.0) * t),
        linearity=Linearity.LINEAR,
    )


def scale_non_uniform(*factors: float) -> InvertibleFunction:
    """Scale axis ``i`` by ``factors[i]`` (1-indexed e_1, e_2, ...), in any dimension.

    Representation preserving: the basis vectors are taken from the type of the
    value being transformed, so a ``G2``/``G3``/``Gn`` value scales to its own
    type.  Pass two factors for the 2D case (``scale_non_uniform(m_x, m_y)``).
    """

    def f(vector: MultiVectorBase) -> MultiVectorBase:
        cls: type[MultiVectorBase] = type(vector)
        return sum(
            (
                m * cls.project(onto=cls.basis_vector(i + 1))(vector)
                for i, m in enumerate(factors)
            ),
            start=cls.zero(),
        )

    def f_inv(vector: MultiVectorBase) -> MultiVectorBase:
        if any(m == 0.0 for m in factors):
            raise ValueError("Not invertible.  Scaling factors cannot be zero.")

        cls: type[MultiVectorBase] = type(vector)
        return sum(
            (
                (1.0 / m) * cls.project(onto=cls.basis_vector(i + 1))(vector)
                for i, m in enumerate(factors)
            ),
            start=cls.zero(),
        )

    forward = "S_{" + ",".join(str(m) for m in factors) + "}"
    inv = "S_{" + ",".join(rf"\frac{{1}}{{{m}}}" for m in factors) + "}"
    return InvertibleFunction(
        func=f,
        latex_repr=forward,
        inverse=f_inv,
        latex_repr_inv=inv,
        interpolate=lambda t: scale_non_uniform(
            *[1.0 + (m - 1.0) * t for m in factors]
        ),
        linearity=Linearity.LINEAR,
    )


def to_matrix(
    fn: InvertibleFunction,
    cls: type[MultiVectorBase],
    n: typing.Optional[int] = None,
    *,
    backend: str = "numpy",
):
    r"""The homogeneous ``(n+1) x (n+1)`` matrix of a linear or affine ``fn``.

    Always homogeneous (4x4 for 3D), even for a purely linear map -- a linear
    map simply gets a zero translation column.  That is what graphics wants:
    one uniform matrix shape for the whole stack.

    Built by probing the basis and the origin (representation-agnostic, via the
    ``MultiVectorBase`` protocol)::

        column i (i < n) = fn(e_i) - fn(0)   # the linear part
        last column      = fn(0)             # translation (zero when linear)
        last row         = (0, ..., 0, 1)

    The translation lands in the **last column** (column-vector / premultiply
    convention), matching mvp's ``pyMatrixStack``.

    ``cls`` is the representation to probe in (``G2`` / ``G3`` / ``Gn`` / ...).
    ``n`` is taken from ``cls.DIMENSION`` for the specialized classes; pass it
    explicitly for the dimension-agnostic ``Gn``.

    ``backend="numpy"`` (default) returns an ``np.float32`` array for GL;
    ``backend="sympy"`` returns an exact ``sympy.Matrix`` (stays symbolic for a
    symbolic ``fn``).

    Raises ``ValueError`` if ``fn`` is non-linear: its projective part (e.g. a
    perspective divide) is not recoverable by probing points in R^n.

    Example:
        >>> from gacalc.transforms import translate, uniform_scale, to_matrix
        >>> from gacalc.g3 import Vector3
        >>> T = translate(2 * Vector3.e_1 + 3 * Vector3.e_2 + 4 * Vector3.e_3)
        >>> M = to_matrix(T, Vector3)
        >>> M.shape
        (4, 4)
        >>> [float(M[i, 3]) for i in range(4)]   # translation in the last column
        [2.0, 3.0, 4.0, 1.0]
        >>> # a linear map (scale) -> 4x4 with a ZERO translation column
        >>> S = to_matrix(uniform_scale(2.0), Vector3)
        >>> [float(S[i, 3]) for i in range(4)]
        [0.0, 0.0, 0.0, 1.0]
        >>> [float(S[i, i]) for i in range(4)]
        [2.0, 2.0, 2.0, 1.0]
    """
    if fn.linearity == Linearity.NONLINEAR:
        raise ValueError(
            "to_matrix is defined for linear/affine functions only; this one "
            "is non-linear (e.g. a perspective divide) -- its projective "
            "matrix cannot be recovered by probing points in R^n."
        )
    if n is None:
        n = getattr(cls, "DIMENSION", None)
        if n is None:
            raise ValueError(
                "n could not be inferred (Gn has no fixed DIMENSION); pass n "
                "explicitly, e.g. to_matrix(fn, Gn, n=3)."
            )

    origin = fn(cls.zero())  # image of the origin -> the last (translation) column
    # images of the unit directions -> the first columns (the linear part)
    directions = [fn(cls.basis_vector(i + 1)) - origin for i in range(n)]

    def coords(v: MultiVectorBase, bottom: int) -> list:
        # one full column: the n coordinates of v -- read straight from its
        # blade-dict (the coefficient each representation already stores; no
        # product to compute, no dependence on component/scalar_product) -- plus
        # the column's bottom entry (0 for a direction column, 1 for translation).
        d = v.to_blade_dict()
        return [d.get((j + 1,), 0) for j in range(n)] + [bottom]

    # the matrix's columns: each unit-direction image (bottom 0), then the origin
    # (translation, bottom 1).
    columns = [coords(d, 0) for d in directions] + [coords(origin, 1)]

    if backend == "sympy":
        return sympy.Matrix.hstack(*(sympy.Matrix(c) for c in columns))
    if backend == "numpy":
        return np.column_stack(
            [np.array([float(x) for x in c], dtype=np.float32) for c in columns]
        )
    raise ValueError(f"unknown backend {backend!r}; use 'numpy' or 'sympy'.")


__all__ = [
    "ComposableFunction",
    "InvertibleFunction",
    "Linearity",
    "NotInvertibleError",
    "inverse",
    "compose",
    "compose_intermediate_fns",
    "compose_intermediate_fns_and_fn",
    "identity",
    "translate",
    "projection_rotation",
    "rotor_rotation",
    "plane_rotation",
    "uniform_scale",
    "scale_non_uniform",
    "to_matrix",
    "MultiVectorFn",
]
