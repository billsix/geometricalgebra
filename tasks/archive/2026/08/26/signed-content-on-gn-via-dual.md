# Define `signed_content` on `Gn` (and simplify its guards) via the dual-is-scalar test

**Created:** 2026-08-26 · **Completed:** 2026-08-26

## Goal

`signed_content` (`src/gacalc/measure.py`) rejected the general `Gn` representation (it required a
`DIMENSION` attribute) and read the result as `wedge.coefficient(Gn.unit_pseudoscalar(dimension))`.
The maintainer's idea (2026-08-26): implement it for `Gn` too, inferring the ambient dimension from
the vectors, and let the math replace the guards — wedge the vectors, take the **dual**; if the
result is a scalar, that scalar is the signed content.

## Why it works (verified 2026-08-26)

For k vectors, `wedge = v₁ ∧ … ∧ v_k` is a grade-k blade, and `dual(A, n) = A·I_n⁻¹` has grade
`n − grade(A)`, so `dual(wedge, n)` is a scalar iff the wedge is top-grade, and that scalar is `c` in
`wedge = c * I_n`. Dependent sets give `wedge = 0` → dual `0`. Probed against g2/g3 with
`n = max basis index` — all identical:

| vectors (as `Gn`) | k | n | result |
| --- | --- | --- | --- |
| `e_1, e_2` / `e_2, e_1` | 2 | 2 | **1** / **-1** (= g2) |
| `2e_1+e_2, e_1+3e_2` | 2 | 2 | **5** (= g2) |
| `e_1, e_2, e_3` | 3 | 3 | **1** (= g3) |
| symbolic `a₁e_1+a₂e_2`, `b₁e_1+b₂e_2` | 2 | 2 | **`a_1*b_2 - a_2*b_1`** |
| `e_1+e_2, 2e_1+2e_2` (parallel) | 2 | 2 | **0** |
| `e_1, e_3, e_1+e_3` (coplanar) | 3 | 3 | **0** |
| `e_1, e_3` / `e_1+e_3, e_2+e_3` (too few) | 2 | 3 | **raise** |
| `e_1, 2e_1` (over-determined) | 2 | 1 | **raise** |

**Constraint found:** the generated graded types' `dual` is hard-locked to their `DIMENSION`
(`g3.Bivector.dual(2)` raises), so max-index inference is `Gn`-only; a fixed type uses its
`DIMENSION`, which is also the right semantics (two `g3` vectors are genuinely not full-space).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-26)

1. **Exactly `k = n`, else raise.** Right count but degenerate (parallel/coplanar) → `0`; too few
   *or* too many → raise. The maintainer refined it so over-determined also raises, making the guard
   `len(vectors) != n` rather than `< n`; so `Gn` `[e_1, 2e_1]` (`k=2, n=1`) raises, and the genuine
   "parallel → 0" case is the `k = n` dependent one. The count guard is required because `is_scalar`
   alone cannot tell a parallel full-count set (want `0`) from a dependent wrong-count set (want
   raise) — both give a zero dual.
2. **All-zero (non-empty) input raises**: `_max_basis_index(..., default=0)` gives `n = 0`, so
   `k ≠ n`. This replaced an earlier "all-zero → 0" answer; returning `0` instead was offered to the
   maintainer as an easy special case. An empty list is already rejected by `_require_vectors`.
3. **No explicit `n` parameter** (the maintainer: "whatever you recommend"); add an override only if
   a real caller needs it.
4. **Switch fully to `dual`** (the maintainer: "sure if you recommend"): one self-validating path,
   identical values, one extra geometric product vs a dict lookup (negligible).
5. **The pass condition is `is_scalar()`, not `max_grade() == 0`**: the degenerate case yields a zero
   dual, and `max_grade()` then crashed on `max([])`; `is_scalar()` returns `True` for zero. The
   `is_scalar` guard is defensive (it cannot fire for `k = n`) and documents the invariant.

## What changed

- `signed_content` takes `n = DIMENSION` for fixed types, else `_max_basis_index(vectors)` (new
  private helper); raises unless `k = n`; returns `wedge.dual(n).scalar_part()`. No `Gn` import is
  needed any more (`wedge.dual(n)` self-dispatches), so the lazy `from gacalc.gn import Gn` was
  removed. The docstring states the semantics: `Gn`'s `n` is the largest basis index present.
- g2/g3 behaviour and the `signed_area`/`signed_volume` wrappers were unchanged.
- **Pre-existing fragility found, not fixed here:** `max_grade()` raised on a zero multivector, so
  `is_vector()` crashed on `Gn.zero()` (which is where an all-zero input raised, inside
  `_require_vectors`). It was kept out of scope and fixed separately in
  `tasks/archive/2026/08/26/max-grade-on-zero-crashes.md`.

Related: `tasks/archive/2026/08/25/pseudoscalar-coefficient-via-unit-pseudoscalar.md` (the
`coefficient`-based line this replaced).

## Verification

409 tests green (4 new: `Gn` full-space numeric matching g2/g3, the symbolic 2×2 determinant,
parallel/coplanar `k=n` → `0`, and the raise cases too-few / over-determined / all-zero); the
obsolete `test_signed_content_needs_full_space_and_fixed_dimension` (asserting "Gn raises") was
replaced. ruff + ty clean on src and tests.
