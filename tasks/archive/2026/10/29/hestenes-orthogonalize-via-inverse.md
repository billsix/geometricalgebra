# A Hestenes orthogonalize variant using the inverse (not the reverse) — equals rejection exactly

**Status:** done — 2026-10-29. The hypothesis was **confirmed**: the inverse form equals the
rejection frame exactly. Work commit subject:
"frame: add make_orthogonal_frame_hestenes_inverse (equals rejection exactly)".
**Priority:** 5
**Difficulty:** 4  (new function + an equivalence test; the hypothesis was verified, not assumed)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

Added `make_orthogonal_frame_hestenes_inverse` (`src/gacalc/frame.py`): a copy of
`make_orthogonal_frame_hestenes` that uses the **inverse** of the prefix blade where the original
uses the **reverse** — `c_k := inverse(A_{k-1}) * A_k` instead of `reverse(A_{k-1}) * A_k`. As the
maintainer expected, this gives the **same directions** as the reverse form but **without the extra
per-vector scaling**: it equals `make_orthogonal_frame` (rejection) **exactly**, not merely up to a
positive scalar. Confirmed by two new symbolic tests.

## What was done

- **New function** `make_orthogonal_frame_hestenes_inverse`, right after the reverse variant, identical
  except `A_k_minus_1.inverse()` in place of `A_k_minus_1.reverse()`:
  ```python
  return [
      (A_k_minus_1.inverse() * A_k).r_vector_part(1)
      for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))
  ]
  ```
  with the same `is_frame` guard and grade-1 narrowing, and a docstring explaining why it lands on the
  rejection result exactly (`inverse(A) = reverse(A) / |A|^2`, so the `|A_{k-1}|^2` factor cancels).
- **No `__init__`/`__all__` change needed** — the frame functions are imported directly from
  `gacalc.frame` (there is no re-export list); `tests/test_frame.py` imports the new name there.
- **CLAUDE.md** frame description updated from two orthogonalization siblings to three.

## Why it works (confirmed)

For a blade `inverse(A) = reverse(A) / |A|^2`, so
`inverse(A_{k-1}) * A_k = (reverse(A_{k-1}) * A_k) / |A_{k-1}|^2 = (|A_{k-1}|^2 * w_k) / |A_{k-1}|^2 =
w_k`. The prefix blades the product uses (`A_0 = 1`, `A_1` a vector, `A_2` a bivector) are all
invertible blades, so `inverse` is valid (`inverse(1) = 1`, hence `c_1 = v_1` unchanged).

## Verification

- Two new symbolic tests in `tests/test_frame.py`
  (`test_hestenes_inverse_equals_rejection_exactly_2d_symbolic` / `_3d_symbolic`) assert
  `c_k^inv - w_k` eager-simplifies to the zero vector for every k — **exact** equality, the strong
  form the reverse variant cannot claim. (Compared by difference-to-zero because the inverse-blade
  product and the rejection build structurally different sympy forms.)
- `python -m pytest` — **692 passed** (690 + the 2 new); `ruff` + `ty` clean.

## Decision

Kept all **three** siblings side by side for teaching (rejection / reverse-closed-form /
inverse-closed-form), not replacing the reverse variant — consistent with how the first two already
coexisted. The exact-equality test lives here; the reverse variant's tests move to parallelism in
`tasks/hestenes-orthogonalize-test-parallelism.md`.

## Possible follow-on (not in scope — the maintainer asked only for the Python variant)

Per the gacalc standing default "every piece of math comes in three forms", the exact
`inverse(A_{k-1}) * A_k == w_k` equivalence could later also get a Lean theorem and a book/notebook
cell. Deliberately skipped here (the request was the Python copy + test); noted rather than silently
dropped.
