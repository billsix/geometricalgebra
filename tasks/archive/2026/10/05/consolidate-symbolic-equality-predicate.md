# Consolidate the symbolic-equality predicate; expand symbolic tests

**Created:** 2026-08-27 · **Completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>); 695 tests,
format/ty green.

## Summary

The maintainer's idea, verbatim: *"Understand sympy equal better, expand on tests, figure out if I can use
how that works."* The **understand** half was done first as `tasks/reference/symbolic-equality.md` (the
generated `__eq__` is per field `structural == OR simplify(sympify(l) − sympify(r)) == 0`, its limits, and
the duplicated test helpers). This task did the **use/expand** half: one public predicate replaced the
hand-rolled helpers, and the symbolic tests grew. It waited on two API decisions (below) until 2026-10-05.

Starting state: the `simplify(a − b) == 0` logic lived in the generated `__eq__` (`tools/gen_specialized.py`
› `eq_method()`) and was re-implemented in tests (`_same_value()` in `tests/test_conformance.py`,
`simplify_equal()` in `tests/test_graded.py`, plus inline one-offs). On 2026-09-09 the per-coefficient rule
was moved into one place, `base._coef_eq`, by `tasks/archive/2026/09/09/fast-numeric-equality.md`, so the
new predicate could delegate to it rather than re-implement it. Numeric equality (`MultiVectorBase.isclose`)
is the separate sibling (`tasks/reference/approximate-float-equality.md`).

## Decisions (the maintainer, 2026-10-05)

1. **Expose it as a public method** `MultiVectorBase.symbolically_equal(other, *, subs=None)`, one home for
   tests and callers (option (a); the rejected option (b) was a test-only helper in `tests/`).
2. **Return a plain `bool`**, conservative: `False` means "not proven equal" (option (a); the rejected
   option (b) was to raise or flag "undecided" when `simplify` cannot prove it).

## What was done

- **Implementation** (`src/gacalc/base.py`): blade-dict-wise over the union of present blades, so any two
  representations compare; per blade it delegates to `_coef_eq` (exact for plain numbers,
  `simplify`-backed when a side is symbolic). With `subs` (type `gacalc.base.SymbolicSubstitution =
  Mapping[sympy.Basic | complex, sympy.Expr | complex]`) it applies the substitution to each blade's
  difference before `simplify`. That is the "hand sympy the relation" recipe from the rotor work
  (`{s**2: 1 - c**2}`), which is why the parameter exists.
- **The three hand-rolled copies were removed** and their call sites rewritten to the method:
  `test_conformance._same_value` (3 sites), `test_graded.simplify_equal` (2), and
  `test_rotor_from_vectors._simplify_equal` (10). Scalar-level one-offs (`scalar_eq`, the `content`
  assertions in `test_measure.py`) compare coefficients, not multivectors, and stayed.
- **New `tests/test_symbolic_equality.py`** pins structurally different but equal forms, unequal values and
  a blade present on one side only, exact numeric comparison, cross-representation (`Gn` vs `g2`), and the
  substitution path (`sqrt(4c⁴ + 4s²c²)` vs `2c`: `False` without the relation, `True` with it).
- **Docs:** `symbolic-equality.md` gained "The public predicate" section in place of the "currently
  duplicated" one; one-liners in README and `CLAUDE.md`; a `CHANGELOG` Added entry.
