# `Frame.to_invertible_function`: does `term_and_coordinate` still earn its place?

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com> asked: "is def term_and_coordinate
still needed? … isn't there something else in the code that calculates this stuff?")

## BLUF

`term_and_coordinate(y, v, m)`, nested in `Frame.to_invertible_function` (`src/gacalc/frame.py`),
reads one frame coordinate. Both inverses use it: the reciprocal inverse keeps only `[1]`, and the
peel uses both halves. It is a thin composition of two library functions that already exist,
`transforms.line_to_line_projection` and `transforms.coordinate_along`, and it computes each
coordinate twice. Decide the form, then simplify. Done means the helper is gone or reduced to one
honest step, results are unchanged, the frame tests (slow peel cases included) pass, and the frames
reference doc matches.

## Context (read first)

- **The helper today:**

  ```python
  term = line_to_line_projection(from_vector=v, to_vector=m, float_close_to_zero=tolerant).inverse(
      y.projected_onto(m))
  return term, coordinate_along(term, along=v, float_close_to_zero=tolerant)
  ```

  It was written in `b95b1c7` (2026-11-07, "Frame: both inverses read each term through
  line_to_line_projection"). That was a deliberate choice: the term is "the point on `v`'s line
  whose projection onto `m` matches `y`'s", read with the named operation
  (`tasks/reference/frames-qr-and-reciprocal-frames.md`, "The code form: one line-to-line
  projection").
- **The redundancy.** In `src/gacalc/transforms.py`, `line_to_line_projection`'s inverse is
  `backward(z) = from_vector * coordinate_along(z, along=shadow)`, where `shadow = v.projected_onto(m)`.
  So the inverse already computes the coordinate `c = coordinate_along(P_m(y), along=P_m(v))` and
  returns `c * v`. `term_and_coordinate` then reads the same `c` back out of `c * v` with a second
  `coordinate_along`, including another "on the line" check. Per coordinate, that is two
  `coordinate_along` calls and two line checks for one number.
- **Callers:**
  - `backward_by_reciprocal` uses only the coordinate (`[1]`);
  - `backward_by_peel` uses the term (to subtract it) and the coordinate.

  The term is always `coordinate * v`.
- **Related library code:** `Frame.coefficients()` already reads its table with the same kind of
  expression, `coordinate_along(v.projected_onto(w), along=w)`.
- **House rules that bear on it:** `CLAUDE.md`:
  - "Write the named geometric operation where the code means it" (the reciprocal frame's `vⁱ · y`
    is named there as an allowed dot-product exception);
  - "Names: inline what is used once" (the helper has two callers).

## Options

- **(a) One coordinate function, no inverse.**
  `coordinate(y, v, m) = coordinate_along(y.projected_onto(m), along=v.projected_onto(m))`: the
  ratio of the two projections ("two heights, one divided by the other", as the docstring already
  says). One `coordinate_along` call per coordinate. The peel forms its term as `x * v`. It still
  uses only named operations (projection, coordinate along a line), but no longer says
  "line-to-line projection".
- **(b) Keep the line-to-line-projection reading, return one thing.** The helper returns only the
  term, `line_to_line_projection(v, m).inverse(y.projected_onto(m))`. The peel subtracts it, and
  both read the coordinate with `coordinate_along(term, along=v)`. This drops the tuple and `[1]`,
  but keeps the double computation.
- **(c) Inline it into both callers.** There are two callers, so the expression would appear twice.
  Not recommended.
- **(d) A library function in `transforms`** for "the coordinate of `y` along `v`, read through
  `m`", for example `oblique_coordinate(y, along=v, through=m)`. It would replace the helper and
  could serve `Frame.coefficients()` too. This adds public API, so it would need a changelog entry.

## Plan

1. Settle the open questions.
2. Change `src/gacalc/frame.py` (and `transforms.py` under (d)). The docstring's "Both read a
   coordinate the same way" paragraph and the reference doc's "The code form" section say which
   form the code uses.
3. Gates:
   - `tests/test_frame_class.py` including the slow peel and reciprocal cases (about 27 minutes for
     all seven);
   - `tests/test_frame.py`;
   - the `frame.py` doctests;
   - container `make format` / `make test`.

## Open questions

1. **Which form:** (a) one `coordinate` function as the ratio of two projections (recommended:
   fewest steps, still named operations), (b) keep the line-to-line-projection inverse but return
   only the term, or (d) a new `transforms` library function?
2. **Under (a) or (b): keep the line-to-line framing in the reference doc** as the geometric
   explanation, even though the code reads the ratio directly? Recommended: yes, as the "why"
   beside the code's "how".
