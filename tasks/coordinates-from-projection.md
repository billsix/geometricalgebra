# Build the line-to-line function and its coordinates from projection

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-14 (William Emerison Six <billsix@gmail.com>)

## BLUF

`transforms.line_to_line_projection` (the `InvertibleFunction` from one vector's line to another's)
and `transforms.coordinate_along` (the scalar `c` with `vector = c * along`) are built today by
**dividing by a vector**: `coordinate_along` returns `vector / along`, through `inverse` and the
geometric product. The maintainer wants them built from **projection** instead, project one vector
onto another and read the result from that, so they rest on an operation the book has already
built. Done means both are defined through `projected_onto` (or a named projection factory), the
behaviour, doctests and the frame code that uses them (`Frame.to_invertible_function`) are
unchanged, and `make test` / `make format` pass.

## Context

- `src/gacalc/transforms.py`: `coordinate_along` (the docstring says "dividing it by `along` then
  leaves the scalar `c`") and `line_to_line_projection` (`forward(x) = coordinate_along(x,
  from_vector) * shadow`, `backward(z) = coordinate_along(z, shadow) * from_vector`, where `shadow =
  from_vector.projected_onto(to_vector)`).
- Users: `src/gacalc/frame.py` (`Frame.to_invertible_function`, both inverse methods read each term
  with `line_to_line_projection`), `tests/test_line_to_line_projection.py`.
- Related: `tasks/line-to-line-rejection-invertible-function.md`,
  `tasks/vector-and-plane-invertible-project-reject.md`, and the reference
  `tasks/reference/frames-qr-and-reciprocal-frames.md`. CLAUDE.md's rule "Write the named geometric
  operation where the code means it" points the same way.
- A lead, not a decision: projection is linear, so for `x = c * from_vector` the forward map is just
  `x.projected_onto(to_vector)` (it equals `c * shadow`) and needs no coordinate at all. The
  backward map and `coordinate_along` itself still need a scalar read off a vector on a known line.

## Open questions

1. `coordinate_along`: how should the scalar come out of a projection? (a) the signed ratio of
   magnitudes, `|v| / |along|` with the sign from whether they point the same way (the cosine of
   the angle is ±1); (b) `projected_onto` followed by the existing division; (c) something you had
   in mind. Recommendation: (a), since it uses only magnitude and direction.
2. The backward map (from the shadow's line back to `from_vector`'s): is it in scope, given that it
   is not itself a projection?
3. Should the old division form survive as a documented duplicate (the "reduction to standard
   position" pattern of two definitions proven equal), or be replaced? Recommendation: replace, and
   keep a test asserting the two agree.
