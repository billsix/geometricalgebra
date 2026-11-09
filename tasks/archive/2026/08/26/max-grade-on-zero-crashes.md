# `max_grade()` (and the grade predicates) crash on the zero multivector

**Created:** 2026-08-26 · **Completed:** 2026-08-26

## The bug

`max_grade()` was `max(self.grades())`, and `grades()` returns `[]` for a zero multivector (empty
blade dict), so `max([])` raised `ValueError: max() iterable argument is empty`. Everything routed
through `max_grade` crashed on zero: `is_r_vector()`, `is_homogeneous_of_grade_r()`, and so
`is_vector()` / `is_bivector()` / `is_trivector()`. It lived in the shared base, so every
representation crashed (`Gn.zero()`, `g2.Vector.zero()`, `g2.G.zero()` all raised from
`.is_vector()`, verified 2026-08-26).

Blast radius was narrower than it looked: products with a zero operand were safe (no blades, so the
product loop short-circuits before any `max_grade()` call), so it was not a silent wrong-answer bug.
The exposure was the predicates: `measure._require_vectors` (so `content` / `area` / `volume` /
`signed_content` crashed on a zero-vector input), `frame.py` (`if not v.is_vector()`), and the
`assert *.is_vector()` checks in `transforms.py`. It was surfaced by
`tasks/archive/2026/08/26/signed-content-on-gn-via-dual.md`.

The inconsistency that pointed at the fix: `is_scalar()` is `self == self.r_vector_part(0)`, does not
use `max_grade`, and already returned `True` for zero, so `Gn.zero().is_scalar()` was `True` while
`Gn.zero().is_vector()` crashed.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-08-26)

**Zero is homogeneous of every grade** — the maintainer: "go with your recommendation, whatever
makes a cleaner API." This is the mathematical convention (zero lies in every grade subspace) and
matches `is_scalar(0) == True`. The rejected alternative was treating zero as grade-0 only (or no
grade), so `is_vector(0) == False`: it would give `_require_vectors` a clean rejection, but it
contradicts `is_scalar(0)` and the math, and makes `content([0])` raise instead of returning `0`.

## What changed

Two edits in `src/gacalc/base.py`:

- `max_grade()` → `max(self.grades(), default=0)`.
- `is_homogeneous_of_grade_r(r)` → `not grades or (max(grades) == r and self.is_r_vector())`.

On zero, `max_grade == 0` and `is_scalar == is_vector == is_bivector == is_trivector == is_r_vector
== True` (verified across `Gn`, a graded `Vector`, the full `G`, and another graded type); products
with a zero operand still return zero. `content([Gn.zero()])` now returns `0`, and an all-zero
`signed_content` raises via its own `k != n` guard (`n = 0`) instead of the `is_vector` crash, so the
signed-content task's all-zero test stayed green.

## Verification

410 tests green, including the new regression test
`tests/test_multivector.py::test_zero_multivector_is_homogeneous_of_every_grade`; ruff + ty clean.
