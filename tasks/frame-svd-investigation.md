# Investigate: can the `Frame`/QR construction rederive the SVD?

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>); split out of the `Frame` task.

## Outcome

All three routes work. They are tests, `tests/test_frame_svd.py` (6 cases, under a second). The
finding is written in `tasks/reference/frames-qr-and-reciprocal-frames.md`, "Does this give the SVD?".

1. **`f = Q ∘ R`:** Q is a chain of rotations from vectors, with an axis flip for a left-handed
   frame; R is the triangular shear-scale, itself a `Frame`. This equals
   `Frame.to_invertible_function()` in 2D and 3D, both handednesses.
2. **The QR algorithm:** repeated `Frame` orthonormalizations of the Gram matrix converge to the
   right singular vectors. In 3D, the `f(w_i)` come out mutually perpendicular with lengths `σ_i`.
3. **The closed-form 2D SVD:** built from dot products and the wedge (the eigenvalues have sum
   `|v_1|² + |v_2|²` and product `|v_1 ∧ v_2|²`), the 𝒢₂ quarter turn, and rotations from vectors.
   It is exact on a rational frame with `σ = 5, 2`. 3D, which needs a cubic's roots, was not
   attempted.

## Judgment calls

- **Tests, not a library `svd()`.** Nothing needs one yet; the reference doc sketches what one would
  return.
- **A bug found and filed rather than fixed here:** `inverse()` rejects a float 𝒢₃ versor because of
  a 1e-16 rounding residue in `Ã * A`, so `versor_rotation` crashes on ordinary 3D float vectors. It
  is filed as `tasks/inverse-float-versor-rounding.md`, priority 3. Route 1 uses `projection_rotation`
  wrapped in an `InvertibleFunction` until then, with a comment naming the task.

## Verification

`tests/test_frame_svd.py` passed. ruff, `ty check` and `tools/check_annotations.py` (0 rows) were
clean on the file.
