# Extract the Kronecker delta into its own function 

**Completed:** 2026-11-07

Requested by William Emerison Six <billsix@gmail.com>, 2026-11-07: "could you extract Kronecker delta to
it's own function, with tests? and then use that as a function?"

## What was done

- **`gacalc.frame.kronecker_delta(k, j) -> int`**, next to `reciprocal_frame`: `δ^k_j`, 1 when `j = k`
  and 0 otherwise.
  - `k` is the upper index (the reciprocal vector) and `j` the lower (the frame vector), as in H&S p. 28,
    eq 3.5, `a^k · a_j = δ^k_j`.
  - Its doctests show a diagonal value, an off-diagonal value, and the 3×3 identity.
  - `reciprocal_frame`'s docstring links to it.
- **Used in `tests/test_frame.py`:**
  - `test_reciprocal_frame_is_the_kronecker_delta_symbolic` replaces its inline `1 if j == k else 0`;
  - `test_reciprocal_frame_on_a_graded_type` replaces its literal identity matrix with a `k, j` loop
    over `kronecker_delta(k, j)`;
  - `reciprocal_frame`'s doctest keeps its literal `[[1, 0], [0, 1]]`, so the reader sees the values.
- **`test_kronecker_delta`** checks:
  - 1 on the diagonal;
  - 0 off it, with specific pairs;
  - symmetry;
  - that `[δ^k_j]` over `1 … 4` is `sympy.eye(4)`.

  It does not restate the implementation's own conditional.
- `CHANGELOG.md` `[Unreleased]` Added entry.
