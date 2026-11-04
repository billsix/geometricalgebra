# `prefix_blades` returns zeros on graded `Vector` input (the `A_0 = 1` seed is dropped)

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>). Found while prototyping
`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`; the bug predates that work.

## BLUF

`prefix_blades`, `make_orthogonal_frame_hestenes`, and `make_orthogonal_frame_hestenes_inverse`
(`src/gacalc/frame.py`) return **all zeros** when given the generated graded `g2.Vector` / `g3.Vector`
types, although their docstrings say they work "on ``Gn`` and the graded ``Vector_n`` types alike".
Done = the three functions give correct results on graded input, with tests on `g2`/`g3` and not only
`Gn`.

## Context

- `prefix_blades` seeds its fold with `type(vectors[0]).one()`. For a graded `Vector` class, `one()` is
  the **zero vector**: a grade-1 type cannot hold a scalar, which is the graded silent drop (the "exp()
  trap") in `tasks/reference/blade-dict-interchange.md`. So `A_0 = 0`, and every later prefix wedge is 0.
- Reproduction (2026-11-04):
  ```
  >>> from gacalc.g3 import Vector, e_1, e_2
  >>> repr(Vector.one())
  'g3.Vector(coeff_e_1=0, coeff_e_2=0, coeff_e_3=0)'
  >>> make_orthogonal_frame_hestenes([1 * e_1, 1 * e_1 + 1 * e_2])
  [g3.Vector(0, 0, 0), g3.Vector(0, 0, 0)]       # (abridged repr)
  ```
  `make_orthogonal_frame_hestenes_inverse` raises `ZeroDivisionError` ("cannot invert a zero-magnitude
  multivector").
- `tests/test_frame.py` tests these functions only on `Gn`, so the bug went unnoticed.
- `make_orthogonal_frame` (rejection) does not use `prefix_blades` and works on graded input. `Frame`
  uses it, so `Frame` is unaffected.

## Plan

1. Seed `A_0` with a scalar one that survives the first wedge, either the full algebra type's `one()`
   (find how a graded type names its full class) or by starting the fold at `A_1 = v_1` and yielding a
   scalar `1` separately. Choose whichever keeps the `Gn` path unchanged.
2. Parametrize the `prefix_blades` / Hestenes tests in `tests/test_frame.py` over `Gn`, `g2`, and `g3`.
3. Check the docstring claim "works on Gn and graded types alike" is then true.
4. Add a `CHANGELOG.md` `[Unreleased]` "Fixed" entry.

## Open questions

None.
