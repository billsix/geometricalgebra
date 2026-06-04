# Unit tests: transforms are representation-preserving (type round-trip)

**Status:** not started — needs go-ahead
**Started:** 2026-06-04

## Goal

Add committed tests asserting the transform layer in `geometricalgebra.transforms` is
representation-preserving: a `G1`/`G2`/`G3`/`Gn` value in yields the **same concrete type** out, with
correct values. This was verified manually with a throwaway smoke script during the
`investigate-how-to-extract-translate-etc` work, but no tests were committed — this task owes that
coverage. (Tracks the leftover "add unit tests" TODO from that task.)

## Plan

- [ ] Decide home + style: a new `tests/test_transforms.py`, or extend `tests/test_conformance.py`
      (which already parametrizes over `[Gn, G1, G2, G3]` and is the natural fixture for "same in,
      same out").
- [ ] **Type round-trip** — for each representation, assert `type(fn(v)) is type(v)` for:
      `translate(b)` (with `b` of the same type), `uniform_scale(m)`, `scale_non_uniform(*factors)`,
      `scale_non_uniform_2d`, `rotate(angle)`, `rotate_90_degrees()`, `rotate_around(angle, center)`,
      `identity()`, and `compose([...])` of a few. (Rotations are 2D — test on `G2`/`Gn`; for `G3`
      restrict to the planar interpretation or just the non-rotation transforms per the 2D scope.)
- [ ] **Value correctness** — spot-check known results, e.g. `rotate(pi/2)` of `3e₁+4e₂` → `−4e₁+3e₂`;
      `scale_non_uniform(2,3)` of `e₁+e₂` → `2e₁+3e₂`; `uniform_scale(2)` of `v` → `2v`;
      `inverse(fn)(fn(v)) == v`. Use `is_close` / simplify-aware comparison for the specialized
      classes (per the lazy-simplify policy).
- [ ] **Invertibility / error paths** — `uniform_scale(0)` and `scale_non_uniform(…, 0, …)` raise;
      `inverse(compose([...]))` round-trips.
- [ ] **`n-D scale`** — `scale_non_uniform(2,3,4)` on a `G3`/`Gn` 3-vector scales each axis; confirm
      it stays the input type.
- [ ] **`basis_vector`** — quick test that `cls.basis_vector(i)` is the i-th unit vector for each rep.
- [ ] Run `python -m pytest -q` (expect the count to rise from 118) and keep `ty check tests` clean.

## Notes / decisions

- Specialized classes don't eagerly simplify, so equality/`is_close` must be simplify-aware — follow
  the existing pattern in `tests/test_conformance.py`.
- Rotations are intentionally 2D (planar e₁e₂); don't assert 3D rotation semantics here (a general
  vector→vector rotate is a separate future task).

## Open questions

- New `test_transforms.py` vs. fold into `test_conformance.py`? (Leaning: new file for the transform
  layer, since transforms are functions, not methods on the parametrized classes — but reuse the
  representation list.)
- Include `G1` (1D) in the round-trip checks where it makes sense (translate/uniform_scale), skipping
  the planar rotations and 2-D scale?
