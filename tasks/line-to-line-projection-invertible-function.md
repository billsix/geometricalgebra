# A checked, invertible projection from one line to another, and the frame inverses rewritten with it

**Status:** in progress — the maintainer approved it and answered the open questions (William Emerison
Six <billsix@gmail.com>, 2026-11-07)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "might there be value in making an
InvertibleFunction for project, given an from vector and to vector, that throws an ValueError forwards if
the input isn't on the from vector (obviously a flag for booleans for close enough, but symbolically
they'd have to be on the same vector), and the same idea for the inverse? if we were to make that, could
we simplify the code we were just making?"

## BLUF

Yes on both counts, with one cost. Projection onto the line of `to`, restricted to the line of `from`, is
invertible whenever `from` and `to` are not perpendicular, so it can be an `InvertibleFunction` that raises
`ValueError` on input off its line (in either direction). It turns both of `Frame`'s inverses into the same
one-line geometric statement: **the `v_i`-component of `y` is the point on `v_i`'s line whose projection
onto `n` matches `y`'s**, with `n = w_i` for the peel and `n = vⁱ` for the reciprocal frame. Done =
the factory with tests and doctests, the two inverses (and `_projection_coefficient`) rewritten with it,
the 3D symbolic test time measured before and after, and the reference doc updated.

## Context

