"""Standard-position (frame-reduction) definitions of projection and rejection.

These are **deliberate duplicate definitions** alongside the canonical Hestenes
``project`` / ``reject`` in :mod:`gacalc.base` (see
``tasks/reference/reduction-to-standard-position.md``).  To project a vector ``a``
onto a vector ``b``, rotate ``b`` onto the ``e_1`` axis (standard position) using
**elementary coordinate-plane rotations**, keep the x-component of the aligned ``a``
(projecting onto the x-axis is just reading off a coordinate), and rotate back::

    project_sp(a, b) = unalign( x-component of align(a) · e_1 ),
        where align rotates b's xy-part onto the x-axis (zeroing b_y), then its
        xz-part onto the x-axis (zeroing b_z), so align(b) = |b| * e_1.

**No versors, no geometric product, no matrices** -- only the high-school 2D
rotation applied to a coordinate plane, one plane at a time ("break the vector into
its components, rotate the plane, add the axis component back").  Using a versor
would be circular: a versor *is* a geometric product, and the point of standard
position is to bootstrap the geometric product from projection/rejection using only
operations trusted independently of it.  This mirrors the matrix-free change-of-frame
in ``multivariate-math/proofs/crossproduct.tex``.

Each plane rotation copies that plane's two coordinates into a 𝒢₂ vector, rotates it
there, and writes the pair back, leaving the third coordinate alone.  The 2D rotation
is the book's ``eq-rotate-formula`` (``book/docs/proof-rotate.rst``), a blend of the
vector and its quarter turn::

    rotate(v) = cos * v + sin * v.rotate_90_degrees(),

with ``cos`` and ``sin`` read off the coordinates of the two vectors the rotation
turns between (``book/docs/proof-rotate-from-a-to-b.rst``); no angle is computed.
The quarter turn is :meth:`gacalc.g2.Vector.rotate_90_degrees`, ``(x, y) -> (-y, x)``.

Proven **equal** to the canonical operations in
``proofs/GacalcProofs/StandardPosition.lean``: ``projectSP_eq_proj`` and
``rejectSP_eq_reject`` transcribe this module (``projectSP`` / ``rejectSP``, built
on the same 2D rotation) and prove it equals the Hestenes ``proj`` / ``reject``, via
``proj_onto_x_axis`` (keep-the-x-component IS the projection onto ``|b| * e_1``),
projection-equivariance under each plane rotation, and the rotations' inverses.  The
derived variants carry an ``_sp`` / ``SP`` suffix in both languages (the stand-in for a
prime, which is not a legal Python identifier character).

When ``b`` lies along the ``e_3`` axis its xy shadow is the zero vector, and the
first rotation, from zero to zero, is the identity; ``project_sp`` / ``reject_sp`` are
defined for every nonzero ``b``.
"""

from collections.abc import Callable

from gacalc import g2
from gacalc.base import MultiVectorBase, Real


def _rotation_from_to(u: g2.Vector, w: g2.Vector) -> Callable[[g2.Vector], g2.Vector]:
    """The 2D rotation turning ``u``'s direction onto ``w``'s.

    Written as the book writes it, a blend of the vector and its quarter turn,
    ``cos * v + sin * v.rotate_90_degrees()``, with ``cos`` and ``sin`` read off the
    coordinates of ``u`` and ``w``.  From the zero vector to the zero vector is the
    identity; from zero to nonzero, or nonzero to zero, raises ``ValueError``.

    Args:
        u: the vector the rotation starts from.
        w: the vector whose direction it ends at.

    Returns:
        Callable[[g2.Vector], g2.Vector]: the rotation.

    Raises:
        ValueError: if exactly one of ``u`` and ``w`` is zero.

    Examples:
        >>> from gacalc.g2 import Vector, e_1, e_2
        >>> _rotation_from_to(1 * e_1, 2 * e_2)(3 * e_1 + 4 * e_2) == -4 * e_1 + 3 * e_2
        True
        >>> _rotation_from_to(Vector.zero(), Vector.zero())(3 * e_1) == 3 * e_1
        True
        >>> _rotation_from_to(Vector.zero(), 1 * e_1)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...cannot rotate between the zero vector and a nonzero vector...
    """
    MultiVectorBase.require_rotation_endpoints(u, w)
    if u == g2.Vector.zero():
        return lambda v: v
    scale: Real = u.magnitude() * w.magnitude()
    cos: Real = (u.coeff_e_1 * w.coeff_e_1 + u.coeff_e_2 * w.coeff_e_2) / scale
    sin: Real = (u.coeff_e_1 * w.coeff_e_2 - u.coeff_e_2 * w.coeff_e_1) / scale

    def rotate(v: g2.Vector) -> g2.Vector:
        # rotate_90_degrees swaps coordinates, (x, y) -> (-y, x); it does not
        # multiply by e_12, so this rotation uses no geometric product.
        return g2.Scalar(cos) * v + g2.Scalar(sin) * v.rotate_90_degrees()

    return rotate


