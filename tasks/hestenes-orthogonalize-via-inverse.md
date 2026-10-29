# A Hestenes orthogonalize variant using the inverse (not the reverse) — should equal rejection exactly

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4  (new function + an equivalence test; the hypothesis must be verified, not assumed)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

Make a copy of `make_orthogonal_frame_hestenes` (`src/gacalc/frame.py`) that uses the **inverse** of
the prefix blade where the original uses the **reverse**: `c_k := inverse(A_{k-1}) * A_k` instead of
`reverse(A_{k-1}) * A_k`. The maintainer's expectation (to verify): this gives vectors in the **same
directions** as the reverse form but **without the extra per-vector scaling** — i.e. it should equal
`make_orthogonal_frame` (the rejection method) **exactly**, not merely up to a positive scalar.

## Context (cold-start)

- File: `src/gacalc/frame.py`. The two existing siblings:
  - `make_orthogonal_frame` — orthogonalize by **rejection** (Gram–Schmidt); result `w_k`.
  - `make_orthogonal_frame_hestenes` — the **closed form** `c_k = reverse(A_{k-1}) * A_k`
    (H&S p. 27, eq 3.2), with `A_k = v_1 ∧ … ∧ v_k`. Currently `c_k == |A_{k-1}|² * w_k` (equal to
    rejection **up to the positive scalar** `|A_{k-1}|²`; proved in `tests/test_frame.py`).
- **Why the inverse removes the scaling (the hypothesis):** for a blade, `inverse(A) = reverse(A) /
  |A|²` (`Ã / |A|²`). So `inverse(A_{k-1}) * A_k = (reverse(A_{k-1}) * A_k) / |A_{k-1}|² =
  (|A_{k-1}|² * w_k) / |A_{k-1}|² = w_k`. The `|A_{k-1}|²` factor cancels → exact equality with
  rejection, same direction, no extra length.
- **Prerequisite that holds:** `inverse` in gacalc is defined for blades/versors (CLAUDE.md known
  issue 2). Each `A_{k-1}` is a blade (a wedge of vectors), and `is_frame` guarantees it is nonzero,
  so `inverse(A_{k-1})` is valid. `A_0 = 1`, `inverse(1) = 1`, so `c_1 = v_1` as before.

## Proposed change

- Add a function next to the other two — proposed name `make_orthogonal_frame_hestenes_inverse`
  (bikeshed welcome) — identical to `make_orthogonal_frame_hestenes` except `A_k_minus_1.inverse()`
  in place of `A_k_minus_1.reverse()`:
  ```python
  return [
      (A_k_minus_1.inverse() * A_k).r_vector_part(1)
      for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))
  ]
  ```
  Keep the `is_frame` guard and the grade-1 narrowing. Docstring: it is the closed form that lands on
  the rejection result exactly (contrast the reverse form's `|A_{k-1}|²` scaling), and say why
  (`inverse = reverse / |A|²`).
- Export it alongside the siblings (`__init__`/`__all__` as the others are).

## Verification

- A new test in `tests/test_frame.py` asserting **exact** equality with `make_orthogonal_frame`
  (`c_k_inv == w_k`), symbolic (2D + 3D general vectors) and numeric — the strong form the reverse
  variant cannot claim. This is the natural home for the exact relationship, now that the reverse
  variant's test moves to parallelism (see `tasks/hestenes-orthogonalize-test-parallelism.md`).
- `make test` green; `make format` ruff + ty clean.

## Notes / possible follow-ons (not in scope unless asked)

- Per the gacalc standing default "every piece of math comes in three forms", the exact
  `inverse(A_{k-1}) * A_k == w_k` equivalence could later also get a Lean theorem and a book/notebook
  cell. This task is the Python copy + test the maintainer asked for; flag the other two forms rather
  than silently dropping them.
- Decide whether the inverse form should **replace** the reverse form or sit beside it. Default:
  keep both side by side for teaching, as the two existing siblings already are.
