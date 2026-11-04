# `frame.py`: replace index arithmetic with `match` + structural recursion — done-record

**Completed:** 2026-11-04. Requested and decided by William Emerison Six <billsix@gmail.com>;
implemented by the agent. The maintainer asked: "see if we can change the inverse part of the frame
function to use match and recursion instead of indexes, actually see if there's anything else in that
file that's possible to do that for too."

## What changed (`src/gacalc/frame.py`, `Frame`)

- **The inverse became a structural recursion with no indices.** `to_invertible_function()`'s
  `backward` previously solved the triangular system with `back_substitute(j)`, `range(j + 1, k)`,
  `coefficients[i][j]`, and `along[j]`. It now calls a nested `peel` over the `(w_i, v_i)` pairs, with
  `case []` / `case [*earlier, (w, v)]` / `case _`. `peel` reads the last coordinate as
  `x_k = (w_k · y) / |w_k|²` (exact, because `w_k` is orthogonal to every earlier `v_i`), subtracts
  `x_k * v_k`, and recurses on the earlier pairs. It reads no coefficient table, and the unit-diagonal
  division is gone.
- **Storage changed.** `Frame` stores `vectors` (a real field, kept as a tuple) and `orthogonal_vectors`.
  `__iter__` returns `iter(self.vectors)`. The `coefficients` field was replaced by a `coefficients()`
  method returning the same table, which keeps the QR view inspectable for the planned notebooks.
- **The basis-index sites kept their index, without the `+ 1`.** `forward` and `backward`'s result map
  use `enumerate(..., start=1)` with `basis_vector(i)`, each with a one-line comment: the index is
  `basis_vector`'s 1-based external numbering.
- **Kept as-is, with reasons:** the `len(vectors) == 0` guards (cheap top-of-function guards);
  `prefix_blades`' `vectors[0]` (left to `tasks/frame-prefix-blades-graded-zero-seed.md`); the
  `make_orthogonal_frame*` and `prefix_blades` bodies (already `match` / `accumulate` / `pairwise`); the
  `k = len(...)` + `n` derivation (needed for the `k = n` check).

## Chronology (harvested from the three commits on this work, 2026-11-04)

1. **Task created.** The agent surveyed `frame.py` for index-driven code and found one real target, the
   inverse's `back_substitute(j)`, plus two `enumerate` + `basis_vector(i + 1)` sites. Everything else was
   already structural or a cheap guard. Two index-free shapes were proposed: (a), a row recursion over the
   same coefficient back-substitution, and (b), peel the last vector. A prototype of (b) on concrete
   oblique 2D and 3D frames with a symbolic input recovered the input exactly. The agent recommended (b),
   provided the symbolic 3D test was not much slower.
2. **Design settled.** The maintainer asked whether (b) would let the `coefficients` field go. The agent
   first answered that `__iter__` still needed it, because the orthogonal `w_j` alone cannot rebuild the
   originals, and recommended keeping it stored. The maintainer then asked about having `__iter__` return
   stored originals instead, and chose that, plus an on-demand `coefficients()` method for the QR view.
   The agent's keep-it-stored recommendation was set aside. Choosing the storage change "alongside (b)"
   settled shape (b).
3. **Implementation.**
   - (b) and the storage change were implemented as planned.
   - For the basis-index sites, zipping with a list of basis vectors was rejected: it would only move the
     index into a `range`. The index stayed, written `enumerate(..., start=1)`.
   - The 3D symbolic round trip slowed from 50.5 s to 60.4 s; (b) was kept.
   - Two 3D tests each recomputed `coefficients()` (about 70 s apiece), so module-scoped fixtures were
     added to share one computation per frame.
   - The annotation checker flagged `peel`'s `list` parameter, which became a `Sequence`.
   - Mid-task, the maintainer asked whether the graded-input `prefix_blades` bug had a task. It already
     did (`tasks/frame-prefix-blades-graded-zero-seed.md`), so nothing was created.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-04)

1. **Shape (b), "peel the last vector"**, chosen over (a), which would have kept the coefficient-table
   back-substitution and only replaced the integer index with a row recursion.
2. **Store the originals; drop the `coefficients` field.** This reversed decision 2 of the original
   `Frame` design (`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`). Nothing
   read the stored coefficients once the inverse was (b), and `Frame` was unreleased (`CHANGELOG.md`
   `[Unreleased]`), so no consumer broke.
3. **Keep an on-demand `coefficients()` method.**

## Verification

- An earlier prototype of (b) on concrete oblique 2D and 3D frames with a symbolic input recovered `x`
  exactly and matched the old inverse's coordinates.
- **Timing of `test_composed_round_trip_is_identity_3d_symbolic`:** 50.5 s before, 60.4 s after (about
  20% slower, judged not "much slower", so (b) was kept).
- `coefficients()` computes on each call, about 68 s for the 3D symbolic frame, so the tests that read it
  share one computation per frame through module-scoped `frame_2d_coefficients` / `frame_3d_coefficients`
  fixtures. `tests/test_frame_class.py` ran in 215 s with 22 tests, against 207 s and 20 tests before.
- `tests/test_frame_class.py` gained `test_coefficients_rebuild_the_vectors`
  (`Σ_j coefficients()[i][j] * w_j == v_i`, symbolic 2D and 3D), which took over what `iter()` used to
  prove. `test_iter_rebuilds_the_original_vectors` was renamed `test_iter_yields_the_original_vectors`.
- `tests/test_frame_class.py` + `tests/test_frame.py` + the `frame.py` doctests passed (44). ruff and
  `ty` were clean, and `tools/check_annotations.py` reported 0 findings for both files. A `list` parameter
  on `peel` was changed to `Sequence` after the checker flagged it as an invariant collection.
- Container `format.sh` gate passed (ruff, `ty`, the changelog check, the ePiX keyword check); full
  container `pytest` with doctests: **716 passed** in 4 min 59 s.

## Docs touched

`CHANGELOG.md` (the existing `[Unreleased]` "Added: `Frame`" entry, amended in place); `CLAUDE.md` (the
`Frame` module-layout line); `tasks/reference/frames-qr-and-reciprocal-frames.md` (the L0 note, gacalc's
peel form under "Inverting without row reduction", and the storage section); `tasks/frame-notebooks-epix.md`
(its Context, and the inverse figure now shows the peel steps).
