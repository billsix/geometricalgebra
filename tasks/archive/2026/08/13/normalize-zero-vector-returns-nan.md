# `normalize()` of an int/symbolic-zero vector returned silent `nan` (now raises)

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Found while verifying `tasks/archive/2026/08/13/harvest-api-design-rationale-from-archive.md`:
the archived "no zero-safe normalize → it raises" claim was only half true.

## The wart

`MultiVectorBase.normalize()` is `self * (abs(self) ** (-1))`. For a **zero** vector the two
numeric paths diverged (verified 2026-08-13):

- **float-zero** (`Vector2(0.0, 0.0)`): `abs` is `0.0`, and `0.0 ** -1` raises
  `ZeroDivisionError` (contract-correct, matches pygame).
- **int/symbolic-zero** (`Vector2.zero()`, `Vector2(0, 0)`): `abs` routes through sympy
  (`magnitude` sympifies an `int` `|A|²`), `sympy.Integer(0) ** -1` is `zoo` (complex infinity),
  and `0 * zoo` is `nan`, so `.normalize()` returned `Vector2(coeff_e_1=nan, coeff_e_2=nan)`
  silently. `inverse()`, with the same `mag_sq ** -1` shape, behaved the same way.

## Decision

Option 1, **raise uniformly**: a `nan`-poisoned multivector is worse than a clean error, and it
unifies the two paths. `ZeroDivisionError` was chosen for parity with the float path. Rejected:
(2) leave as-is and only document it (the float path numeric consumers hit already raised, so the
blast radius was narrow, but the silent `nan` remained); (3) guard only the int/symbolic path.

## What changed

- `normalize()` and `inverse()` raise `ZeroDivisionError` when `magnitude_squared` is zero, for
  every coefficient kind. The guard is in `base.py`, and it keeps the deliberate int-vs-float split
  in `magnitude`/`inverse` (no unconditional sympify; float→float / int→exact /
  symbolic→symbolic, per `tasks/reference/design-decisions.md`).
- Regression + guard test in `tests/test_numeric_magnitude.py` (zero vector of each coefficient
  kind).
- `CHANGELOG.md` entry under 0.0.16 (Fixed); folded into the 0.0.16 breaking release.

## Verification

349 tests + ruff + ty green, in the sandbox and in the pinned container.
