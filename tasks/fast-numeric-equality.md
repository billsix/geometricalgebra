# Fast path for numeric `__eq__`: don't call `sympy.simplify` when both coefficients are plain numbers

**Status:** READY — filed 2026-09-06 by Fable from a modelviewprojection profile; anchors, test plan and acceptance below verified the same day. William Emerison Six <billsix@gmail.com> said "don't start it yet" — not started.
**Priority:** 4
**Difficulty:** 2
**Related:** `tasks/consolidate-symbolic-equality-predicate.md` (the symbolic half; this task is about the numeric case that never needed sympy), `tasks/reference/symbolic-equality.md`.

## BLUF

The generated `__eq__` (`tools/gen_specialized.py`, per field `a == b or sympy.simplify(sympify(a) -
sympify(b)) == 0`) pays `sympy.simplify` whenever two **plain float** coefficients *differ* — the
common case for a game comparing positions. Measured in `github.com/billsix/modelviewprojection`
(gacalc 0.0.19, Python 3.14): `Vector(3.0, 4.0) == Vector(1.5, -2.0)` costs **48 µs** (a tuple
comparison: 0.018 µs); beatstreets' `target != self.vpos` per fighter per frame made `__eq__` 71 ms of
a 173 ms profile (1189 calls). Fix: when both coefficients are `int`/`float` (not sympy objects),
return `a == b` directly — the simplify branch exists to prove symbolic equality and can never turn two
unequal floats into equal ones. Expected: ~0.2 µs per comparison; symbolic behaviour unchanged.

## Where it lives (verified 2026-09-06 against the checkout at 0.0.18; the generated code is the same in the 0.0.19 wheel)

- `tools/gen_specialized.py:885-935` — `field_equal` builds, per coefficient field,
  `self.<f> == other.<f> or sympy.simplify(sympy.sympify(self.<f>) - sympy.sympify(other.<f>)) == 0`.
  Its docstring (lines 887-896) says the native `==` "is exact and instant for numeric `Coef` (a numeric
  multivector never touches sympy)" — true only when the coefficients are **equal**; when two floats
  differ the `or` falls into `simplify`, which is the measured 48 µs (`Vector(3.0, 4.0) == Vector(1.5, -2.0)`).
- The generated result is visible in `src/gacalc/g2.py:1211` (`Vector.__eq__`), `g3.py:1756`, and
  every other specialized type (`grep -n "def __eq__" src/gacalc/g*.py`); regenerate, don't hand-edit.
- The cross-type fallback (`gen_specialized.py:937-960`, blade-dict generator) has the same shape and
  the same fix.
- Tests: `tests/test_multivector.py` / `tests/test_graded.py` hold the equality tests; the symbolic
  cases that must keep passing are listed in `tasks/reference/symbolic-equality.md` ("Limits").
- `CHANGELOG.md` `## [Unreleased]` (line 12) takes the entry: Fixed — numeric `==` no longer calls
  `sympy.simplify` when two plain-number coefficients differ (perf only; results unchanged).

## Plan

- In the generator's `__eq__` template (`field_equal`, and the blade-dict fallback): `if isinstance(a, (int, float)) and isinstance(b, (int, float)):
  compare directly` before the sympy branch (or `if not (isinstance(a, sympy.Basic) or isinstance(b,
  sympy.Basic))`). Regenerate; the existing symbolic tests must still pass.
- Add a test (`tests/test_multivector.py`): two differing numeric vectors compare unequal **without**
  `sympy.simplify` being called (`unittest.mock.patch("sympy.simplify")` asserting `not called`), an
  int-vs-float pair still compares by value (`1 * e_1 == 1.0 * e_1`), and a structurally-different
  symbolic pair (`(x + 1)**2` vs `x**2 + 2*x + 1`) still compares equal through `simplify`.
- Acceptance: `python -c` timing of the differing-float comparison drops from ~48 µs to well under 1 µs;
  `tests/` green; 0.0.20 entry in the changelog; modelviewprojection re-profiles beatstreets with
  `tools/ctc_profile_update.py` after bumping its pin (its `__eq__` share should vanish).
- `ruff` + `ty check src tests` + full suite; changelog entry (a behaviour-preserving speedup; not
  breaking).
