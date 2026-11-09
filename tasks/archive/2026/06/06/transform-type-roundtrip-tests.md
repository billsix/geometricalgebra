# Unit tests: transforms are representation-preserving (type round-trip)

**Created:** 2026-06-04 · **Completed:** 2026-06-06

The representation-preserving transform layer in `geometricalgebra.transforms` had only been checked
with a throwaway smoke script during
`tasks/archive/2026/06/05/investigate-how-to-extract-translate-etc.md`; this task added the committed
tests owed by that task.

## Decisions

- **A new `tests/test_transforms.py`**, not an extension of `tests/test_conformance.py`: transforms
  are functions, not methods on the parametrized classes. It reuses the `[Gn, G1, G2, G3]`
  representation list.
- **`G1` is included for the dimension-general transforms only**; the planar rotations and the 2-D
  scale skip it.
- Value tests for the planar transforms use purely e₁e₂ vectors. Rotations were intentionally 2D,
  so no 3D rotation semantics were asserted; the hazard of a `G3`/`Gn` vector with an e₃ part was
  left to `tasks/archive/2026/06/06/clarify-2d-only-transforms.md`, which then removed the planar
  transforms (and their cases in this file).
- Comparisons use `is_close` (float-tolerant, simplify-aware), as the lazy-simplify classes require.

## What was tested (23 tests)

- **Type round-trip:** `translate`/`uniform_scale`/`scale_non_uniform`/`identity`/`compose` preserve
  type on Gn/G1/G2/G3; `rotate`/`rotate_90_degrees`/`rotate_around`/`scale_non_uniform_2d` on
  Gn/G2/G3.
- **Known values:** `rotate_90_degrees` and `rotate(pi/2)` take `3e₁+4e₂` to `−4e₁+3e₂`;
  `scale_non_uniform_2d(2,3)` takes `e₁+e₂` to `2e₁+3e₂`; `uniform_scale(2)`; `basis_vector(i)` is the
  i-th unit vector.
- **n-D scale:** `scale_non_uniform(2,3,4)` on a 3-vector (Gn/G3) scales each axis and keeps the type.
- **Invertibility:** `inverse(fn)(fn(v)) == v` for scale, translate and compose.
- **Error paths:** the *inverse* of `uniform_scale(0)` / `scale_non_uniform(…, 0, …)` raises. A zero
  scale is a valid forward map; only its inverse is undefined.

## Verification

Suite 164; `ty check tests` and `ruff` clean.
