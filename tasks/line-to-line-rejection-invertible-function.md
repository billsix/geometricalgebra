# An invertible rejection from one line to another, with coordinate versions generated into g1–g3

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "make a follow up for doing something
similar for reject, making an invertible function. … And as part of those tasks, add them to be coordinate
versions in the generated code for g1 g2 g3 etc"
**Depends on:** `tasks/line-to-line-projection-invertible-function.md` (it adds
`transforms.line_to_line_projection` and `transforms.coordinate_along`; build this on that shape).
**Next:** `tasks/vector-and-plane-invertible-project-reject.md`.

## BLUF

`line_to_line_projection(from_vector=a, to_vector=n)` restricts the projection onto `n` to the line of
`a`. The rejection has the same structure: `reject(away_from=n)` restricted to the line of `a` sends
`c * a` to `c * R_n(a)`, a line-to-line bijection whenever `a` is **not parallel** to `n`. Add
`transforms.line_to_line_rejection(from_vector=, away_from=)`, an `InvertibleFunction` that raises
`ValueError` on input off its line in either direction, and generate coordinate (closed-form) versions of
both line-to-line maps into `g1`/`g2`/`g3`. Done = the factory with doctests and tests, the generated
methods agreeing with the `Gn` reference, `make check-generated` and `make check-regions` green, and the
changelog entry.

## Context

- The projection version and its checks: `src/gacalc/transforms.py` (`line_to_line_projection`,
  `coordinate_along`), tests in `tests/test_line_to_line_projection.py`. Its record will be
  `tasks/archive/2026/11/07/line-to-line-projection-invertible-function.md` once archived.
- `MultiVectorBase.reject` (`src/gacalc/base.py`), H&S eq 2.9's complement `P^⊥_B(A) = A − P_B(A)`; the
  dot/wedge reading: `tasks/reference/dot-wedge-projection-rejection.md`.
- The checks: `is_parallel_to` (the domain check and the "parallel ⇒ not invertible" guard; its zero
  case raises) and `is_orthogonal_to`, both with `float_close_to_zero`.
- Generated code: `tools/gen_specialized.py` builds each `g*.py` as `ast` nodes. Existing closed-form
  vector methods to copy the pattern from: `cross` (𝒢₃, the `cross_stub` emitter) and 𝒢₂'s
  `rotate_90_degrees` (method + module-level `InvertibleFunction` factory). The method docstrings come from
  `CUSTOM_METHOD_DOCS`. Read `tasks/reference/code-generator-architecture.md` and CLAUDE.md "Code
  generation" (generate first, read the real output, never hand-edit `g*.py`).

## The math

- Forward: `c * a ↦ c * R_n(a)`; inverse: `d * R_n(a) ↦ d * a`. Both read the coordinate with
  `coordinate_along`, as the projection version does.
- Not invertible when `a ∥ n` (`R_n(a) = 0`): raise `ValueError` at construction.
- **𝒢₁:** every vector is parallel to every other, so the rejection version always raises there. Decide
  whether `g1` gets the method at all (Open question 2).
- **Coordinate versions:** in 𝒢₂ with `a = (a_1, a_2)`, `n = (n_1, n_2)`, the rejection of `a` is
  `((a ∧ n) / n)`, a closed form in the coordinates; the generated method computes the image vector and the
  coordinate directly, without the general inverse. Same for the projection, `((a · n) / |n|²) * n`.
  Exactness rules as everywhere: int → exact rational, float stays float (CLAUDE.md, `magnitude`/`inverse`).

## Plan

1. `transforms.line_to_line_rejection(from_vector=, away_from=, *, float_close_to_zero=False)` with
   doctests (a worked 2D example, off-the-line raises) and `tests/test_line_to_line_rejection.py`
   (round trip on each line over int, rational, float with the flag, symbolic `Gn`; off-line raises in
   each direction; parallel raises; zero/non-vector raise).
2. Generator: emit the coordinate versions of `line_to_line_projection` and `line_to_line_rejection` in
   `g2`/`g3` (and `g1` per Open question 2), per Open question 1's shape. `make generate`, read the emitted
   code, then tests that each generated version equals the `transforms` one (and `Gn`) on symbolic input.
3. `make check-generated`, `make check-regions`, `make format`, full `make test`; `CHANGELOG.md`
   `[Unreleased]` › Added; CLAUDE.md's `transforms.py` and generated-modules lines.

## Open questions

1. **Shape of the generated version.** Recommended: a method on the generated `Vector`,
   `a.line_to_line_projection(to_vector=n)` / `a.line_to_line_rejection(away_from=n)`, returning the
   `InvertibleFunction` typed `InvertibleFunction[Vector]`, with the coordinate formulas inside; the
   `transforms` factories stay the representation-agnostic reference. The alternative is module-level
   factories in each `g*.py`, like `g2.rotate_90_degrees()`.
2. **𝒢₁.** Recommended: generate the projection version (it is the identity on the one line, scaled), and
   leave the rejection version out of `g1`, since it can never be built there.