- Today's code: `src/gacalc/frame.py`, `_projection_coefficient(v, onto=w) = (v.projected_onto(w) /
  w).scalar_part()`, used by `Frame.coefficients()` and the peel step of `Frame.to_invertible_function`;
  `backward_by_reciprocal` reads `x_i = vⁱ · y`. Record of that work:
  `tasks/archive/2026/11/07/name-the-geometric-operation-over-its-formula.md`.
- The math: `tasks/reference/frames-qr-and-reciprocal-frames.md`, "Why one dot product reads off an
  oblique coordinate: similar right triangles" (`x_i = (n̂·y)/(n̂·v_i)`, with `n̂` normal to the face of
  the other frame vectors).
- The "is it on the line" check exists: `MultiVectorBase.is_parallel_to(other, float_close_to_zero=False)`
  (`src/gacalc/base.py`), the wedge-zero test, exact by default, `np.isclose`-tolerant with the flag
  (machine-checked in `proofs/GacalcProofs/Predicates3D.lean`). The same flag name is used by
  `is_orthogonal_to` and `frame.are_linearly_independent`.
- `InvertibleFunction(func=, latex_repr=, inverse=, latex_repr_inv=, linearity=)`:
  `src/gacalc/functions.py`. `MultiVectorBase.project` returns a non-invertible `ComposableFunction`,
  correctly, because a projection of the whole space throws the rejection away.

## The finding (research, 2026-11-07)

**The map.** For vectors `a` (from) and `n` (to) with `a · n ≠ 0`, let `L(x) = P_n(x)` on the line of
`a`. A point `c * a` goes to `c * P_n(a)`, a nonzero multiple of `n`, so `L` is a bijection between the
two lines; its inverse sends `d * P_n(a)` back to `d * a`. Both directions are "divide by the line's
spanning vector, multiply by the other's": `L(x) = (x / a) * P_n(a)` and
`L⁻¹(z) = (z / P_n(a)) * a`. Each is checked with `is_parallel_to` first. If `a · n = 0`, `P_n(a) = 0`
and the factory raises `ValueError` (the projection squashes the line to a point).

**Why it fits the frame inverses.** If `n` is perpendicular to every frame vector except `v_i`, then
`P_n(y) = Σ_j x_j * P_n(v_j) = x_i * P_n(v_i)`, which is on `L`'s codomain line. So

    x_i * v_i  =  L⁻¹(P_n(y))      with L = the line-to-line projection from v_i to n

- **Peel:** `n = w_i` for the last vector (perpendicular to the earlier ones). The step becomes "take the
  `v_last`-component, subtract it, recurse", and the code subtracts a vector instead of `x_last * v`.
- **Reciprocal:** `n = vⁱ` (perpendicular to every `v_j`, `j ≠ i`, by eq 3.5). The same statement, so
  the two inverses differ only in which normal they use, which is the reference doc's similar-triangles
  argument written as code.
- Checked on the doc's worked example (`v_1 = 2 * e_1`, `v_2 = 1 * e_1 + 3 * e_2`, `y = 3 * e_1 + 3 * e_2
  = 1 * v_1 + 1 * v_2`) with `g2`: `n = w_2`, `n = v²`, `n = v¹` each give `x = 1`; `n = w_1`, which is
  not perpendicular to `v_2`, gives `3/2`, the wrong coordinate, as expected.

**What it does not simplify.**

- The coordinate is still read off a vector on a known line (`(x_i * v_i) / v_i`). The checked
  `L⁻¹` makes that safe: today's `_projection_coefficient` takes `.scalar_part()` of `p / w` and would
  silently drop a bivector part if `p` were not parallel to `w`. A small checked "coordinate along `a`"
  (`c * a ↦ c`, raising off the line) is the natural partner; decide whether it is its own function.
- The forward map `e_i ↦ v_i` is not a projection (projecting `e_i`'s line onto `v_i`'s gives
  `(e_i·v_i)/|v_i|² * v_i`, not `v_i`), so it stays `Σ x.coefficient(e_i) * v_i`.
- `Frame.coefficients()` (the QR table) could be written as `L⁻¹` with `a = w_j`, `n = w_j`, which is just
  the projection: no gain there.

**Cost.** More products and inverses than today. On symbolic `Gn`, which simplifies after each, the 3D
tests will likely get slower again (today's projection form already doubled them; see the archived task
above). Measure, as last time.

## Plan

1. Factory: `line_to_line_projection(from_vector=a, to_vector=n, *, float_close_to_zero=False)` in
   `src/gacalc/transforms.py` (beside `projection_rotation`, which takes the same keyword pair), returning
   `InvertibleFunction[MultiVectorBase]`, `Linearity.LINEAR`. Guard `require_vector` on both arguments;
   `ValueError` for `a · n = 0`, and from `func`/`inverse` for input off the line, naming the function.
   Doctests: the worked example, an off-line input raising, a float input within tolerance.
2. Tests: round trip on each line (exact ints, symbolic 2D, floats with the flag), off-line raises in each
   direction, perpendicular `from`/`to` raises.
3. Measure `tests/test_frame.py` + `tests/test_frame_class.py` on the current code.
4. Rewrite `backward_by_peel` and `backward_by_reciprocal` with it; replace `_projection_coefficient` if
   the checked coordinate reader (Open question 2) covers it. Run the full suite; measure again.
5. Update `tasks/reference/frames-qr-and-reciprocal-frames.md` (the similar-triangles section gains the
   code form) and `CLAUDE.md`'s `transforms.py` line; `CHANGELOG.md` `[Unreleased]` › Added.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "1) whatever you recommend 2) sure 3) sure")

1. **Name and home:** `transforms.line_to_line_projection(from_vector=, to_vector=)`, matching
   `projection_rotation`'s keywords.
2. **A checked coordinate reader:** yes, `transforms.coordinate_along(…)`, returning `c` for `c * a` and
   raising `ValueError` off the line; it replaces `_projection_coefficient`.
3. **Both inverses** are rewritten with the line-to-line projection, the reciprocal one included.

The maintainer asked for a commit after each step.

## Open questions

None.

## Related question answered while scoping (2026-11-07)

The maintainer asked whether `MultiVectorBase.coefficient(blade)` should be replaced by the new
projection helper. No: `coefficient` reads the stored component on a basis blade of any grade straight
from the blade dict, with no product. For a unit basis vector it agrees with the projection reading
(`P_{e_i}(x) = x.coefficient(e_i) * e_i`), but the projection form would be slower and vector-only.
The helper solves the other problem: a coefficient along a vector that is not a basis vector.