def _project_via_standard_position(
    a: MultiVectorBase, b: MultiVectorBase
) -> MultiVectorBase:
    MultiVectorBase.require_vectors([a, b])
    cls: type[MultiVectorBase] = type(b)
    if b == cls.zero():
        raise ValueError("project_sp: cannot project onto the zero vector")
    e_1: MultiVectorBase = cls.basis_vector(1)
    e_2: MultiVectorBase = cls.basis_vector(2)
    e_3: MultiVectorBase = cls.basis_vector(3)

    def coordinates(v: MultiVectorBase) -> tuple[Real, Real, Real]:
        # The three coordinates, zeros included (iterating a Gn omits them).
        return v.coefficient(e_1), v.coefficient(e_2), v.coefficient(e_3)

    def in_xy_plane(
        rotation: Callable[[g2.Vector], g2.Vector], v: MultiVectorBase
    ) -> MultiVectorBase:
        x: Real
        y: Real
        z: Real
        x, y, z = coordinates(v)
        rotated: g2.Vector = rotation(x * g2.e_1 + y * g2.e_2)
        return rotated.coeff_e_1 * e_1 + rotated.coeff_e_2 * e_2 + z * e_3

    def in_xz_plane(
        rotation: Callable[[g2.Vector], g2.Vector], v: MultiVectorBase
    ) -> MultiVectorBase:
        x: Real
        y: Real
        z: Real
        x, y, z = coordinates(v)
        rotated: g2.Vector = rotation(x * g2.e_1 + z * g2.e_2)
        return rotated.coeff_e_1 * e_1 + y * e_2 + rotated.coeff_e_2 * e_3

    b_x: Real
    b_y: Real
    b_z: Real
    b_x, b_y, b_z = coordinates(b)
    # First the xy plane: b's shadow there swings onto the x axis.  Then the xz
    # plane: the pair (|shadow|, b_z) swings onto the x axis, so align(b) = |b| * e_1.
    shadow: g2.Vector = b_x * g2.e_1 + b_y * g2.e_2
    shadow_on_x_axis: g2.Vector = shadow.magnitude() * g2.e_1
    tilt: g2.Vector = shadow.magnitude() * g2.e_1 + b_z * g2.e_2
    tilt_on_x_axis: g2.Vector = b.magnitude() * g2.e_1

    def align(v: MultiVectorBase) -> MultiVectorBase:
        return in_xz_plane(
            _rotation_from_to(tilt, tilt_on_x_axis),
            in_xy_plane(_rotation_from_to(shadow, shadow_on_x_axis), v),
        )

    def rotate_back(v: MultiVectorBase) -> MultiVectorBase:
        # Each rotation is undone by the one between the same vectors, the other
        # way round; the two are undone in the reverse order.
        return in_xy_plane(
            _rotation_from_to(shadow_on_x_axis, shadow),
            in_xz_plane(_rotation_from_to(tilt_on_x_axis, tilt), v),
        )

    # align(b) = |b| * e_1, so projecting onto it is "keep the x-component":
    # no dot product, no geometric product -- just read off a coordinate.
    projected_in_standard_position: MultiVectorBase = align(a).coefficient(e_1) * e_1
    return rotate_back(projected_in_standard_position)


def project_sp(a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase:
    """Standard-position projection of vector ``a`` onto vector ``b`` (𝒢₃).

    Rotates ``b`` onto the ``e_1`` axis with elementary plane rotations, keeps the
    x-component of the aligned ``a``, and rotates back.  Equal to
    ``a.projected_onto(b)`` (the canonical Hestenes projection); the equality is the
    theorem ``projectSP_eq_proj`` in ``proofs/GacalcProofs/StandardPosition.lean``.

    Args:
        a: the vector being projected.
        b: the nonzero vector projected onto.

    Returns:
        MultiVectorBase: the component of ``a`` along ``b`` — equal to
        ``a.projected_onto(b)``.

    Raises:
        ValueError: if ``a`` or ``b`` is not a vector, or ``b`` is zero.

    Examples:
        Projecting onto a coordinate axis keeps that one coordinate; only the
        direction of ``b`` matters, not its length:

        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> project_sp(3 * e_1 + 4 * e_2, 1 * e_1) == 3 * e_1
        True
        >>> project_sp(3 * e_1 + 4 * e_2, 5 * e_1) == 3 * e_1
        True
        >>> project_sp(3 * e_1 + 4 * e_2 + 5 * e_3, 2 * e_2) == 4 * e_2
        True

        A general ``b`` agrees with the canonical projection:

        >>> b = 3 * e_1 + 4 * e_2 + 12 * e_3
        >>> a = 1 * e_1 + 2 * e_2 + 3 * e_3
        >>> project_sp(a, b) == a.projected_onto(b)
        True

        Along the ``e_3`` axis the first rotation turns zero into zero, the
        identity, so ``b`` may lie there too:

        >>> project_sp(a, 1 * e_3) == a.projected_onto(e_3)
        True
        >>> project_sp(a, 0 * e_3)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: project_sp: cannot project onto the zero vector
    """
    return _project_via_standard_position(a, b)


def reject_sp(a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase:
    """Standard-position rejection of vector ``a`` from vector ``b`` (𝒢₃).

    The perpendicular component ``a − project_sp(a, b)`` — equal to the canonical
    vector rejection ``a.rejected_away_from(b)`` (for vectors); the theorem is
    ``rejectSP_eq_reject`` in ``proofs/GacalcProofs/StandardPosition.lean``.

    Args:
        a: the vector being split.
        b: the nonzero vector rejected from.

    Returns:
        MultiVectorBase: the component of ``a`` orthogonal to ``b``.

    Raises:
        ValueError: if ``a`` or ``b`` is not a vector, or ``b`` is zero.

    Examples:
        Rejecting from a coordinate axis drops that one coordinate and keeps the
        rest; as with projection, the length of ``b`` does not matter:

        >>> from gacalc.g3 import e_1, e_2, e_3
        >>> reject_sp(3 * e_1 + 4 * e_2, 1 * e_1) == 4 * e_2
        True
        >>> reject_sp(3 * e_1 + 4 * e_2, 5 * e_1) == 4 * e_2
        True

        A general ``b`` agrees with the canonical rejection:

        >>> b = 3 * e_1 + 4 * e_2 + 12 * e_3
        >>> a = 1 * e_1 + 2 * e_2 + 3 * e_3
        >>> reject_sp(a, b) == a.rejected_away_from(b)
        True
    """
    return a - project_sp(a, b)
