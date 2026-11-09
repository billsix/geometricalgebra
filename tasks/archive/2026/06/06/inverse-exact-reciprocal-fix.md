# Fix `inverse()` degrading to floats (exact reciprocal)

**Created:** 2026-06-06 · **Completed:** 2026-06-06
**Superseded:** the "escape hatch not taken" below was taken by the 06/13 numeric-magnitude work (see `tasks/archive/2026/06/13/magnitude-numeric-for-numeric-input.md`).

## Symptom

In `notebooks/displayg2.py`, for the `G2` vector `m = 3 * e_1 + 4 * e_2`, `m.normalize()` gave exact
`{(1,): 3/5, (2,): 4/5}` but `m.inverse()` gave floats `{(1,): 0.12, (2,): 0.16}` instead of
`3/25, 4/25`. The author wanted exact fractions by default.

## Root cause

Not the generated code: `AbstractMultiVector.inverse()` in `base.py` computed
`self.reverse() * (self.magnitude_squared() ** (-1))`. For the specialized classes
`magnitude_squared()` is a raw Python `int` (`25`), and `int ** -1` is a `float` (`0.04`).

- `normalize()` stayed exact because it goes through `abs(self)` → `sympy.sqrt(...)`, which always
  returns a sympy object, and `Integer(5) ** -1` is `Rational(1, 5)`.
- `Gn` never showed this because `Gn.__post_init__` eagerly `sympy.simplify`s every coefficient, so
  its `magnitude_squared()` is already `sympy.Integer(25)`. That eager sympify in `gn.py` was the
  mechanism the author remembered; `G1/G2/G3` deliberately skip it (the lazy-simplify policy).

## The fix (`base.py` `inverse()`)

The reciprocal is routed through sympy:
`mag_sq = typing.cast(sympy.Expr, sympy.sympify(self.magnitude_squared()))`, then
`self.reverse() * (mag_sq ** (-1))`, with a comment explaining the `int ** -1` trap.

- `typing.cast(sympy.Expr, ...)` is required for `ty`: `sympy.sympify()` is typed as returning
  `Basic`, which `ty` does not accept for `**` (`error[unsupported-operator]`). The cast is a runtime
  no-op.
- The named local keeps the line ≤ 88 chars.
- The existing `"Not sure if I'm doing it correctly"` docstring comment was kept, at the author's
  request.
- `dual()` (`self * unit_pseudoscalar(n).inverse()`) was fixed by the same change: `m.dual()` →
  `{(1,): 4, (2,): -3}`, exact.
- The fix is in hand-written `base.py` (inherited); no regeneration.

## Performance (measured)

`G2.inverse()` went from ~2.8 µs to ~13.7 µs (~5× slower), against ~0.6 µs for the hot-path `G2`
product and ~101 µs for the `Gn` reference (the fixed `G2` stays ~7× faster). `inverse()` is a cold
operation, so this was judged not a real problem. The real cost is downstream and is the point:
results carry sympy `Rational`/`Float` coefficients, so a product using the inverse took ~14.1 µs vs
~4.3 µs with a plain-float vector (~3×), inherent to staying exact.

## Escape hatch (not taken at the time)

The fix also sympifies genuinely-float inputs, so a heavy numeric pipeline inherits the sympy cost.
The recorded alternative was to sympify only when the scalar is not already a Python `float`,
keeping float-in → float-out; the author chose the simpler exact-always version.

## Related

This was one instance of open issue #6 (`inverse`'s "not sure if I'm doing it correctly" comment).
The float degradation was fixed; the broader "verify against known results" item stayed open.

## Verification

`m.inverse()` → `{(1,): 3/25, (2,): 4/25}`; `m.dual()` → `{(1,): 4, (2,): -3}`; float inputs stay
numeric (as `sympy.Float`); `ty check src`/`tests` and `ruff` clean; full suite 161 passing.
