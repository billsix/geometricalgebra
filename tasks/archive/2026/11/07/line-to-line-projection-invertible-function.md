# A checked, invertible projection from one line to another, and the frame inverses rewritten with it

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "might there be value in making an
InvertibleFunction for project, given an from vector and to vector, that throws an ValueError forwards if
the input isn't on the from vector … and the same idea for the inverse? if we were to make that, could we
simplify the code we were just making?" · **Done:** 2026-11-07

## BLUF

Projection onto the line of `to`, restricted to the line of `from`, is invertible when the two are not
perpendicular, so it became `transforms.line_to_line_projection`, an `InvertibleFunction` that raises
`ValueError` on input off its line in either direction, with `transforms.coordinate_along` as the checked
reader for a vector's coordinate on a line. Both of `Frame`'s inverses are now the same statement with
different normals. All 803 tests pass, but the full suite takes 26:38 instead of 12:15. The math and the
timings are in `tasks/reference/frames-qr-and-reciprocal-frames.md`, "The code form: one line-to-line
projection".

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "1) whatever you recommend 2) sure 3) sure")

1. Name and home: `transforms.line_to_line_projection(from_vector=, to_vector=)`, matching
   `projection_rotation`'s keywords.
2. A checked coordinate reader, `transforms.coordinate_along`, replacing the unchecked
   `_projection_coefficient` (which took `.scalar_part()` of `p / w` and would have dropped a bivector
   part silently).
3. Both inverses rewritten, the reciprocal one included.

The maintainer also asked for a commit after each step, and, mid-task, for `coordinate_along`'s run of
guard `if`s to become one `match` with guarded cases and a total default (done).

## What changed

- `src/gacalc/transforms.py`: `coordinate_along` (zero line raises, the zero vector gives 0, off the line
  raises, otherwise `(vector / along).scalar_part()`) and `line_to_line_projection` (perpendicular lines
  raise at construction; forward `(x / from) * P(from)`, inverse `(z / P(from)) * from`, each through
  `coordinate_along`). Both take `float_close_to_zero`, passed on to `is_parallel_to` /
  `is_orthogonal_to`. Doctests; `tests/test_line_to_line_projection.py` (round trips over int, rational,
  float with the flag and symbolic `Gn`; off the line in each direction; perpendicular, zero and bivector
  arguments).
- `src/gacalc/frame.py`: a nested `term_and_coordinate(y, v, n)` returns `y`'s term along `v` and its
  coordinate, read through `n`; the peel uses `n = w_k` and subtracts the term, the reciprocal inverse uses
  `n = vⁱ`. `coefficients()` uses `coordinate_along`. A module-level `_has_float` turns the tolerance on
  for float input (two callers). The `to_invertible_function` docstring explains the shared statement
  first, then each method's `n`.
- Docs: the reference doc's new subsection, `CLAUDE.md`'s `transforms.py` line, `CHANGELOG.md`
  `[Unreleased]` › Added.

## Cost, measured (symbolic `Gn`, full `pytest` with doctests)

| | dot products (start of day) | projection coefficients | this task |
|---|---|---|---|
| full suite | 6:19 (776) | 12:15 (787) | 26:38 (803) |
| `test_inverse_methods_are_equivalent_symbolic[3d]` | 38 s | 151 s | 475 s |
| `test_composed_round_trip_is_identity_symbolic[3d-peel]` | 64 s | 200 s | 415 s |
| `test_composed_round_trip_is_identity_symbolic[3d-reciprocal]` | < 20 s | < 20 s | 282 s |
| `test_coefficients_are_triangular_with_unit_diagonal[frame_3d]` | 70 s | 190 s | 212 s |

Each inverse call now runs `is_orthogonal_to` and `is_parallel_to` and one more projection, and `Gn`
simplifies after each product and inverse. Raised with the maintainer.

## Gates

`entrypoint/format.sh` green after each commit; full `pytest` 803 passed (rc=0). The first doctest run
failed twice on the exact `ValueError` text (it contains the vectors' printed form); the examples match it
with `+ELLIPSIS`.

## Follow-ups created

`tasks/line-to-line-rejection-invertible-function.md` (the same for `reject`, with coordinate versions of
both line maps generated into `g1`–`g3`) and `tasks/vector-and-plane-invertible-project-reject.md`.
