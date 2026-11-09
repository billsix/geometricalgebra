# Explicit-inputs rewrite of the remaining symbolic tests + plot-helper cleanup

**Created:** 2026-08-24 · **Completed:** 2026-08-25

Two cleanups surfaced while making the frame/measure symbolic tests readable
(`tasks/archive/2026/08/24/area-volume-content.md`):

1. **Rewrite the remaining symbolic tests to the explicit-inputs style:** general vectors written out
   inline (`a = a_1 e_1 + a_2 e_2`) with outputs asserted against their exact formulas, so each test
   reads like the math (a learning framework: a test you can't read teaches nothing). No shared
   `sym_vec_*` fixtures, no `parametrize`/loops hiding inputs and outputs. The pattern came from
   `tests/test_measure.py`, `tests/test_frame.py` and `tests/test_dot_wedge_projection_split.py`
   (2D symbolic, plus concrete-number 3D where the symbolic output is intractable).
2. **Remove or rewrite redundant helper functions** found in an audit (2026-08-24).

## Part 1: tests

- **`tests/test_multivector.py`** (2026-08-24): the whole symbolic section was rewritten (the
  recommended scope: it was the last big fixture-driven symbolic test file). The `sym_vec2_1`/
  `sym_vec2_2`/`sym_vec3_1`/`sym_vec3_2`/`sym_vec_plane` imports were dropped; each test inlines its
  vectors and asserts the explicit formula (dot `== a_1 b_1 + a_2 b_2`, wedge `== (a_1 b_2 - a_2 b_1)
  e_12`, the product split into dot + wedge, dual, even/odd, reverse, inverse, project/reject,
  normalize). A tautological `sym_vec3_1.dot(sym_vec3_2) == sym_vec3_1.dot(sym_vec3_2)` became the
  explicit 3D dot. 23 tests passed; ruff + ty clean.
- **`tests/test_numeric_magnitude.py`** (2026-08-25): its two `sym_vec3_1` uses became explicit
  `g3.Vector` symbolic vectors, and the `gn` import was dropped (for consistency; low value, since
  those tests check numeric-magnitude behavior, not a formula).
- **`tests/test_conformance.py` was excluded:** it uses `Gn.symbolic_multivector(...)` to check that
  `Gn` and the generated types agree, so its "output" is the equality of two representations, not a
  formula to learn.

## Part 2: helpers

- **`nbplotutils.cosine(v1, v2)` was removed** as redundant with the `MultiVectorBase.cosine` method;
  its two call sites in `nbplotutils.py` use `v1.cosine(v2)` (verified numerically equal, 11/15).
- **`nbplotutils.sine(v1, v2)` kept its rotate-90-then-project form** (William Emerison Six
  <billsix@gmail.com>, 2026-08-24), `rot90 = v1 * e_12; (rot90·v2)/|v1 v2|`, which the maintainer
  likes for teaching. A `signed_area` rewrite (the earlier recommendation) was tried and rejected:
  `signed_area` needs a fixed-`DIMENSION` type, but the plot helpers default to `cls=MultiVector` (the
  dimensionless `Gn`), and `displaymv.py` draws its graph paper with that default, so it would raise
  (as would two vectors in 3D, k < n). Removing `sine` and inlining at its call sites was not chosen.
  The one change was `assert v1.is_vector() and v2.is_vector()`, since the `abs(v1*v2)` step uses
  `|v1 v2|` as `|v1||v2|`, which only holds for vectors (the maintainer's point). The identity
  `sine == signed_area/(|v1||v2|)` still holds for a fixed-dimension 2D type and was recorded for the
  book.
- **`base.py`'s `cosine` method was kept**, as the maintainer confirmed: the canonical
  `cos θ = (Ã ∗ B)/(|A||B|)` (Hestenes & Sobczyk p. 14, eq 1.53b), with 12 uses. No `abs_sin`/`abs_cos`/
  `angle_between` existed (0 hits).

## Verification

Full suite 405 passed; ruff + ty clean; `displayrotations` and `displayg2` (the `create_x_and_y`
sine/cosine path) executed headless.
