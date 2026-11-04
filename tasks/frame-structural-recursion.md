# `frame.py`: replace index arithmetic with `match` + structural recursion

**Status:** proposed — needs go-ahead (open question 1 first)
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>): "see if we can change the inverse part
of the frame function to use match and recursion instead of indexes, actually see if there's anything
else in that file that's possible to do that for too."

## BLUF

`Frame.to_invertible_function()`'s inverse solves the triangular system with index arithmetic:
`back_substitute(j)`, `range(j + 1, k)`, `coefficients[i][j]`, `along[j]`. Rewrite it as a `match`-based
structural recursion over the frame's vectors, with no indices, the way `make_orthogonal_frame` already
recurses. Then apply the same treatment to any other index-driven code in `src/gacalc/frame.py` where it
reads better. Done = no index arithmetic left in `frame.py` except where an index is an external API
(`basis_vector(i)`) or a cheap guard, every `tests/test_frame*.py` test still green (including the
symbolic 3D round trips), and each site kept as-is listed below with its reason.

## Context (read first)

- **The recursion guide:** the "recursive-design.md" reference doc from github.com/billsix/runClaudeInContainer
  (`tasks/reference/recursive-design.md`). Follow it here: let the recursion follow the data's shape; give
  each data shape its own `case`, with `case _` as the total default (`ty` does not prove list patterns
  exhaustive, and drops into `invalid-return-type` without it); per-case comments describe the operation;
  map/filter as comprehensions; no accumulator unless genuinely needed; Python recursion only for bounded
  structures (a frame has at most `n` vectors, so this is fine).
- **The model already in the file:** `make_orthogonal_frame`'s inner `orthogonalize`
  (`case []` / `case [v]` / `case [v, *rest]` / `case _`), which is also the guide's worked example.
- `tasks/reference/frames-qr-and-reciprocal-frames.md`: the math of the inverse (back-substitution =
  `R⁻¹ Qᵀ y`).
- `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`: how `Frame` was built, and
  why its 3D symbolic tests are slow (about 3.5 minutes).

## Survey of `src/gacalc/frame.py` (2026-11-04)

| site | what it does now | candidate change |
|---|---|---|
| `to_invertible_function` › `backward` › `back_substitute(j)` | recursion on an integer `j`; `along[j]`, `coefficients[i][j]`, `coefficients[j][j]`, `zip(range(j + 1, k), later)` | **the main target**; see "The inverse" below |
| `backward`'s result `sum(x_j * basis.basis_vector(j + 1) for j, x_j in enumerate(…))` | coordinates → vector | `zip` the coordinates with a basis list; the `+1` index is `basis_vector`'s 1-based external API, so the index may stay. Decide in step 3 |
| `forward`: `x.scalar_product(basis.basis_vector(i + 1)) * v for i, v in enumerate(frame_vectors)` | `f(x) = Σ (x · e_i) * v_i` | same basis-list question as above; already a map/fold, so this is a spelling question only |
| `to_invertible_function`: `k = len(frame_vectors)`, `cls = type(frame_vectors[0])`, the `n` derivation | the `k = n` check | `k` is needed for the check. If `backward` stops using `k`, it shrinks to the check alone |
| `__iter__`, `__post_init__` | `zip`/comprehensions | already structural; **keep** |
| `are_linearly_independent` / `prefix_blades`: `len(vectors) == 0` guard, `vectors[0]` | empty guard, representation pick | cheap top-of-function guards are right per the cross-project rule; **keep** unless a `match` reads clearly better. `prefix_blades`' `vectors[0]` is also involved in `tasks/frame-prefix-blades-graded-zero-seed.md`; don't touch it here |
| `make_orthogonal_frame*`, `prefix_blades` (`accumulate`, `pairwise`) | already named schemes | **keep** |

## The inverse: two structural shapes

Both recurse over the frame's `(w_j, v_j)` pairs or rows instead of an index. (b) was prototyped
2026-11-04 (`Gn`, concrete oblique 2D and 3D frames, symbolic `x`): it recovered `x` exactly and matched
the current inverse's coordinates.

**(a) Same algorithm, structural.** Recurse over the rows `(along_j, column of coefficients below the
diagonal)`, last row first. `x_j = (along_j − Σ c_ij * x_i) / c_jj`, with the `Σ` a `zip` of the column
against the already-solved later coordinates. This still reads `coefficients`, so building the columns
still needs a transpose (`zip(*coefficients)`) and a split at the diagonal.

**(b) Peel the last vector (no coefficients at all).** Because `w_k` is orthogonal to `v_1 … v_{k-1}`,
`(w_k · y) / |w_k|²` is exactly `x_k`. Subtract `x_k * v_k` from `y` and recurse on the earlier pairs:

```python
def peel(pairs, y):
    match pairs:
        case []:                      # nothing left to solve
            return []
        case [*earlier, (w, v)]:      # the last vector's coordinate, then the rest of y
            x_last = _exact_quotient(w.scalar_product(y), w.magnitude_squared())
            return [*peel(earlier, y - x_last * v), x_last]
        case _:                       # unreachable total default (ty)
            return []
```

This is the geometric reading of back-substitution: measure along the direction only the last vector
has, remove that vector's contribution, and repeat on a smaller frame. It needs no index and no
coefficient table. `coefficients` would then serve only `__iter__`, and the unit-diagonal division
disappears.

## Plan

1. Decide (a) or (b) (open question 1).
2. Rewrite `backward` accordingly. Keep `_exact_quotient` for exactness, keep the docstring's math (update
   it for (b)), and keep the `case _` default with the comment the guide uses.
3. Settle the `forward`/result `enumerate` + `basis_vector(i + 1)` sites: either a basis list zipped with
   the vectors, or the index kept with a one-line reason. Same answer at both sites.
4. Verify:
   - `tests/test_frame_class.py` and `tests/test_frame.py` green, **including the fully symbolic 3D round
     trips**. Record the before/after time of `test_composed_round_trip_is_identity_3d_symbolic`; (b)
     builds different intermediate expressions, which could be faster or slower;
   - the `Frame` doctests;
   - container `format.sh` (ruff + `ty`; `ty` is what catches a missing `case _`);
   - `tools/check_annotations.py` (0 findings).
5. If the change alters what the docstring or reference doc says the inverse does, update
   `tasks/reference/frames-qr-and-reciprocal-frames.md` ("Inverting without row reduction"). No
   `CHANGELOG.md` entry is needed: the behaviour and public API are unchanged.

## Open questions

1. **Which shape for the inverse?** (a) keeps the current algorithm and only removes the indices; it
   still reads the coefficient table. (b) peels the last vector off the frame and never reads the
   coefficients; it is shorter and has a geometric reading, and was prototyped correct on concrete
   frames. **Recommend (b)**, provided the symbolic 3D round-trip test is not much slower; step 4
   measures that.
