# magnitude() should return a Python number for numeric input (don't poison numeric pipelines)

**Created:** 2026-06-13 · **Completed:** 2026-06-13

## Problem

`MultiVectorBase.magnitude()` was `sympy.sqrt(magnitude_squared())`, so it returned a sympy expression
even when every coefficient was a plain Python number. That propagated through the rotor path
(`rotor_from_vectors` uses `|from| * |to|`; `rotate`/`sandwich`), so rotating a numeric vector yielded
sympy coefficients. Against the released gacalc 0.0.3, `abs(Vector3(1.0,0.0,0.0))` and
`rotate`/`rotate_z` of a numeric `Vector3` returned `Float`/`Float`/`Zero`; modelviewprojection's
`to_matrix` then built a `dtype=object` array and `np.linalg.inv` raised
`UFuncTypeError: Cannot cast ... dtype('O') to dtype('float64')` (github.com/billsix/modelviewprojection
`tasks/archive/2026/06/13/mvpviz-focus-failure.md`). The goal: numeric in → numeric out, symbolic in →
symbolic out, without weakening symbolic mode.

## What was done

Both fixes are in `src/gacalc/base.py`, in inherited `MultiVectorBase` methods (`magnitude`/`inverse`
are not emitted per class, so no generator change):

- **`magnitude()`** — when `|A|²` is a Python `float` (already inexact), it uses `math.sqrt` and returns
  a `float`. An `int` `|A|²` keeps `sympy.sqrt`, so `sqrt(25) == 5` exactly and a unit blade normalizes
  to `Rational`s. Symbolic stays symbolic.
- **`inverse()`** — the reciprocal `Ã / |A|²` no longer force-`sympify`s a `float` `|A|²`, which had
  poisoned the numeric inverse path (used by mvp's focus walk against the arrows). `float` → numeric
  reciprocal; `int` → `Rational`; symbolic → symbolic.

**Decision: float only, not `int`.** The first cut also downcast `int`, which broke the pre-existing
`test_graded.py::test_inherited_abc_methods`; it was narrowed to float-only and that test passed again.
The fix stayed inside `magnitude()`/`inverse()`, which was enough for the rotor chain to stay numeric
end to end.

## Verification

`abs(float_vector)` is a Python `float`; `rotor_rotation` of float vectors stays `float` forward and
inverse; `abs(symbolic)` is still a `sympy.Expr`; `3e₁+4e₂` still gives `|A| = 5` and normalizes to
`3/5, 4/5`. Regression test `tests/test_numeric_magnitude.py` (4 cases). The full suite passed (225).

mvp kept its own float-coercion boundary guard regardless (the decision in its `mvpviz-focus-failure`
record): numpy/OpenGL need `float64`, and gacalc may legitimately return sympy in symbolic mode, so this
fix is defence in depth at the source, not a replacement. Related:
`tasks/archive/2026/06/13/magnitude-sympy-cast-to-coef.md` (the same `magnitude` path) and
`tasks/archive/2026/06/27/geometric-product-magnitude-proof.md` (the rotor magnitude).
