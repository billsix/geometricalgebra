# `is_close` → `isclose` — symmetric, float-only

**Created:** 2026-07-21 · **Completed:** 2026-08-02

The task started as a study of `is_close` and ended in a rework. The durable rationale and the
standard-practice research live in `tasks/reference/approximate-float-equality.md`.

## What changed (the maintainer's decisions, 2026-08-02)

The approximate-equality predicate was reworked and **renamed** `is_close` → **`isclose`** (the
name signals float-only):

- **Symmetric:** per-blade **`math.isclose`** (PEP 485,
  `abs(a-b) <= max(rel_tol*max(|a|,|b|), abs_tol)`) replaced the old asymmetric `np.isclose`.
  The generated modules no longer import `numpy`.
- **`abs_tol` defaults to `0.0`** (matching `math.isclose`); all ~72 callers were updated to pass
  `abs_tol=1e-5` explicitly (the maintainer's call: an honest default, with the near-zero
  tolerance visible at each call site). `rel_tol` defaults to `1e-5` (looser than stdlib's
  `1e-9`, to absorb geometric-op float error).
- **Floating-point only:** a symbolic (free-symbol) coefficient raises a clear `TypeError` via a
  new `_require_float` helper in `base.py`, instead of the opaque bare-`float()` crash.
  Pure-number sympy still passes; `==` is the predicate for exact/symbolic values.
- The list inside `all(...)` became a generator expression (lazy, short-circuits), and the
  hard-coded `1e-5` became the `rel_tol`/`abs_tol` parameters.

Touched: `base.py` (`isclose` + `_require_float`), `tools/gen_specialized.py`
(`is_close_method`, `generate_scalar`, `isclose_call`, generated header imports), all callers in
the `src/gacalc/{functions,transforms}.py` doctests and 6 test files, and a new
`tests/test_isclose.py`. The base version (hand-written reference) and the generator's
`is_close_method` override were kept consistent.

## Alternatives considered (the 2026-07-21 study)

The old `is_close` compared blade-by-blade over the union of present blades (absent = `0`) with
`np.isclose(rtol=atol=1e-5)`; the union-with-0 handling was correct. Its issues: it crashed on
symbolic coefficients (`float()` on a sympy expression), built a list inside `all(...)`, and
hard-coded the tolerance.

- **Symbolic handling:** (c-i) fall back to exact equality on the simplified difference, or
  (c-ii) numeric-only with a clear error. The study leaned c-i; the maintainer chose **c-ii**
  (the `_require_float` error above).
- **"Difference is negligible"** (`abs(self - other) < tol`, one norm test) was rejected: it
  changes the semantics from per-coefficient to aggregate, and per-coefficient comparison is the
  conventional, more diagnostic choice.

## Verification

ruff + ty (src/tests/tools) clean; 336 tests passed; generation deterministic; doc-region markers
OK.
