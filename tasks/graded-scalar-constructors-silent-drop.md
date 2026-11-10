# Graded types: `from_real` and `unit_pseudoscalar_squared` on a scalar-less type

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Source:** `tasks/archive/2026/11/10/class-one-replaces-scalar-one.md` (investigation)

## BLUF

The graded `one()` fix left two class-level constructors with the same trap. (1) `from_real(x)` on a
graded type with no scalar slot (`Vector`, `Bivector`, `Trivector`, `Odd_3`) silently returns the
zero value: `g2.Vector.from_real(3) == g2.Vector.zero()`. (2) `unit_pseudoscalar_squared(n)` on a
graded type raises ("cannot hold the basis blade"), although its value is a scalar. Options, per
method: return the algebra's `Scalar` (as `one()` now does), or raise a `ValueError` naming the type.
Decide, implement in `tools/gen_specialized.py`, regenerate, and gate.

## Context (read first)

- `src/gacalc/base.py` `from_real`, `unit_pseudoscalar_squared`, `_require_holds_blade`; the generator's
  `one()` emission in `generate_graded_type`.
- Caveat: `unit_pseudoscalar` and `bases` deliberately seed with `cls.from_real(1)` to get the zero
  value at `cls`'s type, so a `from_real` that raises or changes type must give them another seed.
- `tasks/reference/blade-dict-interchange.md` (the graded silent-drop).
