# An invertible rejection from one line to another, with coordinate versions generated into g1–g3

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "make a follow up for doing something
similar for reject, making an invertible function. … And as part of those tasks, add them to be coordinate
versions in the generated code for g1 g2 g3 etc"
**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`
**Built on:** `tasks/archive/2026/11/07/line-to-line-projection-invertible-function.md` and
`tasks/archive/2026/11/14/coordinates-from-projection.md`.
**Next:** `tasks/vector-and-plane-invertible-project-reject.md`.

## Outcome

- **`transforms.line_to_line_rejection(from_vector=, away_from=, *, float_close_to_zero=False)`**: the
  rejection away from `away_from` restricted to the line of `from_vector`, an `InvertibleFunction`
  sending `c * a` to `c * R(a)` and back. It mirrors `line_to_line_projection` as reshaped by
  `coordinates-from-projection`: the forward map is the rejection itself (`x.rejected_away_from(n)`)
  after the on-line check, and the inverse reads the coordinate on the image line with
  `coordinate_along`. It raises `ValueError` at construction when the vectors are parallel (the
  rejection would squash the line to a point) or either is zero or not a vector, and on input off its
  line in either direction. Doctests cover the worked 2D example. `tests/test_line_to_line_rejection.py`
  covers the round trip over int, rational, float (with the flag) and symbolic `Gn`, the image's
  perpendicularity, and every error.
- **`transforms.require_on_line(vector, along)`**: the on-line check from `coordinates-from-projection`,
  made public (it was `_require_on_line`) and given a doctest, so the generated modules can import it.
  It is a `@validation_guard`, so its message names the caller and call site.
- **Generated coordinate versions** (`tools/gen_specialized.py`, `line_to_line_method_def`):
  `Vector.line_to_line_projection(to_vector=, *, float_close_to_zero=False)` in 𝒢₁–𝒢₃ and
  `Vector.line_to_line_rejection(away_from=, ...)` in 𝒢₂–𝒢₃, each typed `InvertibleFunction[Vector]`.
  Every dot product is written out over the `coeff_e_i` fields, and each division goes through
  `_reciprocal`, so int input stays exact. Each raises `TypeError` for an operand that is not this
  algebra's `Vector` (the `rotate_90_degrees` convention) and `ValueError` as the factory does. Every
  generated module now imports `Linearity` and `require_on_line`. The method is emitted from a source
  template (template-splice) because its body is two nested closures. `tests/test_line_to_line_generated.py`
  checks both directions against the factory on the `Gn` reference with fully symbolic vectors in every
  algebra, plus exactness, errors, the operand check, and that 𝒢₁ has no rejection.
- Docs: CHANGELOG `[Unreleased]` › Added; CLAUDE.md's `transforms.py` and generated-modules entries.
- Also fixed: a doctest line from `coordinates-from-projection` that broke ruff's E501 (the expected
  `ValueError` line was 97 columns). That task's gate log had reported it, but I only searched the log for
  `ty` errors; the line is now `ValueError: ...forward (...): ... is not on the line of ...`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "3) ok 4) ok")

1. **Shape of the generated version:** a method on the generated `Vector`,
   `a.line_to_line_projection(to_vector=n)` / `a.line_to_line_rejection(away_from=n)`, returning an
   `InvertibleFunction[Vector]`, with the coordinate formulas inside; the `transforms` factories stay the
   representation-agnostic reference.
2. **𝒢₁:** generate the projection version only; the rejection can never be built there.

## Judgment calls made during the work

- **Forward map is the rejection itself**, not `coordinate_along(x, from_vector) * shadow` as the plan
  said. `coordinates-from-projection` (done first, same day) moved the projection version to this shape,
  and the two factories stay parallel.
- **`require_on_line` is public**, like `require_vector` / `require_frame`, rather than a private
  `_require_on_line` imported across modules.
- **The generated methods keep the on-line checks as calls to `require_on_line` and
  `is_parallel_to` / `is_orthogonal_to`**, not as written-out wedge components. Only the maps' values
  are closed forms; the checks stay shared so their messages and float tolerance match the factories.
- **The symbolic test vectors are typed `typing.Any`**, with the reason in the helper's docstring: the
  algebra is chosen at run time, and the methods exist only on the generated `Vector`.
