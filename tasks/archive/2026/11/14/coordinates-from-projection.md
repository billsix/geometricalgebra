# Build the line-to-line function and its coordinates from projection

**Created:** 2026-11-14 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`

## Outcome

`transforms.coordinate_along` and the forward map of `transforms.line_to_line_projection` were
built by dividing by a vector. Both now rest on projection, with no change in behaviour:

- **`coordinate_along(v, along=a)`** returns the factor of the projection
  `P(v) = (v · a) * a⁻¹ = (v · a⁻¹) * a`, computed as `v.dot(a.inverse()).scalar_part()`. `v` is
  on the line, so it is its own projection and that factor is its coordinate. The docstring
  derives it and states the equal signed-ratio form `c = (|v| / |a|) * cos(θ)`, `cos(θ) = ±1`.
- **The forward map** is the projection itself, `x.projected_onto(to_vector)`, after a check that
  `x` is on `from_vector`'s line. The check is a new private guard `_require_on_line` (marked
  `@validation_guard`), shared by `coordinate_along` and the forward map. Its message names the
  caller and the call site through `describe_caller`, so the wording changed from
  `coordinate_along: … is not on the line of …` to `coordinate_along (transforms.py:N): …` (or
  `line_to_line_projection.<locals>.forward (…): …`). The doctests were updated to match.
- **The backward map** is unchanged (out of scope by decision).
- Test: `tests/test_line_to_line_projection.py::test_coordinate_along_agrees_with_division` checks
  that the new coordinate equals the old `(vector / along).scalar_part()` on int, float,
  opposite-direction and symbolic input.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-14)

1. `coordinate_along` is the signed ratio of magnitudes (option (a) of the three offered).
2. The backward map is out of scope.
3. The division form is replaced, not kept as a duplicate; a test asserts the two agree.

## Judgment calls made during the work

- **Decision 1 is implemented in its dot-product form.** The approved option was the signed ratio
  `|v| / |along|` with the sign of the cosine. Computing `|v| / |a|` literally takes two square
  roots, which turns exact rationals into radicals and leaves symbolic input as nested `sqrt`s
  (`Frame`'s symbolic 3-D tests depend on rational coordinates). That would break CLAUDE.md's
  rule against trading a square-root-free primitive for one with `√` noise. The value is the
  same quantity: `(v · a) / |a|² = (|v| / |a|) * cos(θ)`. So the code computes the square-root-free
  form, and the docstring presents the ratio of magnitudes as what it equals.
- **`v · a⁻¹`, not `(v · a) / |a|²` in Python arithmetic.** The first try divided two `Real`s
  outside the algebra. A symbolic `Gn` input then gave `(c*a_1**2 + c*a_2**2) / (a_1**2 + a_2**2)`,
  which sympy does not cancel, so `== c` failed. Computing in the algebra, through `inverse`, keeps
  each representation's own exact/float/symbolic handling, as the division did.
- **Why `make test-full` was the gate.** `Frame.to_invertible_function`'s inverses read every term
  with `line_to_line_projection`, and the symbolic frame tests are marked `slow`, so the everyday
  `make test` would not have exercised them.
