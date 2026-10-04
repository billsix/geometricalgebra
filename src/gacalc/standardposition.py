"""Standard-position (frame-reduction) definitions of projection and rejection.

These are **deliberate duplicate definitions** alongside the canonical Hestenes
``project`` / ``reject`` in :mod:`gacalc.base` (see
``tasks/reference/reduction-to-standard-position.md``).  To project a vector ``a``
onto a vector ``b``, rotate ``b`` onto the ``e_1`` axis (standard position) using
**elementary coordinate-plane rotations**, keep the x-component of the aligned ``a``
(projecting onto the x-axis is just reading off a coordinate), and rotate back::

    project_sp(a, b) = unalign( x-component of align(a) · e_1 ),
        where align rotates b's xy-part onto the x-axis (zeroing b_y), then its
        xz-part onto the x-axis (zeroing b_z), so align(b) = |b|·e_1.

**No versors, no geometric product, no matrices** -- only the high-school 2D
rotation applied to a coordinate plane, one plane at a time ("break the vector into
its components, rotate the plane, add the axis component back").  Using a versor
would be circular: a versor *is* a geometric product, and the point of standard
position is to bootstrap the geometric product from projection/rejection using only
operations trusted independently of it.  This mirrors the matrix-free change-of-frame
in ``multivariate-math/proofs/crossproduct.tex``.

Proven **equal** to the canonical operations in
``proofs/GacalcProofs/StandardPosition.lean``: ``projectSP_eq_proj`` and
``rejectSP_eq_reject`` transcribe this module (``projectSP`` / ``rejectSP``, the same
``(cos, sin)`` formulas) and prove it equals the Hestenes ``proj`` / ``reject``, via
``proj_onto_x_axis`` (keep-the-x-component IS the projection onto ``|b|·e_1``),
projection-equivariance under each plane rotation, and the rotations' inverses.  The
derived variants carry an ``_sp`` / ``SP`` suffix in both languages (the stand-in for a
prime, which is not a legal Python identifier character).

Caveat: the ``e_1`` alignment is undefined when ``b`` lies along the ``z`` axis
(``b_x = b_y = 0``), because the first plane rotation would divide by ``|xy-part| =
0``.  The canonical ``project`` has no such restriction; use it, or align to a
different axis, in that case.
"""

from gacalc.base import MultiVectorBase


def _project_via_standard_position(
    a: MultiVectorBase, b: MultiVectorBase
) -> MultiVectorBase:
    cls = type(b)
    e_1: MultiVectorBase = cls.basis_vector(1)
    e_2: MultiVectorBase = cls.basis_vector(2)
    e_3: MultiVectorBase = cls.basis_vector(3)

    # b's coordinates (iteration yields the coefficient values in blade order)
    b_x, b_y, b_z = list(b)
    # magnitude of b's xy-part (numeric-preserving), and of b itself
    xy_magnitude = (b_x * e_1 + b_y * e_2).magnitude()
    magnitude = b.magnitude()

    # (cos, sin) read off b's own coordinates: the xy rotation that zeroes b_y,
    # then the xz rotation that zeroes b_z -- so align(b) = magnitude * e_1.
    cos_xy, sin_xy = b_x / xy_magnitude, -b_y / xy_magnitude
    cos_xz, sin_xz = xy_magnitude / magnitude, -b_z / magnitude

    def rotate_in_xy_plane(
        cos: object, sin: object, v: MultiVectorBase
    ) -> MultiVectorBase:
        x, y, z = list(v)
        return (cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2 + z * e_3

    def rotate_in_xz_plane(
        cos: object, sin: object, v: MultiVectorBase
    ) -> MultiVectorBase:
        x, y, z = list(v)
        return (cos * x - sin * z) * e_1 + y * e_2 + (sin * x + cos * z) * e_3

    def align(v: MultiVectorBase) -> MultiVectorBase:
        return rotate_in_xz_plane(cos_xz, sin_xz, rotate_in_xy_plane(cos_xy, sin_xy, v))

    def rotate_back(v: MultiVectorBase) -> MultiVectorBase:
        # inverse rotation = negate each sine, applied in the reverse order
        return rotate_in_xy_plane(
            cos_xy, -sin_xy, rotate_in_xz_plane(cos_xz, -sin_xz, v)
        )

    a_aligned: MultiVectorBase = align(a)
    # align(b) = magnitude * e_1, so projecting onto it is "keep the x-component":
    # no dot product, no geometric product -- just read off a coordinate.
    a_aligned_x, _a_aligned_y, _a_aligned_z = list(a_aligned)
    projected_in_standard_position: MultiVectorBase = a_aligned_x * e_1
    return rotate_back(projected_in_standard_position)


def project_sp(a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase:
    """Standard-position projection of vector ``a`` onto vector ``b`` (𝒢₃).

    Rotates ``b`` onto the ``e_1`` axis with elementary plane rotations, keeps the
    x-component of the aligned ``a``, and rotates back.  Equal to
    ``a.projected_onto(b)`` (the canonical Hestenes projection); the equality is the
    theorem ``projectSP_eq_proj`` in ``proofs/GacalcProofs/StandardPosition.lean``.

    Args:
        a: the vector being projected.
        b: the vector projected onto (must not lie along the ``z`` axis; see the
            module docstring).

    Returns:
        MultiVectorBase: the component of ``a`` along ``b`` — equal to
        ``a.projected_onto(b)``.
    """
    return _project_via_standard_position(a, b)


def reject_sp(a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase:
    """Standard-position rejection of vector ``a`` from vector ``b`` (𝒢₃).

    The perpendicular component ``a − project_sp(a, b)`` — equal to the canonical
    vector rejection ``a.rejected_away_from(b)`` (for vectors); the theorem is
    ``rejectSP_eq_reject`` in ``proofs/GacalcProofs/StandardPosition.lean``.

    Args:
        a: the vector being split.
        b: the vector rejected from (must not lie along the ``z`` axis; see the
            module docstring).

    Returns:
        MultiVectorBase: the component of ``a`` orthogonal to ``b``.
    """
    return a - project_sp(a, b)
