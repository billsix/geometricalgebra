# Fast path for numeric `__eq__`: don't call `sympy.simplify` when both coefficients are plain numbers

**Created:** 2026-09-06 · **Completed:** 2026-09-09
**Related:** `tasks/archive/2026/10/05/consolidate-symbolic-equality-predicate.md` (the symbolic
half; this task was the numeric case that never needed sympy), `tasks/reference/symbolic-equality.md`
(where the rationale was harvested).

## The problem

The generated `__eq__` (`field_equal` in `tools/gen_specialized.py`) compared each coefficient field
as `a == b or sympy.simplify(sympy.sympify(a) - sympy.sympify(b)) == 0`. Its docstring said native
`==` "is exact and instant for numeric `Coef`", which held only when coefficients were equal: when two
floats differed, the `or` fell into `simplify`. Measured in github.com/billsix/modelviewprojection
(gacalc 0.0.19, Python 3.14): `Vector(3.0, 4.0) == Vector(1.5, -2.0)` cost **48 µs** (a tuple
comparison costs 0.018 µs), and beatstreets' per-fighter-per-frame `target != self.vpos` made
`__eq__` 71 ms of a 173 ms profile (1189 calls). The simplify branch exists to prove symbolic
equality and can never make two unequal floats equal, so plain numbers can be compared directly.
The cross-type blade-dict fallback had the same shape.

## What changed

- **`base._coef_eq`**: one hand-written predicate that the generated `__eq__` calls from both its
  same-type and blade-dict paths, comparing `int`/`float` pairs directly and using `simplify` only
  otherwise. The plan had sketched an inline `isinstance` guard emitted into the generator template;
  since both call sites needed the rule, it went into `base.py` instead of being emitted twice as AST.
- Three tests in `tests/test_multivector.py`: differing numeric vectors compare unequal with
  `sympy.simplify` patched to raise; an int/float pair still compares by value (`1 * e_1 == 1.0 * e_1`);
  `(x + 1)**2` still equals `x**2 + 2*x + 1` through `simplify`.
- `CHANGELOG.md` entry under `[Unreleased]` (Fixed; a behaviour-preserving speedup, not breaking) —
  not under 0.0.20 as first planned, because 0.0.20 was tagged 2026-09-06 before the fix.

## Verification

48 µs → **0.391 µs** (~123×) on `Vector(3.0, 4.0) == Vector(1.5, -2.0)`, beating the "well under
1 µs" bar. `make format`, `make test` (564 passed), `make check-generated`, `make check-regions` green.
