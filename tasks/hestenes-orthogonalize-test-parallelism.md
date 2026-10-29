# Test the reverse-based Hestenes orthogonalize by parallelism, not by the scaling factor

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3  (test rewrite; the geometric assertion must still be exact/symbolic)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

The tests for the original (reverse-based) `make_orthogonal_frame_hestenes` currently assert the
**exact scaling relationship** `c_k == |A_{k-1}|² * w_k` against the rejection result `w_k`. That
obscures the geometric point — the two produce the **same directions** — behind a magnitude factor a
reader has to compute and reverse-engineer. Rewrite those assertions to test that each `c_k` is
**parallel** to the corresponding `w_k` (scaling-independent), so the test states the geometric fact
directly.

## Context (cold-start)

- File: `tests/test_frame.py`. The affected tests (and the helper that computes the factor):
  - `_prev_blade_magnitude_squared(vectors, k)` — computes `|A_{k-1}|²`.
  - `test_hestenes_equals_rejection_2d_symbolic` — asserts `c[1] - factor * w[1] == zero`.
  - `test_hestenes_equals_rejection_3d_concrete` — asserts `h[1] == content([a])**2 * w[1]`, etc.
  - `test_hestenes_equals_rejection_3d_symbolic` — asserts `c[k-1] - factor * w[k-1] == zero`.
- The direction/parallelism test gacalc already has: `A.is_parallel_to(B)` uses the wedge-zero test
  `A ∧ B = 0` (machine-checked in `proofs/GacalcProofs/Predicates3D.lean`) — scale-independent, the
  right tool here.

## Proposed change

- Assert parallelism instead of the computed scaling, e.g. `assert c[k].is_parallel_to(w[k])` (or
  `(c[k] ^ w[k]) == zero`) for each k, in the 2D-symbolic, 3D-concrete, and 3D-symbolic tests. Keep
  `c[0] == w[0]` (`c_1 = w_1 = v_1`, the first vector unchanged — exact, no scaling).
- Drop `_prev_blade_magnitude_squared` and the `content(...)**2` factors **from these reverse-based
  tests** (they exist only to express the scaling). The **exact** (unscaled) equality `== w_k` is the
  natural assertion for the *inverse*-based variant instead — see
  `tasks/hestenes-orthogonalize-via-inverse.md`; these two tasks are best done together.
- Keep each `is_frame`/orthogonality coverage already in the file; this task only reshapes the
  rejection-equivalence assertions.

> Decision to confirm during implementation (not a blocker): whether to keep one test that still
> records the exact `|A_{k-1}|²` factor as documentation of *why* the directions match, or rely on
> the inverse-variant's exact test for that and keep the reverse tests purely about parallelism.
> Leaning toward the latter (cleaner division of labor between the two variants).

## Verification

- `make test` — `test_frame.py` green; the parallelism assertions hold exactly on the symbolic
  vectors (not just numerically).
- `make format` — ruff + ty clean.
