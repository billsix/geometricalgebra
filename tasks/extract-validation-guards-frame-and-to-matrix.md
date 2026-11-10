# Pull validation out of `Frame.to_invertible_function` and `to_matrix` into one-line guards

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

The checks that opened `Frame.to_invertible_function`, `transforms.to_matrix` and
`transforms.to_matrix_template` moved into named `@validation_guard` functions, so each body opens
with one-line calls and reads as the task at hand:

- `frame.require_spanning_frame(vectors)` — the `k = n` check (`n` from `DIMENSION`, or the smallest
  dimension holding the vectors for `Gn`).
- `transforms.require_linear_or_affine(fn)` — a non-linear `fn` has no recoverable matrix.
- `transforms.require_dimension(cls, n) -> int` — returns `n` or `cls.DIMENSION`, raising when
  neither is known. It returns a value so the body stays `n = require_dimension(cls, n)` instead of
  repeating the `getattr` after a separate check.
- `transforms.require_distinct_params(params)` and `transforms.require_params_cover(matrix, params)` —
  the template's repeated-symbol and stray-symbol checks. The stray-symbol check used to raise from
  inside the matrix-reading loop; it now runs over the matrix once before the loop, which no longer
  raises.

Decision (William Emerison Six <billsix@gmail.com>, 2026-11-10): "update to matrix. Matrix" meant
`to_matrix`, `to_matrix_template` and the `ComposableFunction.to_matrix`/`.to_matrix_template`
methods. The methods forward to the `transforms` functions, so they get the guards with no code of
their own. The `inverse_method` default branch stayed in its `match`; the enum change
(`tasks/options-as-enums.md`) owns it.

Messages keep their meaning and start with the caller via `describe_caller()`. CHANGELOG `[Unreleased]`
→ Added. Gate (host): ruff + ty clean; the transforms/frame/functions doctests and
`tests/test_matrix_template.py`, `tests/test_frame.py`, `tests/test_transforms*.py` passed (168).
