# `is_close` → `isclose` — symmetric, float-only

**Status:** DONE 2026-08-02. Work record; the durable rationale + the standard-
practice research live in `tasks/reference/approximate-float-equality.md`.
Created 2026-07-21 (started as an "assess is_close" study; the original study is
kept below for history).

## Outcome (2026-08-02, Bill's decisions)

Reworked the approximate-equality predicate and **renamed** it `is_close` →
**`isclose`** (signals float-only). Final shape:

- **Symmetric** — per-blade **`math.isclose`** (PEP 485,
  `abs(a-b) <= max(rel_tol*max(|a|,|b|), abs_tol)`) instead of the old asymmetric
  `np.isclose`. `numpy` is no longer imported by the generated modules.
- **`abs_tol` defaults to `0.0`** (matching `math.isclose`); **all ~72 current
  callers updated to pass `abs_tol=1e-5`** explicitly (Bill's call: honest default,
  near-zero tolerance visible at each call site). `rel_tol` defaults to `1e-5`
  (looser than stdlib's `1e-9`, to absorb geometric-op float error).
- **Floating-point only** — a symbolic (free-symbol) coefficient now raises a clear
  `TypeError` via the new `_require_float` helper in `base.py`, instead of the
  opaque bare-`float()` crash. Pure-number sympy still passes. Use `==` for
  exact/symbolic.
- Earlier this session (a)+(b): genexpr + tolerance params — subsumed into the
  above (params are now `rel_tol`/`abs_tol`, matching `math.isclose`).

Touched: `base.py` (`isclose` + `_require_float`),
`tools/gen_specialized.py` (`is_close_method`, `generate_scalar`, `isclose_call`,
generated header imports), all callers in `src/gacalc/{functions,transforms}.py`
doctests and 6 test files, and new `tests/test_isclose.py`.

Gates: ruff + ty (src/tests/tools) clean; **336 tests pass**; deterministic;
doc-region markers OK.

---

*Original study (2026-07-21) below.*

## What `is_close` is trying to do

Approximate ("close enough") equality of two multivectors, for the **numeric** case where exact
`==` is wrong because floating-point results never land exactly. It compares blade-by-blade, over
the *union* of present blades (a blade absent on one side is treated as `0`), with `np.isclose`
(`rtol=atol=1e-5`). The base version (`base.py`) is the reference; the generated classes override
with a field-wise `np.isclose` fast path and fall back to `super().is_close` for a different type.

```python
def is_close(self, other):
    left, right = self.to_blade_dict(), other.to_blade_dict()
    return all(
        [
            np.isclose(
                float(left.get(b, 0)), float(right.get(b, 0)), rtol=1e-5, atol=1e-5
            )
            for b in left.keys() | right.keys()
        ]
    )
```

The intent is sound and the union-with-0 handling is correct.

## Does it do it effectively? — three real issues

1. **It silently breaks on symbolic coefficients.** `float(left.get(blade, 0))` raises `TypeError`
   on a sympy expression that isn't a pure number. So `is_close` is **numeric-only** — for a
   library whose whole selling point is symbolic *and* numeric, calling `is_close` on symbolic
   multivectors crashes rather than doing something sensible. That's a sharp edge (either
   intended-but-undocumented, or a gap).
2. **Unnecessary list inside `all(...)`.** `all([… for …])` builds the whole list before testing;
   a generator expression (`all(np.isclose(…) for …)`) is lazy and short-circuits on the first
   mismatch. Pure win.
3. **Tolerance is hard-coded** (`1e-5`) with no way to pass `rtol`/`atol`. Fine as a default, but
   callers with different scales can't adjust.

## What else could be done (options)

- **(a) Genexpr** instead of the list — trivial, do regardless.
- **(b) Optional `rtol`/`atol` params** (defaulting to `1e-5`) — small, ergonomic.
- **(c) Handle symbolic** — when a coefficient isn't numeric, either (i) fall back to *exact*
  equality on the symbolic difference (`(self - other).simplified()` is zero — reuses machinery
  the library already has), or (ii) document "`is_close` is numeric-only; use `==` for symbolic"
  and raise a clear error instead of a bare `float()` `TypeError`. Option (i) makes `is_close` a
  single "are these the same value?" predicate across both modes.
- **(d) Reframe as "difference is negligible":** `abs(self - other) < tol` (the *norm* of the
  difference) is one scalar test instead of per-component — arguably cleaner, but changes the
  semantics (aggregate vs per-coefficient) and interacts with (c)'s symbolic story. Probably not
  worth it; per-coefficient `isclose` is the conventional, more-diagnostic choice.

## Recommendation

Do **(a)** and **(b)** unconditionally (cheap, clearly better). For **(c)**, decide between "make
it work symbolically via exact-diff fallback" (nicer, a bit more code) vs "numeric-only with a
clear error + a docstring line" (honest, minimal). My lean: **(a)+(b)+(c-i)** — a genexpr, tolerance
params, and a symbolic fallback to exact-difference equality — so `is_close` is one predicate that
does the right thing in both modes.

## Open questions

1. Symbolic behavior: **(c-i)** exact-diff fallback, or **(c-ii)** numeric-only with a clear error?
   (My lean: c-i.)

## Note

Since `is_close` is defined on `base.py` and *overridden* in the generated classes, any change
touches both the reference (`base.py`, hand-written) and the generator's `is_close_method`
(`tools/gen_specialized.py`) — keep them consistent.
