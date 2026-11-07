# Extract the Kronecker delta into its own function

**Status:** in progress (2026-11-07)
**Priority:** 4
**Difficulty:** 1
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "could you extract Kronecker delta to
it's own function, with tests? and then use that as a function?"

## BLUF

Add `kronecker_delta(k, j) -> int` to `src/gacalc/frame.py`: `δ^k_j`, 1 when `j = k` and 0 otherwise
(the notation of H&S p. 28, eq 3.5). Give it doctests and tests, and use it where the reciprocal-frame
tests write `1 if j == k else 0` or a literal identity matrix. Done when the function and its tests
exist, the call sites use it, and `make test` and `make format` pass.

## Context

- `tests/test_frame.py`:
  - `test_reciprocal_frame_is_the_kronecker_delta_symbolic` writes `δ: int = 1 if j == k else 0`;
  - `test_reciprocal_frame_on_a_graded_type` compares against a literal identity matrix.
- `reciprocal_frame`'s docstring describes eq 3.5 in words. Its doctest's literal `[[1, 0], [0, 1]]`
  stays as it is, because a doctest shows the reader the values.
