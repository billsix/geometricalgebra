# `normalize()` of an int/symbolic-zero vector returns silent `nan` (should raise)

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-08-13
**Origin:** found while verifying `harvest-api-design-rationale-from-archive` (2026-08-13) —
the archived "no zero-safe normalize → it raises" claim turned out only half true.

## The wart

`MultiVectorBase.normalize()` is `self * (abs(self) ** (-1))`. For a **zero** vector the two
numeric paths diverge (verified 2026-08-13):

- **float-zero** (`Vector2(0.0, 0.0)`) → `abs` is `0.0`, and `0.0 ** -1` raises
  **`ZeroDivisionError`** — contract-correct, matches pygame.
- **int/symbolic-zero** (`Vector2.zero()`, `Vector2(0, 0)`) → `abs` routes through sympy
  (`magnitude` sympifies an `int` `|A|²`), `sympy.Integer(0) ** -1` is `zoo` (complex
  infinity), and `0 * zoo` is `nan` — so `.normalize()` returns
  `Vector2(coeff_e_1=nan, coeff_e_2=nan)` **silently, no raise**.

The silent `nan` is the wart: a degenerate operation yields a `nan`-poisoned value instead
of failing loudly. It's documented in `tasks/reference/design-decisions.md` (the declined
vector-API entry, "API & conventions"); this task is whether to *fix* it.

## Options (decide before implementing)

1. **Raise uniformly (recommended).** Guard `normalize()` — and check `inverse()`, which has
   the same `mag_sq ** -1` shape — to raise a clear error (a `ValueError("cannot normalize a
   zero multivector")`, or `ZeroDivisionError` for parity with the float path) when
   `magnitude_squared` is structurally zero, regardless of coefficient type. A `nan`-poisoned
   multivector is worse than a clean error, and this unifies the two paths.
2. **Leave as-is, document only.** Already documented; the float path (what numeric consumers
   actually hit) already raises, so the blast radius is narrow. Lowest effort.
3. **In between** — guard only the symbolic/int path so the float `ZeroDivisionError` is
   untouched.

## Notes / constraints

- The int-vs-float split in `magnitude`/`inverse` is **deliberate** (numeric preservation —
  see `design-decisions.md` and `tests/test_numeric_magnitude.py`); a fix must **not**
  reintroduce an unconditional sympify, and must keep float→float / int→exact / symbolic→symbolic.
- Add a guard test (likely `tests/test_numeric_magnitude.py`): zero vector of each coefficient
  kind → the chosen behavior.
- Confirm whether `inverse()` of a zero multivector shares the `nan`-silent behavior (likely).
