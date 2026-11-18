# `Frame.to_invertible_function`: does `term_and_coordinate` still earn its place?

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; overnight batch
`overnight-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-18 (the maintainer asked: "is def term_and_coordinate still needed? … isn't
there something else in the code that calculates this stuff?")

## Outcome

The answer was no. `term_and_coordinate` composed two library functions,
`transforms.line_to_line_projection` and `transforms.coordinate_along`. The inverse of the first
already computes the coordinate, `coordinate_along(P_m(y), along=P_m(v))`, and returns it times `v`.
The helper then read the same coordinate back out of `c * v` with a second `coordinate_along`, so
every coordinate was computed twice and line-checked twice. The reciprocal inverse also used only
the coordinate (`[1]`).

`src/gacalc/frame.py` now has one nested `coordinate(y, v, m)`:

```python
coordinate_along(
    y.projected_onto(m), along=v.projected_onto(m), float_close_to_zero=...
)
```

- The reciprocal inverse uses it directly.
- The peel uses `x_last = coordinate(y, v=v, m=w)` and subtracts `v * x_last`.
- The `line_to_line_projection` import is gone from `frame.py`.
- The docstring's "Both read a coordinate the same way" paragraph now leads with the ratio and keeps
  the line-to-line reading as the geometric explanation.

Docs updated to match:
- `tasks/reference/frames-qr-and-reciprocal-frames.md`: "The code form: the coordinate of one
  projection along another" (renamed from "… one line-to-line projection"; its cross-reference
  updated). It keeps the line-to-line geometry and records the earlier double computation.
- `CLAUDE.md`: the `frame.py` layout line.

Results are unchanged.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Form (a): one coordinate function, the ratio of the two projections.
2. Keep the line-to-line framing in the reference doc as the geometric explanation.

## Verification

- ruff and `ty check` were clean on `frame.py`.
- The `frame.py` doctests, `tests/test_frame.py`, `tests/test_frame_svd.py` and the fast
  `tests/test_frame_class.py` cases passed (98).
- All seven slow `tests/test_frame_class.py` cases passed (symbolic 3D round trips, reciprocal
  equals peel) in 25 min 2 s. The same seven took 26 min 46 s with the double computation.
