# Test the reverse-based Hestenes orthogonalize by parallelism, not by the scaling factor

**Status:** done — 2026-10-29. Work commit subject:
"frame tests: assert the reverse Hestenes frame is PARALLEL to rejection".
**Priority:** 5
**Difficulty:** 3  (test rewrite; the geometric assertion is still exact/symbolic)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

The tests for the reverse-based `make_orthogonal_frame_hestenes` asserted the **exact scaling
relationship** `c_k == |A_{k-1}|² * w_k` against the rejection `w_k` — which obscured the geometric
point (the two produce the **same directions**) behind a magnitude factor a reader had to compute
and reverse-engineer. Those assertions now test that each `c_k` is **parallel** to `w_k`
(scale-independent), stating the geometric fact directly; the exact scale moved to the inverse
variant's tests.

## What was done

In `tests/test_frame.py`, the four reverse-variant tests were renamed
`test_hestenes_equals_rejection_*` → `test_hestenes_parallel_to_rejection_*`
(`2d_symbolic` / `3d_concrete` / `3d_symbolic` / `numeric`) and now assert parallelism via
`A.is_parallel_to(B)` (the wedge-zero test `A ∧ B = 0`, machine-checked in
`proofs/GacalcProofs/Predicates3D.lean`):

- symbolic/concrete tests: `c[k].is_parallel_to(w[k])` (exact);
- the numeric test: `c[k].is_parallel_to(w[k], float_close_to_zero=True)`;
- `c[0] == w[0]` (`c_1 = w_1 = v_1`, first vector unchanged) stays an exact check.

The `_prev_blade_magnitude_squared` factor helper was removed, and with it the now-unused
`content` / `Real` / `Sequence` imports. The leading comment block was reframed from "equivalence up
to a positive scalar" to "parallel to rejection", noting the exact scale is pinned elsewhere.
`tasks/define-frame.md`'s 2026-09-02 record got a 2026-10-29 note on the rename/re-scope, and
`tasks/reference/design-decisions.md`'s "two orthogonalizations" bullet was updated in the
session-end sweep.

## Decision

Resolved the "keep one scaling test, or go pure parallelism?" question in favour of **pure
parallelism** for the reverse variant — the exact (factor-1) equality is the inverse variant's job
(`test_hestenes_inverse_equals_rejection_exactly_*`), a clean division of labour between the two.
This task and `hestenes-orthogonalize-via-inverse` were done together, as anticipated.

## Verification

- `python -m pytest` — **692 passed**; the parallelism assertions hold exactly on the symbolic
  vectors (`c_k ∧ w_k` eager-simplifies to zero), not just numerically.
- `ruff` + `ty` clean (via `entrypoint/format.sh`).
