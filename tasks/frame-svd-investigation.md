# Investigate: can the `Frame`/QR construction rederive the SVD?

**Status:** proposed — needs go-ahead; depends on `tasks/frame-class-orthonormal-invertible-function.md`
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>); split out of the `Frame` task at the
maintainer's request.

## BLUF

Find out how far gacalc's `Frame` (orthonormal set + triangular coefficients, i.e. QR) gets toward the
singular value decomposition, expressed as GA transforms. Done = a written finding in
`tasks/reference/frames-qr-and-reciprocal-frames.md` ("Does this give the SVD?"), plus whichever routes
below pan out as code and tests.

## Context (read first)

- `tasks/reference/frames-qr-and-reciprocal-frames.md`: the math, including why one QR is not the SVD.
- `tasks/frame-class-orthonormal-invertible-function.md`: the `Frame` class this builds on. It must be done
  first.
- `tasks/reference/transform-and-composable-function-layer.md`: the `versor_rotation` /
  `scale_non_uniform` / `compose` factories.

## Routes, cheapest first

1. **`f = Q ∘ R` as GA transforms.** Q becomes a versor (a rotor, or a rotor times a reflection when
   `det Q < 0`), R becomes a triangular shear-scale `InvertibleFunction`, and the test checks
   `compose` equals `Frame.to_invertible_function()`. Not the SVD, but the same rotate-after-deform
   shape.
2. **The QR algorithm.** Iterate `A ← R Q` on `fᵀf`, using `Frame`s. It converges to the eigenvectors,
   giving the SVD numerically.
3. **Closed-form 2D SVD as `rotor ∘ scale_non_uniform ∘ rotor`**, checked symbolically. 3D is a stretch:
   cubic roots.

## Open questions

None yet. Raise them once the `Frame` task is done.
